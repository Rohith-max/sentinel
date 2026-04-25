Get Started with SCI GitHub Integration

Quick Setup (5 minutes)

Step 1: Install Dependencies

.venv/Scripts/python -m pip install questionary

Step 2: Configure API Keys

Create or update your .env file:

AI_API_KEY=your_groq_api_key_here
NVD_API_KEY=your_nvd_api_key_here
GITHUB_PAT=your_github_pat_here

Get API Keys:
- Groq API: https://console.groq.com/keys
- NVD API: https://nvd.nist.gov/developers/request-an-api-key
- GitHub PAT: https://github.com/settings/tokens/new
  Required scopes: repo, read:org, read:user, workflow

Step 3: Setup GitHub Authentication

.venv/Scripts/python -m sentinelci.cli github setup

Or use the config command:

.venv/Scripts/python -m sentinelci.cli --config --github-pat "your_pat_here" --non-interactive

Step 4: Verify Authentication

.venv/Scripts/python -m sentinelci.cli github auth

You should see your GitHub username and organizations.

Basic Usage

List Your Repositories

.venv/Scripts/python -m sentinelci.cli github repos

This opens an interactive menu to select repositories.

Filter Repositories

.venv/Scripts/python -m sentinelci.cli github repos --search "api" --visibility private

Analyze Repository Security

.venv/Scripts/python -m sentinelci.cli github analyze owner/repo

Replace owner/repo with your actual repository (e.g., microsoft/vscode)

Save Analysis to File

.venv/Scripts/python -m sentinelci.cli github analyze owner/repo --output report.json

Complete Workflow Example

# 1. Setup (one-time)
.venv/Scripts/python -m sentinelci.cli github setup

# 2. Check authentication
.venv/Scripts/python -m sentinelci.cli github auth

# 3. List repositories
.venv/Scripts/python -m sentinelci.cli github repos

# 4. Analyze a repository
.venv/Scripts/python -m sentinelci.cli github analyze myorg/myrepo

# 5. Save analysis
.venv/Scripts/python -m sentinelci.cli github analyze myorg/myrepo --output security-report.json

Run the Demo

python examples/github_integration_demo.py

This interactive demo shows:
1. Authentication status
2. Repository listing
3. Security analysis

What You Get

Security Analysis Dashboard includes:

🔗 Webhooks
- All configured webhooks
- URLs and events
- Active status

⚙️ GitHub Actions Workflows
- Workflow files
- State and paths
- Last update times

📋 CI/CD Configuration Files
- GitHub Actions
- Jenkins
- GitLab CI
- CircleCI
- Travis CI
- Azure Pipelines
- Bitbucket Pipelines

🛡️ Branch Protection
- Protection rules on default branch
- Required status checks
- Required PR reviews
- Admin enforcement
- Signature requirements

🔐 Secret Scanning Alerts
- Open alerts
- Secret types
- Creation dates

🤖 Dependabot Alerts
- Vulnerability alerts
- Package names
- Severity levels (Critical/High/Medium/Low)
- Summaries

📢 Security Advisories
- Published advisories
- GHSA IDs
- Severity and state

❌ Failed Workflow Runs
- Recent failures
- Workflow names
- Timestamps

🔒 Repository Permissions
- Visibility (public/private)
- Feature flags
- Archive status

🎯 Risk Assessment
- Risk score (0-100)
- Risk level (LOW/MEDIUM/HIGH/CRITICAL)
- Risk factors identified

Common Commands

Authentication:
.venv/Scripts/python -m sentinelci.cli github auth
.venv/Scripts/python -m sentinelci.cli github setup

Repositories:
.venv/Scripts/python -m sentinelci.cli github repos
.venv/Scripts/python -m sentinelci.cli github repos --multi
.venv/Scripts/python -m sentinelci.cli github repos --search "api"
.venv/Scripts/python -m sentinelci.cli github repos --visibility private
.venv/Scripts/python -m sentinelci.cli github repos --language python

Analysis:
.venv/Scripts/python -m sentinelci.cli github analyze owner/repo
.venv/Scripts/python -m sentinelci.cli github analyze owner/repo --output report.json

