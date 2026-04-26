"""
Main scanner orchestration
"""

import asyncio
import time
import subprocess
from urllib.parse import quote
from typing import List, Dict, Any, Optional
from pathlib import Path

from sentinelci.tools.secret_scanner import scan_secrets
from sentinelci.tools.url_forensics import detect_homographs
from sentinelci.tools.firmware_cve import scan_firmware_cves
from sentinelci.tools.dependency_scanner import scan_dependencies
from sentinelci.tools.workflow_scanner import scan_workflows
from sentinelci.output.terminal import (
    render_findings,
    render_verdict,
    render_analysis,
)
from sentinelci.output.report import generate_json_report, generate_markdown_report
from sentinelci.agent import analyze_findings
from sentinelci.config import get_config


def _is_git_repo() -> bool:
    """Check whether current working directory is inside a git repository."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"
    except Exception:
        return False


def _current_branch() -> str:
    """Get current git branch name."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            branch = result.stdout.strip()
            return branch if branch else "main"
    except Exception:
        pass
    return "main"


def _get_remote_url(remote: str = "origin") -> Optional[str]:
    """Get git remote URL."""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            url = result.stdout.strip()
            return url if url else None
    except Exception:
        pass
    return None


def _build_pat_remote_url(remote_url: str, github_pat: str) -> Optional[str]:
    """Build HTTPS remote URL with PAT for GitHub auth."""
    normalized = remote_url.strip()
    if normalized.startswith("git@github.com:"):
        normalized = "https://github.com/" + normalized.split("git@github.com:", 1)[1]
    elif normalized.startswith("ssh://git@github.com/"):
        normalized = "https://github.com/" + normalized.split("ssh://git@github.com/", 1)[1]

    if not normalized.startswith("https://github.com/"):
        return None

    token = quote(github_pat, safe="")
    return normalized.replace("https://", f"https://x-access-token:{token}@", 1)


def _sync_github_remote(remote: str = "origin", branch: Optional[str] = None, github_pat: Optional[str] = None) -> bool:
    """Fetch latest refs from remote to sync watch/scan against GitHub changes."""
    target_branch = branch or _current_branch()

    try:
        if github_pat:
            remote_url = _get_remote_url(remote)
            auth_url = _build_pat_remote_url(remote_url, github_pat) if remote_url else None
            if auth_url:
                # Update local remote-tracking ref using authenticated URL.
                result = subprocess.run(
                    ["git", "fetch", auth_url, f"{target_branch}:refs/remotes/{remote}/{target_branch}"],
                    capture_output=True,
                    text=True,
                    timeout=60,
                )
            else:
                result = subprocess.run(
                    ["git", "fetch", remote, target_branch],
                    capture_output=True,
                    text=True,
                    timeout=45,
                )
        else:
            result = subprocess.run(
                ["git", "fetch", remote, target_branch],
                capture_output=True,
                text=True,
                timeout=45,
            )
        if result.returncode != 0:
            print(f"⚠️  GitHub sync failed: {(result.stderr or '').strip()}")
            return False
        return True
    except Exception as e:
        print(f"⚠️  GitHub sync error: {str(e)}")
        return False


def _get_git_diff_files(include_remote: bool = False, remote: str = "origin", branch: Optional[str] = None) -> List[str]:
    """Get changed file paths from local git diff and optional remote diff."""
    try:
        changed_files: set[str] = set()
        for cmd in (["git", "diff", "--name-only"], ["git", "diff", "--cached", "--name-only"]):
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.splitlines():
                    file_path = line.strip()
                    if file_path and Path(file_path).exists():
                        changed_files.add(file_path)

        if include_remote:
            remote_branch = branch or _current_branch()
            remote_target = f"{remote}/{remote_branch}"
            result = subprocess.run(
                ["git", "diff", "--name-only", f"HEAD..{remote_target}"],
                capture_output=True,
                text=True,
                timeout=20,
            )
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.splitlines():
                    file_path = line.strip()
                    if file_path and Path(file_path).exists():
                        changed_files.add(file_path)
        return sorted(changed_files)
    except Exception:
        return []


