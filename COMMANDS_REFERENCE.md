SCI Commands Reference

GitHub Integration Commands

Authentication

sci github setup
  Configure GitHub Personal Access Token
  - Prompts for PAT securely
  - Validates against GitHub API
  - Stores in ~/.config/sci/config.toml

sci github auth
  Check GitHub authentication status
  - Shows authenticated username
  - Displays user profile information
  - Lists organizations

Repository Management

sci github repos
  List and select repositories interactively
  
  Options:
    --multi              Select multiple repositories
    --search TEXT        Filter by name/description
    --visibility public|private
    --language TEXT      Filter by programming language
  
  Examples:
    sci github repos
    sci github repos --multi
    sci github repos --search "api"
    sci github repos --visibility private
    sci github repos --language python
    sci github repos --search "myproject" --visibility private --language python

Security Analysis

sci github analyze REPOSITORY
  Analyze repository security configuration
  
  Arguments:
    REPOSITORY          Repository full name (owner/repo)
  
  Options:
    --output PATH       Save analysis to JSON file
  
  Examples:
    sci github analyze myorg/myrepo
    sci github analyze myorg/myrepo --output report.json

Code Scanning Commands

Basic Scanning

sci --scan
  Scan current directory for security threats
  
  Options:
    --path PATH         Path to scan (default: .)
    --target PATH       Override target for scan
    --diff              Scan git diff instead of full directory
    --severity LEVEL    Minimum severity (low/medium/high/critical)
    --format FORMAT     Output format (terminal/json/markdown)
    --output PATH       Save results to file
    --no-ai             Disable AI analysis
    --halt-on-critical  Exit with error on critical findings
    --no-firmware       Disable firmware CVE scanning
    --no-urls           Disable homograph URL detection
  
  Examples:
    sci --scan
    sci --scan --path /path/to/code
    sci --scan --diff --severity high
    sci --scan --format json --output findings.json
    sci --scan --no-ai --halt-on-critical

Watch Mode

sci --watch
  Real-time monitoring and scanning on file changes
  
  Options:
    --path PATH         Path to watch (default: .)
    --interval FLOAT    Polling interval in seconds (default: 2.0)
    --severity LEVEL    Minimum severity to report
    --format FORMAT     Output format
    --output PATH       Save results to file
    --no-ai             Disable AI analysis
    --sync-github       Fetch from GitHub remote before scans
    --remote TEXT       Git remote name (default: origin)
    --branch TEXT       Git branch for comparison
    --github-pat TEXT   GitHub PAT for authenticated fetch
    --halt-on-critical  Exit with error on critical findings
    --no-firmware       Disable firmware CVE scanning
    --no-urls           Disable homograph URL detection
  
  Examples:
    sci --watch
    sci --watch --interval 1.0
    sci --watch --sync-github --remote origin --branch main
    sci --watch --path ./src --severity high

Auto-Fix

sci --fix
  Automatically fix supported findings
  
  Options:
    --path PATH         Path to fix (default: .)
    --diff              Fix based on git diff scope
    --severity LEVEL    Minimum severity to include
    --no-firmware       Disable firmware CVE scanning
    --no-urls           Disable homograph URL detection
    --dry-run           Preview changes without writing files
    --no-backup         Do not create .sci.bak backup files
  
  Examples:
    sci --fix
    sci --fix --path ./src
    sci --fix --dry-run
    sci --fix --diff --severity high

Git Hooks

sci hook install
  Install pre-commit git hook
  
  Options:
    --blocking          Fail commit on critical findings
  
  Examples:
    sci hook install
    sci hook install --blocking

sci hook remove
  Remove git hook

Configuration

sci --config
  Configure SCI settings interactively
  
  Options:
    --ai-api-key TEXT       Set AI API key
    --github-pat TEXT       Set GitHub PAT
    --nvd-api-key TEXT      Set NVD API key
    --clear-github-pat      Remove stored GitHub PAT
    --severity LEVEL        Set default minimum severity
    --enable-firmware       Enable firmware CVE scanning
    --disable-firmware      Disable firmware CVE scanning
    --enable-urls           Enable homograph URL detection
    --disable-urls          Disable homograph URL detection
    --non-interactive       Apply options without wizard
  
  Examples:
    sci --config
    sci --config --ai-api-key "gsk_..."
    sci --config --github-pat "ghp_..." --non-interactive
    sci --config --severity high --enable-firmware

