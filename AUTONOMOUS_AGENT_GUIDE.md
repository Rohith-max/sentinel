# 🤖 Autonomous Security Agent Guide

## Overview

The Autonomous Security Agent is a fully automated AI agent with complete freedom to analyze, plan, and execute security fixes without manual intervention. It operates transparently with user confirmation for critical actions.

## Capabilities

### 1. Complete Automation Freedom
- **Analyze** vulnerabilities autonomously
- **Plan** remediation actions
- **Execute** fixes automatically
- **Create** commits and PRs
- **Track** issues
- **Transparent** decision-making

### 2. Intelligent Decision Making
- Severity-based action planning
- Risk assessment
- Impact estimation
- Atomic multi-file commits
- No cloning required (Git Data API)

### 3. User Control
- Transparent plan display
- Confirmation for critical actions
- Detailed execution log
- Rollback capability

## How It Works

### Phase 1: Security Analysis
```
🤖 Autonomous Agent Analyzing...

✓ Scanning repository
✓ Detecting vulnerabilities
✓ Assessing severity
✓ Categorizing issues
```

### Phase 2: Planning Autonomous Actions
```
╔═══════════════════════════════════════════════════════╗
║              🤖 Autonomous Agent Plan                 ║
╠═══════════════════════════════════════════════════════╣
║ Repository: owner/repo                                ║
║ Risk: CRITICAL: 3 critical issue(s) require action    ║
║ Impact: 5 file(s) will be modified, 8 total actions  ║
╚═══════════════════════════════════════════════════════╝

Planned Actions:
┌────┬─────────────────┬──────────────────┬─────────────────┬──────────┐
│ #  │ Action          │ Target           │ Description     │ Severity │
├────┼─────────────────┼──────────────────┼─────────────────┼──────────┤
│ 1  │ 📝 Edit File    │ config.py        │ Remove secret   │ CRITICAL │
│ 2  │ 📝 Edit File    │ .github/ci.yml   │ Restrict perms  │ HIGH     │
│ 3  │ 📝 Edit File    │ package.json     │ Pin dependency  │ HIGH     │
│ 4  │ 📋 Open Issue   │ api/auth.py      │ Track vuln      │ MEDIUM   │
│ 5  │ ⚠️  Log Warning │ utils.py         │ Monitor issue   │ LOW      │
└────┴─────────────────┴──────────────────┴─────────────────┴──────────┘

Detailed Changes:

1. config.py
   → Remove hardcoded secret
   → Add comment: Use environment variable

2. .github/workflows/ci.yml
   → Add permissions block:
      contents: read
      pull-requests: write

3. package.json
   → Pin axios to specific version
```

### Phase 3: User Confirmation
```
⚠️  The agent will autonomously:
  • Edit files to fix vulnerabilities
  • Create commits with changes
  • Push to new branch
  • Open pull request
  • Create tracking issues

Allow autonomous execution? (y/N):
```

### Phase 4: Autonomous Execution
```
🚀 Executing Autonomous Plan...

Step 1/5: Remove hardcoded secret
  ✓ Planned edit for config.py

Step 2/5: Restrict workflow permissions
  ✓ Planned edit for .github/workflows/ci.yml

Step 3/5: Pin dependency version
  ✓ Planned edit for package.json

Step 4/5: Track vulnerability
  ✓ Planned issue creation

Step 5/5: Monitor issue
  ⚠️  Logged warning

📝 Applying file changes...
  ✓ Prepared config.py
  ✓ Prepared .github/workflows/ci.yml
  ✓ Prepared package.json

Creating branch: security/autonomous-fix-3-files
✓ Committed: a1b2c3d

Creating pull request...
✓ PR #42: https://github.com/owner/repo/pull/42

📋 Creating issues...
  ✓ Issue #43
```

### Phase 5: Results
```
╔═══════════════════════════════════════════════════════╗
║              🤖 Execution Results                     ║
╠═══════════════════════════════════════════════════════╣
║ Status: SUCCESS                                       ║
║ Actions Executed: 5                                   ║
║ Actions Failed: 0                                     ║
╚═══════════════════════════════════════════════════════╝

✅ Pull Request Created
  PR: #42
  URL: https://github.com/owner/repo/pull/42
  Branch: security/autonomous-fix-3-files

💾 Execution log saved to repo_execution_log.json
```

## Usage

### Basic Usage
```bash
# Select repository
python -m sentinelci.cli_new github repos --search "myproject"

# Choose: 🤖 Autonomous Agent (Full Automation)

# Review plan and confirm
```

### Advanced Usage
```bash
# Scan organization and run autonomous agent on all repos
python -m sentinelci.cli_new github scan-org my-org

# For each high-risk repo, run autonomous agent
```

