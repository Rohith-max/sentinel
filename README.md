# SentinelCI - AI-Powered Security Automation Platform

A comprehensive security automation platform that scans, analyzes, and remediates security issues across your codebase and GitHub repositories.

## 🚀 Key Features

### Core Scanning
- **Secret Scanning**: Detect hardcoded secrets using TruffleHog with enhanced false positive detection
- **Homograph Detection**: Identify visual URL spoofing attempts
- **CVE Analysis**: Scan firmware for known vulnerabilities using NVD API
- **Real-time Monitoring**: Watch mode for continuous security scanning

### AI-Powered Analysis
- **Advanced Threat Detection**: AI-powered analysis for:
  - Hardcoded secrets exposure
  - Suspicious outbound calls
  - Dependency hash mismatch risks
  - Privilege escalation in workflows
  - Over-permissioned GitHub Actions tokens
  - Untrusted third-party actions
  - Supply chain security risks

### Automated Remediation ✨ NEW
- **Pull Request Generation**: Automatically create PRs with security fixes
- **Issue Creation**: Generate detailed security issues
- **Automated Fixes**: Apply fixes for:
  - Secret removal
  - Dependency pinning
  - Workflow permission tightening
  - Unsafe action replacement

### Incident Visualization ✨ NEW
- **Security Incident Graphs**: Visualize relationships between:
  - Commits → Secrets → Workflows → Alerts
  - Dependencies and vulnerabilities
  - Pipeline events and failures
- **Attack Chain Timeline**: See how compromises could propagate
- **Risk Heatmaps**: Organization-wide security overview

### Organization Scanning ✨ NEW
- **Multi-Repository Analysis**: Scan entire organizations
- **Risk Ranking**: Identify riskiest repositories
- **Pattern Detection**: Find cross-repo security issues
- **Policy Enforcement**: Track org-wide violations

### Autonomous Decision Engine
- **Intelligent Responses**: Automated decision-making:
  - Warn only
  - Block pipeline
  - Require manual approval
  - Suggest automated fixes
  - Open security issues
  - Create pull requests with remediation

### Modern CLI ✨ NEW
- **Interactive Onboarding**: Guided setup wizard
- **Rich Terminal UI**: Beautiful, informative output
- **GitHub Integration**: Deep repository analysis
- **Multiple Output Formats**: Terminal, JSON, Markdown, HTML

## 📦 Installation

```bash
# Install from source
git clone https://github.com/Rohith-max/sentinel.git
cd sentinel
pip install -e .

# Or install from PyPI (coming soon)
pip install sentinelci
```

## 🎯 Quick Start

### First-Time Setup

```bash
# Interactive onboarding wizard
python -m sentinelci.cli_new onboard
```

This will guide you through:
1. AI API key configuration
2. GitHub integration setup
3. Scanning preferences

### Basic Usage

```bash
# Scan local code
sci scan

# Scan GitHub repositories
python -m sentinelci.cli_new github repos --search "myproject"

# Scan entire organization
python -m sentinelci.cli_new github scan-org YOUR_ORG --output report.json

# Auto-fix issues
sci fix --dry-run  # Preview fixes
sci fix            # Apply fixes
```

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 5 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Comprehensive setup and migration guide
- **[CLI_QUICK_REFERENCE.md](CLI_QUICK_REFERENCE.md)** - Command reference
- **[REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md)** - Architecture details
- **[PROJECT_STATUS_REPORT.md](PROJECT_STATUS_REPORT.md)** - Current status and roadmap

## 🎨 Usage Examples

### Example 1: Complete Security Audit

```bash
# 1. Onboard (first time only)
python -m sentinelci.cli_new onboard

# 2. Scan organization
python -m sentinelci.cli_new github scan-org acme-corp --output audit.json

# 3. Analyze specific repository
python -m sentinelci.cli_new github repos --search "api-gateway"
# Select repository → Choose "Full Analysis + Visualization"

# 4. Generate remediation PR
# Select repository → Choose "Generate Security PR"
```

### Example 2: Incident Investigation

```bash
# Analyze repository and view incident graph
python -m sentinelci.cli_new github repos --search "production-api"
# Select → Choose "View Incident Graph"

# Output:
# - Visual graph of security relationships
# - Attack chain timeline showing propagation
# - Critical points identified
# - JSON export for further analysis
```

### Example 3: Automated Remediation

```bash
# 1. Scan and analyze
python -m sentinelci.cli_new github repos --search "backend"

# 2. Simulate autonomous decisions
# Select → Choose "Simulate Autonomous Decisions"

# 3. Generate PRs with fixes
# Select → Choose "Generate Security PR"

# Result:
# - Branch created: security/remove-secret-42
# - File updated with fix
# - PR created with detailed description
# - Ready for review and merge
```

### Example 4: CI/CD Integration

```bash
# In your CI/CD pipeline:
export AI_API_KEY=${{ secrets.AI_API_KEY }}
export GITHUB_PAT=${{ secrets.GITHUB_PAT }}

# Scan and halt on critical issues
sci scan --diff --halt-on-critical --format json --output results.json
```

## 🔧 Commands

### Getting Started
```bash
python -m sentinelci.cli_new onboard    # Interactive setup wizard
sci version                              # Show version
```

