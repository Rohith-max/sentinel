SCI Architecture Overview

System Architecture

┌─────────────────────────────────────────────────────────────────┐
│                         SCI CLI (cli.py)                        │
│  Entry point for all commands and user interactions             │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├─────────────────┬──────────────────┬────────────────┐
             │                 │                  │                │
             ▼                 ▼                  ▼                ▼
    ┌────────────────┐ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
    │ Code Scanning  │ │   GitHub     │ │    Config    │ │   Reports    │
    │    Module      │ │ Integration  │ │  Management  │ │   & Output   │
    └────────────────┘ └──────────────┘ └──────────────┘ └──────────────┘

Module Details

1. Code Scanning Module

┌─────────────────────────────────────────────────────────────────┐
│                      scanner.py                                 │
│  Orchestrates all scanning operations                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────────────┐
             │              │              │                      │
             ▼              ▼              ▼                      ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Secret    │  │  Homograph   │  │  Firmware    │  │     AI       │
    │  Scanner   │  │  Detection   │  │  CVE Scan    │  │   Analysis   │
    │            │  │              │  │              │  │              │
    │ TruffleHog │  │ URL Forensics│  │  binwalk +   │  │    Groq      │
    │  + Regex   │  │   Unicode    │  │   NVD API    │  │   LLaMA 3.3  │
    └────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

Files:
- sentinelci/scanner.py - Main orchestration
- sentinelci/tools/secret_scanner.py - Secret detection
- sentinelci/tools/url_forensics.py - Homograph detection
- sentinelci/tools/firmware_cve.py - CVE scanning
- sentinelci/agent.py - AI analysis

2. GitHub Integration Module

┌─────────────────────────────────────────────────────────────────┐
│                   GitHub Integration                            │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────────────┐
             │              │              │                      │
             ▼              ▼              ▼                      ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Auth     │  │  Repository  │  │   Security   │  │  Dashboard   │
    │ Management │  │  Management  │  │   Analysis   │  │   Rendering  │
    │            │  │              │  │              │  │              │
    │ PAT Store  │  │  Fetch List  │  │  10+ Checks  │  │  Rich UI     │
    │ Validation │  │  Filter      │  │  Risk Score  │  │  Tables      │
    │ User Info  │  │  Select      │  │  Findings    │  │  Panels      │
    └────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

Files:
- sentinelci/github_auth.py - Authentication
- sentinelci/github_repos.py - Repository operations
- sentinelci/github_security.py - Security analysis
- sentinelci/output/github_dashboard.py - UI rendering

3. Configuration Management

┌─────────────────────────────────────────────────────────────────┐
│                      config.py                                  │
│  Centralized configuration management                           │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────────────┐
             │              │              │                      │
             ▼              ▼              ▼                      ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   TOML     │  │ Environment  │  │    .env      │  │   Wizard     │
    │   Config   │  │  Variables   │  │    Files     │  │  Interactive │
    │            │  │              │  │              │  │              │
    │ ~/.config/ │  │  AI_API_KEY  │  │  .env        │  │  Setup Flow  │
    │ sci/       │  │  GITHUB_PAT  │  │  .env.local  │  │              │
    │ config.toml│  │  NVD_API_KEY │  │              │  │              │
    └────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

Files:
- sentinelci/config.py - Configuration logic
- ~/.config/sci/config.toml - User config
- .env, .env.local - Environment variables

4. Output & Reporting

┌─────────────────────────────────────────────────────────────────┐
│                   Output Module                                 │
└────────────┬────────────────────────────────────────────────────┘
             │
             ├──────────────┬──────────────┬──────────────────────┐
             │              │              │                      │
             ▼              ▼              ▼                      ▼
    ┌────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │  Terminal  │  │     JSON     │  │   Markdown   │  │   GitHub     │
    │   Output   │  │    Export    │  │    Report    │  │  Dashboard   │
    │            │  │              │  │              │  │              │
    │   Rich     │  │  Structured  │  │  Human       │  │  Security    │
    │   Tables   │  │  Machine     │  │  Readable    │  │  Analysis    │
    │   Colors   │  │  Readable    │  │  Docs        │  │  Risk Score  │
    └────────────┘  └──────────────┘  └──────────────┘  └──────────────┘

Files:
- sentinelci/output/terminal.py - Terminal rendering
- sentinelci/output/report.py - JSON/Markdown reports
- sentinelci/output/github_dashboard.py - GitHub dashboard

Data Flow

Code Scanning Flow:

User Input
    │
    ▼
CLI Command (sci --scan)
    │
    ▼
Scanner Orchestrator
    │
    ├─────────────┬─────────────┬─────────────┐
    │             │             │             │
    ▼             ▼             ▼             ▼
Secret Scan   Homograph    Firmware CVE   Git Diff
    │             │             │             │
    └─────────────┴─────────────┴─────────────┘
                  │
                  ▼
          Findings Collection
                  │
                  ▼
          Severity Filter
                  │
                  ▼
          AI Analysis (optional)
                  │
                  ▼
          Output Rendering
                  │
                  ▼
          Terminal/JSON/Markdown

GitHub Integration Flow:

User Input
    │
    ▼
CLI Command (sci github analyze)
    │
    ▼
GitHub Auth Check
    │
    ├─── PAT Valid? ───┐
    │                  │
    ▼                  ▼
  Continue          Prompt Setup
    │                  │
    └──────────────────┘
    │
    ▼
GitHub API Calls
    │
    ├──────────┬──────────┬──────────┬──────────┐
    │          │          │          │          │
    ▼          ▼          ▼          ▼          ▼
