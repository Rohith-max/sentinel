"""
Terminal dashboard for GitHub security analysis
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.text import Text
from rich import box


console = Console()


def render_github_dashboard(analysis: Dict[str, Any], risk_score: Dict[str, Any]) -> None:
    """
    Render comprehensive GitHub security dashboard

    Args:
        analysis: Security analysis results
        risk_score: Risk score calculation
    """
    console.clear()
    
    console.print(
        Panel(
            f"[bold cyan]GitHub Security Analysis[/bold cyan]\n"
            f"Repository: [yellow]{analysis['repository']}[/yellow]\n"
            f"Analyzed: {analysis['timestamp'][:19]}",
            box=box.DOUBLE,
        )
    )
    console.print()

    _render_risk_score(risk_score)
    console.print()

    _render_webhooks(analysis.get("webhooks", []))
    console.print()

    _render_workflows(analysis.get("workflows", []))
    console.print()

    _render_ci_cd_files(analysis.get("ci_cd_files", {}))
    console.print()

    _render_branch_protection(analysis.get("branch_protection", {}))
    console.print()

    _render_secret_scanning(analysis.get("secret_scanning", []))
    console.print()

    _render_dependabot(analysis.get("dependabot", []))
    console.print()

    _render_security_advisories(analysis.get("security_advisories", []))
    console.print()

    _render_failed_workflows(analysis.get("failed_workflows", []))
    console.print()

    _render_permissions(analysis.get("permissions", {}))
    console.print()


def _render_risk_score(risk_score: Dict[str, Any]) -> None:
    """Render risk score panel"""
    level = risk_score["level"]
    score = risk_score["score"]
    
    color_map = {
        "LOW": "green",
        "MEDIUM": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red",
    }
    
    color = color_map.get(level, "white")
    
    factors_text = "\n".join(f"• {factor}" for factor in risk_score["factors"]) if risk_score["factors"] else "No significant risk factors"
    
    console.print(
        Panel(
            f"[bold {color}]Risk Level: {level}[/bold {color}]\n"
            f"Risk Score: [{color}]{score}/100[/{color}]\n\n"
            f"[bold]Risk Factors:[/bold]\n{factors_text}",
            title="🎯 Risk Assessment",
            border_style=color,
        )
    )


def _render_webhooks(webhooks: List[Dict[str, Any]]) -> None:
    """Render webhooks table"""
    if not webhooks:
        console.print("[dim]No webhooks configured[/dim]")
        return

    if "error" in webhooks[0]:
        console.print(f"[yellow]⚠️  Webhooks: {webhooks[0]['error']}[/yellow]")
        return

    table = Table(title="🔗 Webhooks", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("URL", style="blue")
    table.add_column("Events", style="magenta")
    table.add_column("Active", style="green")

    for hook in webhooks:
        events = ", ".join(hook.get("events", [])[:3])
        if len(hook.get("events", [])) > 3:
            events += "..."
        
        active_icon = "✓" if hook.get("active") else "✗"
        active_color = "green" if hook.get("active") else "red"
        
        table.add_row(
            str(hook.get("id", "")),
            hook.get("url", "")[:50],
            events,
            f"[{active_color}]{active_icon}[/{active_color}]",
        )

    console.print(table)


def _render_workflows(workflows: List[Dict[str, Any]]) -> None:
    """Render GitHub Actions workflows table"""
    if not workflows:
        console.print("[dim]No GitHub Actions workflows found[/dim]")
        return

    if "error" in workflows[0]:
        console.print(f"[yellow]⚠️  Workflows: {workflows[0]['error']}[/yellow]")
        return

    table = Table(title="⚙️  GitHub Actions Workflows", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Path", style="blue")
    table.add_column("State", style="green")

    for wf in workflows:
        state_color = "green" if wf.get("state") == "active" else "yellow"
        
        table.add_row(
            wf.get("name", ""),
            wf.get("path", ""),
            f"[{state_color}]{wf.get('state', '')}[/{state_color}]",
        )

    console.print(table)


def _render_ci_cd_files(ci_files: Dict[str, bool]) -> None:
    """Render CI/CD files detection"""
    table = Table(title="📋 CI/CD Configuration Files", box=box.ROUNDED)
    table.add_column("File/Directory", style="cyan")
    table.add_column("Detected", style="green")

    for file_path, detected in ci_files.items():
        icon = "[green]✓[/green]" if detected else "[dim]✗[/dim]"
        table.add_row(file_path, icon)

    console.print(table)


def _render_branch_protection(protection: Dict[str, Any]) -> None:
    """Render branch protection rules"""
    if "error" in protection:
        console.print(f"[yellow]⚠️  Branch Protection: {protection['error']}[/yellow]")
        return

    if not protection.get("enabled"):
        console.print(
            Panel(
                f"[red]Branch protection is NOT enabled on '{protection.get('branch', 'main')}'[/red]\n"
                "This is a security risk!",
                title="🛡️  Branch Protection",
                border_style="red",
            )
        )
        return

    status_checks = protection.get("required_status_checks")
    pr_reviews = protection.get("required_pull_request_reviews")
    
    details = []
    details.append(f"Branch: [cyan]{protection.get('branch')}[/cyan]")
    details.append(f"Enforce for admins: {'✓' if protection.get('enforce_admins') else '✗'}")
    details.append(f"Require signatures: {'✓' if protection.get('required_signatures') else '✗'}")
    
    if status_checks:
        details.append(f"Required status checks: [green]✓[/green]")
    
    if pr_reviews:
        required_reviewers = pr_reviews.get("required_approving_review_count", 0)
        details.append(f"Required PR reviews: [green]{required_reviewers}[/green]")

    console.print(
        Panel(
            "\n".join(details),
            title="🛡️  Branch Protection",
            border_style="green",
        )
    )


def _render_secret_scanning(alerts: List[Dict[str, Any]]) -> None:
    """Render secret scanning alerts"""
    if not alerts:
        console.print("[dim]No secret scanning alerts[/dim]")
        return

    if "error" in alerts[0] or "message" in alerts[0]:
        msg = alerts[0].get("error") or alerts[0].get("message")
        console.print(f"[yellow]⚠️  Secret Scanning: {msg}[/yellow]")
        return

    table = Table(title="🔐 Secret Scanning Alerts", box=box.ROUNDED, border_style="red")
    table.add_column("Number", style="cyan")
    table.add_column("Type", style="yellow")
    table.add_column("State", style="red")
    table.add_column("Created", style="blue")

    for alert in alerts:
        table.add_row(
            str(alert.get("number", "")),
            alert.get("secret_type", ""),
            alert.get("state", ""),
            alert.get("created_at", "")[:10],
        )

    console.print(table)


def _render_dependabot(alerts: List[Dict[str, Any]]) -> None:
    """Render Dependabot alerts"""
    if not alerts:
        console.print("[dim]No Dependabot alerts[/dim]")
        return

    if "error" in alerts[0] or "message" in alerts[0]:
        msg = alerts[0].get("error") or alerts[0].get("message")
        console.print(f"[yellow]⚠️  Dependabot: {msg}[/yellow]")
        return

    table = Table(title="🤖 Dependabot Alerts", box=box.ROUNDED)
    table.add_column("Number", style="cyan")
    table.add_column("Package", style="blue")
    table.add_column("Severity", style="red")
    table.add_column("Summary", style="yellow")

    for alert in alerts:
        severity = alert.get("severity", "").upper()
        severity_color = {
            "CRITICAL": "red",
            "HIGH": "orange1",
            "MEDIUM": "yellow",
            "LOW": "blue",
        }.get(severity, "white")
        
        table.add_row(
            str(alert.get("number", "")),
            alert.get("package", ""),
            f"[{severity_color}]{severity}[/{severity_color}]",
            alert.get("summary", "")[:50],
        )

    console.print(table)


def _render_security_advisories(advisories: List[Dict[str, Any]]) -> None:
    """Render security advisories"""
    if not advisories:
        console.print("[green]✓ No open security advisories[/green]")
        return

    if "error" in advisories[0]:
        console.print(f"[yellow]⚠️  Security Advisories: {advisories[0]['error']}[/yellow]")
        return

    table = Table(title="📢 Security Advisories", box=box.ROUNDED)
    table.add_column("GHSA ID", style="cyan")
    table.add_column("Severity", style="red")
    table.add_column("Summary", style="yellow")
    table.add_column("State", style="blue")

    for adv in advisories:
        severity = adv.get("severity", "").upper()
        severity_color = {
            "CRITICAL": "red",
            "HIGH": "orange1",
            "MEDIUM": "yellow",
            "LOW": "blue",
        }.get(severity, "white")
        
        table.add_row(
            adv.get("ghsa_id", ""),
            f"[{severity_color}]{severity}[/{severity_color}]",
            adv.get("summary", "")[:50],
            adv.get("state", ""),
        )

    console.print(table)


def _render_failed_workflows(runs: List[Dict[str, Any]]) -> None:
    """Render recent failed workflow runs"""
    if not runs:
        console.print("[green]✓ No recent failed workflows[/green]")
        return

    if "error" in runs[0]:
        console.print(f"[yellow]⚠️  Failed Workflows: {runs[0]['error']}[/yellow]")
        return

    table = Table(title="❌ Recent Failed Workflow Runs", box=box.ROUNDED)
    table.add_column("Name", style="cyan")
    table.add_column("Conclusion", style="red")
    table.add_column("Updated", style="blue")

    for run in runs:
        table.add_row(
            run.get("name", "")[:40],
            run.get("conclusion", ""),
            run.get("updated_at", "")[:10],
        )

    console.print(table)


def _render_permissions(permissions: Dict[str, Any]) -> None:
    """Render repository permissions"""
    if "error" in permissions:
        console.print(f"[yellow]⚠️  Permissions: {permissions['error']}[/yellow]")
        return

    visibility = permissions.get("visibility", "unknown")
    visibility_color = "red" if visibility == "public" else "green"

    details = []
    details.append(f"Visibility: [{visibility_color}]{visibility.upper()}[/{visibility_color}]")
    details.append(f"Issues: {'✓' if permissions.get('has_issues') else '✗'}")
    details.append(f"Wiki: {'✓' if permissions.get('has_wiki') else '✗'}")
    details.append(f"Forking: {'✓' if permissions.get('allow_forking') else '✗'}")
    details.append(f"Archived: {'✓' if permissions.get('archived') else '✗'}")

    console.print(
        Panel(
            "\n".join(details),
            title="🔒 Repository Permissions",
            border_style=visibility_color,
        )
    )
