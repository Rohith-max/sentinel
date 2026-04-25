"""
Terminal dashboard for AI security analysis and autonomous decisions
"""

from typing import Dict, Any, List
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.tree import Tree
from rich import box
from rich.text import Text


console = Console()


def render_ai_analysis(analysis: Dict[str, Any]) -> None:
    """
    Render AI security analysis dashboard

    Args:
        analysis: Analysis result dict
    """
    console.print()
    console.print(
        Panel(
            f"[bold cyan]AI Security Analysis[/bold cyan]\n"
            f"Repository: [yellow]{analysis['repository']}[/yellow]\n"
            f"Analyzed: {analysis['timestamp'][:19]}",
            box=box.DOUBLE,
        )
    )
    console.print()

    # Risk score
    _render_risk_score(analysis)
    console.print()

    # Findings
    findings = analysis.get("findings", [])
    if findings:
        _render_findings_table(findings)
        console.print()
        _render_findings_details(findings)
    else:
        console.print("[green]✅ No security issues detected[/green]")

    console.print()

    # Summary
    _render_summary(analysis)
    console.print()

    # Recommendations
    _render_recommendations(analysis.get("recommendations", []))
    console.print()

    # Audit explanation
    _render_audit_explanation(analysis.get("audit_explanation", ""))


def _render_risk_score(analysis: Dict[str, Any]) -> None:
    """Render risk score panel"""
    risk_score = analysis.get("risk_score", 0)
    risk_level = analysis.get("risk_level", "LOW")

    color_map = {
        "LOW": "green",
        "MEDIUM": "yellow",
        "HIGH": "orange1",
        "CRITICAL": "red",
    }

    color = color_map.get(risk_level, "white")

    # Create progress bar
    bar_length = 50
    filled = int((risk_score / 100) * bar_length)
    bar = "█" * filled + "░" * (bar_length - filled)

    console.print(
        Panel(
            f"[bold {color}]Risk Level: {risk_level}[/bold {color}]\n"
            f"Risk Score: [{color}]{risk_score}/100[/{color}]\n\n"
            f"[{color}]{bar}[/{color}]",
            title="🎯 Risk Assessment",
            border_style=color,
        )
    )


def _render_findings_table(findings: List[Dict[str, Any]]) -> None:
    """Render findings summary table"""
    table = Table(title="🔍 Security Findings Summary", box=box.ROUNDED)
    table.add_column("Category", style="cyan")
    table.add_column("Severity", style="bold")
    table.add_column("Title", style="yellow")
    table.add_column("Confidence", justify="center")

    severity_colors = {
        "CRITICAL": "red",
        "HIGH": "orange1",
        "MEDIUM": "yellow",
        "LOW": "blue",
    }

    for finding in findings:
        severity = finding.get("severity", "LOW")
        severity_color = severity_colors.get(severity, "white")
        confidence = finding.get("confidence", 0.0)

        table.add_row(
            finding.get("category", "unknown"),
            f"[{severity_color}]{severity}[/{severity_color}]",
            finding.get("title", "")[:50],
            f"{confidence:.0%}",
        )

    console.print(table)


def _render_findings_details(findings: List[Dict[str, Any]]) -> None:
    """Render detailed findings"""
    console.print("[bold]📋 Detailed Findings[/bold]\n")

    severity_colors = {
        "CRITICAL": "red",
        "HIGH": "orange1",
        "MEDIUM": "yellow",
        "LOW": "blue",
    }

    for idx, finding in enumerate(findings, 1):
        severity = finding.get("severity", "LOW")
        color = severity_colors.get(severity, "white")

        content = []
        content.append(f"[bold]Category:[/bold] {finding.get('category', 'unknown')}")
        content.append(f"[bold]Severity:[/bold] [{color}]{severity}[/{color}]")
        content.append(f"[bold]Location:[/bold] {finding.get('location', 'unknown')}")
        content.append(f"[bold]Confidence:[/bold] {finding.get('confidence', 0.0):.0%}")
        content.append(f"\n[bold]Description:[/bold]\n{finding.get('description', '')}")
        
        if finding.get("evidence"):
            content.append(f"\n[bold]Evidence:[/bold]\n{finding.get('evidence', '')}")
        
        content.append(f"\n[bold]Remediation:[/bold]\n{finding.get('remediation', '')}")

        console.print(
            Panel(
                "\n".join(content),
                title=f"Finding {idx}: {finding.get('title', 'Unknown')}",
                border_style=color,
            )
        )
        console.print()


def _render_summary(analysis: Dict[str, Any]) -> None:
    """Render analysis summary"""
    summary = analysis.get("summary", "")
    if summary:
        console.print(
            Panel(
                summary,
                title="📊 Executive Summary",
                border_style="cyan",
            )
        )


def _render_recommendations(recommendations: List[str]) -> None:
    """Render recommendations"""
    if not recommendations:
        return

    console.print("[bold cyan]💡 Recommendations[/bold cyan]\n")

    for idx, rec in enumerate(recommendations, 1):
        console.print(f"  {idx}. {rec}")


def _render_audit_explanation(explanation: str) -> None:
    """Render audit explanation"""
    if explanation:
        console.print(
            Panel(
                explanation,
                title="📝 Audit Explanation",
                border_style="blue",
            )
        )


