"""
Concise output formatting - brief, actionable information
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box


console = Console()


def render_finding_brief(finding: Dict[str, Any]) -> None:
    """Render a single finding in brief format"""
    category = finding.get("category", "Unknown")
    severity = finding.get("severity", "MEDIUM")
    location = finding.get("location", "unknown")
    
    # Color based on severity
    color = {
        "CRITICAL": "red",
        "HIGH": "yellow",
        "MEDIUM": "blue",
        "LOW": "dim",
    }.get(severity, "white")
    
    console.print(f"[{color}]●[/{color}] [{color}]{severity}[/{color}] - {category} in `{location}`")
    
    # Show fix if available
    remediation = finding.get("remediation", "")
    if remediation:
        # Extract key action
        if "remove" in remediation.lower():
            console.print(f"  [dim]→ Remove hardcoded value[/dim]")
        elif "pin" in remediation.lower():
            console.print(f"  [dim]→ Pin to specific version[/dim]")
        elif "restrict" in remediation.lower() or "permission" in remediation.lower():
            console.print(f"  [dim]→ Restrict permissions[/dim]")
        elif "update" in remediation.lower():
            console.print(f"  [dim]→ Update to patched version[/dim]")


def render_analysis_brief(analysis: Dict[str, Any]) -> None:
    """Render AI analysis in brief format"""
    repo = analysis.get("repository", "unknown")
    risk_score = analysis.get("risk_score", 0)
    risk_level = analysis.get("risk_level", "LOW")
    findings = analysis.get("findings", [])
    
    # Header
    console.print()
    console.print(f"[bold cyan]📊 {repo}[/bold cyan]")
    
    # Risk score
    color = {
        "CRITICAL": "red",
        "HIGH": "yellow",
        "MEDIUM": "blue",
        "LOW": "green",
    }.get(risk_level, "white")
    
    console.print(f"[{color}]Risk: {risk_level} ({risk_score}/100)[/{color}]")
    console.print()
    
    # Findings summary
    if not findings:
        console.print("[green]✅ No issues found[/green]")
        return
    
    # Count by severity
    severity_counts = {}
    for f in findings:
        sev = f.get("severity", "MEDIUM")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    
    console.print(f"[yellow]⚠️  {len(findings)} issue(s):[/yellow]")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if sev in severity_counts:
            color = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "blue",
                "LOW": "dim",
            }.get(sev, "white")
            console.print(f"  [{color}]{sev}: {severity_counts[sev]}[/{color}]")
    
    console.print()
    
    # Top findings
    console.print("[bold]Top Issues:[/bold]")
    for finding in findings[:5]:
        render_finding_brief(finding)
    
    if len(findings) > 5:
        console.print(f"  [dim]... and {len(findings) - 5} more[/dim]")
    
    console.print()
    
    # Recommendations
    recommendations = analysis.get("recommendations", [])
    if recommendations:
        console.print("[bold]Actions:[/bold]")
        for rec in recommendations[:3]:
            console.print(f"  • {rec}")
        if len(recommendations) > 3:
            console.print(f"  [dim]... and {len(recommendations) - 3} more[/dim]")


def render_decision_brief(decision: Dict[str, Any]) -> None:
    """Render autonomous decision in brief format"""
    action = decision.get("action", "warn_only")
    severity = decision.get("severity", "MEDIUM")
    finding_id = decision.get("finding_id", "unknown")
    
    # Action icon
    icons = {
        "block_pipeline": "🚫",
        "require_approval": "⏸️",
        "create_pr": "📝",
        "open_issue": "📋",
        "suggest_fix": "💡",
        "warn_only": "⚠️",
    }
    
    icon = icons.get(action, "•")
    
    # Color
    color = {
        "CRITICAL": "red",
        "HIGH": "yellow",
        "MEDIUM": "blue",
        "LOW": "dim",
    }.get(severity, "white")
    
    console.print(f"{icon} [{color}]{action.replace('_', ' ').title()}[/{color}] - {finding_id}")


def render_simulation_brief(simulation: Dict[str, Any]) -> None:
    """Render simulation results in brief format"""
    repo = simulation.get("repository", "unknown")
    overall_action = simulation.get("overall_action", "warn_only")
    decisions = simulation.get("decisions", [])
    blocked = simulation.get("blocked", False)
    requires_approval = simulation.get("requires_approval", False)
    
    console.print()
    console.print(f"[bold cyan]🎬 Simulation: {repo}[/bold cyan]")
    console.print()
    
    # Overall status
    if blocked:
        console.print("[red]🚫 Pipeline would be BLOCKED[/red]")
    elif requires_approval:
        console.print("[yellow]⏸️  Manual approval REQUIRED[/yellow]")
    else:
        console.print("[green]✅ Pipeline would proceed with warnings[/green]")
    
    console.print()
    
    # Decision summary
    console.print(f"[bold]Decisions ({len(decisions)}):[/bold]")
    
    # Group by action
    action_counts = {}
    for d in decisions:
        action = d.get("action", "warn_only")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    for action, count in action_counts.items():
        icon = {
            "block_pipeline": "🚫",
            "require_approval": "⏸️",
            "create_pr": "📝",
            "open_issue": "📋",
            "suggest_fix": "💡",
            "warn_only": "⚠️",
        }.get(action, "•")
        
        console.print(f"  {icon} {action.replace('_', ' ').title()}: {count}")
    
    console.print()
    
    # Stats
    fixes_suggested = simulation.get("fixes_suggested", 0)
    issues_to_open = simulation.get("issues_to_open", 0)
    prs_to_create = simulation.get("prs_to_create", 0)
    
    if fixes_suggested > 0:
        console.print(f"[green]💡 {fixes_suggested} fix(es) available[/green]")
    if prs_to_create > 0:
        console.print(f"[blue]📝 {prs_to_create} PR(s) ready to create[/blue]")
    if issues_to_open > 0:
        console.print(f"[yellow]📋 {issues_to_open} issue(s) to track[/yellow]")


def render_pr_result(result: Dict[str, Any]) -> None:
    """Render PR creation result"""
    console.print()
    console.print("[bold green]✅ Pull Request Created[/bold green]")
    console.print()
    console.print(f"  PR: #{result['pr_number']}")
    console.print(f"  URL: {result['pr_url']}")
    console.print(f"  Branch: {result['branch']}")
    console.print(f"  Files: {result['files_changed']}")
    console.print()
    console.print("[dim]No cloning required - patched remotely via Git Data API[/dim]")
