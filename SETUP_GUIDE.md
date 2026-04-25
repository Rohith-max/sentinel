# SentinelCI Setup & Migration Guide

## Quick Start

### 1. Install Dependencies

```bash
# Install/update dependencies
pip install -e .

# Or manually install new dependencies
pip install typer==0.9.0 questionary==2.0.1
```

### 2. Run Onboarding

```bash
# Interactive setup wizard
python -m sentinelci.cli_new onboard
```

### 3. Test New Features

```bash
# Check GitHub authentication
python -m sentinelci.cli_new github auth

# List repositories
python -m sentinelci.cli_new github repos

# Scan organization
python -m sentinelci.cli_new github scan-org YOUR_ORG_NAME
```

## Architecture Overview

### New Module Structure

```
sentinelci/
├── core/                    # NEW: Core modules
│   ├── __init__.py
│   ├── auth.py             # GitHub authentication
│   ├── discovery.py        # Repository discovery
│   ├── remediation.py      # PR/Issue generation
│   └── visualization.py    # Incident graphs & heatmaps
├── cli_new.py              # NEW: Modern CLI with Typer
├── cli.py                  # EXISTING: Original CLI (to be migrated)
├── scanner.py              # EXISTING: Core scanning
├── agent.py                # EXISTING: AI analysis
├── ai_analyzer.py          # EXISTING: Advanced AI
├── autonomous_engine.py    # EXISTING: Decision engine
├── github_security.py      # EXISTING: GitHub analysis
├── github_auth.py          # DEPRECATED: Use core/auth.py
├── github_repos.py         # DEPRECATED: Use core/discovery.py
├── config.py               # EXISTING: Configuration
└── fixer.py                # EXISTING: Auto-fix
```

## New Features

### 1. Automated Remediation

Generate PRs and issues automatically:

```python
from sentinelci.core.remediation import RemediationEngine

engine = RemediationEngine()

# Create security issue
issue = engine.create_security_issue(
    "owner/repo",
    "🔒 Security: Exposed Secret Detected",
    "Secret found in config.py line 42",
    labels=["security", "critical"]
)

# Generate PR with fix
pr = engine.generate_secret_removal_pr(
    "owner/repo",
    finding,
    fixed_content
)
```

### 2. Incident Graph Visualization

Visualize security incidents and attack chains:

```python
from sentinelci.core.visualization import IncidentGraph

graph = IncidentGraph()

# Add nodes
graph.add_commit_node("abc123", "Add feature", "user", "2024-01-01")
graph.add_secret_node("secret_1", "config.py:42", "CRITICAL")
graph.add_workflow_node("wf_1", "CI Pipeline", "failed")

# Add relationships
graph.add_edge("commit:abc123", "secret:secret_1", "exposed")
graph.add_edge("secret:secret_1", "workflow:wf_1", "triggered")

# Render
graph.render_graph()
graph.render_attack_chain()

# Export
graph.export_json("incident_graph.json")
```

### 3. Organization-Wide Scanning

Scan all repositories in an organization:

```bash
# Scan entire organization
sci github scan-org acme-corp --output report.json
```

Features:
- Aggregate risk heatmap
- Rank riskiest repositories
- Cross-repo pattern detection
- Policy violation tracking

### 4. Interactive CLI

Modern CLI with rich interactions:

```bash
# Interactive onboarding
sci onboard

# Interactive repository selection
sci github repos --search "api"

# Action menu for each repository:
# 1. Analyze Security Configuration
# 2. Run AI Security Analysis
# 3. Simulate Autonomous Decisions
# 4. Generate Security PR
# 5. View Incident Graph
# 6. Full Analysis + Visualization
```

## Migration Steps

### Step 1: Update Dependencies

```bash
pip install -e .
```

### Step 2: Run Onboarding

```bash
python -m sentinelci.cli_new onboard
```

This will:
- Configure AI API key
- Setup GitHub PAT (optional)
- Set scanning preferences
- Create config file

### Step 3: Test New Commands

```bash
# Test authentication
python -m sentinelci.cli_new github auth

# Test repository discovery
python -m sentinelci.cli_new github repos

# Test organization scanning
python -m sentinelci.cli_new github scan-org YOUR_ORG
```

### Step 4: Migrate Existing Workflows

Replace old commands with new ones:

**Old:**
```bash
sci github auth
sci github repos
```

**New:**
```bash
python -m sentinelci.cli_new github auth
python -m sentinelci.cli_new github repos
```

### Step 5: Update Scripts

If you have scripts using the old CLI, update them:

**Old:**
```python
from sentinelci.github_auth import GitHubAuth
from sentinelci.github_repos import GitHubRepoManager

auth = GitHubAuth()
manager = GitHubRepoManager()
repos = manager.fetch_all_repositories()
```

**New:**
```python
from sentinelci.core.auth import GitHubAuth
from sentinelci.core.discovery import RepositoryDiscovery

auth = GitHubAuth()
discovery = RepositoryDiscovery()
repos = discovery.fetch_user_repositories()
```

## Configuration

### Config File Location

