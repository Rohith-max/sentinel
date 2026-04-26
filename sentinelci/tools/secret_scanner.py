"""
Secret scanning tool using TruffleHog
"""

import json
import math
import re
import shutil
import sys
import subprocess
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List


@dataclass
class SecretFinding:
    """Represents a secret finding"""

    type: str
    file: str
    line_number: int
    value_masked: str  # Masked sensitive value
    severity: str
    confidence: float
    description: str

    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return asdict(self)


def _mask_value(value: str, show_chars: int = 4) -> str:
    """Mask sensitive value, showing only first and last few characters"""
    if len(value) <= show_chars * 2:
        return "*" * len(value)
    return value[:show_chars] + "*" * (len(value) - show_chars * 2) + value[-show_chars:]


_SECRET_PATTERNS = [
    # Only match actual hardcoded values, not variable assignments
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("AWS Secret Key", re.compile(r"(?i)aws[_-]?secret[_-]?(?:access[_-]?)?key['\"]?\s*[:=]\s*['\"]([A-Za-z0-9/+=]{40})['\"]")),
    ("GitHub Token", re.compile(r"\bghp_[A-Za-z0-9]{36,}\b")),
    ("GitHub PAT", re.compile(r"\bgho_[A-Za-z0-9]{36,}\b")),
    ("Stripe Secret Key", re.compile(r"\bsk_live_[A-Za-z0-9]{24,}\b")),
    ("Stripe Publishable Key", re.compile(r"\bpk_live_[A-Za-z0-9]{24,}\b")),
    ("OpenAI API Key", re.compile(r"\bsk-[A-Za-z0-9]{48,}\b")),
    ("Anthropic API Key", re.compile(r"\bsk-ant-api03-[A-Za-z0-9_-]{95,}\b")),
    ("Groq API Key", re.compile(r"\bgsk_[A-Za-z0-9]{52,}\b")),
    ("SendGrid API Key", re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b")),
    ("Slack Webhook", re.compile(r"https://hooks\.slack\.com/services/T[A-Z0-9]{8,}/B[A-Z0-9]{8,}/[A-Za-z0-9]{24,}")),
    ("Private Key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("JWT Token", re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b")),
    # Only match actual hardcoded credentials with real values (minimum 16 chars)
    ("Hardcoded Password", re.compile(r"(?i)(?:password|passwd|pwd)['\"]?\s*[:=]\s*['\"]([A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?]{16,})['\"]")),
    ("Hardcoded API Key", re.compile(r"(?i)(?:api[_-]?key|apikey)['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_-]{32,})['\"]")),
    ("Hardcoded Token", re.compile(r"(?i)(?:auth[_-]?token|access[_-]?token|bearer[_-]?token)['\"]?\s*[:=]\s*['\"]([A-Za-z0-9_-]{32,})['\"]")),
]

_PLACEHOLDER_MARKERS = {
    "example",
    "demo",
    "format",
    "placeholder",
    "dummy",
    "fake",
    "test",
    "sample",
    "your_",
    "abc123",
    "def456",
    "xxxx",
    "here",
}

_EXPLANATORY_CONTEXT_MARKERS = {
    "before (wrong)",
    "after (correct)",
    "example fix",
    "format only",
    "demo format",
    "get your",
    "api key from",
    "request-an-api-key",
}


def _shannon_entropy(value: str) -> float:
    """Compute Shannon entropy for heuristic secret detection."""
    if not value or len(value) < 16:  # Require minimum 16 chars for entropy check
        return 0.0
    freq = {char: value.count(char) / len(value) for char in set(value)}
    return -sum(p * math.log2(p) for p in freq.values())


def _is_likely_placeholder(candidate: str, line: str) -> bool:
    """Heuristics to ignore example/demo tokens in docs and prompts."""
    candidate_l = candidate.lower()
    line_l = line.lower()

    if any(marker in candidate_l for marker in _PLACEHOLDER_MARKERS):
        return True

    if any(marker in line_l for marker in _EXPLANATORY_CONTEXT_MARKERS):
        return True

    if candidate_l.startswith("sk-") and len(candidate) < 20:
        return True

    if "your_" in candidate_l and "_here" in candidate_l:
        return True

    if line_l.startswith("#") and any(word in line_l for word in ["comment", "example", "get", "from"]):
        return True
    
    # Ignore common UI/component property names
    ui_properties = {
        "placeholder", "label", "title", "description", "text", "value",
        "name", "id", "className", "style", "type", "variant", "size"
    }
    if candidate_l in ui_properties:
        return True
    
    # Ignore if it's in JSX/React context
    if any(jsx in line for jsx in ["<Text", "<TextInput", "<Input", "<Button", "placeholder=", "style="]):
        return True

    return False


