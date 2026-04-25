"""
Verification system to check if autonomous agent actions were actually executed
"""

import requests
from typing import Dict, Any, List, Optional
from rich.console import Console
from rich.table import Table
from rich import box

from sentinelci.core.auth import GitHubAuth, GitHubAuthError

console = Console()


class ActionVerifier:
    """Verifies that autonomous agent actions were actually executed"""
    
    def __init__(self):
        self.auth = GitHubAuth()
        self.base_url = "https://api.github.com"
    
    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated headers"""
        pat = self.auth.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")
        
        return {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }
    
    def verify_execution_log(self, log_file: str) -> Dict[str, Any]:
        """
        Verify an execution log against actual GitHub state
        
        Returns verification report
        """
        import json
        
        try:
            with open(log_file, 'r') as f:
                log_data = json.load(f)
        except FileNotFoundError:
            return {"error": f"Log file not found: {log_file}"}
        except json.JSONDecodeError:
            return {"error": f"Invalid JSON in log file: {log_file}"}
        
        plan = log_data.get("plan", {})
        results = log_data.get("results", {})
        repository = plan.get("repository", "")
        
        if not repository:
            return {"error": "No repository found in log"}
        
        console.print(f"\n[bold cyan]Verifying Execution Log[/bold cyan]")
        console.print(f"Repository: {repository}")
        console.print(f"Log File: {log_file}\n")
        
        verification_report = {
            "repository": repository,
            "log_file": log_file,
            "claimed_status": results.get("status", "unknown"),
            "claimed_executed": results.get("actions_executed", 0),
            "claimed_failed": results.get("actions_failed", 0),
            "verifications": [],
            "actual_executed": 0,
            "actual_failed": 0,
            "discrepancies": []
        }
        
        # Verify each action
        actions = plan.get("actions", [])
        for i, action in enumerate(actions, 1):
            verification = self._verify_action(repository, action, i)
            verification_report["verifications"].append(verification)
            
            if verification["actually_executed"]:
                verification_report["actual_executed"] += 1
            else:
                verification_report["actual_failed"] += 1
        
        # Check for discrepancies
        if verification_report["claimed_executed"] != verification_report["actual_executed"]:
            verification_report["discrepancies"].append(
                f"Claimed {verification_report['claimed_executed']} executed, actually {verification_report['actual_executed']}"
            )
        
        if verification_report["claimed_failed"] != verification_report["actual_failed"]:
            verification_report["discrepancies"].append(
                f"Claimed {verification_report['claimed_failed']} failed, actually {verification_report['actual_failed']}"
            )
        
        self._display_verification_report(verification_report)
        
        return verification_report
    
    def _verify_action(self, repository: str, action: Dict[str, Any], action_num: int) -> Dict[str, Any]:
        """Verify a single action"""
        action_type = action.get("action_type", "")
        target = action.get("target", "")
        description = action.get("description", "")
        
        verification = {
            "action_number": action_num,
            "action_type": action_type,
            "target": target,
            "description": description,
            "actually_executed": False,
            "verification_method": "",
            "details": "",
            "github_url": None
        }
        
        if action_type == "open_issue":
            verification.update(self._verify_issue_creation(repository, action))
        elif action_type == "create_pr":
            verification.update(self._verify_pr_creation(repository, action))
        elif action_type == "edit_file":
            verification.update(self._verify_file_edit(repository, action))
        elif action_type == "log_warning":
            # Log warnings are always "successful" since they're just local logs
            verification.update({
                "actually_executed": True,
                "verification_method": "local_log",
                "details": "Warning logged locally (no GitHub action required)"
            })
        
        return verification
    
    def _verify_issue_creation(self, repository: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if an issue was actually created"""
        try:
            # Get recent issues from the repository
            response = requests.get(
                f"{self.base_url}/repos/{repository}/issues",
                headers=self._get_headers(),
                params={"state": "open", "sort": "created", "direction": "desc", "per_page": 10},
                timeout=10,
            )
            
            if response.status_code != 200:
                return {
                    "actually_executed": False,
                    "verification_method": "github_api",
                    "details": f"Failed to fetch issues: HTTP {response.status_code}"
                }
            
            issues = response.json()
            issue_title = action.get("changes", {}).get("issue_title", "")
            
            # Look for matching issue
            for issue in issues:
                if issue_title in issue.get("title", ""):
                    return {
                        "actually_executed": True,
                        "verification_method": "github_api",
                        "details": f"Found issue: {issue['title']}",
                        "github_url": issue["html_url"],
                        "issue_number": issue["number"]
                    }
            
            return {
                "actually_executed": False,
                "verification_method": "github_api",
                "details": f"Issue with title '{issue_title}' not found in recent issues"
            }
            
        except Exception as e:
            return {
                "actually_executed": False,
                "verification_method": "github_api",
                "details": f"Verification failed: {str(e)}"
            }
    
    def _verify_pr_creation(self, repository: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if a PR was actually created"""
        try:
            # Get recent PRs from the repository
            response = requests.get(
                f"{self.base_url}/repos/{repository}/pulls",
                headers=self._get_headers(),
                params={"state": "open", "sort": "created", "direction": "desc", "per_page": 10},
                timeout=10,
            )
            
            if response.status_code != 200:
                return {
                    "actually_executed": False,
                    "verification_method": "github_api",
                    "details": f"Failed to fetch PRs: HTTP {response.status_code}"
                }
            
            prs = response.json()
            
            # Look for autonomous security PRs
            for pr in prs:
                if "Autonomous Security Fix" in pr.get("title", "") or "security" in pr.get("title", "").lower():
                    return {
                        "actually_executed": True,
                        "verification_method": "github_api",
                        "details": f"Found PR: {pr['title']}",
                        "github_url": pr["html_url"],
                        "pr_number": pr["number"]
                    }
            
            return {
                "actually_executed": False,
                "verification_method": "github_api",
                "details": "No autonomous security PR found in recent PRs"
            }
            
        except Exception as e:
            return {
                "actually_executed": False,
                "verification_method": "github_api",
                "details": f"Verification failed: {str(e)}"
            }
    
    def _verify_file_edit(self, repository: str, action: Dict[str, Any]) -> Dict[str, Any]:
        """Verify if a file was actually edited"""
        # This would require checking commit history or comparing file content
        # For now, return a placeholder
        return {
            "actually_executed": False,
            "verification_method": "commit_history",
            "details": "File edit verification not yet implemented"
        }
    
    def _display_verification_report(self, report: Dict[str, Any]) -> None:
        """Display verification report"""
        console.print()
        
        # Summary
        status_color = "green" if not report["discrepancies"] else "red"
        console.print(f"[bold {status_color}]Verification Summary[/bold {status_color}]")
        console.print(f"Repository: {report['repository']}")
        console.print(f"Claimed Status: {report['claimed_status'].upper()}")
        console.print()
        
        # Comparison table
        comparison_table = Table(
            title="Claimed vs Actual Results",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        
        comparison_table.add_column("Metric", style="bold")
        comparison_table.add_column("Claimed", style="blue")
        comparison_table.add_column("Actual", style="green")
        comparison_table.add_column("Match", style="bold")
        
        executed_match = "✓" if report["claimed_executed"] == report["actual_executed"] else "✗"
        failed_match = "✓" if report["claimed_failed"] == report["actual_failed"] else "✗"
        
        comparison_table.add_row(
            "Actions Executed",
            str(report["claimed_executed"]),
            str(report["actual_executed"]),
            f"[green]{executed_match}[/green]" if executed_match == "✓" else f"[red]{executed_match}[/red]"
        )
        
        comparison_table.add_row(
            "Actions Failed",
            str(report["claimed_failed"]),
            str(report["actual_failed"]),
            f"[green]{failed_match}[/green]" if failed_match == "✓" else f"[red]{failed_match}[/red]"
        )
        
        console.print(comparison_table)
        console.print()
        
        # Detailed verification table
        details_table = Table(
            title="Action Verification Details",
            box=box.ROUNDED,
            show_header=True,
            header_style="bold cyan",
        )
        
        details_table.add_column("#", width=3)
        details_table.add_column("Action", width=15)
        details_table.add_column("Target", width=25)
        details_table.add_column("Status", width=10)
        details_table.add_column("Details", width=40)
        
        for verification in report["verifications"]:
            status = "[green]SUCCESS[/green]" if verification["actually_executed"] else "[red]FAILED[/red]"
            
            details_table.add_row(
                str(verification["action_number"]),
                verification["action_type"].replace("_", " ").title(),
                verification["target"][:25],
                status,
                verification["details"][:40]
            )
        
        console.print(details_table)
        
        # Show GitHub URLs if any
        github_actions = [v for v in report["verifications"] if v.get("github_url")]
        if github_actions:
            console.print()
            console.print("[bold green]Verified GitHub Actions:[/bold green]")
            for verification in github_actions:
                if verification.get("issue_number"):
                    console.print(f"  Issue #{verification['issue_number']}: {verification['github_url']}")
                elif verification.get("pr_number"):
                    console.print(f"  PR #{verification['pr_number']}: {verification['github_url']}")
        
        # Show discrepancies
        if report["discrepancies"]:
            console.print()
            console.print("[bold red]Discrepancies Found:[/bold red]")
            for discrepancy in report["discrepancies"]:
                console.print(f"  - {discrepancy}")
        else:
            console.print()
            console.print("[bold green]No discrepancies found - agent reported accurately![/bold green]")
        
        console.print()


def verify_latest_execution() -> None:
    """Verify the most recent execution log"""
    import glob
    import os
    
    # Find the most recent execution log
    log_files = glob.glob("*_execution_log.json")
    if not log_files:
        console.print("[red]No execution logs found[/red]")
        return
    
    # Get the most recent one
    latest_log = max(log_files, key=os.path.getctime)
    
    verifier = ActionVerifier()
    verifier.verify_execution_log(latest_log)


def verify_execution_log(log_file: str) -> None:
    """Verify a specific execution log"""
    verifier = ActionVerifier()
    verifier.verify_execution_log(log_file)