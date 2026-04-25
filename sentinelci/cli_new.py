"""
Modern CLI interface for SentinelCI with Typer
"""

import sys
from typing import Optional, List
import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
import questionary

from sentinelci import __version__
from sentinelci.config import get_config
from sentinelci.core.auth import GitHubAuth, GitHubAuthError
from sentinelci.core.discovery import RepositoryDiscovery
from sentinelci.core.remediation import RemediationEngine
from sentinelci.core.visualization import IncidentGraph, render_org_risk_heatmap

app = typer.Typer(
    name="sci",
    help="SentinelCI - AI-powered security scanning and automation",
    add_completion=False,
)
console = Console()


# ============================================================================
# ONBOARDING & SETUP
# ============================================================================

@app.command()
def onboard():
    """Interactive onboarding wizard"""
    console.print(Panel.fit(
        "[bold cyan]Welcome to SentinelCI![/bold cyan]\n\n"
        "Let's get you set up with security scanning and automation.",
        title="🚀 Onboarding",
    ))

    config = get_config()

    # Step 1: AI API Key
    console.print("\n[bold]Step 1: AI Analysis Configuration[/bold]")
    console.print("SentinelCI uses AI for advanced security analysis.")
    
    current_key = config.get_api_key()
    if current_key:
        console.print(f"[green]✓[/green] AI API key already configured")
        if not Confirm.ask("Update AI API key?", default=False):
            ai_key = current_key
        else:
            ai_key = Prompt.ask("Enter your AI API key (Groq)", password=True)
            config.set("api", "ai_api_key", ai_key)
    else:
        console.print("Get your free API key from: https://console.groq.com/keys")
        ai_key = Prompt.ask("Enter your AI API key (Groq)", password=True)
        config.set("api", "ai_api_key", ai_key)

    # Step 2: GitHub PAT
    console.print("\n[bold]Step 2: GitHub Integration (Optional)[/bold]")
    console.print("Connect GitHub for repository scanning and automation.")
    
    if Confirm.ask("Configure GitHub integration?", default=True):
        auth = GitHubAuth()
        if auth.has_pat():
            console.print(f"[green]✓[/green] GitHub PAT already configured")
            if not Confirm.ask("Update GitHub PAT?", default=False):
                pass
            else:
                _setup_github_pat()
        else:
            _setup_github_pat()

    # Step 3: Scanning preferences
    console.print("\n[bold]Step 3: Scanning Preferences[/bold]")
    
    severity = questionary.select(
        "Default minimum severity level:",
        choices=["low", "medium", "high", "critical"],
        default="medium",
    ).ask()
    config.set("scan", "severity_threshold", severity)

    enable_firmware = Confirm.ask("Enable firmware CVE scanning?", default=True)
    config.set("scan", "enable_firmware_scanning", str(enable_firmware))

    enable_urls = Confirm.ask("Enable homograph URL detection?", default=True)
    config.set("scan", "enable_url_detection", str(enable_urls))

    # Step 4: Complete
    console.print("\n[bold green]✓ Onboarding Complete![/bold green]")
    console.print("\n[bold]Next Steps:[/bold]")
    console.print("  • Run [cyan]sci scan[/cyan] to scan your code")
    console.print("  • Run [cyan]sci github repos[/cyan] to analyze GitHub repositories")
    console.print("  • Run [cyan]sci --help[/cyan] to see all commands")
    console.print()


def _setup_github_pat():
    """Setup GitHub PAT"""
    console.print("\nTo create a GitHub PAT:")
    console.print("1. Go to: https://github.com/settings/tokens/new")
    console.print("2. Select scopes: repo, read:org, read:user, workflow")
    console.print("3. Generate token and copy it\n")

    pat = Prompt.ask("Enter GitHub PAT", password=True)
    
    auth = GitHubAuth()
    try:
        user = auth.validate_pat(pat)
        auth.store_pat(pat)
        console.print(f"[green]✓[/green] Authenticated as: {user.get('login')}")
    except GitHubAuthError as e:
        console.print(f"[red]✗[/red] {str(e)}")
        sys.exit(1)


