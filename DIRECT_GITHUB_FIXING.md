# Direct GitHub Fixing - No Local Cloning Required

## Overview
SentinelCI v1.0.6 introduces **Direct GitHub Fixing** - the ability to scan and fix vulnerabilities in GitHub repositories without cloning them locally. All changes are made directly via the GitHub API.

## Features

### What It Does
1. **Scans** repository directly from GitHub
2. **Detects** vulnerabilities (secrets, workflows, dependencies)
3. **Fixes** issues via GitHub API
4. **Creates** new branch automatically
5. **Commits** changes with descriptive messages
6. **Opens** pull request with fix summary
7. **Extracts** secrets to .env.example

### What It Fixes
- ✅ Hardcoded secrets (API keys, tokens, passwords)
- ✅ Excessive workflow permissions (write-all → minimal)
- ✅ Unpinned GitHub Actions
- ✅ Script injection vulnerabilities (basic)
- ⚠️ Dependency updates (detection only, manual update required)

## Usage

### Command Syntax
```bash
sci github direct-fix OWNER/REPO [OPTIONS]
```

### Options
- `--branch TEXT` - Base branch to create PR against (default: main)
- `--dry-run` - Preview changes without committing
- `--severity TEXT` - Minimum severity to fix (default: medium)

### Examples

#### Basic Usage
```bash
# Fix vulnerabilities in a repository
sci github direct-fix rohith911/my-repo
```

#### Dry Run (Preview Only)
```bash
# See what would be fixed without making changes
sci github direct-fix rohith911/my-repo --dry-run
```

#### Custom Branch
```bash
# Create PR against develop branch
sci github direct-fix rohith911/my-repo --branch develop
```

#### High Severity Only
```bash
# Only fix critical and high severity issues
sci github direct-fix rohith911/my-repo --severity high
```

## How It Works

### Step-by-Step Process

1. **Authentication Check**
   - Verifies GitHub PAT is configured
   - Checks token has required permissions

2. **Repository Clone (Temporary)**
   - Shallow clone for scanning only
   - Deleted after scan completes
   - No local changes made

3. **Vulnerability Scan**
   - Runs all scanners (secrets, workflows, dependencies)
   - Filters by severity level
   - Groups findings by file

4. **Fix Generation**
   - Analyzes each finding
   - Generates appropriate fix
   - Validates fix syntax

5. **Branch Creation**
   - Creates new branch: `security/auto-fix-N-issues`
   - Based on specified base branch

6. **Direct Commits**
   - Fetches file content via API
   - Applies fixes
   - Commits each file individually
   - Descriptive commit messages

7. **Pull Request**
   - Creates PR with summary
   - Lists all fixed files
   - Includes environment variables
   - Requests review

## Fix Types

### 1. Secret Extraction

**Before:**
```python
API_KEY = "sk_live_your_actual_key_here"
```

**After:**
```python
import os
API_KEY = os.getenv("API_KEY")
```

**Also Creates:**
```bash
# .env.example
API_KEY=your_api_key_here
```

### 2. Workflow Permissions

**Before:**
```yaml
permissions: write-all
```

**After:**
```yaml
permissions:
  contents: read
  pull-requests: write
```

### 3. Unpinned Actions

**Before:**
```yaml
- uses: actions/checkout@main
```

**After:**
```yaml
- uses: actions/checkout@v4
```

### 4. Script Injection (Basic)

**Before:**
```yaml
run: echo "Title: ${{ github.event.issue.title }}"
```

**After:**
```yaml
env:
  ISSUE_TITLE: ${{ github.event.issue.title }}
run: echo "Title: $ISSUE_TITLE"
```

## Requirements

### GitHub Token Permissions
Your GitHub PAT needs these scopes:
- `repo` - Full repository access
- `workflow` - Update GitHub Actions workflows

### Setup
```bash
# Configure GitHub PAT
sci github setup

# Verify authentication
sci github auth
```

## Output Example

```bash
$ sci github direct-fix rohith911/my-app

🔍 Scanning repository: rohith911/my-app

📥 Cloning repository...

🔍 Scanning for vulnerabilities...

⚠️  Found 5 issue(s)
  CRITICAL: 1
  HIGH: 3
  MEDIUM: 1

🔧 Apply fixes directly to GitHub? [Y/n]: y

🔧 Applying fixes directly to GitHub...

┌─────────────────────────────────────────┐
│     Direct GitHub Fixer                 │
│ Repository: rohith911/my-app            │
│ Findings: 5                             │
└─────────────────────────────────────────┘

Files to fix: 3

Creating branch: security/auto-fix-5-issues

Processing: config.py
✓ Fixed config.py

Processing: .github/workflows/ci.yml
✓ Fixed .github/workflows/ci.yml

Processing: app.py
✓ Fixed app.py

Creating .env.example with 3 variables

Creating pull request...
✓ Pull request created: https://github.com/rohith911/my-app/pull/42

✅ Successfully fixed 3 file(s)
   Branch: security/auto-fix-5-issues
   PR: https://github.com/rohith911/my-app/pull/42

⚠️  3 environment variable(s) extracted
   Add these to GitHub Secrets or your environment
```