Webhooks  Workflows  Branch    Dependabot  Secrets
                     Protection
    │          │          │          │          │
    └──────────┴──────────┴──────────┴──────────┘
                  │
                  ▼
          Analysis Collection
                  │
                  ▼
          Risk Score Calculation
                  │
                  ▼
          Dashboard Rendering
                  │
                  ▼
          Terminal Display / JSON Export

Component Dependencies

External Dependencies:
- click - CLI framework
- rich - Terminal rendering
- requests - HTTP client
- groq - AI analysis
- questionary - Interactive selection
- platformdirs - Config paths
- tomli-w - TOML writing

Optional Tools:
- trufflehog - Secret scanning
- binwalk - Firmware analysis

API Integrations:
- GitHub API (api.github.com)
- NVD API (services.nvd.nist.gov)
- Groq API (AI analysis)

Security Model

Authentication:
┌─────────────────────────────────────────────────────────────────┐
│                    Credential Storage                           │
├─────────────────────────────────────────────────────────────────┤
│ 1. Environment Variables (highest priority)                     │
│    - AI_API_KEY, GROQ_API_KEY                                   │
│    - GITHUB_PAT, GH_PAT, GITHUB_TOKEN                           │
│    - NVD_API_KEY, NIST_NVD_API_KEY                              │
│                                                                  │
│ 2. .env Files (project-level)                                   │
│    - .env                                                        │
│    - .env.local                                                  │
│                                                                  │
│ 3. Config File (user-level)                                     │
│    - ~/.config/sci/config.toml                                  │
│                                                                  │
│ Priority: Environment > .env > Config File                      │
└─────────────────────────────────────────────────────────────────┘

Token Validation:
┌─────────────────────────────────────────────────────────────────┐
│                    GitHub PAT Validation                        │
├─────────────────────────────────────────────────────────────────┤
│ 1. Check if PAT exists                                          │
│ 2. Validate against GitHub API (GET /user)                      │
│ 3. Check required scopes                                        │
│ 4. Handle expired/invalid tokens                                │
│ 5. Prompt for new PAT if needed                                 │
└─────────────────────────────────────────────────────────────────┘

Risk Scoring Algorithm

┌─────────────────────────────────────────────────────────────────┐
│                    Risk Score Calculation                       │
├─────────────────────────────────────────────────────────────────┤
│ Base Score: 0                                                   │
│                                                                  │
│ + 20 points: No branch protection                               │
│ + 15 points: Vulnerability alerts disabled                      │
│ + 15 points per: Exposed secret                                 │
│ + 10 points per: Critical Dependabot alert                      │
│ +  5 points per: High severity Dependabot alert                 │
│ +  2 points per: Failed workflow (max 10)                       │
│ +  5 points: Public repo with forking enabled                   │
│                                                                  │
│ Risk Levels:                                                    │
│   0-14:  LOW                                                    │
│  15-29:  MEDIUM                                                 │
│  30-49:  HIGH                                                   │
│  50+:    CRITICAL                                               │
└─────────────────────────────────────────────────────────────────┘

Extension Points

Adding New Scanners:
1. Create scanner in sentinelci/tools/
2. Implement scan function returning findings
3. Add to scanner.py orchestration
4. Update CLI options

Adding New GitHub Checks:
1. Add method to GitHubSecurityAnalyzer
2. Call GitHub API endpoint
3. Update analyze_repository method
4. Add dashboard rendering
5. Update risk score calculation

Adding New Output Formats:
1. Create renderer in sentinelci/output/
2. Implement format function
3. Add to CLI format choices
4. Update report generation

File Structure

sentinelci/
├── __init__.py
├── cli.py                      # CLI entry point
├── config.py                   # Configuration management
├── scanner.py                  # Scan orchestration
├── agent.py                    # AI analysis
├── fixer.py                    # Auto-fix logic
├── hooks.py                    # Git hooks
├── github_auth.py              # GitHub authentication
├── github_repos.py             # Repository management
├── github_security.py          # Security analysis
├── tools/
│   ├── __init__.py
│   ├── secret_scanner.py       # Secret detection
│   ├── url_forensics.py        # Homograph detection
│   └── firmware_cve.py         # CVE scanning
└── output/
    ├── __init__.py
    ├── terminal.py             # Terminal output
    ├── report.py               # JSON/Markdown reports
    └── github_dashboard.py     # GitHub dashboard

Configuration Files:
- ~/.config/sci/config.toml     # User configuration
- .env                          # Project environment
- .env.local                    # Local overrides
- pyproject.toml                # Package metadata

Documentation:
- README.md                     # Main documentation
- README_GITHUB.md              # GitHub integration
- GITHUB_QUICKSTART.md          # Quick start
- COMMANDS_REFERENCE.md         # Command reference
- ARCHITECTURE.md               # This file
- IMPLEMENTATION_SUMMARY.md     # Implementation details

Testing Strategy

Unit Tests:
- Authentication validation
- Repository filtering
- Risk score calculation
- Security check logic

Integration Tests:
- GitHub API interactions
- End-to-end workflows
- CLI command execution

Demo Scripts:
- examples/github_integration_demo.py

Performance Considerations

Caching:
- NVD API responses (1 hour TTL)
- GitHub API responses (session-level)

Rate Limiting:
- GitHub API: 5000 requests/hour (authenticated)
- NVD API: 50 requests/30s (with key), 5 requests/30s (without)

Optimization:
- Parallel scanning of multiple files
- Batch API requests where possible
- Efficient filtering before API calls

Deployment

Installation:
pip install -e .

Configuration:
sci --config
sci github setup

Usage:
sci --scan
sci github analyze owner/repo

CI/CD Integration:
sci --scan --halt-on-critical --format json --output findings.json