Code Scanning:
.venv/Scripts/python -m sentinelci.cli --scan
.venv/Scripts/python -m sentinelci.cli --scan --diff --severity high
.venv/Scripts/python -m sentinelci.cli --watch --interval 2
.venv/Scripts/python -m sentinelci.cli --fix --dry-run

Troubleshooting

PAT Not Working

Check scopes:
- Go to https://github.com/settings/tokens
- Verify your token has: repo, read:org, read:user, workflow
- Regenerate if needed

Check expiration:
- Tokens can expire
- Create a new token if expired

Verify in config:
.venv/Scripts/python -m sentinelci.cli github auth

Secret Scanning Not Available

This feature requires GitHub Advanced Security:
- Available on public repos (free)
- Requires paid plan for private repos
- Check repository settings

Dependabot Not Showing

Enable Dependabot:
- Go to repository Settings > Security
- Enable Dependabot alerts
- Enable Dependabot security updates

Rate Limiting

GitHub API limits:
- 5000 requests/hour (authenticated)
- 60 requests/hour (unauthenticated)

If you hit limits:
- Wait for the limit to reset
- Use authenticated requests (PAT)
- Add delays between bulk operations

Network Errors

Check connectivity:
- Verify internet connection
- Check firewall settings
- Try again after a moment

Python API Usage

from sentinelci.github_auth import GitHubAuth
from sentinelci.github_repos import GitHubRepoManager
from sentinelci.github_security import GitHubSecurityAnalyzer

# Check authentication
auth = GitHubAuth()
status = auth.check_auth_status()
print(f"Authenticated: {status['authenticated']}")

# List repositories
manager = GitHubRepoManager()
repos = manager.fetch_all_repositories()
print(f"Found {len(repos)} repositories")

# Filter repositories
filtered = manager.filter_repositories(repos, search="api", visibility="private")
print(f"Filtered to {len(filtered)} repositories")

# Analyze security
analyzer = GitHubSecurityAnalyzer()
analysis = analyzer.analyze_repository("owner/repo")
risk = analyzer.calculate_risk_score(analysis)
print(f"Risk Level: {risk['level']}, Score: {risk['score']}")

Next Steps

1. Setup authentication
2. Explore your repositories
3. Analyze security configurations
4. Review risk assessments
5. Address identified issues
6. Integrate with CI/CD

Documentation

- README.md - Main documentation
- README_GITHUB.md - Detailed GitHub integration guide
- GITHUB_QUICKSTART.md - Quick reference
- COMMANDS_REFERENCE.md - All commands
- ARCHITECTURE.md - System architecture
- IMPLEMENTATION_SUMMARY.md - Implementation details
- FEATURE_CHECKLIST.md - Feature list

Support

For issues or questions:
1. Check documentation
2. Review troubleshooting section
3. Check GitHub API status
4. Verify API keys and permissions

Tips

1. Use --multi for selecting multiple repositories
2. Use --search to quickly find repositories
3. Save analysis to JSON for later review
4. Combine with code scanning for comprehensive security
5. Run regularly to track security posture
6. Address CRITICAL and HIGH risk items first

Example Session

$ .venv/Scripts/python -m sentinelci.cli github setup
🔑 GitHub Personal Access Token Setup
Enter GitHub PAT: ****
🔍 Validating PAT...
✅ PAT validated and stored for user: yourusername

$ .venv/Scripts/python -m sentinelci.cli github auth
✅ Authenticated as: yourusername
   Name: Your Name
   Email: you@example.com
   Profile: https://github.com/yourusername

📋 Organizations (3):
   • org1
   • org2
   • org3

$ .venv/Scripts/python -m sentinelci.cli github repos --search "api"
🔍 Fetching repositories...
Found 5 repositories

[Interactive selection menu appears]

$ .venv/Scripts/python -m sentinelci.cli github analyze myorg/myapi
🔍 Analyzing repository: myorg/myapi

[Security dashboard displays with risk assessment and findings]

Ready to Start!

You now have everything you need to:
✅ Authenticate with GitHub
✅ List and select repositories
✅ Analyze security configurations
✅ Assess security risks
✅ Export analysis results

Run your first analysis:
.venv/Scripts/python -m sentinelci.cli github analyze owner/repo
