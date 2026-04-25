# SentinelCI CLI Quick Reference

## Getting Started

```bash
# Interactive onboarding (recommended for first-time users)
sci onboard

# Check version
sci version
```

## GitHub Commands

### Authentication

```bash
# Check authentication status
sci github auth

# Setup GitHub PAT
sci github setup
```

### Repository Management

```bash
# List all repositories (interactive selection)
sci github repos

# Filter repositories
sci github repos --search "api"
sci github repos --visibility private
sci github repos --language python
sci github repos --search "backend" --visibility private --language go

# Scan specific organization
sci github scan-org ORGANIZATION_NAME
sci github scan-org acme-corp --output acme_report.json
```

### Repository Actions (Interactive Menu)

After selecting a repository, choose from:

1. **Analyze Security Configuration**
   - Branch protection
   - Secret scanning alerts
   - Dependabot alerts
   - Workflow analysis
   - Risk scoring

2. **Run AI Security Analysis**
   - Hardcoded secrets detection
   - Suspicious outbound calls
   - Dependency vulnerabilities
   - Privilege escalation
   - Token permissions
   - Third-party actions
   - Supply chain risks

3. **Simulate Autonomous Decisions**
   - Automated response simulation
   - Action recommendations
   - Risk-based decisions
   - Fix suggestions

4. **Generate Security PR**
   - Automated branch creation
   - File updates
   - PR with remediation steps
   - Ready to review and merge

5. **View Incident Graph**
   - Visual relationship graph
   - Attack chain timeline
   - Propagation analysis
   - JSON export

6. **Full Analysis + Visualization**
   - Runs all analyses
   - Complete security report
   - All visualizations

## Code Scanning (Existing Commands)

### Basic Scanning

```bash
# Scan current directory
sci scan

# Scan specific path
sci scan --path /path/to/code

# Scan git diff only
sci scan --diff

# Scan with GitHub sync
sci scan --diff --sync-github --remote origin --branch main
```

### Watch Mode

```bash
# Real-time monitoring
sci watch

# Watch with custom interval
sci watch --interval 1.0

# Watch with GitHub sync
sci watch --sync-github --remote origin --branch main
```

### Auto-Fix

```bash
# Fix detected issues
sci fix

# Fix with dry-run (preview only)
sci fix --dry-run

# Fix without backups
sci fix --no-backup
```

### Output Formats

```bash
# Terminal output (default)
sci scan --format terminal

# JSON output
sci scan --format json --output report.json

# Markdown output
sci scan --format markdown --output report.md
```

### Severity Filtering

```bash
# Show only critical issues
sci scan --severity critical

# Show high and above
sci scan --severity high

# Show medium and above (default)
sci scan --severity medium

# Show all issues
sci scan --severity low
```

### Feature Toggles

```bash
# Disable AI analysis
sci scan --no-ai

# Disable firmware scanning
sci scan --no-firmware

# Disable URL detection
sci scan --no-urls

# Halt on critical findings
sci scan --halt-on-critical
```

## Git Hooks

```bash
# Install pre-commit hook
sci hook install

# Install blocking hook (fails on critical)
sci hook install --blocking

# Remove hook
sci hook remove
```

## Reports

```bash
# Generate report from findings
sci report findings.json

# Generate with specific format
sci report findings.json --format markdown --output report.md
sci report findings.json --format html --output report.html
```

## Configuration

```bash
# Interactive configuration wizard
sci config

# Set specific options
sci config --ai-api-key YOUR_KEY
sci config --github-pat YOUR_PAT
sci config --nvd-api-key YOUR_KEY
sci config --severity medium
sci config --enable-firmware
sci config --enable-urls

# Non-interactive configuration
sci config --ai-api-key KEY --github-pat PAT --non-interactive

# Clear GitHub PAT
sci config --clear-github-pat
```

## Common Workflows

### Workflow 1: First-Time Setup

```bash
# 1. Run onboarding
sci onboard

# 2. Scan your code
sci scan --path ./myproject

# 3. Review findings and fix
sci fix --dry-run  # Preview fixes
sci fix            # Apply fixes
```

### Workflow 2: GitHub Repository Audit

```bash
# 1. Setup GitHub authentication
sci github setup

# 2. List and select repositories
sci github repos --search "production"

# 3. Select repository and choose "Full Analysis + Visualization"

# 4. Review results and generate PRs if needed
```