def _iter_text_files(path: str):
    """Yield text files from a directory or a single file target."""
    target = Path(path)
    ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", ".next", ".dist", "test-vulnerable-repo", "test-repo-template", "tests", "test"}
    ignored_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".exe", ".dll", ".pyc"}
    ignored_files = {"TESTING_GUIDE.md", "TEST-RESULTS.md", "HOWTO-TEST.md"}

    if target.is_file():
        # Skip test/documentation files
        if target.name in ignored_files:
            return
        yield target
        return

    if not target.exists():
        return

    for item in target.rglob("*"):
        if not item.is_file():
            continue
        if item.suffix.lower() in ignored_suffixes:
            continue
        if item.name in ignored_files:
            continue
        if any(part in ignored_dirs for part in item.parts):
            continue
        yield item


def _fallback_regex_scan(path: str) -> List[SecretFinding]:
    """Fallback scanner when TruffleHog is unavailable or incompatible."""
    findings: List[SecretFinding] = []

    for file_path in _iter_text_files(path):
        try:
            lines = file_path.read_text(encoding="utf-8", errors="ignore").splitlines()
        except OSError:
            continue

        for line_num, line in enumerate(lines, start=1):
            if not line.strip() or line.strip().startswith("#"):
                continue

            for detector_name, pattern in _SECRET_PATTERNS:
                for match in pattern.finditer(line):
                    if match.groups() and len(match.groups()) >= 2:
                        candidate = match.group(2)
                    else:
                        candidate = match.group(0)

                    if len(candidate) < 8:
                        continue

                    if _is_likely_placeholder(candidate, line):
                        continue

                    entropy = _shannon_entropy(candidate)
                    # Require high entropy (4.5+) and minimum 16 characters for generic patterns
                    if entropy < 4.5 and detector_name in ["Hardcoded Password", "Hardcoded API Key", "Hardcoded Token"]:
                        continue
                    
                    # Skip if it looks like a variable name or common word
                    if len(candidate) < 16 and not any(c.isdigit() for c in candidate):
                        continue

                    findings.append(
                        SecretFinding(
                            type=detector_name,
                            file=str(file_path),
                            line_number=line_num,
                            value_masked=_mask_value(candidate),
                            severity="HIGH",
                            confidence=min(0.95, 0.55 + (entropy / 10.0)),
                            description=f"Potential secret detected by fallback scanner ({detector_name})",
                        )
                    )
    return findings


def _resolve_executable(name: str) -> str | None:
    """Resolve executable from PATH or active virtualenv Scripts directory."""
    resolved = shutil.which(name) or shutil.which(f"{name}.exe")
    if resolved:
        return resolved

    scripts_dir = Path(sys.executable).parent
    candidates = [scripts_dir / name, scripts_dir / f"{name}.exe"]
    for candidate in candidates:
        if candidate.exists():
            return str(candidate)
    return None


def _parse_trufflehog_filesystem_output(output: str) -> List[SecretFinding]:
    """Parse TruffleHog v3 JSON-lines filesystem output."""
    findings: List[SecretFinding] = []
    for line in output.strip().split("\n"):
        if not line.strip():
            continue
        try:
            data = json.loads(line)
        except json.JSONDecodeError:
            continue

        detector_name = data.get("DetectorName", "Unknown")
        file_path = data.get("SourceMetadata", {}).get("Data", {}).get("File", "unknown")
        line_num = data.get("SourceMetadata", {}).get("Data", {}).get("Line", 0)
        raw_value = data.get("Raw", "")
        verified = data.get("Verified", False)

        findings.append(
            SecretFinding(
                type=detector_name,
                file=file_path,
                line_number=line_num,
                value_masked=_mask_value(raw_value),
                severity="CRITICAL" if verified else "HIGH",
                confidence=0.95 if verified else 0.85,
                description=f"Detected {detector_name} secret",
            )
        )
    return findings


def scan_secrets(path: str = ".") -> List[SecretFinding]:
    """
    Scan for hardcoded secrets using TruffleHog

    Args:
        path: Directory or file to scan

    Returns:
        List of secret findings
    """
    findings: List[SecretFinding] = []
    trufflehog_path = _resolve_executable("trufflehog")

    if trufflehog_path:
        try:
            # Preferred modern invocation (v3+).
            result = subprocess.run(
                [trufflehog_path, "filesystem", path, "--json"],
                capture_output=True,
                text=True,
                timeout=90,
            )

            if result.returncode in (0, 1) and result.stdout.strip():
                return _parse_trufflehog_filesystem_output(result.stdout)

            # Legacy truffleHog v2 is git-history-only and cannot scan arbitrary paths.
            stderr_lower = (result.stderr or "").lower()
            if "unrecognized arguments" in stderr_lower or "git_url" in stderr_lower:
                # Silently fall back to built-in scanner for legacy TruffleHog
                pass
            elif result.returncode not in (0, 1):
                print(f"⚠️  TruffleHog error: {(result.stderr or '').strip()}")

        except subprocess.TimeoutExpired:
            print("⚠️  TruffleHog scan timed out; using fallback scanner")
        except Exception as e:
            print(f"⚠️  TruffleHog invocation failed ({str(e)}); using fallback scanner")
    # Silently use fallback scanner if TruffleHog not installed

    return _fallback_regex_scan(path)