# ============================================================================
# GITHUB COMMANDS
# ============================================================================

github_app = typer.Typer(help="GitHub integration commands")
app.add_typer(github_app, name="github")


@github_app.command()
def auth():
    """Check GitHub authentication status"""
    auth_manager = GitHubAuth()
    
    try:
        user = auth_manager.get_authenticated_user()
        console.print(Panel.fit(
            f"[green]✓ Authenticated[/green]\n\n"
            f"User: [cyan]{user.get('login')}[/cyan]\n"
            f"Name: {user.get('name', 'N/A')}\n"
            f"Email: {user.get('email', 'N/A')}",
            title="GitHub Authentication",
        ))
    except GitHubAuthError as e:
        console.print(f"[red]✗ Not authenticated:[/red] {str(e)}")
        console.print("\nRun [cyan]sci onboard[/cyan] or [cyan]sci github setup[/cyan] to configure")
        sys.exit(1)


@github_app.command()
def setup():
    """Setup GitHub Personal Access Token"""
    _setup_github_pat()


@github_app.command()
def logout():
    """Remove GitHub Personal Access Token (logout)"""
    config = get_config()
    
    # Check if PAT exists
    if not config.get_github_pat():
        console.print("ℹ️  No GitHub PAT configured - already logged out")
        return
    
    # Confirm logout
    if not Confirm.ask("Remove GitHub PAT and logout?", default=False):
        console.print("❌ Logout cancelled")
        return
    
    # Remove PAT from config
    config.remove("git", "github_pat")
    
    console.print("✅ GitHub PAT removed successfully")
    console.print("ℹ️  You are now logged out")
    console.print("\nRun [cyan]sci github setup[/cyan] to login again")


@github_app.command()
def repos(
    search: Optional[str] = typer.Option(None, help="Filter by name/description"),
    visibility: Optional[str] = typer.Option(None, help="Filter by public/private"),
    language: Optional[str] = typer.Option(None, help="Filter by language"),
    org: Optional[str] = typer.Option(None, help="Scan organization repositories"),
):
    """List and analyze repositories"""
    try:
        discovery = RepositoryDiscovery()
        
        console.print("🔍 Fetching repositories...")
        
        if org:
            all_repos = discovery.fetch_organization_repositories(org)
            console.print(f"Found {len(all_repos)} repositories in organization: {org}")
        else:
            all_repos = discovery.fetch_user_repositories()
            console.print(f"Found {len(all_repos)} repositories")

        # Apply filters
        filtered_repos = discovery.filter_repositories(
            all_repos,
            search=search,
            visibility=visibility,
            language=language,
        )

        if not filtered_repos:
            console.print("[yellow]No repositories match the filters[/yellow]")
            return

        console.print(f"Showing {len(filtered_repos)} repositories\n")

        # Interactive selection
        selected = _select_repositories_interactive(filtered_repos)

        if selected:
            _show_repository_actions(selected)

    except GitHubAuthError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        console.print("\nRun [cyan]sci github setup[/cyan] to configure authentication")
        sys.exit(1)


