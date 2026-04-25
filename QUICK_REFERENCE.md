SentinelCI Quick Reference Card

Installation & Setup

pip install -e .
sci --config --ai-api-key "your_groq_key"
sci --config --nvd-api-key "your_nvd_key"
sci github setup

Basic Commands

Code Scanning:
sci --scan                          # Scan current directory
sci --scan --diff                   # Scan git diff only
sci --scan --severity high          # High severity and above
sci --watch --interval 2            # Watch mode

GitHub Integration:
sci github auth                     # Check authentication
sci github repos                    # Interactive repository selection
sci github repos --search "api"     # Filter repositories
sci github analyze owner/repo       # Analyze security config

AI Analysis:
# After selecting repo with 'sci github repos':
- Run AI Security Analysis          # AI-powered analysis
- Simulate Autonomous Decisions     # Decision simulation
- Full Analysis + Simulation        # Complete analysis
- Clone and Scan Code              # Clone + scan

Auto-Fix:
sci --fix --dry-run                # Preview fixes
sci --fix --path ./src             # Apply fixes

Git Hooks:
sci hook install                   # Install pre-commit hook
sci hook install --blocking        # Block on critical
sci hook remove                    # Remove hook

Configuration

Environment Variables:
AI_API_KEY=your_groq_key
NVD_API_KEY=your_nvd_key
GITHUB_PAT=your_github_pat

Config File (~/.config/sci/config.toml):
[api]
ai_api_key = "gsk_..."
nvd_api_key = "..."

[git]
github_pat = "ghp_..."

[scan]
severity_threshold = "medium"
enable_firmware_scanning = true
enable_url_detection = true

AI Analysis Categories

1. Secrets - Hardcoded credentials
2. Outbound Calls - Suspicious network calls
3. Dependencies - Hash mismatches, unpinned versions
4. Privilege Escalation - Unnecessary elevated privileges
5. Token Permissions - Over-permissioned tokens
6. Third-Party Actions - Untrusted actions
7. Supply Chain - Verification gaps

Autonomous Actions

Warn Only - Low severity, informational
Block Pipeline - Critical issues, prevents deployment
Require Approval - High severity, needs review
Suggest Fix - Automated fix available
Open Issue - Creates GitHub issue
Create PR - Automated fix pull request

Decision Rules

CRITICAL → Block Pipeline + Create PR/Issue
HIGH → Require Approval + Create PR/Fix
MEDIUM → Warn Only + Open Issue
LOW → Warn Only

Risk Levels

LOW: 0-14 points (green)
MEDIUM: 15-29 points (yellow)
HIGH: 30-49 points (orange)
CRITICAL: 50+ points (red)

Output Formats

Terminal - Rich UI with colors
JSON - Machine-readable
Markdown - Documentation

Common Workflows

Quick Scan:
sci --scan --diff --severity high

Full Repository Analysis:
sci github repos
# Select repo → Full Analysis + Simulation

CI/CD Integration:
sci --scan --halt-on-critical --format json --output findings.json

Watch Mode:
sci --watch --interval 2 --sync-github

Keyboard Shortcuts

Interactive Menus:
↑↓ - Navigate
Space - Select (multi-select)
Enter - Confirm
Ctrl+C - Cancel

Troubleshooting

API Key Issues:
sci --config --ai-api-key "your_key"

GitHub Auth:
sci github setup

No Findings:
- Check file patterns
- Verify git repository
- Review severity threshold

False Positives:
- Enhanced detection active
- Context-aware scanning
- Adjust confidence threshold

Performance:
- Use --diff for faster scans
- Enable caching
- Parallel processing active

File Locations

Config: ~/.config/sci/config.toml
Logs: ./sentinelci/output/
Reports: ./*_analysis.json, *_decisions.json
Backups: ./*.sci.bak

Exit Codes

0 - Success
1 - Critical findings (with --halt-on-critical)
2 - Error (config, scan failure)

Quick Tips

1. Use --diff for faster scans
2. Enable AI analysis for better insights
3. Review autonomous decisions before applying
4. Pin dependencies with hashes
5. Use GitHub Secrets for credentials
6. Pin third-party actions to SHA
7. Restrict token permissions
8. Enable branch protection
9. Regular security audits
10. Automate in CI/CD

Common Patterns

Scan PR Changes:
sci --scan --diff --severity high --halt-on-critical

Weekly Audit:
sci github repos --search "myorg/*"
# Select all → Full Analysis

Pre-commit:
sci hook install --blocking

Watch Development:
sci --watch --interval 1 --path ./src

Export Analysis:
sci github repos
# Select repo → Export Repository Info

API Keys

Groq API:
https://console.groq.com/keys

NVD API:
https://nvd.nist.gov/developers/request-an-api-key

GitHub PAT:
https://github.com/settings/tokens/new
Scopes: repo, read:org, read:user, workflow

Documentation

README.md - Main documentation
AI_ANALYSIS_GUIDE.md - AI analysis guide
GITHUB_QUICKSTART.md - GitHub integration
COMMANDS_REFERENCE.md - All commands
ARCHITECTURE.md - System design
LATEST_UPDATES.md - Recent changes

Support

Check documentation first
Verify API keys and permissions
Review error messages
Check GitHub API status
Ensure network connectivity

Examples

# Basic scan
sci --scan

# Scan with AI
sci --scan --path . --severity high

# GitHub analysis
sci github repos --search "api" --visibility private

# Full workflow
sci github repos
# Select → Full Analysis + Simulation

# CI/CD
sci --scan --diff --halt-on-critical --format json

# Watch mode
sci --watch --interval 2 --sync-github

# Auto-fix
sci --fix --dry-run --path ./src

# Export
sci --report --format markdown --output report.md

Version Info

sci --version-info
sci version

Help

sci --help
sci github --help
sci scan --help
sci github repos --help

Quick Start

1. Install: pip install -e .
2. Configure: sci --config
3. Setup GitHub: sci github setup
4. Select repo: sci github repos
5. Analyze: Choose action from menu
6. Review: Check terminal output
7. Export: Save JSON results
8. Fix: Apply suggested remediations

That's it! You're ready to use SentinelCI.