def _get_scan_targets(
    path: str,
    use_diff: bool,
    sync_github: bool = False,
    remote: str = "origin",
    branch: Optional[str] = None,
) -> List[str]:
    """Determine concrete scan targets from path and diff settings."""
    if use_diff:
        diff_files = _get_git_diff_files(include_remote=sync_github, remote=remote, branch=branch)
        if diff_files:
            return diff_files
        return [path]

    target = Path(path)
    if target.exists() and target.is_file():
        return [str(target)]
    return [path]


def _summarize_targets(scan_targets: List[str]) -> str:
    """Human-friendly display summary for scan targets."""
    if len(scan_targets) == 1:
        return scan_targets[0]
    return f"{len(scan_targets)} changed files"


def _filter_findings_by_severity(
    findings: List[Dict[str, Any]],
    severity: str,
) -> List[Dict[str, Any]]:
    """Filter findings by minimum severity"""
    severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
    min_level = severity_order.get(severity.upper(), 2)

    return [
        f for f in findings
        if severity_order.get(f.get("severity", "LOW").upper(), 1) >= min_level
    ]


async def _run_parallel_scans(
    scan_targets: List[str],
    enable_firmware: bool = True,
    enable_urls: bool = True,
    enable_dependencies: bool = True,
    enable_workflows: bool = True,
) -> List[Dict[str, Any]]:
    """Run enabled scans in parallel and normalize findings."""
    all_findings: List[Dict[str, Any]] = []
    tasks = []

    if len(scan_targets) == 1:
        tasks.append(asyncio.to_thread(scan_secrets, scan_targets[0]))
    else:
        for target in scan_targets:
            tasks.append(asyncio.to_thread(scan_secrets, target))

    if enable_urls:
        if len(scan_targets) == 1:
            tasks.append(asyncio.to_thread(detect_homographs, scan_targets[0]))
        else:
            for target in scan_targets:
                tasks.append(asyncio.to_thread(detect_homographs, target))

    if enable_dependencies:
        if len(scan_targets) == 1:
            tasks.append(asyncio.to_thread(scan_dependencies, scan_targets[0]))
        else:
            for target in scan_targets:
                tasks.append(asyncio.to_thread(scan_dependencies, target))

    if enable_workflows:
        if len(scan_targets) == 1:
            tasks.append(asyncio.to_thread(scan_workflows, scan_targets[0]))
        else:
            for target in scan_targets:
                tasks.append(asyncio.to_thread(scan_workflows, target))

    if enable_firmware:
        firmware_extensions = {".bin", ".img", ".rom", ".fw", ".firmware"}
        firmware_targets: List[str] = []
        for target in scan_targets:
            p = Path(target)
            if p.is_dir() or p.suffix.lower() in firmware_extensions:
                firmware_targets.append(target)

        if len(firmware_targets) == 1:
            tasks.append(asyncio.to_thread(scan_firmware_cves, firmware_targets[0]))
        elif len(firmware_targets) > 1:
            for target in firmware_targets:
                tasks.append(asyncio.to_thread(scan_firmware_cves, target))

    # Run in parallel
    results = await asyncio.gather(*tasks)

    # Convert all results to dictionaries.
    for result_list in results:
        for finding_obj in result_list:
            if hasattr(finding_obj, 'to_dict'):
                all_findings.append(finding_obj.to_dict())
            else:
                all_findings.append(finding_obj)

    # Deduplicate findings that may appear when scanning multiple changed files.
    deduped: List[Dict[str, Any]] = []
    seen: set[tuple] = set()
    for finding in all_findings:
        signature = (
            finding.get("type"),
            finding.get("file"),
            finding.get("line_number"),
            finding.get("description"),
            finding.get("severity"),
        )
        if signature in seen:
            continue
        seen.add(signature)
        deduped.append(finding)

    return deduped


def _snapshot_files(path: str) -> Dict[str, float]:
    """Capture a file modification snapshot for watch mode."""
    target = Path(path)
    if not target.exists():
        return {}

    if target.is_file():
        try:
            return {str(target): target.stat().st_mtime}
        except OSError:
            return {}

    snapshot: Dict[str, float] = {}
    ignored_dirs = {".git", "node_modules", "__pycache__", ".venv", ".next", ".dist"}

    for item in target.rglob("*"):
        if not item.is_file():
            continue
        if any(part in ignored_dirs for part in item.parts):
            continue
        try:
            snapshot[str(item)] = item.stat().st_mtime
        except OSError:
            continue
    return snapshot


