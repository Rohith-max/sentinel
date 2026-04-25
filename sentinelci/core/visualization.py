"""
Security incident graph visualization
"""

from typing import Dict, Any, List, Set, Tuple
from datetime import datetime
from rich.console import Console
from rich.tree import Tree
from rich.panel import Panel
from rich.table import Table
from rich import box


class IncidentGraph:
    """Builds and visualizes security incident relationships"""

    def __init__(self):
        self.nodes: Dict[str, Dict[str, Any]] = {}
        self.edges: List[Tuple[str, str, str]] = []  # (from, to, relationship)
        self.console = Console()

    def add_commit_node(self, commit_sha: str, message: str, author: str, timestamp: str):
        """Add a commit node"""
        self.nodes[f"commit:{commit_sha}"] = {
            "type": "commit",
            "sha": commit_sha,
            "message": message,
            "author": author,
            "timestamp": timestamp,
        }

    def add_workflow_node(self, workflow_id: str, name: str, status: str):
        """Add a workflow node"""
        self.nodes[f"workflow:{workflow_id}"] = {
            "type": "workflow",
            "id": workflow_id,
            "name": name,
            "status": status,
        }

    def add_secret_node(self, secret_id: str, location: str, severity: str):
        """Add a secret exposure node"""
        self.nodes[f"secret:{secret_id}"] = {
            "type": "secret",
            "id": secret_id,
            "location": location,
            "severity": severity,
        }

    def add_dependency_node(self, dep_name: str, version: str, vulnerability: str):
        """Add a dependency node"""
        self.nodes[f"dependency:{dep_name}"] = {
            "type": "dependency",
            "name": dep_name,
            "version": version,
            "vulnerability": vulnerability,
        }

    def add_alert_node(self, alert_id: str, alert_type: str, severity: str):
        """Add an alert node"""
        self.nodes[f"alert:{alert_id}"] = {
            "type": "alert",
            "id": alert_id,
            "alert_type": alert_type,
            "severity": severity,
        }

    def add_edge(self, from_node: str, to_node: str, relationship: str):
        """Add a relationship edge"""
        self.edges.append((from_node, to_node, relationship))

    def build_from_findings(self, findings: List[Dict[str, Any]], repo_data: Dict[str, Any]):
        """Build graph from security findings"""
        # Add repository node
        repo_name = repo_data.get("name", "unknown")
        
        # Process findings
        for idx, finding in enumerate(findings):
            finding_type = finding.get("category", finding.get("type", "unknown"))
            severity = finding.get("severity", "MEDIUM")
            location = finding.get("location", finding.get("file", "unknown"))

            if "secret" in finding_type.lower():
                secret_id = f"secret_{idx}"
                self.add_secret_node(secret_id, location, severity)
                
                # Link to file/commit if available
                if "commit" in finding:
                    commit_sha = finding["commit"]
                    self.add_commit_node(
                        commit_sha,
                        finding.get("commit_message", ""),
                        finding.get("author", "unknown"),
                        finding.get("timestamp", ""),
                    )
                    self.add_edge(f"commit:{commit_sha}", f"secret:{secret_id}", "exposed")

            elif "dependency" in finding_type.lower() or "cve" in finding_type.lower():
                dep_name = finding.get("package", finding.get("component", f"dep_{idx}"))
                self.add_dependency_node(
                    dep_name,
                    finding.get("version", "unknown"),
                    finding.get("vulnerability", finding.get("description", "")),
                )

            elif "workflow" in finding_type.lower() or "action" in finding_type.lower():
                workflow_id = finding.get("workflow_id", f"workflow_{idx}")
                self.add_workflow_node(
                    workflow_id,
                    finding.get("workflow_name", location),
                    finding.get("status", "unknown"),
                )

            # Add alert node for each finding
            alert_id = f"alert_{idx}"
            self.add_alert_node(alert_id, finding_type, severity)

        # Add workflow relationships
        workflows = repo_data.get("workflows", [])
        for workflow in workflows:
            workflow_id = str(workflow.get("id", ""))
            if f"workflow:{workflow_id}" in self.nodes:
                # Link failed workflows to alerts
                if workflow.get("status") == "failure":
                    for edge_from, edge_to, rel in self.edges:
                        if edge_to.startswith("alert:") and "workflow" in self.nodes.get(edge_to, {}).get("alert_type", "").lower():
                            self.add_edge(f"workflow:{workflow_id}", edge_to, "triggered")

    def generate_attack_chain(self) -> List[Dict[str, Any]]:
        """Generate attack chain timeline"""
        chain = []

        # Sort nodes by timestamp if available
        timestamped_nodes = []
        for node_id, node_data in self.nodes.items():
            timestamp = node_data.get("timestamp", "")
            if timestamp:
                timestamped_nodes.append((timestamp, node_id, node_data))

        timestamped_nodes.sort()

        # Build attack chain
        for timestamp, node_id, node_data in timestamped_nodes:
            node_type = node_data.get("type", "unknown")
            
            if node_type == "commit":
                chain.append({
                    "step": len(chain) + 1,
                    "timestamp": timestamp,
                    "event": "Code Commit",
                    "description": f"Commit {node_data['sha'][:7]}: {node_data['message'][:50]}",
                    "risk": "LOW",
                })

            elif node_type == "secret":
                chain.append({
                    "step": len(chain) + 1,
                    "timestamp": timestamp,
                    "event": "Secret Exposed",
                    "description": f"Secret exposed in {node_data['location']}",
                    "risk": node_data['severity'],
                })

            elif node_type == "workflow":
                if node_data['status'] == "failure":
                    chain.append({
                        "step": len(chain) + 1,
                        "timestamp": timestamp,
                        "event": "Workflow Failed",
                        "description": f"Workflow '{node_data['name']}' failed",
                        "risk": "MEDIUM",
                    })

        # Add propagation analysis
        for step in chain:
            if step["event"] == "Secret Exposed":
                chain.append({
                    "step": len(chain) + 1,
                    "timestamp": step["timestamp"],
                    "event": "Potential Compromise",
                    "description": "Exposed secret could be used to access protected resources",
                    "risk": "CRITICAL",
                })

        return chain

    def render_graph(self):
        """Render the incident graph"""
        self.console.print("\n[bold cyan]🔍 Security Incident Graph[/bold cyan]\n")

        # Create tree visualization
        tree = Tree("🏢 Repository")

        # Group nodes by type
        commits = {k: v for k, v in self.nodes.items() if v["type"] == "commit"}
        secrets = {k: v for k, v in self.nodes.items() if v["type"] == "secret"}
        workflows = {k: v for k, v in self.nodes.items() if v["type"] == "workflow"}
        dependencies = {k: v for k, v in self.nodes.items() if v["type"] == "dependency"}
        alerts = {k: v for k, v in self.nodes.items() if v["type"] == "alert"}

        # Add commits branch
        if commits:
            commits_branch = tree.add("📝 Commits")
            for node_id, node_data in list(commits.items())[:5]:
                commits_branch.add(f"[dim]{node_data['sha'][:7]}[/dim] {node_data['message'][:40]}")

        # Add secrets branch
        if secrets:
            secrets_branch = tree.add("🔑 Exposed Secrets")
            for node_id, node_data in secrets.items():
                severity_color = self._get_severity_color(node_data['severity'])
                secrets_branch.add(f"[{severity_color}]{node_data['severity']}[/{severity_color}] {node_data['location']}")

        # Add workflows branch
        if workflows:
            workflows_branch = tree.add("⚙️  Workflows")
            for node_id, node_data in workflows.items():
                status_icon = "✅" if node_data['status'] == "success" else "❌"
                workflows_branch.add(f"{status_icon} {node_data['name']}")

        # Add dependencies branch
        if dependencies:
            deps_branch = tree.add("📦 Dependencies")
            for node_id, node_data in dependencies.items():
                deps_branch.add(f"[yellow]{node_data['name']}[/yellow] {node_data['version']}")

        # Add alerts branch
        if alerts:
            alerts_branch = tree.add("🚨 Alerts")
            for node_id, node_data in alerts.items():
                severity_color = self._get_severity_color(node_data['severity'])
                alerts_branch.add(f"[{severity_color}]{node_data['severity']}[/{severity_color}] {node_data['alert_type']}")

        self.console.print(tree)

        # Show relationships
        if self.edges:
            self.console.print("\n[bold cyan]🔗 Relationships[/bold cyan]\n")
            for from_node, to_node, relationship in self.edges[:10]:
                from_type = from_node.split(":")[0]
                to_type = to_node.split(":")[0]
                self.console.print(f"  {from_type} [dim]→[/dim] {relationship} [dim]→[/dim] {to_type}")

    def render_attack_chain(self):
        """Render attack chain timeline"""
        chain = self.generate_attack_chain()

        if not chain:
            self.console.print("\n[yellow]No attack chain detected[/yellow]\n")
            return

        self.console.print("\n[bold red]⚠️  Attack Chain Timeline[/bold red]\n")

        table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
        table.add_column("Step", style="dim", width=6)
        table.add_column("Event", width=20)
        table.add_column("Description", width=50)
        table.add_column("Risk", width=10)

        for step in chain:
            risk_color = self._get_severity_color(step["risk"])
            table.add_row(
                str(step["step"]),
                step["event"],
                step["description"],
                f"[{risk_color}]{step['risk']}[/{risk_color}]",
            )

        self.console.print(table)

        # Show propagation summary
        critical_steps = [s for s in chain if s["risk"] == "CRITICAL"]
        if critical_steps:
            self.console.print(f"\n[bold red]⚠️  {len(critical_steps)} CRITICAL propagation point(s) detected[/bold red]")
            self.console.print("[yellow]Immediate remediation required to prevent compromise[/yellow]\n")

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity level"""
        severity_colors = {
            "CRITICAL": "bold red",
            "HIGH": "red",
            "MEDIUM": "yellow",
            "LOW": "blue",
        }
        return severity_colors.get(severity.upper(), "white")

    def export_json(self, output_file: str):
        """Export graph to JSON"""
        import json

        data = {
            "nodes": self.nodes,
            "edges": [{"from": f, "to": t, "relationship": r} for f, t, r in self.edges],
            "attack_chain": self.generate_attack_chain(),
        }

        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)


def render_org_risk_heatmap(org_analysis: Dict[str, Any]):
    """Render organization-wide risk heatmap"""
    console = Console()

    console.print("\n[bold cyan]🏢 Organization Risk Heatmap[/bold cyan]\n")

    repos = org_analysis.get("repositories", [])
    if not repos:
        console.print("[yellow]No repositories analyzed[/yellow]\n")
        return

    # Sort by risk score
    repos_sorted = sorted(repos, key=lambda r: r.get("risk_score", 0), reverse=True)

    table = Table(box=box.ROUNDED, show_header=True, header_style="bold cyan")
    table.add_column("Rank", style="dim", width=6)
    table.add_column("Repository", width=40)
    table.add_column("Risk Score", width=12)
    table.add_column("Critical", width=10)
    table.add_column("High", width=10)
    table.add_column("Medium", width=10)

    for idx, repo in enumerate(repos_sorted[:20], 1):
        risk_score = repo.get("risk_score", 0)
        risk_level = repo.get("risk_level", "LOW")
        
        # Get severity counts
        findings = repo.get("findings", [])
        critical_count = sum(1 for f in findings if f.get("severity") == "CRITICAL")
        high_count = sum(1 for f in findings if f.get("severity") == "HIGH")
        medium_count = sum(1 for f in findings if f.get("severity") == "MEDIUM")

        # Color code risk score
        if risk_score >= 70:
            score_color = "bold red"
        elif risk_score >= 45:
            score_color = "red"
        elif risk_score >= 20:
            score_color = "yellow"
        else:
            score_color = "green"

        table.add_row(
            str(idx),
            repo.get("name", "unknown"),
            f"[{score_color}]{risk_score}/100[/{score_color}]",
            f"[red]{critical_count}[/red]" if critical_count > 0 else "0",
            f"[yellow]{high_count}[/yellow]" if high_count > 0 else "0",
            f"[blue]{medium_count}[/blue]" if medium_count > 0 else "0",
        )

    console.print(table)

    # Summary statistics
    total_repos = len(repos)
    critical_repos = sum(1 for r in repos if r.get("risk_level") == "CRITICAL")
    high_repos = sum(1 for r in repos if r.get("risk_level") == "HIGH")

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Total Repositories: {total_repos}")
    console.print(f"  [red]Critical Risk: {critical_repos}[/red]")
    console.print(f"  [yellow]High Risk: {high_repos}[/yellow]")
    console.print()
