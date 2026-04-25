"""
Command-line interface for SCI
"""

import sys
from typing import List, Dict, Any
import click
from sentinelci import __version__
from sentinelci.config import get_config


@click.group(invoke_without_command=True)
@click.pass_context
@click.option("--scan", "root_scan", is_flag=True, help="Run scan via root flag")
@click.option("--watch", "root_watch", is_flag=True, help="Run watch via root flag")
@click.option("--fix", "root_fix", is_flag=True, help="Run auto-fix via root flag")
@click.option("--config", "root_config", is_flag=True, help="Run config wizard via root flag")
@click.option("--report", "root_report", is_flag=True, help="Run report via root flag")
@click.option("--version-info", "root_version", is_flag=True, help="Show extended version info")
@click.option("--path", "root_path", default=".", show_default=True, help="Path for scan/watch/fix")
@click.option("--target", "root_target", type=click.Path(), help="Override target for scan/watch/fix")
@click.option("--incident-file", default="findings.json", help="Input report file")
@click.option("--diff", is_flag=True, help="Use git diff file scope")
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    show_default=True,
    help="Minimum severity level to report",
)
@click.option(
    "--format",
    "root_format",
    type=click.Choice(["terminal", "json", "markdown", "html"]),
    default="terminal",
    show_default=True,
    help="Output format",
)
@click.option("--output", "root_output", type=click.Path(), help="Output file for scan/report")
@click.option("--no-ai", is_flag=True, help="Disable AI analysis")
@click.option("--interval", default=2.0, type=click.FloatRange(min=0.5), show_default=True)
@click.option("--sync-github", is_flag=True, help="Fetch from GitHub remote before diff scans")
@click.option("--remote", default="origin", show_default=True, help="Git remote name")
@click.option("--branch", default=None, help="Git branch for remote diff comparison")
@click.option("--github-pat", default=None, help="GitHub PAT for authenticated remote fetch")
@click.option("--halt-on-critical", is_flag=True, help="Exit with failure on critical findings")
@click.option("--no-firmware", is_flag=True, help="Disable firmware CVE scanning")
@click.option("--no-urls", is_flag=True, help="Disable homograph URL detection")
@click.option("--dry-run", is_flag=True, help="Preview fix actions without writing files")
@click.option("--no-backup", is_flag=True, help="Disable .sci.bak backups during fix")
@click.version_option(version=__version__, prog_name="sci")
def main(
    ctx: click.Context,
    root_scan: bool,
    root_watch: bool,
    root_fix: bool,
    root_config: bool,
    root_report: bool,
    root_version: bool,
    root_path: str,
    root_target: str,
    incident_file: str,
    diff: bool,
    severity: str,
    root_format: str,
    root_output: str,
    no_ai: bool,
    interval: float,
    sync_github: bool,
    remote: str,
    branch: str,
    github_pat: str,
    halt_on_critical: bool,
    no_firmware: bool,
    no_urls: bool,
    dry_run: bool,
    no_backup: bool,
) -> None:
    """SCI - AI-powered security scanning for your code"""
    
    # Check for first-time installation
    config = get_config()
    is_first_run = not config.get_api_key() and not config.get_github_pat()
    
    # Show banner and onboarding on first run (unless running specific commands)
    if is_first_run and ctx.invoked_subcommand is None and not any([
        root_scan, root_watch, root_fix, root_config, root_report, root_version
    ]):
        from sentinelci.output.terminal import render_banner
        render_banner()
        
        click.echo("Welcome to SentinelCI! It looks like this is your first time.")
        click.echo("Let's get you set up with the interactive onboarding wizard.")
        click.echo()
        
        if click.confirm("Run setup wizard now?", default=True):
            # Import and run the modern onboarding
            try:
                import subprocess
                import sys
                result = subprocess.run([
                    sys.executable, "-m", "sentinelci.cli_new", "onboard"
                ], check=False)
                if result.returncode == 0:
                    click.echo("\nSetup complete! You can now use SentinelCI.")
                    click.echo("Try: sci scan")
                    return
            except Exception:
                pass
            
            # Fallback to basic setup
            click.echo("Setting up basic configuration...")
            click.echo("You can run 'sci github setup' later for GitHub integration.")
        else:
            click.echo("You can run setup later with: sci onboard")
            click.echo("Or use the modern CLI: python -m sentinelci.cli_new onboard")
    
    if ctx.invoked_subcommand is not None:
        return

    target_path = root_target or root_path

    if root_scan:
        ctx.invoke(
            scan,
            path=target_path,
            diff=diff,
            target=root_target,
            severity=severity,
            format=root_format if root_format != "html" else "terminal",
            output=root_output,
            no_ai=no_ai,
            watch=False,
            watch_interval=interval,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            halt_on_critical=halt_on_critical,
            no_firmware=no_firmware,
            no_urls=no_urls,
        )
        return

    if root_watch:
        ctx.invoke(
            watch,
            path=target_path,
            severity=severity,
            format=root_format if root_format != "html" else "terminal",
            output=root_output,
            no_ai=no_ai,
            interval=interval,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            halt_on_critical=halt_on_critical,
            no_firmware=no_firmware,
            no_urls=no_urls,
        )
        return

    if root_fix:
        ctx.invoke(
            fix,
            path=target_path,
            diff=diff,
            severity=severity,
            no_firmware=no_firmware,
            no_urls=no_urls,
            dry_run=dry_run,
            no_backup=no_backup,
        )
        return

    if root_config:
        ctx.invoke(config)
        return

    if root_report:
        ctx.invoke(
            report,
            incident_file=incident_file,
            format=root_format,
            output=root_output,
        )
        return

    if root_version:
        ctx.invoke(version)
        return

    click.echo(ctx.get_help())