## Comparison: Direct Fix vs Local Fix

| Feature | Direct Fix | Local Fix |
|---------|-----------|-----------|
| **Cloning** | Temporary (scan only) | Full clone required |
| **Disk Space** | Minimal | Full repo size |
| **Speed** | Fast (API calls) | Slower (git operations) |
| **Network** | API only | Git + API |
| **Local Changes** | None | Creates local branch |
| **Cleanup** | Automatic | Manual |
| **Use Case** | Remote repos | Local development |

## Best Practices

### 1. Always Dry Run First
```bash
sci github direct-fix owner/repo --dry-run
```
Review what will be changed before committing.

### 2. Review Pull Requests
- Check all changes before merging
- Verify secrets are properly extracted
- Test application still works
- Update GitHub Secrets with extracted values

### 3. Use Severity Filtering
```bash
# Fix only critical issues first
sci github direct-fix owner/repo --severity critical

# Then fix high severity
sci github direct-fix owner/repo --severity high
```

### 4. Backup Important Repos
- Test on non-critical repos first
- Have backups before running on production
- Can always close PR if issues arise

### 5. Environment Variables
After fixing, add extracted secrets to:
- GitHub Secrets (Settings → Secrets and variables → Actions)
- Environment configuration files
- Secret management systems (Vault, AWS Secrets Manager, etc.)

## Troubleshooting

### "GitHub PAT not configured"
```bash
sci github setup
```

### "Failed to clone repository"
- Check repository exists and is accessible
- Verify PAT has `repo` scope
- Check network connectivity

### "Failed to create branch"
- Branch may already exist
- Delete old branch or use different name
- Check PAT has write permissions

### "Failed to create PR"
- Check PAT has `repo` scope
- Verify base branch exists
- Ensure no conflicting PRs

### "No vulnerabilities found"
- Repository may be secure
- Try lower severity: `--severity low`
- Check if files are in ignored directories

## Limitations

### Cannot Fix
- Complex code refactoring
- Dependency version updates (detects only)
- Infrastructure configuration
- Database schema changes
- Third-party service configurations

### Requires Manual Review
- All workflow permission changes
- Action version updates
- Environment variable configuration
- Application testing after fixes

## Security Considerations

### Token Security
- Never commit GitHub PAT to code
- Use secure storage (keyring)
- Rotate tokens regularly
- Use fine-grained PATs when possible

### Fix Validation
- All fixes are reviewed via PR
- No direct commits to main branch
- Changes are transparent
- Can be reverted if needed

### Extracted Secrets
- Secrets are moved to .env.example
- Original secrets visible in PR
- Rotate secrets after extraction
- Update GitHub Secrets immediately

## Advanced Usage

### Batch Fixing Multiple Repos
```bash
# Fix all repos in organization
for repo in $(gh repo list myorg --json name -q '.[].name'); do
  sci github direct-fix myorg/$repo --dry-run
done
```

### CI/CD Integration
```yaml
# .github/workflows/security-fix.yml
name: Auto Security Fix

on:
  schedule:
    - cron: '0 0 * * 0'  # Weekly
  workflow_dispatch:

jobs:
  fix:
    runs-on: ubuntu-latest
    steps:
      - name: Install SentinelCI
        run: pip install sentinelci
      
      - name: Run Direct Fix
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          sci github setup --token $GITHUB_TOKEN
          sci github direct-fix ${{ github.repository }}
```

## Version History

### v1.0.6 (Current)
- ✨ Added direct GitHub fixing capability
- ✨ API-based file modifications
- ✨ Automatic PR creation
- ✨ Secret extraction to .env.example

### v1.0.5
- ✨ Comprehensive scanning (secrets, dependencies, workflows)
- ✨ Workflow security scanner
- ✨ Dependency vulnerability scanner

## Summary

Direct GitHub Fixing provides:
- 🚀 Fast remote repository fixes
- 🔒 Secure API-based modifications
- 📝 Automatic PR creation
- 🎯 No local cloning required
- ✅ Transparent change review

Perfect for:
- Remote repository management
- Automated security fixes
- CI/CD integration
- Organization-wide security improvements