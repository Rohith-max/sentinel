GitHub Integration Module

Complete GitHub integration for SCI with authentication, repository management, and security analysis.

Features

1. GitHub Authentication
   - Secure PAT storage in config
   - Automatic validation against GitHub API
   - Graceful handling of expired/invalid tokens
   - Environment variable support

2. Repository Management
   - Fetch all accessible repositories (personal + organizations)
   - Interactive selection with questionary
   - Multi-select support
   - Filter by name, visibility, language
   - Display metadata: visibility, branch, last commit, open PRs

3. Security Analysis Dashboard
   - Webhooks configuration
   - GitHub Actions workflows
   - CI/CD pipeline detection (GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure, Bitbucket)
   - Branch protection rules
   - Secret scanning alerts
   - Dependabot vulnerability alerts
   - Security advisories
   - Failed workflow runs
   - Repository permissions model
   - Risk score calculation

Installation

Install dependencies:

pip install questionary

Or update your environment:

pip install -e .

Usage

1. Setup GitHub PAT

sci github setup

This will prompt you to enter your GitHub Personal Access Token.

To create a PAT:
- Go to https://github.com/settings/tokens/new
- Select scopes: repo, read:org, read:user, workflow
- Generate and copy the token

2. Check Authentication Status

sci github auth

Shows:
- Authenticated username
- User profile information
- Organizations

3. List and Select Repositories

Single selection:

sci github repos

Multi-selection:

sci github repos --multi

With filters:

sci github repos --search "myproject" --visibility private --language python

4. Analyze Repository Security

sci github analyze owner/repo

With JSON output:

sci github analyze owner/repo --output analysis.json

Security Analysis Components

Webhooks
- Lists all configured webhooks
- Shows URL, events, and active status

GitHub Actions Workflows
- All workflows in .github/workflows
- State and last update time

CI/CD Detection
- Checks for common CI/CD files
- GitHub Actions, Jenkins, GitLab CI, CircleCI, Travis, Azure Pipelines, Bitbucket

Branch Protection
- Protection rules on default branch
- Required status checks
- Required PR reviews
- Admin enforcement
- Signature requirements

Secret Scanning
- Open secret scanning alerts
- Secret types detected
- Creation dates

Dependabot Alerts
- Open vulnerability alerts
- Package names
- Severity levels (Critical, High, Medium, Low)
- Summaries

Security Advisories
- Published security advisories
- GHSA IDs
- Severity and state

Failed Workflows
- Recent failed workflow runs
- Helps identify CI/CD issues

Repository Permissions
- Visibility (public/private)
- Feature flags (issues, wiki, forking)
- Archive status

Risk Score Calculation

The analyzer calculates a risk score (0-100) based on:

- No branch protection: +20 points
- Vulnerability alerts disabled: +15 points
- Critical Dependabot alerts: +10 points each
- High severity Dependabot alerts: +5 points each
- Exposed secrets: +15 points each
- Failed workflows: +2 points each (max 10)
- Public repo with forking: +5 points

Risk Levels:
- LOW: 0-14
- MEDIUM: 15-29
- HIGH: 30-49
- CRITICAL: 50+

Environment Variables

Set in .env or .env.local:

GITHUB_PAT=your_github_pat_here

Or use any of these alternatives:
- GH_PAT
- GITHUB_TOKEN

Configuration File

Stored in ~/.config/sci/config.toml:

[git]
github_pat = "ghp_..."

API Endpoints Used

- GET /user - User information
- GET /user/orgs - User organizations
- GET /user/repos - User repositories
- GET /repos/{owner}/{repo} - Repository details
- GET /repos/{owner}/{repo}/hooks - Webhooks
- GET /repos/{owner}/{repo}/actions/workflows - Workflows
- GET /repos/{owner}/{repo}/actions/runs - Workflow runs
- GET /repos/{owner}/{repo}/branches/{branch}/protection - Branch protection
- GET /repos/{owner}/{repo}/secret-scanning/alerts - Secret scanning
- GET /repos/{owner}/{repo}/dependabot/alerts - Dependabot alerts
- GET /repos/{owner}/{repo}/security-advisories - Security advisories
- GET /repos/{owner}/{repo}/vulnerability-alerts - Vulnerability alert status
- GET /repos/{owner}/{repo}/pulls - Pull requests

Required PAT Scopes

- repo: Full repository access
- read:org: Read organization data
- read:user: Read user profile
- workflow: Access to GitHub Actions workflows

Error Handling

The module gracefully handles:
- Missing or invalid PAT
- Expired tokens
- Network errors
- API rate limits
- Missing permissions
- Repository not found
- Feature not available (e.g., secret scanning on free tier)

Examples

Complete workflow:

# Setup authentication
sci github setup

# Check status
sci github auth

# List repositories
sci github repos

# Analyze a repository
sci github analyze myorg/myrepo

# Save analysis to file
sci github analyze myorg/myrepo --output security-report.json

# Filter and select repositories
sci github repos --search "api" --visibility private --multi

Integration with Existing Scans

The GitHub module is standalone but can be integrated with existing SCI scans:

# Scan local code
sci --scan --path .

# Analyze GitHub security
sci github analyze owner/repo

# Combined workflow
sci github repos  # Select repo
# Clone it locally
sci --scan --path ./cloned-repo  # Scan code
sci github analyze owner/repo  # Analyze GitHub config

Architecture

sentinelci/
├── github_auth.py          # Authentication and PAT management
├── github_repos.py         # Repository fetching and selection
├── github_security.py      # Security analysis engine
└── output/
    └── github_dashboard.py # Terminal dashboard rendering

Module Dependencies

- requests: GitHub API calls
- questionary: Interactive selection
- rich: Terminal dashboard rendering
- click: CLI commands

Troubleshooting

PAT validation fails:
- Ensure PAT has required scopes
- Check token hasn't expired
- Verify network connectivity

Secret scanning not available:
- Feature requires GitHub Advanced Security
- Only available on paid plans for private repos

Dependabot alerts not showing:
- Ensure Dependabot is enabled in repo settings
- Check PAT has repo scope

Rate limiting:
- GitHub API has rate limits (5000/hour for authenticated)
- Module includes basic caching for NVD lookups
- Consider adding delays between bulk operations
