# SentinelCI

**AI-Powered Security Scanning and Autonomous Remediation Platform**

[![PyPI version](https://badge.fury.io/py/sentinelci.svg)](https://badge.fury.io/py/sentinelci)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

SentinelCI is an advanced security scanning platform that combines AI-powered analysis with autonomous remediation capabilities. It detects vulnerabilities, security misconfigurations, and compliance issues across your codebase and CI/CD pipelines, then automatically creates fixes and pull requests.

## 🚀 Quick Start

### Installation

**Python (Recommended):**
```bash
pip install sentinelci
```

**NPM:**
```bash
npm install -g sentinelci
```

### Important: PATH Configuration

After installing via pip, if the `sci` command is not found, you need to add Python's Scripts directory to your PATH:

**Windows:**
```powershell
# The warning message will show you the exact path, typically:
# C:\Users\YourName\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_xxx\LocalCache\local-packages\Python311\Scripts

# Add to PATH temporarily (current session):
$env:PATH += ";C:\Users\YourName\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.11_xxx\LocalCache\local-packages\Python311\Scripts"

# Or add permanently via System Properties > Environment Variables
```

**macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc:
export PATH="$HOME/.local/bin:$PATH"

# Then reload:
source ~/.bashrc  # or source ~/.zshrc
```

### Initial Setup

```bash
# Run the interactive setup wizard
sci onboard

# Or set up manually
sci github setup  # Configure GitHub integration
```

### Basic Usage

```bash
# Scan current directory
sci scan

# Analyze GitHub repositories
sci github repos

# Run autonomous security agent
sci github repos
# Select repository → "Autonomous Agent (Full Automation)"
```

## ✨ Key Features

### 🔍 **Comprehensive Security Scanning**
- **Secret Detection**: Finds hardcoded API keys, tokens, passwords
- **Vulnerability Analysis**: CVE scanning with NVD integration
- **Dependency Scanning**: Identifies vulnerable packages and versions
- **CI/CD Security**: Analyzes GitHub Actions workflows for security issues
- **Code Quality**: Detects security anti-patterns and misconfigurations

### 🤖 **AI-Powered Analysis**
- **Intelligent Threat Detection**: AI analyzes context and severity
- **False Positive Reduction**: Smart filtering reduces noise
- **Risk Assessment**: Automated severity scoring and impact analysis
- **Contextual Recommendations**: Tailored fix suggestions

### 🛠️ **Autonomous Remediation**
- **Automatic Issue Creation**: Creates GitHub issues for tracking
- **Pull Request Generation**: Generates PRs with security fixes
- **Code Patching**: Applies fixes directly to repositories
- **Pipeline Fixes**: Corrects CI/CD security misconfigurations
- **No Cloning Required**: Uses GitHub API for remote operations

### 🏢 **Enterprise Features**
- **Organization Scanning**: Scan all repositories in an organization
- **Risk Heatmaps**: Visual security dashboards
- **Compliance Reporting**: Generate security reports
- **Integration Ready**: Works with existing CI/CD pipelines

## 📋 Requirements

- **Python**: 3.11 or higher
- **AI API Key**: Groq (recommended), OpenAI, or Anthropic
- **GitHub PAT**: For repository analysis and autonomous features (optional)
- **NVD API Key**: For enhanced CVE scanning (optional)

## 🔧 Configuration

### AI API Setup

SentinelCI supports multiple AI providers:

1. **Groq (Recommended - Fast & Free)**
   - Get API key: https://console.groq.com/keys
   - Set: `sci onboard` or `export AI_API_KEY=your_key`

2. **OpenAI**
   - Get API key: https://platform.openai.com/api-keys
   - Set: `export AI_API_KEY=your_key`

3. **Anthropic**
   - Get API key: https://console.anthropic.com/
   - Set: `export AI_API_KEY=your_key`

### GitHub Integration

```bash
# Set up GitHub Personal Access Token
sci github setup

# Required scopes:
# - 'repo' (for private repositories)
# - 'public_repo' (for public repositories)
```

### Environment Variables

```bash
# AI Configuration
export AI_API_KEY="your_ai_api_key"
export GROQ_API_KEY="your_groq_key"  # Alternative

# GitHub Configuration  
export GITHUB_PAT="your_github_token"
export GITHUB_TOKEN="your_github_token"  # Alternative

# NVD Configuration (Optional)
export NVD_API_KEY="your_nvd_key"
```

## 📖 Usage Examples

### Local Scanning

```bash
# Basic scan
sci scan

# Scan with specific severity
sci scan --severity high

# Output to JSON
sci scan --output results.json --format json

# Watch mode (continuous scanning)
sci scan --watch
```

### GitHub Repository Analysis

```bash
# List and analyze repositories
sci github repos

# Scan specific organization
sci github scan-org your-org-name

# Check authentication
sci github auth
```

### Autonomous Security Agent

The autonomous agent can automatically:
- Detect security vulnerabilities
- Create fixes and patches
- Generate pull requests
- Open tracking issues
- Apply changes without manual intervention

```bash
sci github repos
# Select repository
# Choose "Autonomous Agent (Full Automation)"
# Review and approve the execution plan
```

### Pipeline Security Analysis

```bash
# Analyze CI/CD pipelines
sci pipeline analyze .github/workflows/

# Auto-fix pipeline issues
sci pipeline fix .github/workflows/ci.yml
```

## 🔒 Security Categories

SentinelCI detects and fixes:

### **Secrets & Credentials**
- API keys, tokens, passwords in code
- Hardcoded credentials in configuration files
- Exposed secrets in environment variables

### **Dependencies & Supply Chain**
- Vulnerable package versions
- Outdated dependencies
- Malicious packages
- License compliance issues

### **CI/CD Pipeline Security**
- Excessive workflow permissions
- Unpinned action versions
- Code injection vulnerabilities
- Missing security checks

### **Code Security**
- SQL injection patterns
- XSS vulnerabilities
- Insecure cryptographic practices
- Authentication bypasses

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scanner       │    │   AI Analyzer    │    │  Autonomous     │
│   Engine        │───▶│   (Groq/OpenAI)  │───▶│  Agent          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Local Files   │    │   Threat Intel   │    │  GitHub API     │
│   Git Repos     │    │   CVE Database   │    │  Issue/PR Gen   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone repository
git clone https://github.com/sentinelci/sentinelci.git
cd sentinelci

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Format code
black sentinelci/
ruff check sentinelci/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://docs.sentinelci.dev
- **Issues**: https://github.com/sentinelci/sentinelci/issues
- **Discussions**: https://github.com/sentinelci/sentinelci/discussions

## 🙏 Acknowledgments

- Built with [Typer](https://typer.tiangolo.com/) and [Rich](https://rich.readthedocs.io/)
- AI powered by [Groq](https://groq.com/), [OpenAI](https://openai.com/), and [Anthropic](https://anthropic.com/)
- Security data from [NVD](https://nvd.nist.gov/) and [GitHub Security Advisories](https://github.com/advisories)

---

**Made with ❤️ by the SentinelCI Team**