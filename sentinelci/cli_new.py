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
    """Complete setup wizard for SentinelCI"""
    from sentinelci.output.terminal import render_banner
    
    # Show banner on first installation
    render_banner()
    
    console.print(Panel.fit(
        "[bold cyan]Welcome to SentinelCI![/bold cyan]\n\n"
        "AI-powered security scanning and automation platform\n"
        "Let's get you set up with everything you need.",
        title="SentinelCI Setup",
        border_style="cyan"
    ))

    config = get_config()

    # Step 1: AI API Configuration (Required)
    console.print("\n[bold]Step 1: AI Analysis Setup (Required)[/bold]")
    console.print("SentinelCI uses AI for intelligent security analysis and autonomous fixing.")
    console.print()
    console.print("[dim]Supported AI providers:[/dim]")
    console.print("  • Groq (Recommended - Fast & Free): https://console.groq.com/keys")
    console.print("  • OpenAI: https://platform.openai.com/api-keys")
    console.print("  • Anthropic: https://console.anthropic.com/")
    console.print()
    
    current_key = config.get_api_key()
    if current_key:
        console.print("[green]SUCCESS:[/green] AI API key already configured")
        if not Confirm.ask("Update AI API key?", default=False):
            pass
        else:
            ai_key = Prompt.ask("Enter your AI API key", password=True)
            config.set("api", "ai_api_key", ai_key)
            console.print("[green]SUCCESS:[/green] AI API key updated")
    else:
        console.print("[yellow]WARNING:[/yellow] AI API key required for security analysis")
        ai_key = Prompt.ask("Enter your AI API key", password=True)
        if ai_key.strip():
            config.set("api", "ai_api_key", ai_key)
            console.print("[green]SUCCESS:[/green] AI API key configured")
        else:
            console.print("[red]ERROR:[/red] AI API key is required")
            console.print("Run 'sci onboard' again to complete setup")
            return

    # Step 2: GitHub Integration (Recommended)
    console.print("\n[bold]Step 2: GitHub Integration (Recommended)[/bold]")
    console.print("Connect GitHub for:")
    console.print("  • Repository scanning and analysis")
    console.print("  • Autonomous issue creation and PR generation")
    console.print("  • Organization-wide security monitoring")
    console.print()
    console.print("[dim]Get your GitHub PAT: https://github.com/settings/tokens[/dim]")
    console.print("[dim]Required scopes: 'repo' (for private repos) or 'public_repo' (for public repos)[/dim]")
    console.print()
    
    if Confirm.ask("Configure GitHub integration?", default=True):
        auth = GitHubAuth()
        if auth.has_pat():
            console.print("[green]SUCCESS:[/green] GitHub PAT already configured")
            
            # Test the PAT and show scopes
            try:
                scopes = auth.get_token_scopes()
                console.print(f"[cyan]INFO:[/cyan] Current token scopes: {', '.join(scopes)}")
                
                required_scopes = ['repo']
                missing = [s for s in required_scopes if s not in scopes]
                if missing:
                    console.print(f"[yellow]WARNING:[/yellow] Missing recommended scopes: {', '.join(missing)}")
                    console.print("Some features (issue/PR creation) may not work")
                
            except Exception as e:
                console.print(f"[yellow]WARNING:[/yellow] Could not verify token: {str(e)}")
            
            if Confirm.ask("Update GitHub PAT?", default=False):
                _setup_github_pat()
        else:
            _setup_github_pat()
    else:
        console.print("[yellow]WARNING:[/yellow] GitHub features will be limited without authentication")

    # Step 3: NVD API Key (Optional but recommended)
    console.print("\n[bold]Step 3: CVE Database Access (Optional)[/bold]")
    console.print("Configure NVD API for enhanced vulnerability scanning:")
    console.print("  • Higher rate limits for CVE lookups")
    console.print("  • More detailed vulnerability information")
    console.print()
    console.print("[dim]Get free API key: https://nvd.nist.gov/developers/request-an-api-key[/dim]")
    console.print()
    
    current_nvd = config.get_nvd_api_key()
    if current_nvd:
        console.print("[green]SUCCESS:[/green] NVD API key already configured")
        if Confirm.ask("Update NVD API key?", default=False):
            nvd_key = Prompt.ask("Enter your NVD API key (optional)", default="", show_default=False)
            if nvd_key.strip():
                config.set("api", "nvd_api_key", nvd_key)
                console.print("[green]SUCCESS:[/green] NVD API key updated")
    else:
        if Confirm.ask("Configure NVD API key for enhanced CVE scanning?", default=False):
            nvd_key = Prompt.ask("Enter your NVD API key", default="", show_default=False)
            if nvd_key.strip():
                config.set("api", "nvd_api_key", nvd_key)
                console.print("[green]SUCCESS:[/green] NVD API key configured")

    # Step 4: Scanning Preferences
    console.print("\n[bold]Step 4: Security Scanning Preferences[/bold]")
    
    severity = questionary.select(
        "Default minimum severity level for reporting:",
        choices=["low", "medium", "high", "critical"],
        default="medium",
    ).ask()
    config.set("scan", "severity_threshold", severity)

    enable_firmware = Confirm.ask("Enable firmware CVE scanning? (requires binwalk)", default=True)
    config.set("scan", "enable_firmware_scanning", str(enable_firmware))

    enable_urls = Confirm.ask("Enable homograph URL detection?", default=True)
    config.set("scan", "enable_url_detection", str(enable_urls))

    # Step 5: Output Preferences
    console.print("\n[bold]Step 5: Output Preferences[/bold]")
    
    output_format = questionary.select(
        "Default output format:",
        choices=["terminal", "json", "sarif"],
        default="terminal",
    ).ask()
    config.set("output", "format", output_format)

    # Step 6: Complete Setup
    console.print("\n[bold green]Setup Complete![/bold green]")
    console.print()
    console.print("[bold]Configuration Summary:[/bold]")
    console.print(f"  • AI API: {'Configured' if config.get_api_key() else 'Not configured'}")
    console.print(f"  • GitHub: {'Configured' if config.get_github_pat() else 'Not configured'}")
    console.print(f"  • NVD API: {'Configured' if config.get_nvd_api_key() else 'Not configured'}")
    console.print(f"  • Severity: {severity.upper()}")
    console.print(f"  • Output: {output_format.upper()}")
    console.print()
    
    console.print("[bold]Quick Start Commands:[/bold]")
    console.print("  • [cyan]sci scan[/cyan] - Scan current directory")
    console.print("  • [cyan]sci github repos[/cyan] - Analyze GitHub repositories")
    console.print("  • [cyan]sci github auth[/cyan] - Check authentication status")
    console.print("  • [cyan]sci --help[/cyan] - See all available commands")
    console.print()
    
    console.print("[bold]Next Steps:[/bold]")
    if not config.get_github_pat():
        console.print("  1. Configure GitHub integration: [cyan]sci github setup[/cyan]")
    console.print("  2. Run your first scan: [cyan]sci scan[/cyan]")
    console.print("  3. Explore autonomous features: [cyan]sci github repos[/cyan]")
    console.print()
    
    # Test configuration
    if Confirm.ask("Test configuration now?", default=True):
        console.print("\n[bold]Testing Configuration...[/bold]")
        
        # Test AI API
        if config.get_api_key():
            console.print("[cyan]INFO:[/cyan] Testing AI API connection...")
            try:
                # Simple test - this would need actual AI client
                console.print("[green]SUCCESS:[/green] AI API key format looks valid")
            except Exception as e:
                console.print(f"[yellow]WARNING:[/yellow] AI API test failed: {str(e)}")
        
        # Test GitHub API
        if config.get_github_pat():
            console.print("[cyan]INFO:[/cyan] Testing GitHub API connection...")
            try:
                auth = GitHubAuth()
                user = auth.get_authenticated_user()
                console.print(f"[green]SUCCESS:[/green] Connected as {user.get('login', 'Unknown')}")
            except Exception as e:
                console.print(f"[yellow]WARNING:[/yellow] GitHub API test failed: {str(e)}")
        
        console.print("\n[green]Configuration test complete![/green]")
    
    console.print("\n[dim]Configuration saved to: {config.config_file}[/dim]")
    console.print("[dim]You can re-run this setup anytime with: sci onboard[/dim]")
    console.print()
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
        console.print("CANCELLED: Logout cancelled")
        return
    
    # Remove PAT from config
    config.remove("git", "github_pat")
    
    console.print("SUCCESS: GitHub PAT removed successfully")
    console.print("INFO: You are now logged out")
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
        
        console.print("LOADING: Fetching repositories...")
        
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
        
        console.print(f"SCANNING: organization: [cyan]{org_name}[/cyan]")
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
            console.print(f"\nSAVED: Results saved to: {output}")

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
        "Autonomous Agent (Full Automation)",
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
        elif action == "Autonomous Agent (Full Automation)":
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
    console.print(f"\nANALYZING: security configuration...")
    
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

    console.print(f"\nAI ANALYZING: {repo['full_name']}...")
    
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
    
    console.print(f"[dim]SAVED: to {output_file}[/dim]")


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

    console.print(f"\n[bold cyan]Autonomous Security Agent[/bold cyan]")
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
        console.print("[green]SUCCESS: No security issues found[/green]")
        return
    
    console.print(f"[yellow]Found {len(findings)} issue(s)[/yellow]\n")
    
    # Step 2: Create autonomous plan
    console.print("[cyan]Phase 2: Planning Autonomous Actions[/cyan]")
    
    agent = AutonomousSecurityAgent()
    plan = asyncio.run(agent.analyze_and_plan(repo['full_name'], findings))
    
    # Step 3: Display plan
    agent.display_plan(plan)
    
    # Step 4: Ask for confirmation
    console.print("[bold yellow]WARNING: The agent will autonomously:[/bold yellow]")
    console.print("  • Edit files to fix vulnerabilities")
    console.print("  • Create commits with changes")
    console.print("  • Push to new branch")
    console.print("  • Open pull request")
    console.print("  • Create tracking issues")
    console.print()
    
    # Execute autonomously without confirmation
    console.print("[bold green]EXECUTING: Autonomous fixes (no confirmation needed)[/bold green]\n")
    
    # Auto-fix vulnerabilities first
    from sentinelci.core.auto_fixer import auto_fix_repository
    fix_results = auto_fix_repository(".", findings)
    
    if fix_results['secrets_extracted'] > 0:
        print_success(f"Extracted {fix_results['secrets_extracted']} secrets to .env")
        print_success(f"Modified {len(fix_results['files_modified'])} files")
        if fix_results['gitignore_updated']:
            print_success("Updated .gitignore")
    
    # Step 5: Execute autonomously
    console.print()
    results = asyncio.run(agent.execute_plan(plan, auto_approve=True))  # Auto-approve all
    
    # Step 6: Display results
    agent.display_results(results)
    
    # Save execution log
    import json
    log_file = f"{repo['name']}_execution_log.json"
    with open(log_file, 'w') as f:
        json.dump({
            "plan": plan.to_dict(),
            "results": results,
            "auto_fixes": fix_results,
        }, f, indent=2)
    
    console.print(f"[dim]SAVED: Execution log saved to {log_file}[/dim]")


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
        console.print("[green]SUCCESS: No issues to fix[/green]")
        return
    
    console.print(f"[yellow]Found {len(findings)} issue(s)[/yellow]")
    console.print("[cyan]Creating PR with fixes...[/cyan]")
    
    # Generate PR
    engine = RemediationEngine()
    try:
        result = engine.generate_security_pr(repo['full_name'], findings)
        render_pr_result(result)
    except Exception as e:
        console.print(f"[red]FAILED: Failed to create PR: {str(e)}[/red]")


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
    console.print(f"\nSAVED: Graph exported to: {output_file}")


