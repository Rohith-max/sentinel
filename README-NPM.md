# SentinelCI

**AI-Powered Security Scanning and Autonomous Remediation Platform**

[![npm version](https://badge.fury.io/js/sentinelci.svg)](https://badge.fury.io/js/sentinelci)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This is the **NPM wrapper** for SentinelCI, which automatically manages the Python-based security scanning platform. Perfect for Node.js projects and JavaScript developers who want powerful security scanning without dealing with Python directly.

## 🚀 Quick Start

### Installation

```bash
# Install globally
npm install -g sentinelci

# Or use with npx (no installation needed)
npx sentinelci onboard
```

### Requirements

- **Node.js**: 16.0.0 or higher
- **Python**: 3.11 or higher (auto-detected and managed)

### First Run

```bash
# Interactive setup wizard (shows banner!)
npx sentinelci onboard

# Or if installed globally
sentinelci onboard
```

## ✨ Features

### 🔍 **Comprehensive Security Scanning**
- **Secret Detection**: Finds hardcoded API keys, tokens, passwords
- **Vulnerability Analysis**: CVE scanning with NVD integration
- **Dependency Scanning**: Identifies vulnerable packages and versions
- **CI/CD Security**: Analyzes GitHub Actions workflows for security issues

### 🤖 **AI-Powered Analysis**
- **Intelligent Threat Detection**: AI analyzes context and severity
- **False Positive Reduction**: Smart filtering reduces noise
- **Risk Assessment**: Automated severity scoring and impact analysis

### 🛠️ **Autonomous Remediation**
- **Automatic Issue Creation**: Creates GitHub issues for tracking
- **Pull Request Generation**: Generates PRs with security fixes
- **Code Patching**: Applies fixes directly to repositories
- **No Cloning Required**: Uses GitHub API for remote operations

## 📖 Usage

### Command Line

```bash
# Setup (first time)
npx sentinelci onboard

# Scan current directory
npx sentinelci scan

# Scan with options
npx sentinelci scan --severity high --format json --output results.json

# GitHub repository analysis
npx sentinelci github repos

# Show version and banner
npx sentinelci version

# Get help
npx sentinelci --help
```

### Programmatic API

```javascript
const SentinelCI = require('sentinelci');

async function scanProject() {
  const sci = new SentinelCI();
  
  // Initialize (checks Python, installs if needed)
  await sci.init();
  
  // Scan current directory
  await sci.scan({
    path: '.',
    severity: 'medium',
    format: 'json',
    output: 'results.json'
  });
}

// Convenience functions
const { scan, onboard, version } = require('sentinelci/lib');

await scan({ severity: 'high' });
await onboard();
await version();
```

### Package.json Integration

Add to your `package.json` scripts:

```json
{
  "scripts": {
    "security:scan": "sentinelci scan",
    "security:setup": "sentinelci onboard",
    "security:github": "sentinelci github repos"
  }
}
```

Then run:

```bash
npm run security:scan
npm run security:setup
npm run security:github
```

## 🔧 Configuration

### Environment Variables

```bash
# AI Configuration
export AI_API_KEY="your_ai_api_key"
export GROQ_API_KEY="your_groq_key"

# GitHub Configuration  
export GITHUB_PAT="your_github_token"
export GITHUB_TOKEN="your_github_token"

# NVD Configuration (Optional)
export NVD_API_KEY="your_nvd_key"
```

### Config File

The NPM wrapper uses the same configuration as the Python package:

- **Location**: `~/.config/sci/config.toml`
- **Setup**: Run `npx sentinelci onboard` for interactive configuration

## 🏗️ How It Works

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   NPM Wrapper   │    │   Python Core    │    │  AI Analysis    │
│   (Node.js)     │───▶│   (SentinelCI)   │───▶│  (Groq/OpenAI)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                        │                       │
         ▼                        ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Auto-Install  │    │   Security Scan  │    │  GitHub API     │
│   Python Deps   │    │   Local Files    │    │  Issue/PR Gen   │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

1. **NPM Install**: Installs Node.js wrapper
2. **Auto-Detection**: Finds Python 3.11+ automatically
3. **Auto-Install**: Installs Python `sentinelci` package via pip
4. **Seamless Usage**: All commands work transparently

## 🎯 Use Cases

### For JavaScript/Node.js Projects

```bash
# Add to CI/CD pipeline
npx sentinelci scan --format json --output security-report.json

# Pre-commit hook
npx sentinelci scan --diff --severity high
```

### For GitHub Actions

```yaml
name: Security Scan
on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Security Scan
        run: |
          npx sentinelci scan --format json --output security.json
        env:
          AI_API_KEY: ${{ secrets.AI_API_KEY }}
          GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
```

### For Development Teams

```bash
# Team onboarding
npm install -g sentinelci
sentinelci onboard

# Daily security checks
sentinelci github repos  # Analyze all team repositories
```

## 🔒 Security Categories

- **Secrets & Credentials**: API keys, tokens, passwords
- **Dependencies**: Vulnerable packages, outdated versions
- **CI/CD Pipelines**: Workflow permissions, action security
- **Code Security**: Injection patterns, crypto issues

## 🚨 Troubleshooting

### Python Not Found

```bash
# Install Python 3.11+
# Windows: https://python.org/downloads/
# macOS: brew install python@3.11
# Ubuntu: sudo apt install python3.11

# Verify installation
python3 --version
```

### Permission Issues

```bash
# If pip install fails, try:
python3 -m pip install --user sentinelci

# Or use virtual environment:
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
pip install sentinelci
```

### NPM Issues

```bash
# Clear npm cache
npm cache clean --force

# Reinstall
npm uninstall -g sentinelci
npm install -g sentinelci
```

## 📦 What's Included

- **CLI Commands**: Full `sci` command suite
- **Programmatic API**: Node.js integration
- **Auto-Management**: Python dependency handling
- **Cross-Platform**: Windows, macOS, Linux support

## 🤝 Contributing

This NPM package is a wrapper around the main Python project:

- **Main Project**: https://github.com/sentinelci/sentinelci
- **NPM Issues**: Report NPM-specific issues here
- **Python Issues**: Report core functionality issues in main repo

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: https://docs.sentinelci.dev
- **Issues**: https://github.com/sentinelci/sentinelci/issues
- **NPM Package**: https://www.npmjs.com/package/sentinelci

---

**Perfect for JavaScript developers who want enterprise-grade security scanning! 🚀**