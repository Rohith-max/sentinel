# SCI - Security Scanning CLI

A Python CLI tool that scans for security threats using AI-powered analysis.

## Features

- **Secret Scanning**: Detect hardcoded secrets using TruffleHog with enhanced false positive detection
- **Homograph Detection**: Identify visual URL spoofing attempts
- **CVE Analysis**: Scan firmware for known vulnerabilities using NVD API
- **AI Security Analysis**: Advanced AI-powered analysis for:
  - Hardcoded secrets exposure
  - Suspicious outbound calls
  - Dependency hash mismatch risks
  - Privilege escalation in workflows
  - Over-permissioned GitHub Actions tokens
  - Untrusted third-party actions
  - Supply chain security risks
- **Autonomous Decision Engine**: Intelligent automated responses:
  - Warn only
  - Block pipeline
  - Require manual approval
  - Suggest automated fixes
  - Open security issues
  - Create pull requests with remediation
- **GitHub Integration**: Repository security analysis and risk assessment
- **Multiple Output Formats**: Terminal (Rich), JSON, and Markdown reports
- **Git Integration**: Pre-commit and post-commit hook support

## Installation

```bash
pip install sci
```

## Quick Start

```bash
# Preferred root flag style
sci --scan --diff

# Include GitHub remote changes in diff scope (requires git remote configured)
sci --scan --diff --sync-github --remote origin --branch main

# PAT-authenticated GitHub sync (recommended for private repos)
sci --scan --diff --sync-github --remote origin --branch main --github-pat <YOUR_PAT>

# Scan a specific directory
sci --scan --target /path/to/code

# Real-time watch mode with fast polling
sci --watch --interval 1.0

# Watch + GitHub sync before each diff scan loop
sci --watch --interval 2 --sync-github --remote origin --branch main

# Auto-fix supported findings
sci --fix --path /path/to/code

# Install git pre-commit hook
sci hook install

# Generate a report from findings
sci report findings.json

# Complete onboarding in one command (including PAT)
sci config --ai-api-key <AI_KEY> --github-pat <GITHUB_PAT> --severity medium --enable-firmware --enable-urls --non-interactive
```

## Commands

Code Scanning:
- `sci --scan` - Scan for security threats
- `sci --watch` - Real-time watch mode that rescans on file changes
- `sci --fix` - Auto-fix supported findings (secrets and homograph URLs)
- `--sync-github --remote --branch` - Optional GitHub remote sync controls for scan/watch

GitHub Integration:
- `sci github auth` - Check GitHub authentication status
- `sci github setup` - Configure GitHub Personal Access Token
- `sci github repos` - List and select repositories interactively
- `sci github analyze REPO` - Comprehensive security analysis of a repository

Configuration & Reports:
- `sci --config` - Configure settings
- `sci --report` - Generate or convert reports
- `sci --version-info` - Display extended version details
- `sci hook install/remove` - Manage git hooks

## Configuration

Configure via `~/.config/sci/config.toml`:

```toml
[api]
ai_api_key = "gsk_..."
nvd_api_key = "your_nvd_key..."

[git]
github_pat = "ghp_..."

[scan]
severity_threshold = "medium"
enable_firmware_scanning = true
enable_url_detection = true

[output]
format = "terminal"
```

Environment variables (.env file):
- AI_API_KEY or GROQ_API_KEY - AI analysis
- NVD_API_KEY - CVE scanning (optional but recommended)
- GITHUB_PAT, GH_PAT, or GITHUB_TOKEN - GitHub integration

## GitHub Integration

Comprehensive GitHub repository security analysis with AI-powered insights:

```bash
# Setup authentication
sci github setup

# Check auth status
sci github auth

# List and select repositories (interactive menu)
sci github repos --search "myproject" --visibility private

# After selecting a repository, choose from:
# - Analyze Security Configuration
# - Run AI Security Analysis
# - Simulate Autonomous Decisions
# - Full Analysis + Simulation
# - Clone and Scan Code
# - Export Repository Info
```

AI Security Analysis includes:
- Hardcoded secrets exposure detection
- Suspicious outbound calls analysis
- Dependency hash mismatch risks
- Privilege escalation in workflows
- Over-permissioned tokens
- Untrusted third-party actions
- Supply chain security risks

Autonomous Decision Engine:
- Automatically determines appropriate responses
- Blocks pipelines for critical issues
- Requires approval for high severity
- Suggests automated fixes
- Creates PRs with remediation
- Opens security issues for tracking

See AI_ANALYSIS_GUIDE.md for detailed usage.

## Documentation

For detailed usage and examples, see the included documentation.

## License

MIT

well here is something my boss wouldnt find and would ruin his career, the api key used by the company

API_SECRET = 
