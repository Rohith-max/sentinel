"""
Automated remediation helpers for SCI findings.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Dict, Any, List

from sentinelci.scanner import collect_findings


_SECRET_ASSIGNMENT_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*\s*=\s*)([\"\'])([^\"\']+)(\2)")


def _resolve_file_path(base_path: str, finding_file: str) -> Path | None:
    """Resolve finding file paths that may be relative to scan target."""
    candidate = Path(finding_file)
    if candidate.exists():
        return candidate

    base = Path(base_path)
    joined = (base / finding_file).resolve() if base.exists() else candidate
    if joined.exists():
        return joined

    return None


def _redact_secret_line(line: str) -> str:
    """Redact obvious assignment-based secrets in a single line."""
    updated = _SECRET_ASSIGNMENT_RE.sub(r'\1\2REDACTED_BY_SENTINALCI\4', line)
    if updated != line:
        return updated

    stripped = line.strip()
    if stripped.startswith("#"):
        return line

    return f"# SENTINALCI_REDACTED: {line}"


def _neutralize_url_line(line: str) -> str:
    """Neutralize suspicious homograph URLs by commenting the line."""
    stripped = line.strip()
    if stripped.startswith("#"):
        return line
    return f"# SENTINALCI_BLOCKED_HOMOGRAPH: {line}"


def _apply_line_update(file_path: Path, line_number: int, new_line: str, backup: bool) -> bool:
    """Apply a line-level file update safely."""
    if line_number <= 0:
        return False

    content = file_path.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
    original_content = "".join(content)
    if line_number > len(content):
        return False

    idx = line_number - 1
    old_line = content[idx]

    if old_line.endswith("\r\n"):
        nl = "\r\n"
    elif old_line.endswith("\n"):
        nl = "\n"
    else:
        nl = ""

    replacement = new_line.rstrip("\r\n") + nl
    if replacement == old_line:
        return False

    content[idx] = replacement

    if backup:
        backup_path = file_path.with_suffix(file_path.suffix + ".sci.bak")
        if not backup_path.exists():
            backup_path.write_text(original_content, encoding="utf-8")

    file_path.write_text("".join(content), encoding="utf-8")
    return True


def run_fix(
    path: str = ".",
    use_diff: bool = False,
    severity: str = "medium",
    enable_firmware: bool = True,
    enable_urls: bool = True,
    dry_run: bool = False,
    backup: bool = True,
) -> Dict[str, Any]:
    """Find and remediate issues where safe automatic fixes are available."""
    findings = collect_findings(
        path=path,
        use_diff=use_diff,
        severity=severity,
        enable_firmware=enable_firmware,
        enable_urls=enable_urls,
    )

    summary: Dict[str, Any] = {
        "total_findings": len(findings),
        "fixed": 0,
        "fixable": 0,
        "skipped": 0,
        "dry_run": dry_run,
        "changes": [],
    }

    for finding in findings:
        finding_type = str(finding.get("type", ""))
        file_value = str(finding.get("file", ""))
        line_number = int(finding.get("line_number", 0) or 0)

        if not file_value or line_number <= 0:
            summary["skipped"] += 1
            continue

        if finding_type == "Homograph URL":
            summary["fixable"] += 1
            resolved = _resolve_file_path(path, file_value)
            if not resolved:
                summary["skipped"] += 1
                continue

            if dry_run:
                summary["changes"].append(
                    {
                        "file": str(resolved),
                        "line": line_number,
                        "action": "comment_homograph_url",
                    }
                )
                continue

            content = resolved.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
            if line_number > len(content):
                summary["skipped"] += 1
                continue

            new_line = _neutralize_url_line(content[line_number - 1])
            if _apply_line_update(resolved, line_number, new_line, backup=backup):
                summary["fixed"] += 1
                summary["changes"].append(
                    {
                        "file": str(resolved),
                        "line": line_number,
                        "action": "comment_homograph_url",
                    }
                )
            else:
                summary["skipped"] += 1
            continue

        # Secret findings are emitted by detector names, so treat anything with value_masked as secret-like.
        if "value_masked" in finding:
            summary["fixable"] += 1
            resolved = _resolve_file_path(path, file_value)
            if not resolved:
                summary["skipped"] += 1
                continue

            if dry_run:
                summary["changes"].append(
                    {
                        "file": str(resolved),
                        "line": line_number,
                        "action": "redact_secret_assignment",
                    }
                )
                continue

            content = resolved.read_text(encoding="utf-8", errors="ignore").splitlines(keepends=True)
            if line_number > len(content):
                summary["skipped"] += 1
                continue

            new_line = _redact_secret_line(content[line_number - 1])
            if _apply_line_update(resolved, line_number, new_line, backup=backup):
                summary["fixed"] += 1
                summary["changes"].append(
                    {
                        "file": str(resolved),
                        "line": line_number,
                        "action": "redact_secret_assignment",
                    }
                )
            else:
                summary["skipped"] += 1
            continue

        # CVE findings are advisory and not auto-fixable safely.
        summary["skipped"] += 1

    return summary