### Code Scanning
```bash
sci scan                                 # Scan current directory
sci scan --path /path/to/code           # Scan specific path
sci scan --diff                          # Scan git diff only
sci watch                                # Real-time monitoring
sci fix                                  # Auto-fix issues
sci fix --dry-run                        # Preview fixes
```

### GitHub Integration ✨ NEW
```bash
python -m sentinelci.cli_new github auth              # Check authentication
python -m sentinelci.cli_new github setup             # Configure GitHub PAT
python -m sentinelci.cli_new github repos             # List & analyze repositories
python -m sentinelci.cli_new github scan-org ORG      # Scan entire organization
```

### Repository Actions (Interactive Menu)
After selecting a repository:
1. **Analyze Security Configuration** - Branch protection, alerts, workflows
2. **Run AI Security Analysis** - Advanced threat detection
3. **Simulate Autonomous Decisions** - Automated response simulation
4. **Generate Security PR** ✨ NEW - Create PR with fixes
5. **View Incident Graph** ✨ NEW - Visualize security relationships
6. **Full Analysis + Visualization** - Complete security audit

### Configuration & Reports
```bash
sci config                               # Configure settings
sci report findings.json                 # Generate report
sci hook install                         # Install git pre-commit hook
```

## ⚙️ Configuration

### Config File Location
- **User config**: `~/.config/sci/config.toml`
- **Environment variables**: `.env` file in project root

### Config Structure
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

### Environment Variables
```bash
# AI Analysis
AI_API_KEY=gsk_...
GROQ_API_KEY=gsk_...

# GitHub Integration
GITHUB_PAT=ghp_...
GH_PAT=ghp_...
GITHUB_TOKEN=ghp_...

# CVE Scanning
NVD_API_KEY=...
```

## 🔐 GitHub Integration

### Setup

```bash
# Configure GitHub PAT
python -m sentinelci.cli_new github setup

# Check authentication
python -m sentinelci.cli_new github auth
```

### Features

**Repository Analysis:**
- Security configuration audit
- Branch protection review
- Secret scanning alerts
- Dependabot alerts
- Workflow analysis
- Risk scoring

**AI Security Analysis:**
- Hardcoded secrets detection
- Suspicious outbound calls
- Dependency vulnerabilities
- Privilege escalation
- Over-permissioned tokens
- Untrusted third-party actions
- Supply chain risks

**Automated Remediation:** ✨ NEW
- Generate PRs with security fixes
- Create security issues
- Automated branch management
- File updates via GitHub API

**Incident Visualization:** ✨ NEW
- Security relationship graphs
- Attack chain timelines
- Propagation analysis
- Risk assessment

**Organization Scanning:** ✨ NEW
- Scan all org repositories
- Aggregate risk heatmap
- Cross-repo pattern detection
- Policy violation tracking

### Usage

```bash
# List repositories with filters
python -m sentinelci.cli_new github repos --search "api" --visibility private

# Scan entire organization
python -m sentinelci.cli_new github scan-org acme-corp --output report.json

# Interactive repository analysis
python -m sentinelci.cli_new github repos
# Select repository → Choose action from menu
```

## 🏗️ Architecture

### Modular Structure

```
sentinelci/
├── core/                    # Core modules
│   ├── auth.py             # GitHub authentication
│   ├── discovery.py        # Repository discovery
│   ├── remediation.py      # PR/Issue generation
│   └── visualization.py    # Graphs & heatmaps
├── cli_new.py              # Modern CLI (Typer)
├── scanner.py              # Code scanning engine
├── ai_analyzer.py          # AI security analysis
├── autonomous_engine.py    # Decision engine
├── github_security.py      # GitHub analysis
└── config.py               # Configuration
```

### Key Components

- **Authentication**: Secure GitHub PAT management
- **Discovery**: Repository and organization scanning
- **Remediation**: Automated PR and issue generation
- **Visualization**: Incident graphs and heatmaps
- **Analysis**: AI-powered threat detection
- **Automation**: Autonomous decision-making

## 🧪 Testing

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run specific test
pytest tests/test_auth.py

# Run with coverage
pytest --cov=sentinelci
```

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Update documentation
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for development setup.

## 📋 Roadmap

### Completed ✅
- Modular architecture
- Automated remediation (PR/Issue generation)
- Incident graph visualization
- Organization-wide scanning
- Interactive CLI with onboarding

### In Progress 🚧
- Comprehensive test suite
- Performance optimizations
- Web dashboard

### Planned 📋
- Parallel scanning
- Custom rule engine
- Slack/Teams notifications
- CI/CD integrations
- API server

See [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md) for details.

## 📄 License

MIT License - see [LICENSE](LICENSE) file

## 🙏 Acknowledgments

- TruffleHog for secret scanning
- Groq for AI analysis
- GitHub API for repository integration
- Rich for terminal UI

## 📞 Support

- **Documentation**: See guides in repository
- **Issues**: https://github.com/Rohith-max/sentinel/issues
- **Discussions**: https://github.com/Rohith-max/sentinel/discussions
- **Email**: support@sentinelci.dev

---

**Made with ❤️ by the SentinelCI Team** 