## Decision Logic

### Critical Severity (Auto-fix)
- **Secrets**: Remove hardcoded values
- **Permissions**: Restrict to minimum required
- **Dependencies**: Pin to specific versions

### High Severity (Auto-fix)
- **Vulnerabilities**: Update to patched versions
- **Misconfigurations**: Apply secure defaults
- **Unsafe patterns**: Replace with safe alternatives

### Medium Severity (Track)
- **Create issues** for manual review
- **Suggest fixes** in issue description
- **Monitor** for escalation

### Low Severity (Log)
- **Log warnings** for awareness
- **No immediate action** required
- **Track trends** over time

## Transparency Features

### 1. Detailed Plan Display
- Shows every action before execution
- Explains why each action is needed
- Estimates impact and risk

### 2. Step-by-Step Execution
- Real-time progress updates
- Success/failure indicators
- Transparent error messages

### 3. Complete Audit Trail
- Execution log saved to JSON
- All actions recorded
- Timestamps and results

### 4. User Control
- Confirmation required for critical actions
- Can cancel at any time
- Review plan before execution

## Safety Features

### 1. No Auto-Approve for Critical
- Critical actions always require confirmation
- User must explicitly approve
- Can review plan first

### 2. Atomic Commits
- All file changes in single commit
- Easy to revert if needed
- No partial states

### 3. Branch-Based Changes
- Never commits to main/master
- Creates new branch for changes
- PR for review before merge

### 4. Rollback Capability
- Can close PR to reject changes
- Can revert commit if needed
- Original files preserved

## Example Scenarios

### Scenario 1: Exposed Secrets
```
Finding: Hardcoded API key in config.py

Agent Plan:
1. Remove hardcoded value
2. Add comment to use environment variable
3. Create issue to update deployment

Execution:
✓ Edited config.py
✓ Committed changes
✓ Created PR #42
✓ Created issue #43

Result: Secret removed, deployment tracked
```

### Scenario 2: Over-Permissioned Workflow
```
Finding: GitHub Actions workflow has write-all permissions

Agent Plan:
1. Add explicit permissions block
2. Restrict to read-only by default
3. Grant only necessary write permissions

Execution:
✓ Edited .github/workflows/ci.yml
✓ Committed changes
✓ Created PR #44

Result: Workflow permissions restricted
```

### Scenario 3: Vulnerable Dependency
```
Finding: axios@0.21.0 has known vulnerability

Agent Plan:
1. Pin axios to patched version 0.21.4
2. Update package-lock.json
3. Create issue to test changes

Execution:
✓ Edited package.json
✓ Edited package-lock.json
✓ Committed changes
✓ Created PR #45
✓ Created issue #46

Result: Dependency updated, testing tracked
```

## Best Practices

### 1. Review Plans Carefully
- Read the detailed changes
- Understand the impact
- Verify the risk assessment

### 2. Test Changes
- Review PR before merging
- Run tests in CI/CD
- Verify fixes work as expected

### 3. Monitor Execution
- Watch real-time progress
- Check for errors
- Review execution log

### 4. Provide Feedback
- Report issues
- Suggest improvements
- Share success stories

## Limitations

### Current Limitations
1. **Language Support**: Best for JavaScript, Python, YAML
2. **Complex Fixes**: May need manual intervention
3. **Context Understanding**: Limited to file-level changes
4. **Testing**: Cannot run tests automatically

### Future Enhancements
1. **Multi-language support**: More languages
2. **Test execution**: Run tests before PR
3. **Rollback automation**: Auto-revert on test failure
4. **Learning**: Improve from feedback

## Troubleshooting

### Issue: Agent fails to create PR
**Solution**: Check GitHub PAT permissions (needs `repo` scope)

### Issue: Changes not applied correctly
**Solution**: Review execution log, may need manual fix

### Issue: Confirmation not working
**Solution**: Ensure terminal is interactive

### Issue: Rate limit exceeded
**Solution**: Wait or use authenticated requests

## FAQ

**Q: Is it safe to let the agent run autonomously?**
A: Yes, with confirmation. Agent requires approval for critical actions and creates PRs for review.

**Q: Can I rollback changes?**
A: Yes, close the PR or revert the commit.

**Q: Does it clone the repository?**
A: No, uses Git Data API for remote operations.

**Q: What if the agent makes a mistake?**
A: Review PR before merging, can reject changes.

**Q: Can I customize the agent's behavior?**
A: Yes, modify decision logic in `autonomous_agent.py`.

## Support

- **Documentation**: See this guide
- **Issues**: Report on GitHub
- **Discussions**: Ask questions
- **Email**: support@sentinelci.dev

---

**Made with ❤️ by the SentinelCI Team**