@github_app.command()
def scan_org(
    org_name: str = typer.Argument(..., help="Organization name"),
    output: Optional[str] = typer.Option(None, help="Output file for results"),
):
    """Scan all repositories in an organization"""
    try:
        discovery = RepositoryDiscovery()
        
        console.print(f"🔍 Scanning organization: [cyan]{org_name}[/cyan]")
        repos = discovery.fetch_organization_repositories(org_name)
        
        console.print(f"Found {len(repos)} repositories\n")

        # Analyze each repository
        from sentinelci.github_security import GitHubSecurityAnalyzer
        from sentinelci.ai_analyzer import AISecurityAnalyzer
        import asyncio

        analyzer = GitHubSecurityAnalyzer()
        config = get_config()
        ai_analyzer = AISecurityAnalyzer(config.get_api_key())

        org_results = {
            "organization": org_name,
            "total_repositories": len(repos),
            "repositories": [],
        }

        for idx, repo in enumerate(repos, 1):
            console.print(f"[{idx}/{len(repos)}] Analyzing {repo['full_name']}...")
            
            try:
                # Security analysis
                analysis = analyzer.analyze_repository(repo['full_name'])
                risk_data = analyzer.calculate_risk_score(analysis)

                # AI analysis
                metadata = {
                    "name": repo['full_name'],
                    "visibility": repo['visibility'],
                    "language": repo.get('language', ''),
                }
                
                ai_result = asyncio.run(
                    ai_analyzer.analyze_repository(
                        repo['full_name'],
                        metadata,
                        analysis.get('workflows', []),
                        [],
                        {"ci_cd_files": analysis.get('ci_cd_files', {})},
                    )
                )

                org_results["repositories"].append({
                    "name": repo['full_name'],
                    "risk_score": ai_result.risk_score,
                    "risk_level": ai_result.risk_level,
                    "findings": [f.to_dict() for f in ai_result.findings],
                })

            except Exception as e:
                console.print(f"  [yellow]⚠ Error analyzing {repo['full_name']}: {str(e)}[/yellow]")

        # Render heatmap
        render_org_risk_heatmap(org_results)

        # Save results
        if output:
            import json
            with open(output, 'w') as f:
                json.dump(org_results, f, indent=2)
            console.print(f"\n💾 Results saved to: {output}")

    except GitHubAuthError as e:
        console.print(f"[red]Error:[/red] {str(e)}")
        sys.exit(1)


def _select_repositories_interactive(repos: List[dict]) -> List[dict]:
    """Interactive repository selection"""
    choices = []
    for repo in repos:
        label = f"{repo['full_name']:<50} [{repo['visibility']:<7}] {repo.get('language', 'N/A'):<15}"
        choices.append(questionary.Choice(title=label, value=repo))

    selected = questionary.checkbox(
        "Select repositories (Space to select, Enter to confirm):",
        choices=choices,
    ).ask()

    return selected or []


def _show_repository_actions(repos: List[dict]):
    """Show action menu for selected repositories"""
    actions = [
        "Analyze Security Configuration",
        "Run AI Security Analysis",
        "🤖 Autonomous Agent (Full Automation)",
        "Generate Security PR",
        "View Incident Graph",
        "Full Analysis + Visualization",
        "Cancel",
    ]

    for repo in repos:
        console.print(f"\n{'='*70}")
        console.print(f"Repository: [cyan]{repo['full_name']}[/cyan]")
        console.print(f"{'='*70}\n")

        action = questionary.select(
            "What would you like to do?",
            choices=actions,
        ).ask()

        if not action or action == "Cancel":
            continue

        if action == "Analyze Security Configuration":
            _action_analyze_security(repo)
        elif action == "Run AI Security Analysis":
            _action_ai_analysis(repo)
        elif action == "🤖 Autonomous Agent (Full Automation)":
            _action_simulate_decisions(repo)
        elif action == "Generate Security PR":
            _action_generate_pr(repo)
        elif action == "View Incident Graph":
            _action_view_incident_graph(repo)
        elif action == "Full Analysis + Visualization":
            _action_full_analysis(repo)


def _action_analyze_security(repo: dict):
    """Analyze repository security"""
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.output.github_dashboard import render_github_dashboard

    analyzer = GitHubSecurityAnalyzer()
    console.print(f"\n🔍 Analyzing security configuration...")
    
    analysis = analyzer.analyze_repository(repo['full_name'])
    risk_score = analyzer.calculate_risk_score(analysis)

    render_github_dashboard(analysis, risk_score)