### Workflow 3: Organization Security Audit

```bash
# 1. Scan entire organization
sci github scan-org acme-corp --output acme_audit.json

# 2. Review risk heatmap

# 3. Focus on high-risk repositories

# 4. Generate remediation PRs
```

### Workflow 4: CI/CD Integration

```bash
# In your CI/CD pipeline:

# 1. Install SentinelCI
pip install sci

# 2. Configure (use environment variables)
export AI_API_KEY=${{ secrets.AI_API_KEY }}
export GITHUB_PAT=${{ secrets.GITHUB_PAT }}

# 3. Scan code
sci scan --diff --halt-on-critical --format json --output scan_results.json

# 4. Upload results as artifact
```

### Workflow 5: Pre-Commit Hook

```bash
# 1. Install hook
sci hook install --blocking

# 2. Make changes and commit
git add .
git commit -m "Add feature"

# 3. Hook runs automatically
# - Scans staged changes
# - Blocks commit if critical issues found
# - Shows findings in terminal
```

## Environment Variables

```bash
# AI Analysis
export AI_API_KEY=gsk_...
export GROQ_API_KEY=gsk_...

# GitHub Integration
export GITHUB_PAT=ghp_...
export GH_PAT=ghp_...
export GITHUB_TOKEN=ghp_...

# CVE Scanning
export NVD_API_KEY=...
```

## Configuration File

Location: `~/.config/sci/config.toml`

```toml
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
```

## Exit Codes

- `0` - Success (no critical issues or not halting)
- `1` - Critical issues found (with --halt-on-critical)
- `2` - Error (configuration, network, etc.)

## Tips & Tricks

### Tip 1: Use Filters to Speed Up Discovery

```bash
# Instead of listing all repos
sci github repos

# Filter to specific subset
sci github repos --visibility private --language python --search "api"
```

### Tip 2: Save Organization Scans for Later

```bash
# Scan once
sci github scan-org acme --output acme_scan.json

# Reuse results for visualization
# (Load from JSON and visualize)
```

### Tip 3: Combine with Git Aliases

```bash
# Add to ~/.gitconfig
[alias]
    scan = !sci scan --diff
    fix = !sci fix --dry-run

# Usage
git scan
git fix
```

### Tip 4: Use Watch Mode During Development

```bash
# Terminal 1: Development
vim mycode.py

# Terminal 2: Continuous scanning
sci watch --interval 2
```

### Tip 5: Generate Reports for Compliance

```bash
# Scan and generate multiple formats
sci scan --format json --output compliance/scan.json
sci report compliance/scan.json --format markdown --output compliance/report.md
sci report compliance/scan.json --format html --output compliance/report.html
```

## Troubleshooting

### Issue: Command not found

```bash
# Ensure installed
pip install sci

# Or use module syntax
python -m sentinelci.cli_new COMMAND
```

### Issue: Authentication failed

```bash
# Re-setup GitHub PAT
sci github setup

# Or set environment variable
export GITHUB_PAT=ghp_your_token_here
```

### Issue: AI analysis not working

```bash
# Check API key
sci config

# Or set environment variable
export AI_API_KEY=gsk_your_key_here
```

### Issue: Rate limit exceeded

```bash
# For GitHub API: Wait or use authenticated requests
sci github setup  # Authenticated requests have higher limits

# For NVD API: Add API key for higher limits
sci config --nvd-api-key YOUR_KEY
```

## Getting Help

```bash
# General help
sci --help

# Command-specific help
sci scan --help
sci github --help
sci github repos --help

# Version information
sci version
```

## Quick Command Reference

| Command | Description |
|---------|-------------|
| `sci onboard` | Interactive setup wizard |
| `sci scan` | Scan code for security issues |
| `sci watch` | Real-time monitoring |
| `sci fix` | Auto-fix issues |
| `sci github auth` | Check GitHub authentication |
| `sci github setup` | Configure GitHub PAT |
| `sci github repos` | List and analyze repositories |
| `sci github scan-org ORG` | Scan entire organization |
| `sci hook install` | Install git pre-commit hook |
| `sci report FILE` | Generate report |
| `sci config` | Configure settings |
| `sci version` | Show version |

## Support

- Documentation: See README.md and SETUP_GUIDE.md
- Issues: https://github.com/your-org/sentinelci/issues
- Help: `sci --help`