Reports

sci --report
  Generate or convert security reports
  
  Options:
    --incident-file PATH    Input report file (default: findings.json)
    --format FORMAT         Output format (terminal/json/markdown/html)
    --output PATH           Save report to file
  
  Examples:
    sci --report
    sci --report --incident-file findings.json
    sci --report --format markdown --output report.md

Version Information

sci --version-info
  Display extended version and environment information

sci version
  Display version details

Subcommand Mode

All root flags also available as subcommands:

sci scan [OPTIONS]
sci watch [OPTIONS]
sci fix [OPTIONS]
sci config [OPTIONS]
sci report [OPTIONS]
sci hook install [OPTIONS]
sci hook remove

Environment Variables

AI_API_KEY or GROQ_API_KEY
  AI analysis API key (required for AI features)

NVD_API_KEY or NIST_NVD_API_KEY
  National Vulnerability Database API key
  Optional but recommended for CVE scanning
  Get from: https://nvd.nist.gov/developers/request-an-api-key

GITHUB_PAT or GH_PAT or GITHUB_TOKEN
  GitHub Personal Access Token
  Required for GitHub integration features
  Get from: https://github.com/settings/tokens/new
  Scopes: repo, read:org, read:user, workflow

Configuration File

Location: ~/.config/sci/config.toml

[api]
ai_api_key = "gsk_..."
nvd_api_key = "..."

[git]
github_pat = "ghp_..."

[scan]
severity_threshold = "medium"
enable_firmware_scanning = true
enable_url_detection = true

[output]
format = "terminal"

Common Workflows

Initial Setup

sci --config
sci github setup

Local Code Scanning

sci --scan --path .
sci --scan --diff --severity high
sci --fix --dry-run

Continuous Monitoring

sci --watch --interval 2
sci --watch --sync-github --remote origin

GitHub Security Analysis

sci github auth
sci github repos --search "myproject"
sci github analyze owner/repo --output report.json

Combined Workflow

# Analyze GitHub configuration
sci github analyze owner/repo

# Clone repository
git clone https://github.com/owner/repo

# Scan code
sci --scan --path ./repo --severity high

# Watch for changes
sci --watch --path ./repo

# Auto-fix issues
sci --fix --path ./repo

CI/CD Integration

# Pre-commit hook
sci hook install --blocking

# CI pipeline
sci --scan --diff --halt-on-critical --format json --output findings.json

# Generate report
sci --report --incident-file findings.json --format markdown --output report.md

Exit Codes

0 - Success (no critical findings or findings within threshold)
1 - Critical findings (when --halt-on-critical is used)
2 - Error (configuration error, scan failure, etc.)

Output Formats

terminal
  Rich terminal output with colors and tables
  Default format for interactive use

json
  Machine-readable JSON format
  Suitable for CI/CD integration and automation

markdown
  Human-readable Markdown format
  Suitable for documentation and reports

html
  HTML format (report command only)
  Suitable for web viewing

Severity Levels

LOW
  Minor issues, informational findings

MEDIUM
  Moderate security concerns
  Default threshold

HIGH
  Serious security issues
  Should be addressed promptly

CRITICAL
  Severe security vulnerabilities
  Requires immediate attention

Quick Reference

Setup:
  sci --config
  sci github setup

Scan:
  sci --scan
  sci --scan --diff --severity high

Watch:
  sci --watch --interval 2

Fix:
  sci --fix --dry-run

GitHub:
  sci github auth
  sci github repos
  sci github analyze owner/repo

Reports:
  sci --report --format markdown

Hooks:
  sci hook install --blocking

For detailed documentation:
- README.md - Main documentation
- README_GITHUB.md - GitHub integration
- GITHUB_QUICKSTART.md - Quick start guide