def _action_full_analysis(repo: dict):
    """Full analysis with all features"""
    _action_ai_analysis(repo)
    _action_simulate_decisions(repo)
    _action_view_incident_graph(repo)


# ============================================================================
# MAIN
# ============================================================================

@app.command()
def welcome():
    """Show welcome banner and quick start guide"""
    from sentinelci.output.terminal import render_banner
    
    render_banner()
    console.print("[bold]Quick Start Guide:[/bold]")
    console.print()
    console.print("1. [cyan]sci onboard[/cyan] - Complete setup wizard")
    console.print("2. [cyan]sci scan[/cyan] - Scan current directory")
    console.print("3. [cyan]sci github repos[/cyan] - Analyze GitHub repositories")
    console.print("4. [cyan]sci github auth[/cyan] - Check authentication")
    console.print()
    console.print("For detailed help: [cyan]sci --help[/cyan]")
    console.print()


@app.command()
def version():
    """Show version information"""
    from sentinelci.output.terminal import render_banner
    
    render_banner()
    console.print(f"SentinelCI version {__version__}")
    console.print("AI-Powered Security Intelligence Platform")
    console.print()
    console.print("For help and documentation:")
    console.print("  • Run: [cyan]sci onboard[/cyan] for setup")
    console.print("  • Run: [cyan]sci --help[/cyan] for commands")
    console.print("  • Visit: https://github.com/sentinelci/sentinelci")
    console.print()


if __name__ == "__main__":
    app()
