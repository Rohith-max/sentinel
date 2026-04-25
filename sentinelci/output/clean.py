"""
Clean, professional output formatting without emojis
"""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box
from typing import List, Dict, Any

console = Console()


# Status indicators (no emojis)
STATUS_SUCCESS = "[green]SUCCESS[/green]"
STATUS_FAILED = "[red]FAILED[/red]"
STATUS_WARNING = "[yellow]WARNING[/yellow]"
STATUS_INFO = "[cyan]INFO[/cyan]"


def print_header(title: str, subtitle: str = None) -> None:
    """Print section header"""
    console.print()
    console.print(f"[bold cyan]{title}[/bold cyan]")
    if subtitle:
        console.print(f"[dim]{subtitle}[/dim]")
    console.print()


def print_success(message: str) -> None:
    """Print success message"""
    console.print(f"[green]SUCCESS:[/green] {message}")


def print_error(message: str) -> None:
    """Print error message"""
    console.print(f"[red]ERROR:[/red] {message}")


def print_warning(message: str) -> None:
    """Print warning message"""
    console.print(f"[yellow]WARNING:[/yellow] {message}")


def print_info(message: str) -> None:
    """Print info message"""
    console.print(f"[cyan]INFO:[/cyan] {message}")


def print_step(step_num: int, total: int, description: str) -> None:
    """Print step progress"""
    console.print(f"[cyan]Step {step_num}/{total}:[/cyan] {description}")


def print_table(title: str, headers: List[str], rows: List[List[str]], styles: List[str] = None) -> None:
    """Print formatted table"""
    table = Table(
        title=title,
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
    )
    
    # Add columns
    for i, header in enumerate(headers):
        style = styles[i] if styles and i < len(styles) else None
        table.add_column(header, style=style)
    
    # Add rows
    for row in rows:
        table.add_row(*row)
    
    console.print(table)
    console.print()


def print_panel(content: str, title: str = None, border_style: str = "cyan") -> None:
    """Print content in a panel"""
    console.print()
    console.print(Panel(
        content,
        title=title,
        border_style=border_style,
        box=box.ROUNDED,
    ))
    console.print()


def print_findings_summary(findings: List[Dict[str, Any]]) -> None:
    """Print clean findings summary"""
    if not findings:
        print_success("No security issues found")
        return
    
    # Count by severity
    severity_counts = {}
    for finding in findings:
        severity = finding.get("severity", "UNKNOWN")
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    # Print summary
    console.print()
    console.print(f"[bold]Security Scan Results[/bold]")
    console.print(f"Total Issues: {len(findings)}")
    console.print()
    
    for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        if severity in severity_counts:
            color = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "blue",
                "LOW": "dim",
            }.get(severity, "white")
            console.print(f"  [{color}]{severity}:[/{color}] {severity_counts[severity]}")
    
    console.print()


def print_scan_progress(current: int, total: int, item: str) -> None:
    """Print scan progress"""
    console.print(f"[dim]Scanning [{current}/{total}]:[/dim] {item}")


def print_divider() -> None:
    """Print section divider"""
    console.print("[dim]" + "-" * 70 + "[/dim]")


def confirm(message: str, default: bool = False) -> bool:
    """Ask for confirmation"""
    from rich.prompt import Confirm
    return Confirm.ask(message, default=default)


def prompt(message: str, password: bool = False) -> str:
    """Prompt for input"""
    from rich.prompt import Prompt
    return Prompt.ask(message, password=password)