def _changed_from_snapshots(previous: Dict[str, float], current: Dict[str, float]) -> List[str]:
    """Compute changed/added/deleted files between two snapshots."""
    changed: List[str] = []
    all_paths = set(previous) | set(current)
    for path in all_paths:
        if path not in previous or path not in current:
            changed.append(path)
            continue
        if previous[path] != current[path]:
            changed.append(path)
    return sorted(changed)


def run_scan(
    path: str = ".",
    use_diff: bool = False,
    severity: str = "medium",
    output_format: str = "terminal",
    output_file: Optional[str] = None,
    use_ai: bool = True,
    watch_mode: bool = False,
    watch_interval: float = 2.0,
    sync_github: bool = False,
    remote: str = "origin",
    branch: Optional[str] = None,
    github_pat: Optional[str] = None,
    halt_on_critical: bool = False,
    enable_firmware: bool = True,
    enable_urls: bool = True,
    enable_dependencies: bool = True,
    enable_workflows: bool = True,
) -> int:
    """
    Run security scan

    Args:
        path: Path to scan
        use_diff: Scan git diff only
        severity: Minimum severity to report
        output_format: Output format (terminal, json, markdown)
        output_file: File to save results
        use_ai: Enable AI analysis
        watch_mode: Watch for changes
        watch_interval: Polling interval in seconds for watch mode
        sync_github: Fetch from GitHub remote before diff scans
        remote: Git remote name for sync/diff operations
        branch: Git branch name to compare against remote
        github_pat: GitHub PAT for authenticated git fetch
        halt_on_critical: Exit with error on critical findings
        enable_firmware: Enable CVE scanning
        enable_urls: Enable URL detection
        enable_dependencies: Enable dependency vulnerability scanning
        enable_workflows: Enable GitHub Actions workflow scanning

    Returns:
        Exit code (0 = success, 1 = critical findings, 2 = error)
    """
    config = get_config()
    if use_ai and not config.validate():
        return 2

    if watch_mode:
        run_watch(
            path=path,
            severity=severity,
            output_format=output_format,
            output_file=output_file,
            use_ai=use_ai,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            halt_on_critical=halt_on_critical,
            enable_firmware=enable_firmware,
            enable_urls=enable_urls,
            enable_dependencies=enable_dependencies,
            enable_workflows=enable_workflows,
            interval_seconds=watch_interval,
        )
        return 0

    try:
        filtered_findings = collect_findings(
            path=path,
            use_diff=use_diff,
            severity=severity,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            enable_firmware=enable_firmware,
            enable_urls=enable_urls,
            enable_dependencies=enable_dependencies,
            enable_workflows=enable_workflows,
        )
    except Exception as e:
        print(f"❌ Scan failed: {str(e)}")
        return 2

    # Count by severity
    critical_count = len([f for f in filtered_findings if f.get("severity") == "CRITICAL"])
    high_count = len([f for f in filtered_findings if f.get("severity") == "HIGH"])

    # Render output
    if output_format == "terminal":
        render_findings(filtered_findings)
        render_verdict(critical_count, high_count, halt_on_critical)
    elif output_format == "json":
        json_report = generate_json_report(filtered_findings, output_file=output_file)
        if not output_file:
            print(json_report)
    elif output_format == "markdown":
        md_report = generate_markdown_report(filtered_findings, output_file=output_file)
        if not output_file:
            print(md_report)

    # Optional AI analysis
    if use_ai and filtered_findings:
        try:
            analysis = asyncio.run(analyze_findings(filtered_findings))
            if output_format == "terminal":
                render_analysis(analysis)
        except Exception as e:
            print(f"⚠️  AI analysis failed: {str(e)}")

    # Save JSON report when output_file is provided.
    if output_format != "json" and output_file:
        output_path = Path(output_file)
        json_output_path = output_path.with_suffix(".json") if output_path.suffix else Path(f"{output_file}.json")
        generate_json_report(filtered_findings, output_file=str(json_output_path))

    # Determine exit code
    if halt_on_critical and critical_count > 0:
        return 1
    elif critical_count > 0 or high_count > 0:
        return 0  # Still success but with findings

    return 0