- **User config**: `~/.config/sci/config.toml`
- **Environment variables**: `.env` file in project root

### Config Structure

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

## Usage Examples

### Example 1: Onboard and Scan

```bash
# 1. Onboard
python -m sentinelci.cli_new onboard

# 2. Scan local code
sci scan --path ./myproject

# 3. Scan GitHub repository
python -m sentinelci.cli_new github repos --search "myproject"
# Select repository → Choose "Full Analysis + Visualization"
```

### Example 2: Organization Security Audit

```bash
# Scan entire organization
python -m sentinelci.cli_new github scan-org acme-corp --output acme_audit.json

# Results include:
# - Risk heatmap
# - Ranked repositories
# - Cross-repo patterns
# - Policy violations
```

### Example 3: Generate Security PRs

```bash
# 1. Analyze repository
python -m sentinelci.cli_new github repos --search "api-gateway"

# 2. Select repository

# 3. Choose "Generate Security PR"

# 4. Select finding to fix

# 5. PR is automatically created with:
#    - Branch creation
#    - File updates
#    - PR description
#    - Remediation steps
```

### Example 4: Visualize Incident Graph

```bash
# 1. Analyze repository
python -m sentinelci.cli_new github repos

# 2. Select repository

# 3. Choose "View Incident Graph"

# Output:
# - Visual graph of relationships
# - Attack chain timeline
# - Propagation analysis
# - JSON export
```

## Troubleshooting

### Issue: "No module named 'typer'"

**Solution:**
```bash
pip install typer==0.9.0
```

### Issue: "GitHub PAT not configured"

**Solution:**
```bash
python -m sentinelci.cli_new github setup
```

Or set environment variable:
```bash
export GITHUB_PAT=ghp_your_token_here
```

### Issue: "AI API key not configured"

**Solution:**
```bash
python -m sentinelci.cli_new onboard
```

Or set environment variable:
```bash
export AI_API_KEY=gsk_your_key_here
```

### Issue: "Permission denied" when creating PR

**Solution:**

Ensure your GitHub PAT has these scopes:
- `repo` - Full repository access
- `workflow` - Update GitHub Actions workflows
- `read:org` - Read organization data

Create new PAT: https://github.com/settings/tokens/new

## Testing

### Unit Tests

```bash
# Test core modules
pytest tests/test_auth.py
pytest tests/test_discovery.py
pytest tests/test_remediation.py
pytest tests/test_visualization.py
```

### Integration Tests

```bash
# Test CLI commands
python -m sentinelci.cli_new github auth
python -m sentinelci.cli_new github repos --search "test"
```

### Manual Testing

```bash
# 1. Test onboarding
python -m sentinelci.cli_new onboard

# 2. Test authentication
python -m sentinelci.cli_new github auth

# 3. Test repository discovery
python -m sentinelci.cli_new github repos

# 4. Test organization scanning
python -m sentinelci.cli_new github scan-org YOUR_ORG

# 5. Test visualization
# Select a repository → Choose "View Incident Graph"
```

## Performance

### Optimization Tips

1. **Use filters** to reduce API calls:
   ```bash
   sci github repos --visibility private --language python
   ```

2. **Cache results** for repeated analysis:
   ```bash
   sci github scan-org acme --output cache.json
   # Reuse cache.json for visualization
   ```

3. **Parallel scanning** (coming soon):
   ```bash
   sci github scan-org acme --parallel 5
   ```

## Security

### Best Practices

1. **Never commit secrets**:
   - Use `.env` files (gitignored)
   - Use environment variables
   - Use GitHub Secrets

2. **Rotate PATs regularly**:
   ```bash
   sci github setup  # Update PAT
   ```

3. **Use minimal permissions**:
   - Only grant required scopes
   - Use fine-grained PATs when possible

4. **Review PRs carefully**:
   - Automated PRs should be reviewed
   - Verify fixes before merging

## Support

### Documentation

- [README.md](README.md) - Project overview
- [REFACTORING_SUMMARY.md](REFACTORING_SUMMARY.md) - Architecture details
- [COMMANDS_REFERENCE.md](COMMANDS_REFERENCE.md) - Command reference

### Getting Help

1. Check documentation
2. Run `sci --help` or `python -m sentinelci.cli_new --help`
3. Check GitHub issues
4. Contact support

## Roadmap

### Completed ✅

- Modular architecture
- Automated remediation (PR/Issue generation)
- Incident graph visualization
- Organization-wide scanning
- Interactive CLI with onboarding

### In Progress 🚧

- Integration with existing CLI
- Comprehensive test suite
- Performance optimizations

### Planned 📋

- Parallel scanning
- Custom rule engine
- Slack/Teams notifications
- CI/CD integrations
- Web dashboard
- API server

## Contributing

### Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/sentinelci.git
cd sentinelci

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .
```

### Adding New Features

1. Create module in `sentinelci/core/`
2. Add tests in `tests/`
3. Update CLI in `cli_new.py`
4. Update documentation
5. Submit PR

## License

MIT License - see [LICENSE](LICENSE) file