def _action_ai_analysis(repo: dict):
    """Run AI security analysis"""
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.output.concise import render_analysis_brief
    import asyncio

    config = get_config()
    api_key = config.get_api_key()
    
    if not api_key:
        console.print("[red]AI API key not configured. Run: sci onboard[/red]")
        return

    console.print(f"\n🤖 Analyzing {repo['full_name']}...")
    
    github_analyzer = GitHubSecurityAnalyzer()
    analysis = github_analyzer.analyze_repository(repo['full_name'])
    
    metadata = {
        "name": repo['full_name'],
        "visibility": repo['visibility'],
        "language": repo.get('language', ''),
    }
    
    ai_analyzer = AISecurityAnalyzer(api_key)
    result = asyncio.run(
        ai_analyzer.analyze_repository(
            repo['full_name'],
            metadata,
            analysis.get('workflows', []),
            [],
            {"ci_cd_files": analysis.get('ci_cd_files', {})},
        )
    )

    render_analysis_brief(result.to_dict())

    # Save results
    import json
    output_file = f"{repo['name']}_analysis.json"
    with open(output_file, 'w') as f:
        json.dump(result.to_dict(), f, indent=2)
    
    console.print(f"[dim]💾 Saved to {output_file}[/dim]")


def _action_simulate_decisions(repo: dict):
    """Run fully autonomous agent with complete automation"""
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.core.autonomous_agent import AutonomousSecurityAgent
    import asyncio

    config = get_config()
    api_key = config.get_api_key()
    
    if not api_key:
        console.print("[red]AI API key not configured. Run: sci onboard[/red]")
        return

    console.print(f"\n[bold cyan]🤖 Autonomous Security Agent[/bold cyan]")
    console.print(f"[dim]Repository: {repo['full_name']}[/dim]\n")
    
    # Step 1: Analyze repository
    console.print("[cyan]Phase 1: Security Analysis[/cyan]")
    
    github_analyzer = GitHubSecurityAnalyzer()
    analysis = github_analyzer.analyze_repository(repo['full_name'])
    
    metadata = {
        "name": repo['full_name'],
        "visibility": repo['visibility'],
        "language": repo.get('language', ''),
    }
    
    ai_analyzer = AISecurityAnalyzer(api_key)
    ai_result = asyncio.run(
        ai_analyzer.analyze_repository(
            repo['full_name'],
            metadata,
            analysis.get('workflows', []),
            [],
            {"ci_cd_files": analysis.get('ci_cd_files', {})},
        )
    )
    
    findings = [f.to_dict() for f in ai_result.findings]
    
    if not findings:
        console.print("[green]✅ No security issues found[/green]")
        return
    
    console.print(f"[yellow]Found {len(findings)} issue(s)[/yellow]\n")
    
    # Step 2: Create autonomous plan
    console.print("[cyan]Phase 2: Planning Autonomous Actions[/cyan]")
    
    agent = AutonomousSecurityAgent()
    plan = asyncio.run(agent.analyze_and_plan(repo['full_name'], findings))
    
    # Step 3: Display plan
    agent.display_plan(plan)
    
    # Step 4: Ask for confirmation
    console.print("[bold yellow]⚠️  The agent will autonomously:[/bold yellow]")
    console.print("  • Edit files to fix vulnerabilities")
    console.print("  • Create commits with changes")
    console.print("  • Push to new branch")
    console.print("  • Open pull request")
    console.print("  • Create tracking issues")
    console.print()
    
    if not Confirm.ask("[bold]Allow autonomous execution?[/bold]", default=False):
        console.print("\n[yellow]❌ Autonomous execution cancelled[/yellow]")
        
        # Save plan for review
        import json
        plan_file = f"{repo['name']}_autonomous_plan.json"
        with open(plan_file, 'w') as f:
            json.dump(plan.to_dict(), f, indent=2)
        console.print(f"[dim]💾 Plan saved to {plan_file}[/dim]")
        return
    
    # Step 5: Execute autonomously
    console.print()
    results = asyncio.run(agent.execute_plan(plan, auto_approve=False))
    
    # Step 6: Display results
    agent.display_results(results)
    
    # Save execution log
    import json
    log_file = f"{repo['name']}_execution_log.json"
    with open(log_file, 'w') as f:
        json.dump({
            "plan": plan.to_dict(),
            "results": results,
        }, f, indent=2)
    
    console.print(f"[dim]💾 Execution log saved to {log_file}[/dim]")