def collect_findings(
    path: str = ".",
    use_diff: bool = False,
    severity: str = "medium",
    sync_github: bool = False,
    remote: str = "origin",
    branch: Optional[str] = None,
    github_pat: Optional[str] = None,
    enable_firmware: bool = True,
    enable_urls: bool = True,
    enable_dependencies: bool = True,
    enable_workflows: bool = True,
) -> List[Dict[str, Any]]:
    """Collect findings without rendering, useful for scan and fix flows."""
    if sync_github and _is_git_repo():
        config = get_config()
        effective_pat = github_pat or config.get_github_pat()
        _sync_github_remote(remote=remote, branch=branch, github_pat=effective_pat)

    scan_targets = _get_scan_targets(path, use_diff, sync_github=sync_github, remote=remote, branch=branch)
    
    # Show what we're scanning
    from rich.console import Console
    console = Console()
    
    target_summary = _summarize_targets(scan_targets)
    console.print(f"[cyan]🔍 Scanning:[/cyan] {target_summary}")
    
    # Show enabled scanners
    scanners = []
    scanners.append("secrets")
    if enable_dependencies:
        scanners.append("dependencies")
    if enable_workflows:
        scanners.append("workflows")
    if enable_urls:
        scanners.append("URLs")
    if enable_firmware:
        scanners.append("firmware CVEs")
    
    console.print(f"[dim]   Enabled scanners: {', '.join(scanners)}[/dim]")
    console.print()

    findings = asyncio.run(
        _run_parallel_scans(
            scan_targets,
            enable_firmware=enable_firmware,
            enable_urls=enable_urls,
            enable_dependencies=enable_dependencies,
            enable_workflows=enable_workflows,
        )
    )
    
    filtered = _filter_findings_by_severity(findings, severity)
    
    # Show scan results summary
    if filtered:
        console.print(f"[yellow]⚠️  Found {len(filtered)} issue(s) at {severity.upper()}+ severity[/yellow]\n")
    else:
        console.print(f"[green]✅ No issues found at {severity.upper()}+ severity[/green]\n")
    
    return filtered


def run_watch(
    path: str = ".",
    severity: str = "medium",
    output_format: str = "terminal",
    output_file: Optional[str] = None,
    use_ai: bool = True,
    sync_github: bool = False,
    remote: str = "origin",
    branch: Optional[str] = None,
    github_pat: Optional[str] = None,
    halt_on_critical: bool = False,
    enable_firmware: bool = True,
    enable_urls: bool = True,
    enable_dependencies: bool = True,
    enable_workflows: bool = True,
    interval_seconds: float = 2.0,
) -> None:
    """Continuously monitor local changes and rerun scans in real time."""
    print(f"👁️  SCI watch mode running for: {path}")
    print(f"⏱️  Poll interval: {interval_seconds:.1f}s")
    print("Press Ctrl+C to stop\n")

    # Run an initial baseline scan.
    run_scan(
        path=path,
        use_diff=False,
        severity=severity,
        output_format=output_format,
        output_file=output_file,
        use_ai=use_ai,
        watch_mode=False,
        halt_on_critical=halt_on_critical,
        enable_firmware=enable_firmware,
        enable_urls=enable_urls,
        enable_dependencies=enable_dependencies,
        enable_workflows=enable_workflows,
    )

    previous_snapshot = _snapshot_files(path)
    try:
        while True:
            time.sleep(interval_seconds)
            current_snapshot = _snapshot_files(path)
            changed_paths = _changed_from_snapshots(previous_snapshot, current_snapshot)
            if not changed_paths:
                continue

            previous_snapshot = current_snapshot
            print(f"\n🔄 Detected {len(changed_paths)} file change(s)")
            if len(changed_paths) <= 3:
                for changed in changed_paths:
                    print(f"   - {changed}")

            # Use git diff targets when possible for focused rescans.
            use_diff = _is_git_repo()
            run_scan(
                path=path,
                use_diff=use_diff,
                severity=severity,
                output_format=output_format,
                output_file=output_file,
                use_ai=use_ai,
                watch_mode=False,
                sync_github=sync_github,
                remote=remote,
                branch=branch,
                github_pat=github_pat,
                halt_on_critical=halt_on_critical,
                enable_firmware=enable_firmware,
                enable_urls=enable_urls,
                enable_dependencies=enable_dependencies,
                enable_workflows=enable_workflows,
            )
    except KeyboardInterrupt:
        print("\n⏹️  Watch mode stopped")
