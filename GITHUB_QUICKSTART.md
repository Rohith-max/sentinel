GitHub Integration Quick Start

Setup (One-time)

1. Install dependencies:

pip install -e .

2. Setup GitHub PAT:

sci github setup

Enter your GitHub Personal Access Token when prompted.

To create a PAT: https://github.com/settings/tokens/new
Required scopes: repo, read:org, read:user, workflow

Basic Commands

Check Authentication

sci github auth

Shows your GitHub username, profile, and organizations.

List Repositories

sci github repos

Interactive selection of repositories with metadata.

Options:
  --multi              Select multiple repositories
  --search TEXT        Filter by name/description
  --visibility public|private
  --language TEXT      Filter by programming language

Examples:

sci github repos --search "api"
sci github repos --visibility private --language python
sci github repos --multi

Analyze Repository Security

sci github analyze owner/repo

Displays comprehensive security dashboard with:
- Webhooks
- GitHub Actions workflows
- CI/CD files
- Branch protection
- Secret scanning alerts
- Dependabot alerts
- Security advisories
- Failed workflows
- Permissions
- Risk score

Save to file:

sci github analyze owner/repo --output report.json

Complete Workflow Example

# 1. Setup authentication
sci github setup

# 2. Verify authentication
sci github auth

# 3. List and filter repositories
sci github repos --search "myproject" --visibility private

# 4. Analyze selected repository
sci github analyze myorg/myproject

# 5. Save analysis
sci github analyze myorg/myproject --output security-analysis.json

Environment Variables

Set in .env file:

GITHUB_PAT=your_github_pat_here

Or use:
- GH_PAT
- GITHUB_TOKEN

Configuration

Stored in ~/.config/sci/config.toml:

[git]
github_pat = "ghp_..."

Security Dashboard Components

Risk Score (0-100)
- LOW: 0-14
- MEDIUM: 15-29
- HIGH: 30-49
- CRITICAL: 50+

Webhooks
- All configured webhooks
- URLs and events
- Active status

GitHub Actions
- Workflow files
- State and paths
- Last update times

CI/CD Detection
- GitHub Actions (.github/workflows)
- Jenkins (Jenkinsfile)
- GitLab CI (.gitlab-ci.yml)
- CircleCI (.circleci/config.yml)
- Travis (.travis.yml)
- Azure Pipelines (azure-pipelines.yml)
- Bitbucket (bitbucket-pipelines.yml)

Branch Protection
- Default branch rules
- Required status checks
- Required PR reviews
- Admin enforcement
- Signature requirements

Secret Scanning
- Open alerts
- Secret types
- Creation dates

Dependabot
- Vulnerability alerts
- Package names
- Severity levels
- Summaries

Security Advisories
- Published advisories
- GHSA IDs
- Severity and state

Failed Workflows
- Recent failures
- Workflow names
- Timestamps

Permissions
- Visibility (public/private)
- Feature flags
- Archive status

Troubleshooting

PAT not working:
- Verify scopes: repo, read:org, read:user, workflow
- Check token hasn't expired
- Ensure network connectivity

Secret scanning unavailable:
- Requires GitHub Advanced Security
- Only on paid plans for private repos

Dependabot not showing:
- Enable in repository settings
- Verify PAT has repo scope

Rate limiting:
- 5000 requests/hour for authenticated users
- Add delays for bulk operations

Python API Usage

from sentinelci.github_auth import GitHubAuth
from sentinelci.github_repos import GitHubRepoManager
from sentinelci.github_security import GitHubSecurityAnalyzer

# Authentication
auth = GitHubAuth()
status = auth.check_auth_status()

# List repositories
manager = GitHubRepoManager()
repos = manager.fetch_all_repositories()
filtered = manager.filter_repositories(repos, search="api")

# Security analysis
analyzer = GitHubSecurityAnalyzer()
analysis = analyzer.analyze_repository("owner/repo")
risk = analyzer.calculate_risk_score(analysis)

Integration with Code Scanning

Combine GitHub security analysis with local code scanning:

# Analyze GitHub configuration
sci github analyze owner/repo

# Clone and scan code
git clone https://github.com/owner/repo
sci --scan --path ./repo

# Watch for changes
sci --watch --path ./repo

# Auto-fix issues
sci --fix --path ./repo

Demo Script

Run the interactive demo:

python examples/github_integration_demo.py

This demonstrates:
1. Authentication check
2. Repository listing
3. Security analysis

Testing

Run tests:

pytest tests/test_github_integration.py -v

Next Steps

1. Setup authentication: sci github setup
2. Explore repositories: sci github repos
3. Analyze security: sci github analyze REPO
4. Integrate with CI/CD pipelines
5. Automate security checks

For detailed documentation, see README_GITHUB.md