def render_autonomous_decisions(simulation: Dict[str, Any]) -> None:
    """
    Render autonomous decision simulation

    Args:
        simulation: Simulation result dict
    """
    console.print()
    console.print(
        Panel(
            f"[bold magenta]Autonomous Decision Simulation[/bold magenta]\n"
            f"Repository: [yellow]{simulation['repository']}[/yellow]\n"
            f"Timestamp: {simulation['timestamp'][:19]}",
            box=box.DOUBLE,
        )
    )
    console.print()

    # Overall action
    _render_overall_action(simulation)
    console.print()

    # Statistics
    _render_statistics(simulation)
    console.print()

    # Decisions
    decisions = simulation.get("decisions", [])
    if decisions:
        _render_decisions_tree(decisions)
        console.print()
        _render_decision_details(decisions)


def _render_overall_action(simulation: Dict[str, Any]) -> None:
    """Render overall action panel"""
    overall_action = simulation.get("overall_action", "warn_only")
    explanation = simulation.get("explanation", "")
    blocked = simulation.get("blocked", False)
    requires_approval = simulation.get("requires_approval", False)

    if blocked:
        color = "red"
        icon = "🚫"
        status = "BLOCKED"
    elif requires_approval:
        color = "yellow"
        icon = "⏸️"
        status = "APPROVAL REQUIRED"
    else:
        color = "green"
        icon = "✅"
        status = "ALLOWED"

    console.print(
        Panel(
            f"[bold {color}]{icon} Pipeline Status: {status}[/bold {color}]\n\n"
            f"{explanation}",
            title="🎬 Overall Decision",
            border_style=color,
        )
    )


def _render_statistics(simulation: Dict[str, Any]) -> None:
    """Render decision statistics"""
    table = Table(title="📊 Decision Statistics", box=box.ROUNDED)
    table.add_column("Metric", style="cyan")
    table.add_column("Count", justify="center", style="bold")

    table.add_row("Total Decisions", str(len(simulation.get("decisions", []))))
    table.add_row("Fixes Suggested", str(simulation.get("fixes_suggested", 0)))
    table.add_row("Issues to Open", str(simulation.get("issues_to_open", 0)))
    table.add_row("PRs to Create", str(simulation.get("prs_to_create", 0)))

    console.print(table)


def _render_decisions_tree(decisions: List[Dict[str, Any]]) -> None:
    """Render decisions as tree"""
    tree = Tree("[bold cyan]🌳 Decision Tree[/bold cyan]")

    action_groups = {}
    for decision in decisions:
        action = decision.get("action", "warn_only")
        if action not in action_groups:
            action_groups[action] = []
        action_groups[action].append(decision)

    action_icons = {
        "block_pipeline": "🚫",
        "require_approval": "⏸️",
        "suggest_fix": "💡",
        "open_issue": "📋",
        "create_pr": "📝",
        "warn_only": "⚠️",
    }

    for action, group_decisions in action_groups.items():
        icon = action_icons.get(action, "•")
        action_branch = tree.add(f"{icon} {action.replace('_', ' ').title()} ({len(group_decisions)})")
        
        for decision in group_decisions:
            action_branch.add(
                f"[{_get_severity_color(decision.get('severity', 'LOW'))}]"
                f"{decision.get('finding_id', 'Unknown')}"
                f"[/{_get_severity_color(decision.get('severity', 'LOW'))}]"
            )

    console.print(tree)


def _render_decision_details(decisions: List[Dict[str, Any]]) -> None:
    """Render detailed decision information"""
    console.print("[bold magenta]🔍 Decision Details[/bold magenta]\n")

    action_icons = {
        "block_pipeline": "🚫",
        "require_approval": "⏸️",
        "suggest_fix": "💡",
        "open_issue": "📋",
        "create_pr": "📝",
        "warn_only": "⚠️",
    }

    for idx, decision in enumerate(decisions, 1):
        action = decision.get("action", "warn_only")
        icon = action_icons.get(action, "•")
        severity = decision.get("severity", "LOW")
        color = _get_severity_color(severity)

        content = []
        content.append(f"[bold]Action:[/bold] {icon} {action.replace('_', ' ').title()}")
        content.append(f"[bold]Severity:[/bold] [{color}]{severity}[/{color}]")
        content.append(f"[bold]Confidence:[/bold] {decision.get('confidence', 0.0):.0%}")
        content.append(f"[bold]Reason:[/bold] {decision.get('reason', '')}")
        content.append(f"\n{decision.get('explanation', '')}")

        if decision.get("automated_fix"):
            content.append(f"\n[bold]Automated Fix:[/bold]\n```\n{decision.get('automated_fix', '')}\n```")

        if decision.get("pr_title"):
            content.append(f"\n[bold]PR Title:[/bold] {decision.get('pr_title', '')}")

        if decision.get("issue_title"):
            content.append(f"\n[bold]Issue Title:[/bold] {decision.get('issue_title', '')}")

        console.print(
            Panel(
                "\n".join(content),
                title=f"Decision {idx}: {decision.get('finding_id', 'Unknown')}",
                border_style=color,
            )
        )
        console.print()


def _get_severity_color(severity: str) -> str:
    """Get color for severity level"""
    colors = {
        "CRITICAL": "red",
        "HIGH": "orange1",
        "MEDIUM": "yellow",
        "LOW": "blue",
    }
    return colors.get(severity, "white")


def render_combined_report(analysis: Dict[str, Any], simulation: Dict[str, Any]) -> None:
    """
    Render combined analysis and simulation report

    Args:
        analysis: Analysis result dict
        simulation: Simulation result dict
    """
    render_ai_analysis(analysis)
    console.print("\n" + "="*70 + "\n")
    render_autonomous_decisions(simulation)
