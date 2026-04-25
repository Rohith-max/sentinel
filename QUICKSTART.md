# SentinelCI Quick Start Guide

Get up and running with SentinelCI in 5 minutes!

## Prerequisites

- Python 3.11 or higher
- Git
- GitHub account (for repository scanning)

## Installation

### Option 1: Install from Source (Recommended for Development)

```bash
# Clone the repository
git clone https://github.com/Rohith-max/sentinel.git
cd sentinel

# Install dependencies
pip install -e .

# Verify installation
python -m sentinelci.cli_new version
```

### Option 2: Install from PyPI (Coming Soon)

```bash
pip install sentinelci
```

## First-Time Setup

### Step 1: Run Onboarding

```bash
python -m sentinelci.cli_new onboard
```

This interactive wizard will:
1. Configure your AI API key (get one from https://console.groq.com/keys)
2. Setup GitHub integration (optional)
3. Set scanning preferences

### Step 2: Test Your Setup

```bash
# Check GitHub authentication
python -m sentinelci.cli_new github auth

# List your repositories
python -m sentinelci.cli_new github repos
```

## Quick Examples

### Example 1: Scan Local Code

```bash
# Scan current directory
sci scan

# Scan specific path
sci scan --path /path/to/your/code

# Scan only changed files
sci scan --diff
```

### Example 2: Analyze GitHub Repository

```bash
# List and select repositories
python -m sentinelci.cli_new github repos --search "myproject"

# Interactive menu will appear:
# 1. Analyze Security Configuration
# 2. Run AI Security Analysis
# 3. Simulate Autonomous Decisions
# 4. Generate Security PR
# 5. View Incident Graph
# 6. Full Analysis + Visualization

# Choose option 6 for complete analysis
```

### Example 3: Scan Organization

```bash
# Scan all repositories in your organization
python -m sentinelci.cli_new github scan-org YOUR_ORG_NAME --output report.json

# View risk heatmap and ranked repositories
```

### Example 4: Auto-Fix Issues

```bash
# Preview fixes (dry-run)
sci fix --dry-run

# Apply fixes
sci fix

# Fix specific path
sci fix --path /path/to/code
```

## Common Commands

```bash
# Onboarding
python -m sentinelci.cli_new onboard

# GitHub authentication
python -m sentinelci.cli_new github auth
python -m sentinelci.cli_new github setup

# Repository analysis
python -m sentinelci.cli_new github repos
python -m sentinelci.cli_new github scan-org ORG_NAME

# Code scanning
sci scan
sci scan --diff
sci watch

# Auto-fix
sci fix
sci fix --dry-run

# Configuration
sci config

# Help
python -m sentinelci.cli_new --help
sci --help
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```bash
# AI Analysis (required)
AI_API_KEY=gsk_your_groq_api_key_here

# GitHub Integration (optional)
GITHUB_PAT=ghp_your_github_token_here

# CVE Scanning (optional, for higher rate limits)
NVD_API_KEY=your_nvd_api_key_here
```

### Config File

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
```

## Troubleshooting

### Issue: "No module named 'typer'"

```bash
pip install typer==0.9.0 questionary==2.0.1
```

### Issue: "GitHub PAT not configured"

```bash
# Option 1: Run setup
python -m sentinelci.cli_new github setup

# Option 2: Set environment variable
export GITHUB_PAT=ghp_your_token_here
```

### Issue: "AI API key not configured"

```bash
# Option 1: Run onboarding
python -m sentinelci.cli_new onboard

# Option 2: Set environment variable
export AI_API_KEY=gsk_your_key_here
```

## Next Steps

1. **Read the Documentation**
   - [SETUP_GUIDE.md](SETUP_GUIDE.md) - Comprehensive setup guide
   - [CLI_QUICK_REFERENCE.md](CLI_QUICK_REFERENCE.md) - Command reference
   - [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Architecture details

2. **Try Advanced Features**
   - Generate security PRs
   - View incident graphs
   - Scan entire organizations
   - Simulate autonomous decisions

3. **Integrate with CI/CD**
   - Add to GitHub Actions
   - Configure pre-commit hooks
   - Set up automated scanning

4. **Customize**
   - Adjust severity thresholds
   - Configure scanning options
   - Set up notifications

## Getting Help

- **Documentation**: See README.md and guides in the repository
- **Issues**: https://github.com/Rohith-max/sentinel/issues
- **Help Command**: `python -m sentinelci.cli_new --help`

## What's Next?

After completing the quick start:

1. **Scan Your First Repository**
   ```bash
   python -m sentinelci.cli_new github repos
   ```

2. **Generate Your First Security PR**
   - Select a repository
   - Choose "Generate Security PR"
   - Review and merge

3. **Scan Your Organization**
   ```bash
   python -m sentinelci.cli_new github scan-org YOUR_ORG
   ```

4. **Set Up Automation**
   - Install git hooks: `sci hook install`
   - Add to CI/CD pipeline
   - Configure notifications

## Support

Need help? We're here for you!

- 📖 Read the [documentation](README.md)
- 🐛 Report [issues](https://github.com/Rohith-max/sentinel/issues)
- 💬 Ask questions in [discussions](https://github.com/Rohith-max/sentinel/discussions)
- 📧 Email: support@sentinelci.dev

---

**Happy Scanning! 🔒**