def _action_generate_pr(repo: dict):
    """Generate security PR using Git Data API (no cloning)"""
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.core.remediation import RemediationEngine
    from sentinelci.output.concise import render_pr_result
    import asyncio

    config = get_config()
    api_key = config.get_api_key()
    
    if not api_key:
        console.print("[red]AI API key not configured. Run: sci onboard[/red]")
        return

    console.print(f"\n📝 Generating security PR for {repo['full_name']}...")
    console.print("[dim]Using Git Data API - no cloning required[/dim]\n")
    
    # Analyze repository
    github_analyzer = GitHubSecurityAnalyzer()
    analysis = github_analyzer.analyze_repository(repo['full_name'])
    
    metadata = {
        "name": repo['full_name'],
        "visibility": repo['visibility'],
        "language": repo.get('language', ''),
    }
    
    ai_analyzer = AISecurityAnalyzer(api_key)
    ai_result = asyncio.run(
        ai_analyzer.analyze_repository(
            repo['full_name'],
            metadata,
            analysis.get('workflows', []),
            [],
            {"ci_cd_files": analysis.get('ci_cd_files', {})},
        )
    )
    
    findings = [f.to_dict() for f in ai_result.findings]
    
    if not findings:
        console.print("[green]✅ No issues to fix[/green]")
        return
    
    console.print(f"[yellow]Found {len(findings)} issue(s)[/yellow]")
    console.print("[cyan]Creating PR with fixes...[/cyan]")
    
    # Generate PR
    engine = RemediationEngine()
    try:
        result = engine.generate_security_pr(repo['full_name'], findings)
        render_pr_result(result)
    except Exception as e:
        console.print(f"[red]❌ Failed to create PR: {str(e)}[/red]")


def _action_view_incident_graph(repo: dict):
    """View incident graph"""
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    import asyncio

    config = get_config()
    api_key = config.get_api_key()
    
    if not api_key:
        console.print("[red]AI API key not configured. Run: sci onboard[/red]")
        return

    console.print(f"\n📊 Building incident graph...")
    
    github_analyzer = GitHubSecurityAnalyzer()
    analysis = github_analyzer.analyze_repository(repo['full_name'])
    
    metadata = {
        "name": repo['full_name'],
        "visibility": repo['visibility'],
        "language": repo.get('language', ''),
    }
    
    ai_analyzer = AISecurityAnalyzer(api_key)
    ai_result = asyncio.run(
        ai_analyzer.analyze_repository(
            repo['full_name'],
            metadata,
            analysis.get('workflows', []),
            [],
            {"ci_cd_files": analysis.get('ci_cd_files', {})},
        )
    )

    # Build and render graph
    graph = IncidentGraph()
    graph.build_from_findings(
        [f.to_dict() for f in ai_result.findings],
        {"name": repo['full_name'], "workflows": analysis.get('workflows', [])},
    )
    
    graph.render_graph()
    graph.render_attack_chain()

    # Export
    output_file = f"{repo['name']}_incident_graph.json"
    graph.export_json(output_file)
    console.print(f"\n💾 Graph exported to: {output_file}")


def _action_full_analysis(repo: dict):
    """Full analysis with all features"""
    _action_ai_analysis(repo)
    _action_simulate_decisions(repo)
    _action_view_incident_graph(repo)


# ============================================================================
# MAIN
# ============================================================================

@app.command()
def version():
    """Show version information"""
    console.print(f"SentinelCI version {__version__}")


if __name__ == "__main__":
    app()