@main.command()
@click.argument("path", default=".", required=False)
@click.option("--diff", is_flag=True, help="Scan git diff instead of directory")
@click.option("--target", type=click.Path(), help="Target directory or file to scan")
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="Minimum severity level to report",
)
@click.option(
    "--format",
    type=click.Choice(["terminal", "json", "markdown"]),
    default="terminal",
    help="Output format",
)
@click.option(
    "--output", type=click.Path(), help="Output file path (for json/markdown formats)"
)
@click.option("--no-ai", is_flag=True, help="Disable AI analysis")
@click.option("--watch", is_flag=True, help="Watch mode - scan on each commit")
@click.option(
    "--watch-interval",
    type=click.FloatRange(min=0.5),
    default=2.0,
    show_default=True,
    help="Watch polling interval in seconds",
)
@click.option("--sync-github", is_flag=True, help="Fetch from GitHub remote before diff scans")
@click.option("--remote", default="origin", show_default=True, help="Git remote name")
@click.option("--branch", default=None, help="Git branch for remote diff comparison")
@click.option("--github-pat", default=None, help="GitHub PAT for authenticated remote fetch")
@click.option("--halt-on-critical", is_flag=True, help="Exit with error on critical findings")
@click.option("--no-firmware", is_flag=True, help="Disable firmware CVE scanning")
@click.option("--no-urls", is_flag=True, help="Disable homograph URL detection")
def scan(
    path: str,
    diff: bool,
    target: str,
    severity: str,
    format: str,
    output: str,
    no_ai: bool,
    watch: bool,
    watch_interval: float,
    sync_github: bool,
    remote: str,
    branch: str,
    github_pat: str,
    halt_on_critical: bool,
    no_firmware: bool,
    no_urls: bool,
) -> None:
    """Scan for security threats"""
    from sentinelci.scanner import run_scan

    try:
        exit_code = run_scan(
            path=target or path,
            use_diff=diff,
            severity=severity,
            output_format=format,
            output_file=output,
            use_ai=not no_ai,
            watch_mode=watch,
            watch_interval=watch_interval,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            halt_on_critical=halt_on_critical,
            enable_firmware=not no_firmware,
            enable_urls=not no_urls,
        )
        sys.exit(exit_code)
    except Exception as e:
        click.echo(f"❌ Scan failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", default=".", required=False)
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="Minimum severity level to report",
)
@click.option(
    "--format",
    type=click.Choice(["terminal", "json", "markdown"]),
    default="terminal",
    help="Output format",
)
@click.option("--output", type=click.Path(), help="Output file path (for json/markdown formats)")
@click.option("--no-ai", is_flag=True, help="Disable AI analysis")
@click.option("--interval", type=click.FloatRange(min=0.5), default=2.0, show_default=True)
@click.option("--sync-github", is_flag=True, help="Fetch from GitHub remote before diff scans")
@click.option("--remote", default="origin", show_default=True, help="Git remote name")
@click.option("--branch", default=None, help="Git branch for remote diff comparison")
@click.option("--github-pat", default=None, help="GitHub PAT for authenticated remote fetch")
@click.option("--halt-on-critical", is_flag=True, help="Exit with error on critical findings")
@click.option("--no-firmware", is_flag=True, help="Disable firmware CVE scanning")
@click.option("--no-urls", is_flag=True, help="Disable homograph URL detection")
def watch(
    path: str,
    severity: str,
    format: str,
    output: str,
    no_ai: bool,
    interval: float,
    sync_github: bool,
    remote: str,
    branch: str,
    github_pat: str,
    halt_on_critical: bool,
    no_firmware: bool,
    no_urls: bool,
) -> None:
    """Watch files in real time and rescan on change"""
    from sentinelci.scanner import run_watch

    try:
        run_watch(
            path=path,
            severity=severity,
            output_format=format,
            output_file=output,
            use_ai=not no_ai,
            sync_github=sync_github,
            remote=remote,
            branch=branch,
            github_pat=github_pat,
            halt_on_critical=halt_on_critical,
            enable_firmware=not no_firmware,
            enable_urls=not no_urls,
            interval_seconds=interval,
        )
    except KeyboardInterrupt:
        click.echo("\n⏹️  Watch mode stopped")
        sys.exit(0)
    except Exception as e:
        click.echo(f"❌ Watch failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("path", default=".", required=False)
@click.option("--diff", is_flag=True, help="Fix based on git diff scope")
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    help="Minimum severity level to include",
)
@click.option("--no-firmware", is_flag=True, help="Disable firmware CVE scanning")
@click.option("--no-urls", is_flag=True, help="Disable homograph URL detection")
@click.option("--dry-run", is_flag=True, help="Preview changes without writing files")
@click.option("--no-backup", is_flag=True, help="Do not create .sci.bak backup files")
def fix(
    path: str,
    diff: bool,
    severity: str,
    no_firmware: bool,
    no_urls: bool,
    dry_run: bool,
    no_backup: bool,
) -> None:
    """Auto-fix supported findings (secrets and homograph URLs)"""
    from sentinelci.fixer import run_fix

    try:
        summary = run_fix(
            path=path,
            use_diff=diff,
            severity=severity,
            enable_firmware=not no_firmware,
            enable_urls=not no_urls,
            dry_run=dry_run,
            backup=not no_backup,
        )
        click.echo(
            "\n".join(
                [
                    f"Total findings: {summary['total_findings']}",
                    f"Fixable: {summary['fixable']}",
                    f"Fixed: {summary['fixed']}",
                    f"Skipped: {summary['skipped']}",
                ]
            )
        )
        if summary["changes"]:
            click.echo("\nApplied changes:")
            for item in summary["changes"]:
                click.echo(f"- {item['action']} -> {item['file']}:{item['line']}")
    except Exception as e:
        click.echo(f"❌ Fix failed: {str(e)}", err=True)
        sys.exit(1)


