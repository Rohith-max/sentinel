# Autofixing Guide - SentinelCI

## Overview
SentinelCI has multiple levels of autofixing capabilities, from simple fixes to fully autonomous agent execution.

## 1. Basic Autofix Command

### Simple Secret & URL Fixes
```bash
# Scan and fix secrets/URLs
python3.11 -m sentinelci fix .

# Dry run (preview changes)
python3.11 -m sentinelci fix . --dry-run

# Fix only high severity issues
python3.11 -m sentinelci fix . --severity high

# Fix without creating backups
python3.11 -m sentinelci fix . --no-backup
```

**What it fixes:**
- Hardcoded secrets (extracts to .env)
- Homograph URLs
- Creates backups (.sci.bak files)

**Limitations:**
- Does NOT fix dependencies
- Does NOT fix workflow issues
- Does NOT create PRs

## 2. Autonomous Agent (Full Automation)

### Setup Required
```bash
# 1. Configure AI API key
python3.11 -m sentinelci config --ai-api-key YOUR_GROQ_OR_ANTHROPIC_KEY

# 2. Configure GitHub PAT
python3.11 -m sentinelci github setup
```

### Run Autonomous Agent
```bash
# Interactive mode - select repositories
python3.11 -m sentinelci github repos

# Then select: "Autonomous Agent (Full Automation)"
```

**What the autonomous agent does:**
1. Scans repository for all vulnerabilities
2. Creates autonomous action plan
3. Automatically fixes vulnerabilities:
   - Extracts secrets to .env files
   - Updates .gitignore
   - Modifies source code to use environment variables
   - Fixes workflow permissions
   - Updates vulnerable dependencies (where possible)
4. Creates new branch
5. Commits changes
6. Pushes to GitHub
7. Opens pull request
8. Creates tracking issues

**No user confirmation needed** - Fully autonomous!

## 3. Manual Workflow

### Step-by-Step Manual Fixing

#### Step 1: Scan
```bash
python3.11 -m sentinelci scan . --no-ai
```

#### Step 2: Review findings
Check the output for:
- CRITICAL: Script injection, hardcoded secrets
- HIGH: Vulnerable dependencies, excessive permissions
- MEDIUM: Unpinned actions

#### Step 3: Fix manually or use autofix
```bash
# For secrets/URLs
python3.11 -m sentinelci fix .

# For dependencies - update manually
# Edit requirements.txt or package.json

# For workflows - edit .github/workflows/*.yml
```

## 4. Available Commands

### Scan Commands
```bash
# Basic scan
python3.11 -m sentinelci scan .

# Scan with AI analysis
python3.11 -m sentinelci scan . --ai

# Scan specific directory
python3.11 -m sentinelci scan test-vulnerable-repo

# Scan git diff only
python3.11 -m sentinelci scan . --diff
```

### Fix Commands
```bash
# Auto-fix
python3.11 -m sentinelci fix .

# Dry run
python3.11 -m sentinelci fix . --dry-run

# Fix git diff only
python3.11 -m sentinelci fix . --diff
```

### GitHub Commands
```bash
# Setup GitHub authentication
python3.11 -m sentinelci github setup

# Check authentication status
python3.11 -m sentinelci github auth

# List and select repositories
python3.11 -m sentinelci github repos

# Verify autonomous agent execution
python3.11 -m sentinelci github verify
```

### Configuration Commands
```bash
# Configure AI API key
python3.11 -m sentinelci config --ai-api-key YOUR_KEY

# Configure GitHub PAT
python3.11 -m sentinelci config --github-pat YOUR_PAT

# Show current configuration
python3.11 -m sentinelci config --show
```

## 5. Autonomous Agent Features

### What Gets Fixed Automatically

#### Secrets
- Extracts hardcoded API keys to .env
- Extracts GitHub tokens to .env
- Updates source code to use `os.getenv()` or `process.env`
- Adds .env to .gitignore

#### Workflows
- Fixes excessive permissions (write-all → minimal)
- Adds security scanning jobs
- Fixes script injection vulnerabilities
- Updates unpinned actions (where safe)

#### Dependencies
- Identifies vulnerable packages
- Suggests updates in PR description
- (Manual update still required for safety)

### Execution Flow
```
1. Scan Repository
   ↓
2. AI Analysis
   ↓
3. Create Action Plan
   ↓
4. Auto-Fix Vulnerabilities
   ↓
5. Create Branch
   ↓
6. Commit Changes
   ↓
7. Push to GitHub
   ↓
8. Open Pull Request
   ↓
9. Create Issues
```

## 6. Example Usage

### Example 1: Quick Fix
```bash
# Scan and fix in one go
python3.11 -m sentinelci scan . && python3.11 -m sentinelci fix .
```

### Example 2: Autonomous Agent
```bash
# Setup (one time)
python3.11 -m sentinelci config --ai-api-key gsk_...
python3.11 -m sentinelci github setup

# Run autonomous agent
python3.11 -m sentinelci github repos
# Select repository
# Choose "Autonomous Agent (Full Automation)"
```

### Example 3: CI/CD Integration
```bash
# In your CI pipeline
python3.11 -m sentinelci scan . --severity high --halt-on-critical
```

## 7. Output Files

### Scan Results
- `findings.json` - Scan results
- `{repo}_analysis.json` - AI analysis results

### Execution Logs
- `{repo}_execution_log.json` - Autonomous agent execution log
- Contains: plan, results, auto-fixes

### Backups
- `*.sci.bak` - Backup files before fixes

## 8. Troubleshooting

### "AI API key not configured"
```bash
python3.11 -m sentinelci config --ai-api-key YOUR_KEY
```

### "Not authenticated" (GitHub)
```bash
python3.11 -m sentinelci github setup
```

### "No fixable issues"
The basic `fix` command only handles secrets and URLs.
Use the autonomous agent for comprehensive fixing.

### "binwalk not found"
This is optional - only needed for firmware scanning.
Can be safely ignored for regular code repositories.

## 9. Best Practices

1. **Always test in dry-run first**
   ```bash
   python3.11 -m sentinelci fix . --dry-run
   ```

2. **Review autonomous agent PRs**
   - Check the changes before merging
   - Verify secrets are properly extracted
   - Test the application still works

3. **Use severity filtering**
   ```bash
   python3.11 -m sentinelci scan . --severity high
   ```

4. **Enable backups**
   - Default behavior creates .sci.bak files
   - Don't use --no-backup unless you're sure

5. **Commit before fixing**
   - Always commit your work before running fixes
   - Makes it easy to revert if needed

## Summary

- **Basic fixes**: `python3.11 -m sentinelci fix .`
- **Autonomous agent**: `python3.11 -m sentinelci github repos` → Select "Autonomous Agent"
- **Scan only**: `python3.11 -m sentinelci scan .`
- **Configuration**: `python3.11 -m sentinelci config --help`
