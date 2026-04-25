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
    ("AWS Access Key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("GitHub Token", re.compile(r"\bghp_[A-Za-z0-9]{36}\b")),
    ("Generic API Key", re.compile(r"(?i)\b(api[_-]?key|token|secret|password)\b\s*[:=]\s*['\"]([^'\"]{8,})['\"]")),
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
    if not value:
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

    return False


def _iter_text_files(path: str):
    """Yield text files from a directory or a single file target."""
    target = Path(path)
    ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", ".next", ".dist"}
    ignored_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".pdf", ".zip", ".exe", ".dll", ".pyc"}

    if target.is_file():
        yield target
        return

    if not target.exists():
        return

    for item in target.rglob("*"):
        if not item.is_file():
            continue
        if item.suffix.lower() in ignored_suffixes:
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
                    if entropy < 3.6 and detector_name == "Generic API Key":
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
                print("⚠️  Legacy truffleHog detected; using built-in fallback secret scanner for filesystem scanning")
            elif result.returncode not in (0, 1):
                print(f"⚠️  TruffleHog error: {(result.stderr or '').strip()}")

        except subprocess.TimeoutExpired:
            print("⚠️  TruffleHog scan timed out; using fallback scanner")
        except Exception as e:
            print(f"⚠️  TruffleHog invocation failed ({str(e)}); using fallback scanner")
    else:
        print("⚠️  TruffleHog not installed; using built-in fallback secret scanner")

    return _fallback_regex_scan(path)
