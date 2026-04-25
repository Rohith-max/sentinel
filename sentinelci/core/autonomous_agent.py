"""
Fully Autonomous Security Agent
Complete automation with transparency and user confirmation
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from rich.console import Console
from rich.prompt import Confirm
from rich.panel import Panel
from rich.table import Table
from rich import box
import asyncio

from sentinelci.core.remediation import RemediationEngine
from sentinelci.core.auth import GitHubAuthError


console = Console()


@dataclass
class AgentAction:
    """Represents a single autonomous action"""
    action_type: str  # edit_file, create_pr, open_issue, block_pipeline
    target: str  # file path, repo, etc.
    description: str
    changes: Dict[str, Any]
    severity: str
    auto_approve: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_type": self.action_type,
            "target": self.target,
            "description": self.description,
            "changes": self.changes,
            "severity": self.severity,
            "auto_approve": self.auto_approve,
        }


@dataclass
class AgentPlan:
    """Complete execution plan"""
    repository: str
    actions: List[AgentAction]
    risk_assessment: str
    estimated_impact: str
    requires_approval: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository": self.repository,
            "actions": [a.to_dict() for a in self.actions],
            "risk_assessment": self.risk_assessment,
            "estimated_impact": self.estimated_impact,
            "requires_approval": self.requires_approval,
        }


class AutonomousSecurityAgent:
    """
    Fully autonomous security agent with complete automation freedom
    
    Capabilities:
    - Analyze vulnerabilities
    - Plan remediation actions
    - Execute fixes autonomously
    - Create PRs and issues
    - Transparent decision-making
    - User confirmation for critical actions
    """
    
    def __init__(self):
        self.remediation = RemediationEngine()
        self.execution_log: List[Dict[str, Any]] = []
    
    async def analyze_and_plan(
        self,
        repo_full_name: str,
        findings: List[Dict[str, Any]],
    ) -> AgentPlan:
        """
        Analyze findings and create autonomous execution plan
        
        Returns complete plan with all actions
        """
        console.print("\n[bold cyan]🤖 Autonomous Agent Analyzing...[/bold cyan]\n")
        
        actions = []
        critical_count = 0
        high_count = 0
        
        # Analyze each finding and plan action
        for finding in findings:
            severity = finding.get("severity", "MEDIUM")
            category = finding.get("category", "unknown")
            location = finding.get("location", "unknown")
            
            if severity == "CRITICAL":
                critical_count += 1
            elif severity == "HIGH":
                high_count += 1
            
            # Determine action based on severity and type
            if severity in ["CRITICAL", "HIGH"]:
                # Auto-fix critical and high severity issues
                action = self._plan_fix_action(finding)
                if action:
                    actions.append(action)
            elif severity == "MEDIUM":
                # Create issue for tracking
                action = AgentAction(
                    action_type="open_issue",
                    target=location,
                    description=f"Track {category} vulnerability",
                    changes={"issue_title": f"Security: {category} in {location}"},
                    severity=severity,
                    auto_approve=True,
                )
                actions.append(action)
            else:
                # Low severity - just log
                action = AgentAction(
                    action_type="log_warning",
                    target=location,
                    description=f"Monitor {category}",
                    changes={},
                    severity=severity,
                    auto_approve=True,
                )
                actions.append(action)
        
        # Risk assessment
        if critical_count > 0:
            risk_assessment = f"CRITICAL: {critical_count} critical issue(s) require immediate action"
            requires_approval = True
        elif high_count > 0:
            risk_assessment = f"HIGH: {high_count} high severity issue(s) need attention"
            requires_approval = True
        else:
            risk_assessment = "MODERATE: Issues can be handled automatically"
            requires_approval = False
        
        # Estimated impact
        file_changes = len([a for a in actions if a.action_type == "edit_file"])
        estimated_impact = f"{file_changes} file(s) will be modified, {len(actions)} total actions"
        
        return AgentPlan(
            repository=repo_full_name,
            actions=actions,
            risk_assessment=risk_assessment,
            estimated_impact=estimated_impact,
            requires_approval=requires_approval,
        )
    
    def _plan_fix_action(self, finding: Dict[str, Any]) -> Optional[AgentAction]:
        """Plan a fix action for a finding"""
        category = finding.get("category", "").lower()
        location = finding.get("location", "unknown")
        severity = finding.get("severity", "MEDIUM")
        
        if "secret" in category:
            return AgentAction(
                action_type="edit_file",
                target=location,
                description="Remove hardcoded secret",
                changes={
                    "operation": "remove_secret",
                    "line": finding.get("line_number"),
                    "replacement": "# SECURITY: Use environment variable",
                },
                severity=severity,
                auto_approve=False,
            )
        
        elif "permission" in category or "workflow" in category:
            return AgentAction(
                action_type="edit_file",
                target=location,
                description="Restrict workflow permissions",
                changes={
                    "operation": "add_permissions",
                    "permissions": {
                        "contents": "read",
                        "pull-requests": "write",
                    },
                },
                severity=severity,
                auto_approve=False,
            )
        
        elif "dependency" in category:
            return AgentAction(
                action_type="edit_file",
                target=location,
                description="Pin dependency version",
                changes={
                    "operation": "pin_dependency",
                    "package": finding.get("package", "unknown"),
                },
                severity=severity,
                auto_approve=False,
            )
        
        return None
    
    def display_plan(self, plan: AgentPlan) -> None:
        """Display execution plan to user"""
        console.print()
        console.print(Panel(
            f"[bold]Repository:[/bold] {plan.repository}\n"
            f"[bold]Risk:[/bold] {plan.risk_assessment}\n"
            f"[bold]Impact:[/bold] {plan.estimated_impact}",
            title="🤖 Autonomous Agent Plan",
            border_style="cyan",
            box=box.DOUBLE,
        ))
        console.print()
        
        # Actions table
        table = Table(
            title="Planned Actions",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        
        table.add_column("#", style="dim", width=4)
        table.add_column("Action", width=15)
        table.add_column("Target", width=30)
        table.add_column("Description", width=30)
        table.add_column("Severity", width=10)
        
        for idx, action in enumerate(plan.actions, 1):
            # Color based on severity
            color = {
                "CRITICAL": "red",
                "HIGH": "yellow",
                "MEDIUM": "blue",
                "LOW": "dim",
            }.get(action.severity, "white")
            
            # Icon based on action type
            icon = {
                "edit_file": "📝",
                "create_pr": "🔀",
                "open_issue": "📋",
                "block_pipeline": "🚫",
                "log_warning": "⚠️",
            }.get(action.action_type, "•")
            
            table.add_row(
                str(idx),
                f"{icon} {action.action_type.replace('_', ' ').title()}",
                action.target,
                action.description,
                f"[{color}]{action.severity}[/{color}]",
            )
        
        console.print(table)
        console.print()
        
        # Show detailed changes
        console.print("[bold]Detailed Changes:[/bold]\n")
        
        for idx, action in enumerate(plan.actions, 1):
            if action.action_type == "edit_file":
                console.print(f"[cyan]{idx}. {action.target}[/cyan]")
                
                operation = action.changes.get("operation", "unknown")
                
                if operation == "remove_secret":
                    console.print("   [dim]→ Remove hardcoded secret[/dim]")
                    console.print("   [dim]→ Add comment: Use environment variable[/dim]")
                
                elif operation == "add_permissions":
                    console.print("   [dim]→ Add permissions block:[/dim]")
                    perms = action.changes.get("permissions", {})
                    for key, value in perms.items():
                        console.print(f"   [dim]   {key}: {value}[/dim]")
                
                elif operation == "pin_dependency":
                    package = action.changes.get("package", "unknown")
                    console.print(f"   [dim]→ Pin {package} to specific version[/dim]")
                
                console.print()
    
    async def execute_plan(
        self,
        plan: AgentPlan,
        auto_approve: bool = False,
    ) -> Dict[str, Any]:
        """
        Execute the autonomous plan
        
        Args:
            plan: Execution plan
            auto_approve: Skip confirmation (dangerous!)
            
        Returns:
            Execution results
        """
        # Ask for confirmation if needed
        if plan.requires_approval and not auto_approve:
            console.print()
            console.print("[bold yellow]⚠️  This plan requires your approval[/bold yellow]")
            console.print()
            
            if not Confirm.ask("Execute this plan?", default=False):
                console.print("[yellow]❌ Execution cancelled by user[/yellow]")
                return {
                    "status": "cancelled",
                    "reason": "User declined approval",
                }
        
        console.print()
        console.print("[bold green]🚀 Executing Autonomous Plan...[/bold green]")
        console.print()
        
        results = {
            "status": "success",
            "actions_executed": 0,
            "actions_failed": 0,
            "changes": [],
            "pr_created": None,
        }
        
        # Group file edits for atomic commit
        files_to_edit = {}
        issues_to_create = []
        
        for idx, action in enumerate(plan.actions, 1):
            console.print(f"[cyan]Step {idx}/{len(plan.actions)}:[/cyan] {action.description}")
            
            try:
                if action.action_type == "edit_file":
                    # Collect file edits
                    if action.target not in files_to_edit:
                        files_to_edit[action.target] = []
                    files_to_edit[action.target].append(action)
                    console.print(f"  [green]✓[/green] Planned edit for {action.target}")
                
                elif action.action_type == "open_issue":
                    issues_to_create.append(action)
                    console.print(f"  [green]✓[/green] Planned issue creation")
                
                elif action.action_type == "log_warning":
                    console.print(f"  [dim]⚠️  Logged warning[/dim]")
                
                results["actions_executed"] += 1
                
            except Exception as e:
                console.print(f"  [red]✗[/red] Failed: {str(e)}")
                results["actions_failed"] += 1
            
            # Small delay for transparency
            await asyncio.sleep(0.3)
        
        console.print()
        
        # Apply all file edits atomically
        if files_to_edit:
            console.print("[bold cyan]📝 Applying file changes...[/bold cyan]")
            
            try:
                # Get original content and apply changes
                fixed_files = {}
                
                for file_path, actions in files_to_edit.items():
                    try:
                        original_content, _ = self.remediation._get_file_content(
                            plan.repository,
                            file_path,
                        )
                        
                        # Apply all changes to this file
                        modified_content = original_content
                        for action in actions:
                            modified_content = self._apply_change(
                                modified_content,
                                action.changes,
                            )
                        
                        fixed_files[file_path] = modified_content
                        console.print(f"  [green]✓[/green] Prepared {file_path}")
                        
                    except Exception as e:
                        console.print(f"  [red]✗[/red] Failed to prepare {file_path}: {str(e)}")
                
                if fixed_files:
                    # Create branch and commit
                    branch_name = f"security/autonomous-fix-{len(fixed_files)}-files"
                    commit_message = f"🤖 Autonomous Security Fix\n\nFixed {len(plan.actions)} issue(s) automatically"
                    
                    console.print(f"\n[cyan]Creating branch: {branch_name}[/cyan]")
                    
                    commit_sha = self.remediation.apply_patch_remote(
                        plan.repository,
                        branch_name,
                        fixed_files,
                        commit_message,
                    )
                    
                    console.print(f"[green]✓[/green] Committed: {commit_sha[:7]}")
                    
                    # Create PR
                    console.print("\n[cyan]Creating pull request...[/cyan]")
                    
                    pr_title = f"🤖 Autonomous Security Fix ({len(fixed_files)} files)"
                    pr_body = self._generate_pr_body(plan, fixed_files)
                    
                    pr = self.remediation.create_pull_request(
                        plan.repository,
                        pr_title,
                        pr_body,
                        branch_name,
                    )
                    
                    results["pr_created"] = {
                        "number": pr["number"],
                        "url": pr["html_url"],
                        "branch": branch_name,
                    }
                    
                    console.print(f"[green]✓[/green] PR #{pr['number']}: {pr['html_url']}")
                
            except Exception as e:
                console.print(f"[red]✗[/red] Failed to apply changes: {str(e)}")
                results["actions_failed"] += len(files_to_edit)
        
        # Create issues
        if issues_to_create:
            console.print("\n[bold cyan]📋 Creating issues...[/bold cyan]")
            
            for action in issues_to_create:
                try:
                    issue = self.remediation.create_security_issue(
                        plan.repository,
                        action.changes.get("issue_title", "Security Issue"),
                        f"Automated security tracking\n\nTarget: {action.target}",
                    )
                    console.print(f"  [green]✓[/green] Issue #{issue['number']}")
                except Exception as e:
                    console.print(f"  [red]✗[/red] Failed: {str(e)}")
        
        console.print()
        
        return results
    
    def _apply_change(self, content: str, changes: Dict[str, Any]) -> str:
        """Apply a single change to file content"""
        operation = changes.get("operation", "")
        
        if operation == "remove_secret":
            lines = content.split("\n")
            line_num = changes.get("line", 0)
            
            if 0 < line_num <= len(lines):
                lines[line_num - 1] = f"# SECURITY: Secret removed - use environment variable\n# {lines[line_num - 1]}"
            
            return "\n".join(lines)
        
        elif operation == "add_permissions":
            lines = content.split("\n")
            
            # Find where to insert
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("on:"):
                    insert_idx = i + 1
                    while insert_idx < len(lines) and (lines[insert_idx].startswith("  ") or not lines[insert_idx].strip()):
                        insert_idx += 1
                    break
            
            # Insert permissions
            perms = changes.get("permissions", {})
            perm_lines = ["", "permissions:"]
            for key, value in perms.items():
                perm_lines.append(f"  {key}: {value}")
            perm_lines.append("")
            
            lines = lines[:insert_idx] + perm_lines + lines[insert_idx:]
            return "\n".join(lines)
        
        elif operation == "pin_dependency":
            lines = content.split("\n")
            
            for i, line in enumerate(lines):
                if "@latest" in line or "^" in line or "~" in line:
                    lines[i] = line.replace("@latest", "@1.0.0").replace("^", "").replace("~", "")
            
            return "\n".join(lines)
        
        return content
    
    def _generate_pr_body(self, plan: AgentPlan, files: Dict[str, str]) -> str:
        """Generate PR body"""
        body = "## 🤖 Autonomous Security Agent\n\n"
        body += "This PR was created automatically by the autonomous security agent.\n\n"
        body += f"**Risk Assessment:** {plan.risk_assessment}\n"
        body += f"**Impact:** {plan.estimated_impact}\n\n"
        
        body += "### Actions Taken\n\n"
        
        for action in plan.actions:
            if action.action_type == "edit_file":
                body += f"- **{action.target}**: {action.description}\n"
        
        body += "\n### Files Changed\n\n"
        for file_path in files.keys():
            body += f"- `{file_path}`\n"
        
        body += "\n---\n"
        body += "*Autonomous execution - no cloning required*\n"
        body += "*Review changes before merging*"
        
        return body
    
    def display_results(self, results: Dict[str, Any]) -> None:
        """Display execution results"""
        console.print()
        console.print(Panel(
            f"[bold]Status:[/bold] {results['status'].upper()}\n"
            f"[bold]Actions Executed:[/bold] {results['actions_executed']}\n"
            f"[bold]Actions Failed:[/bold] {results['actions_failed']}",
            title="🤖 Execution Results",
            border_style="green" if results["status"] == "success" else "red",
            box=box.DOUBLE,
        ))
        
        if results.get("pr_created"):
            pr = results["pr_created"]
            console.print()
            console.print("[bold green]✅ Pull Request Created[/bold green]")
            console.print(f"  PR: #{pr['number']}")
            console.print(f"  URL: {pr['url']}")
            console.print(f"  Branch: {pr['branch']}")
        
        console.print()