@main.group()
def hook() -> None:
    """Manage git hooks for pre-commit scanning"""
    pass


@hook.command()
@click.option(
    "--blocking",
    is_flag=True,
    help="Fail commit on critical findings (default: warn only)",
)
def install(blocking: bool) -> None:
    """Install pre-commit git hook"""
    from sentinelci.hooks import install_hook

    try:
        install_hook(blocking=blocking)
        click.echo("✅ Git hook installed successfully")
    except Exception as e:
        click.echo(f"❌ Failed to install hook: {str(e)}", err=True)
        sys.exit(1)


@hook.command()
def remove() -> None:
    """Remove git hook"""
    from sentinelci.hooks import remove_hook

    try:
        remove_hook()
        click.echo("✅ Git hook removed")
    except Exception as e:
        click.echo(f"❌ Failed to remove hook: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.argument("incident_file", required=False)
@click.option(
    "--format",
    type=click.Choice(["terminal", "json", "markdown", "html"]),
    default="terminal",
    help="Output format for the report",
)
@click.option("--output", type=click.Path(), help="Save report to file")
def report(incident_file: str, format: str, output: str) -> None:
    """Generate or convert security reports"""
    from sentinelci.output.report import render_report

    try:
        render_report(incident_file or "findings.json", format=format, output_file=output)
    except Exception as e:
        click.echo(f"❌ Report generation failed: {str(e)}", err=True)
        sys.exit(1)


@main.command()
@click.option("--ai-api-key", default=None, help="Set AI API key")
@click.option("--github-pat", default=None, help="Set GitHub PAT for sync")
@click.option("--nvd-api-key", default=None, help="Set NVD API key for CVE lookups")
@click.option("--clear-github-pat", is_flag=True, help="Remove stored GitHub PAT from config")
@click.option(
    "--severity",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default=None,
    help="Set default minimum severity",
)
@click.option("--enable-firmware/--disable-firmware", default=None, help="Enable or disable firmware CVE scanning")
@click.option("--enable-urls/--disable-urls", default=None, help="Enable or disable homograph URL detection")
@click.option("--non-interactive", is_flag=True, help="Apply options and skip interactive onboarding wizard")
def config(
    ai_api_key: str,
    github_pat: str,
    nvd_api_key: str,
    clear_github_pat: bool,
    severity: str,
    enable_firmware: bool,
    enable_urls: bool,
    non_interactive: bool,
) -> None:
    """Configure SCI settings"""
    cfg = get_config()

    if any(value is not None for value in [ai_api_key, github_pat, nvd_api_key, severity, enable_firmware, enable_urls]) or clear_github_pat:
        cfg.configure_onboarding(
            ai_api_key=ai_api_key,
            github_pat=github_pat,
            nvd_api_key=nvd_api_key,
            clear_github_pat=clear_github_pat,
            severity=severity,
            enable_firmware=enable_firmware,
            enable_urls=enable_urls,
        )
        click.echo("✅ Configuration options saved")

    if non_interactive:
        click.echo("✅ Non-interactive onboarding complete")
        return

    cfg.setup_wizard()


@main.command()
def version() -> None:
    """Display version and environment information"""
    import platform
    from importlib.metadata import version as get_version

    click.echo(f"SCI {__version__}")
    click.echo(f"Python {platform.python_version()}")
    try:
        ai_sdk_version = get_version("groq")
        click.echo(f"AI SDK {ai_sdk_version}")
    except Exception:
        click.echo("AI SDK not installed")
    click.echo("AI Model: llama-3.3-70b-versatile")


@main.group()
def github() -> None:
    """GitHub integration and security analysis"""
    pass


@github.command()
def auth() -> None:
    """Check GitHub authentication status"""
    from sentinelci.github_auth import GitHubAuth

    try:
        auth = GitHubAuth()
        status = auth.check_auth_status()

        if status["authenticated"]:
            user = status["user"]
            orgs = status["organizations"]
            
            click.echo(f"✅ Authenticated as: [bold cyan]{user['login']}[/bold cyan]")
            click.echo(f"   Name: {user.get('name', 'N/A')}")
            click.echo(f"   Email: {user.get('email', 'N/A')}")
            click.echo(f"   Profile: {user.get('html_url', '')}")
            
            # Show token scopes
            try:
                scopes = auth.get_token_scopes()
                if scopes:
                    click.echo(f"\n🔑 Token Scopes:")
                    for scope in scopes:
                        click.echo(f"   • {scope}")
                    
                    # Check for required scopes
                    required = ['repo']
                    missing = [s for s in required if s not in scopes]
                    if missing:
                        click.echo(f"\n⚠️  Missing recommended scopes: {', '.join(missing)}")
                        click.echo("   Some features (like creating issues/PRs) may not work")
                else:
                    click.echo(f"\n⚠️  No scopes detected - token may have limited permissions")
            except Exception as e:
                click.echo(f"\n⚠️  Could not check token scopes: {str(e)}")
            
            if orgs:
                click.echo(f"\n📋 Organizations ({len(orgs)}):")
                for org in orgs[:10]:
                    click.echo(f"   • {org['login']}")
                if len(orgs) > 10:
                    click.echo(f"   ... and {len(orgs) - 10} more")
            else:
                click.echo("\n📋 No organizations")
        else:
            click.echo(f"❌ Not authenticated: {status['error']}")
            click.echo("\nRun 'sci github setup' to configure GitHub PAT")
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@github.command()
def setup() -> None:
    """Setup GitHub Personal Access Token"""
    from sentinelci.github_auth import GitHubAuth, GitHubAuthError

    try:
        auth = GitHubAuth()
        auth.prompt_and_store_pat()
        click.echo("\n✅ GitHub authentication configured successfully")
    except GitHubAuthError as e:
        click.echo(f"❌ Setup failed: {str(e)}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\n❌ Setup cancelled")
        sys.exit(1)


@github.command()
def logout() -> None:
    """Remove GitHub Personal Access Token (logout)"""
    from sentinelci.config import get_config

    try:
        config = get_config()
        
        # Check if PAT exists
        if not config.get_github_pat():
            click.echo("INFO: No GitHub PAT configured - already logged out")
            return
        
        # Confirm logout
        if not click.confirm("Remove GitHub PAT and logout?", default=False):
            click.echo("Logout cancelled")
            return
        
        # Remove PAT from config
        config.remove("git", "github_pat")
        
        click.echo("SUCCESS: GitHub PAT removed successfully")
        click.echo("INFO: You are now logged out")
        click.echo("\nRun 'sci github setup' to login again")
        
    except Exception as e:
        click.echo(f"ERROR: {str(e)}", err=True)
        sys.exit(1)


@github.command()
def verify() -> None:
    """Verify autonomous agent execution results"""
    from sentinelci.core.verification import verify_latest_execution
    
    try:
        verify_latest_execution()
    except Exception as e:
        click.echo(f"ERROR: {str(e)}", err=True)
        sys.exit(1)


@github.command()
@click.option("--multi", is_flag=True, help="Select multiple repositories")
@click.option("--search", default=None, help="Filter repositories by name/description")
@click.option("--visibility", type=click.Choice(["public", "private"]), help="Filter by visibility")
@click.option("--language", default=None, help="Filter by programming language")
def repos(multi: bool, search: str, visibility: str, language: str) -> None:
    """List and select GitHub repositories"""
    from sentinelci.github_repos import GitHubRepoManager, GitHubAuthError

    try:
        manager = GitHubRepoManager()
        
        click.echo("🔍 Fetching repositories...")
        all_repos = manager.fetch_all_repositories()
        
        if not all_repos:
            click.echo("No repositories found")
            return

        filtered_repos = manager.filter_repositories(
            all_repos,
            search=search,
            visibility=visibility,
            language=language,
        )

        if not filtered_repos:
            click.echo("No repositories match the filters")
            return

        click.echo(f"Found {len(filtered_repos)} repositories\n")

        selected = manager.select_repositories_interactive(filtered_repos, multi_select=multi)

        if selected:
            click.echo(f"\n✅ Selected {len(selected)} repository(ies):")
            for repo in selected:
                click.echo(f"   • {repo['full_name']}")
            
            # Show action menu for selected repositories
            _show_repo_action_menu(selected)
        else:
            click.echo("\n❌ No repositories selected")

    except GitHubAuthError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        click.echo("\nRun 'sci github setup' to configure GitHub PAT")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


def _show_repo_action_menu(repos: List[Dict[str, Any]]) -> None:
    """Show action menu for selected repositories"""
    try:
        import questionary
    except ImportError:
        click.echo("\n⚠️  Install questionary for interactive menu: pip install questionary")
        return

    actions = [
        "Analyze Security Configuration",
        "Run AI Security Analysis",
        "Autonomous Agent (Full Automation)",
        "Full Analysis + Simulation",
        "Clone and Scan Code",
        "Export Repository Info",
        "Cancel",
    ]

    for repo in repos:
        click.echo(f"\n{'='*70}")
        click.echo(f"Repository: {repo['full_name']}")
        click.echo(f"{'='*70}\n")

        try:
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
            elif action == "Full Analysis + Simulation":
                _action_full_analysis(repo)
            elif action == "Clone and Scan Code":
                _action_clone_and_scan(repo)
            elif action == "Export Repository Info":
                _action_export_info(repo)

        except KeyboardInterrupt:
            click.echo("\n❌ Cancelled")
            break


def _action_analyze_security(repo: Dict[str, Any]) -> None:
    """Analyze repository security configuration"""
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.output.github_dashboard import render_github_dashboard

    try:
        analyzer = GitHubSecurityAnalyzer()
        click.echo(f"\n🔍 Analyzing security configuration...")
        
        analysis = analyzer.analyze_repository(repo['full_name'])
        risk_score = analyzer.calculate_risk_score(analysis)

        render_github_dashboard(analysis, risk_score)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


def _action_ai_analysis(repo: Dict[str, Any]) -> None:
    """Run AI security analysis"""
    from sentinelci.config import get_config
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.output.ai_dashboard import render_ai_analysis
    import asyncio

    try:
        config = get_config()
        api_key = config.get_api_key()
        
        if not api_key:
            click.echo("❌ AI API key not configured. Run: sci --config")
            return

        click.echo(f"\n🤖 Running AI security analysis...")
        
        # Gather repository data
        github_analyzer = GitHubSecurityAnalyzer()
        analysis = github_analyzer.analyze_repository(repo['full_name'])
        
        # Prepare data for AI analysis
        metadata = {
            "name": repo['full_name'],
            "visibility": repo['visibility'],
            "language": repo.get('language', ''),
        }
        
        workflows = analysis.get('workflows', [])
        dependencies = []  # Would need to fetch from package files
        pipeline_data = {
            "ci_cd_files": analysis.get('ci_cd_files', {}),
            "failed_workflows": analysis.get('failed_workflows', []),
        }

        # Run AI analysis
        ai_analyzer = AISecurityAnalyzer(api_key)
        result = asyncio.run(
            ai_analyzer.analyze_repository(
                repo['full_name'],
                metadata,
                workflows,
                dependencies,
                pipeline_data,
            )
        )

        # Render results
        render_ai_analysis(result.to_dict())

        # Save to file
        import json
        output_file = f"{repo['name']}_ai_analysis.json"
        with open(output_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)
        
        click.echo(f"\n💾 Analysis saved to: {output_file}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


def _action_simulate_decisions(repo: Dict[str, Any]) -> None:
    """Run fully autonomous agent with complete automation"""
    from sentinelci.config import get_config
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.core.autonomous_agent import AutonomousSecurityAgent
    import asyncio

    try:
        config = get_config()
        api_key = config.get_api_key()
        
        if not api_key:
            click.echo("ERROR: AI API key not configured. Run: sci --config")
            return

        click.echo(f"\nAutonomous Security Agent")
        click.echo(f"Repository: {repo['full_name']}\n")
        
        # Phase 1: Security Analysis
        click.echo("Phase 1: Security Analysis")
        
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
            click.echo("SUCCESS: No security issues found")
            return
        
        click.echo(f"Found {len(findings)} issue(s)\n")
        
        # Phase 2: Create autonomous plan
        click.echo("Phase 2: Planning Autonomous Actions")
        
        agent = AutonomousSecurityAgent()
        plan = asyncio.run(agent.analyze_and_plan(repo['full_name'], findings))
        
        # Phase 3: Display plan
        agent.display_plan(plan)
        
        # Phase 4: Ask for confirmation
        click.echo("WARNING: The agent will autonomously:")
        click.echo("  - Edit files to fix vulnerabilities")
        click.echo("  - Create commits with changes")
        click.echo("  - Push to new branch")
        click.echo("  - Open pull request")
        click.echo("  - Create tracking issues\n")
        
        if not click.confirm("Allow autonomous execution?", default=False):
            click.echo("\nExecution cancelled")
            
            # Save plan for review
            import json
            plan_file = f"{repo['name']}_autonomous_plan.json"
            with open(plan_file, 'w') as f:
                json.dump(plan.to_dict(), f, indent=2)
            click.echo(f"Plan saved to {plan_file}")
            return
        
        # Phase 5: Execute autonomously
        click.echo()
        results = asyncio.run(agent.execute_plan(plan, auto_approve=False))
        
        # Phase 6: Display results
        agent.display_results(results)
        
        # Save execution log
        import json
        log_file = f"{repo['name']}_execution_log.json"
        with open(log_file, 'w') as f:
            json.dump({
                "plan": plan.to_dict(),
                "results": results,
            }, f, indent=2)
        
        click.echo(f"Execution log saved to {log_file}")

    except Exception as e:
        click.echo(f"ERROR: {str(e)}", err=True)
        import traceback
        traceback.print_exc()


def _action_full_analysis(repo: Dict[str, Any]) -> None:
    """Run full analysis with simulation"""
    from sentinelci.config import get_config
    from sentinelci.ai_analyzer import AISecurityAnalyzer
    from sentinelci.autonomous_engine import AutonomousEngine
    from sentinelci.github_security import GitHubSecurityAnalyzer
    from sentinelci.output.ai_dashboard import render_combined_report
    import asyncio
    import json

    try:
        config = get_config()
        api_key = config.get_api_key()
        
        if not api_key:
            click.echo("❌ AI API key not configured. Run: sci --config")
            return

        click.echo(f"\n🚀 Running full security analysis...")
        
        # Gather repository data
        github_analyzer = GitHubSecurityAnalyzer()
        analysis = github_analyzer.analyze_repository(repo['full_name'])
        
        metadata = {
            "name": repo['full_name'],
            "visibility": repo['visibility'],
            "language": repo.get('language', ''),
        }
        
        workflows = analysis.get('workflows', [])
        dependencies = []
        pipeline_data = {
            "ci_cd_files": analysis.get('ci_cd_files', {}),
            "failed_workflows": analysis.get('failed_workflows', []),
        }

        # Run AI analysis
        ai_analyzer = AISecurityAnalyzer(api_key)
        ai_result = asyncio.run(
            ai_analyzer.analyze_repository(
                repo['full_name'],
                metadata,
                workflows,
                dependencies,
                pipeline_data,
            )
        )

        # Simulate decisions
        engine = AutonomousEngine()
        simulation = engine.simulate(
            repo['full_name'],
            [f.to_dict() for f in ai_result.findings],
        )

        # Render combined report
        render_combined_report(ai_result.to_dict(), simulation.to_dict())

        # Save to files
        analysis_file = f"{repo['name']}_full_analysis.json"
        with open(analysis_file, 'w') as f:
            json.dump({
                "ai_analysis": ai_result.to_dict(),
                "autonomous_decisions": simulation.to_dict(),
            }, f, indent=2)
        
        click.echo(f"\n💾 Full analysis saved to: {analysis_file}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


def _action_clone_and_scan(repo: Dict[str, Any]) -> None:
    """Clone repository and scan code"""
    import subprocess
    import tempfile
    import shutil
    from pathlib import Path
    import os

    try:
        click.echo(f"\n📥 Cloning repository...")
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / repo['name']
        
        click.echo(f"Temp directory: {temp_dir}")
        click.echo(f"Clone URL: {repo['clone_url']}")
        
        # Clone repository with explicit config to ensure working tree
        result = subprocess.run(
            [
                "git", "clone",
                "--config", "core.bare=false",
                "--config", "core.worktree=.",
                repo['clone_url'],
                str(repo_path)
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
        
        if result.returncode != 0:
            click.echo(f"❌ Clone failed: {result.stderr}")
            
            # Check if repository is empty
            if "does not have any commits yet" in result.stderr or "empty repository" in result.stderr.lower():
                click.echo("⚠️  Repository appears to be empty (no commits)")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        click.echo(f"✅ Cloned to: {repo_path}")
        
        # Verify clone worked - check if files exist
        if not repo_path.exists():
            click.echo(f"❌ Repository path doesn't exist: {repo_path}")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        # Check if .git exists
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            click.echo(f"❌ .git directory not found - clone may have failed")
            shutil.rmtree(temp_dir, ignore_errors=True)
            return
        
        # List files to verify
        files = [f for f in repo_path.iterdir() if f.name != '.git']
        all_items = list(repo_path.iterdir())
        
        click.echo(f"📁 Found {len(all_items)} items in repository:")
        for f in all_items[:10]:  # Show first 10 items
            click.echo(f"  - {f.name}")
        if len(all_items) > 10:
            click.echo(f"  ... and {len(all_items) - 10} more")
        
        # Check if repository is empty (only .git)
        if len(files) == 0:
            click.echo("\n⚠️  Repository appears to be empty (no files besides .git)")
            
            # Check if there are any commits
            check_commits = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
            )
            
            if check_commits.returncode != 0:
                click.echo("⚠️  No commits found in repository - nothing to scan")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # Try to list branches
            list_branches = subprocess.run(
                ["git", "branch", "-a"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
            )
            
            click.echo(f"Branches: {list_branches.stdout}")
            
            # Try to reset to HEAD
            click.echo("Attempting to restore working tree...")
            reset_result = subprocess.run(
                ["git", "reset", "--hard", "HEAD"],
                cwd=str(repo_path),
                capture_output=True,
                text=True,
            )
            
            if reset_result.returncode != 0:
                click.echo(f"❌ Reset failed: {reset_result.stderr}")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
            
            # Re-check files
            files = [f for f in repo_path.iterdir() if f.name != '.git']
            click.echo(f"📁 After reset: {len(files)} files (excluding .git)")
            
            if len(files) == 0:
                click.echo("❌ Still no files - repository may be truly empty")
                shutil.rmtree(temp_dir, ignore_errors=True)
                return
        
        click.echo(f"\n🔍 Scanning code...")
        
        # Run scan
        from sentinelci.scanner import run_scan
        exit_code = run_scan(
            path=str(repo_path),
            use_diff=False,
            severity="medium",
            output_format="terminal",
            output_file=None,
            use_ai=True,
            watch_mode=False,
            enable_firmware=True,
            enable_urls=True,
        )
        
        # Cleanup
        click.echo(f"\n🧹 Cleaning up temporary directory...")
        shutil.rmtree(temp_dir, ignore_errors=True)
        
        if exit_code == 0:
            click.echo("\n✅ Scan completed successfully")
        else:
            click.echo(f"\n⚠️  Scan completed with exit code: {exit_code}")

    except subprocess.TimeoutExpired:
        click.echo(f"❌ Clone timed out after 300 seconds")
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        import traceback
        traceback.print_exc()
        if 'temp_dir' in locals():
            shutil.rmtree(temp_dir, ignore_errors=True)


def _action_export_info(repo: Dict[str, Any]) -> None:
    """Export repository information"""
    import json

    try:
        output_file = f"{repo['name']}_info.json"
        
        with open(output_file, 'w') as f:
            json.dump(repo, f, indent=2)
        
        click.echo(f"\n💾 Repository info exported to: {output_file}")
        click.echo(f"\nRepository: {repo['full_name']}")
        click.echo(f"Visibility: {repo['visibility']}")
        click.echo(f"Language: {repo.get('language', 'N/A')}")
        click.echo(f"Stars: {repo.get('stars', 0)}")
        click.echo(f"Open PRs: {repo.get('open_prs', 0)}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)


@github.command()
@click.argument("repository")
@click.option("--output", type=click.Path(), help="Save analysis to JSON file")
def analyze(repository: str, output: str) -> None:
    """Analyze GitHub repository security configuration"""
    from sentinelci.github_security import GitHubSecurityAnalyzer, GitHubAuthError
    from sentinelci.output.github_dashboard import render_github_dashboard
    import json

    try:
        analyzer = GitHubSecurityAnalyzer()
        
        click.echo(f"🔍 Analyzing repository: {repository}\n")
        
        analysis = analyzer.analyze_repository(repository)
        risk_score = analyzer.calculate_risk_score(analysis)

        render_github_dashboard(analysis, risk_score)

        if output:
            output_data = {
                "analysis": analysis,
                "risk_score": risk_score,
            }
            
            with open(output, "w") as f:
                json.dump(output_data, f, indent=2)
            
            click.echo(f"\n💾 Analysis saved to: {output}")

    except GitHubAuthError as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        click.echo("\nRun 'sci github setup' to configure GitHub PAT")
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
