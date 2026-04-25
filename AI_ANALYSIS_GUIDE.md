AI Security Analysis & Autonomous Decision Engine

Complete Guide

Overview

SentinelCI now includes advanced AI-powered security analysis and an autonomous decision engine that can automatically determine appropriate responses to security findings.

Features

AI Security Analysis
- Hardcoded secrets exposure detection
- Suspicious outbound calls analysis
- Dependency hash mismatch risks
- Privilege escalation in workflows
- Over-permissioned GitHub Actions tokens
- Untrusted third-party actions
- Supply chain security risks

Autonomous Decision Engine
- Warn only
- Block pipeline
- Require manual approval
- Suggest automated fix
- Open security issue
- Create pull request with remediation

Quick Start

1. Setup

Ensure you have AI API key configured:

sci --config --ai-api-key "your_groq_api_key"

2. Select Repository

sci github repos

This opens an interactive menu where you can select repositories.

3. Choose Action

After selecting a repository, you'll see an action menu:

- Analyze Security Configuration
- Run AI Security Analysis
- Simulate Autonomous Decisions
- Full Analysis + Simulation
- Clone and Scan Code
- Export Repository Info

AI Security Analysis

What It Analyzes

1. Hardcoded Secrets
   - API keys in code
   - Passwords in configuration
   - Tokens in environment variables
   - Credentials in workflow files
   - Exposed secrets in logs

2. Suspicious Outbound Calls
   - Unknown or suspicious domains
   - Data exfiltration attempts
   - Unverified external API calls
   - Insecure HTTP connections
   - Direct IP address calls

3. Dependency Risks
   - Missing dependency hashes
   - Unpinned versions
   - Known vulnerable packages
   - Typosquatting attempts
   - Lack of integrity checks

4. Privilege Escalation
   - Unnecessary sudo usage
   - Running as root
   - Privilege escalation commands
   - Insecure permission changes
   - Unrestricted script execution

5. Token Permissions
   - Overly broad permissions
   - Write when read is sufficient
   - Missing permission restrictions
   - Unnecessary repo-wide access
   - Admin privileges

6. Third-Party Actions
   - Actions from unknown publishers
   - Unpinned action versions
   - Missing commit SHA pinning
   - Suspicious action names
   - Excessive permissions

7. Supply Chain
   - Lack of dependency verification
   - Missing SBOM
   - No provenance attestation
   - Unsigned artifacts
   - Insecure build processes

Output Format

JSON Structure:

{
  "repository": "owner/repo",
  "timestamp": "2024-01-01T00:00:00",
  "risk_score": 75,
  "risk_level": "HIGH",
  "findings": [
    {
      "category": "secrets",
      "severity": "CRITICAL",
      "title": "Hardcoded API Key",
      "description": "...",
      "location": ".github/workflows/deploy.yml:15",
      "evidence": "...",
      "remediation": "...",
      "confidence": 0.95
    }
  ],
  "summary": "...",
  "recommendations": [...],
  "audit_explanation": "..."
}

Terminal Output:

╔═══════════════════════════════════════════════════════════════╗
║                   AI Security Analysis                        ║
╚═══════════════════════════════════════════════════════════════╝

🎯 Risk Assessment
Risk Level: HIGH
Risk Score: 75/100
████████████████████████████████████░░░░░░░░░░░░░░

🔍 Security Findings Summary
┌──────────────┬──────────┬────────────────────┬────────────┐
│ Category     │ Severity │ Title              │ Confidence │
├──────────────┼──────────┼────────────────────┼────────────┤
│ secrets      │ CRITICAL │ Hardcoded API Key  │ 95%        │
│ dependencies │ HIGH     │ Unpinned Version   │ 85%        │
└──────────────┴──────────┴────────────────────┴────────────┘

📋 Detailed Findings
[Detailed panels for each finding]

📊 Executive Summary
[AI-generated summary]

💡 Recommendations
1. Implement GitHub secret scanning
2. Pin dependency versions with hashes
3. Restrict token permissions

📝 Audit Explanation
[Plain English explanation]

Autonomous Decision Engine

How It Works

The engine uses a rule-based system to automatically determine appropriate actions based on:
- Finding category
- Severity level
- Confidence score
- Context

Decision Types

1. Warn Only
   - Low severity issues
   - Informational findings
   - No blocking action

2. Block Pipeline
   - Critical security issues
   - Immediate risk
   - Prevents deployment

3. Require Approval
   - High severity issues
   - Needs human review
   - Pauses pipeline

4. Suggest Fix
   - Automated fix available
   - Shows remediation code
   - No automatic application

5. Open Issue
   - Creates GitHub issue
   - Tracks security finding
   - Assigns labels

6. Create PR
   - Automated fix PR
   - Includes remediation
   - Requires review

Decision Rules

Secrets:
- CRITICAL → Block Pipeline + Create PR
- HIGH → Require Approval + Suggest Fix
- MEDIUM → Warn Only + Open Issue
- LOW → Warn Only

Outbound Calls:
- CRITICAL → Block Pipeline + Open Issue
- HIGH → Require Approval + Suggest Fix
- MEDIUM → Warn Only + Open Issue
- LOW → Warn Only

Dependencies:
- CRITICAL → Block Pipeline + Create PR
- HIGH → Require Approval + Create PR
- MEDIUM → Warn Only + Open Issue
- LOW → Warn Only

Privilege Escalation:
- CRITICAL → Block Pipeline + Create PR
- HIGH → Require Approval + Suggest Fix
- MEDIUM → Warn Only + Open Issue
- LOW → Warn Only

Token Permissions:
- CRITICAL → Block Pipeline + Create PR
- HIGH → Require Approval + Create PR
- MEDIUM → Warn Only + Suggest Fix
- LOW → Warn Only

Third-Party Actions:
- CRITICAL → Block Pipeline + Open Issue
- HIGH → Require Approval + Create PR
- MEDIUM → Warn Only + Suggest Fix
- LOW → Warn Only

Supply Chain:
- CRITICAL → Block Pipeline + Open Issue
- HIGH → Require Approval + Open Issue
- MEDIUM → Warn Only + Open Issue
- LOW → Warn Only

Simulation Output

Terminal Display:

╔═══════════════════════════════════════════════════════════════╗
║            Autonomous Decision Simulation                     ║
╚═══════════════════════════════════════════════════════════════╝

🎬 Overall Decision
🚫 Pipeline Status: BLOCKED

Pipeline BLOCKED due to 2 CRITICAL issue(s).
Immediate remediation required before proceeding.

📊 Decision Statistics
┌─────────────────┬───────┐
│ Metric          │ Count │
├─────────────────┼───────┤
│ Total Decisions │ 5     │
│ Fixes Suggested │ 3     │
│ Issues to Open  │ 2     │
│ PRs to Create   │ 2     │
└─────────────────┴───────┘

🌳 Decision Tree
├─ 🚫 Block Pipeline (2)
│  ├─ Hardcoded API Key
│  └─ Critical Dependency Vulnerability
├─ 📝 Create PR (2)
│  ├─ Hardcoded API Key
│  └─ Unpinned Third-Party Action
└─ ⚠️ Warn Only (1)
   └─ Minor Permission Concern

🔍 Decision Details
[Detailed panels for each decision]

JSON Export:

{
  "repository": "owner/repo",
  "timestamp": "2024-01-01T00:00:00",
  "decisions": [
    {
      "action": "block_pipeline",
      "reason": "Exposed secrets pose immediate security risk",
      "explanation": "...",
      "confidence": 0.95,
      "severity": "CRITICAL",
      "finding_id": "Hardcoded API Key",
      "automated_fix": "...",
      "pr_title": "🔒 Security Fix: Hardcoded API Key",
      "pr_body": "..."
    }
  ],
  "overall_action": "block_pipeline",
  "explanation": "...",
  "blocked": true,
  "requires_approval": false,
  "fixes_suggested": 3,
  "issues_to_open": 2,
  "prs_to_create": 2
}

Usage Examples

Basic AI Analysis

sci github repos
# Select repository
# Choose "Run AI Security Analysis"

Full Analysis with Simulation

sci github repos
# Select repository
# Choose "Full Analysis + Simulation"

This runs both AI analysis and autonomous decision simulation, providing:
- Complete security findings
- Risk assessment
- Automated decisions
- Suggested fixes
- PR/Issue templates

Clone and Scan

sci github repos
# Select repository
# Choose "Clone and Scan Code"

This:
1. Clones the repository
2. Runs code scanning
3. Detects secrets, CVEs, etc.
4. Provides AI analysis
5. Cleans up temporary files

Python API

from sentinelci.ai_analyzer import AISecurityAnalyzer
from sentinelci.autonomous_engine import AutonomousEngine
import asyncio

# Initialize analyzer
analyzer = AISecurityAnalyzer(api_key="your_key")

# Run analysis
result = asyncio.run(
    analyzer.analyze_repository(
        repo_name="owner/repo",
        metadata={...},
        workflows=[...],
        dependencies=[...],
        pipeline_data={...},
    )
)

# Simulate decisions
engine = AutonomousEngine()
simulation = engine.simulate(
    repository="owner/repo",
    findings=[f.to_dict() for f in result.findings],
)

# Export results
engine.export_decisions(simulation, "decisions.json")

Integration with CI/CD

GitHub Actions Example:

name: Security Analysis
on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install SentinelCI
        run: pip install -e .
      
      - name: Run AI Analysis
        env:
          AI_API_KEY: ${{ secrets.AI_API_KEY }}
          GITHUB_PAT: ${{ secrets.GITHUB_TOKEN }}
        run: |
          sci github repos --search "${{ github.repository }}"
          # Automated analysis would go here
      
      - name: Check Results
        run: |
          if [ -f "*_decisions.json" ]; then
            # Parse decisions and fail if blocked
            python -c "import json; d=json.load(open('*_decisions.json')); exit(1 if d['blocked'] else 0)"
          fi

Best Practices

1. Regular Scanning
   - Run analysis on every PR
   - Schedule weekly full scans
   - Monitor for new vulnerabilities

2. Review Decisions
   - Don't blindly trust automation
   - Review suggested fixes
   - Verify automated PRs

3. Tune Sensitivity
   - Adjust confidence thresholds
   - Customize decision rules
   - Balance security vs. velocity

4. Track Metrics
   - Monitor risk scores over time
   - Track remediation time
   - Measure false positive rate

5. Integrate with Workflow
   - Use in pre-commit hooks
   - Add to CI/CD pipeline
   - Automate issue creation

Troubleshooting

AI Analysis Fails

Check API key:
sci --config --ai-api-key "your_key"

Verify connectivity:
curl https://api.groq.com/openai/v1/models

No Findings Detected

This could mean:
- Repository is secure
- Analysis needs more context
- Workflows/dependencies not found

Check that repository has:
- GitHub Actions workflows
- Dependency files
- Active development

Simulation Not Blocking

Review decision rules:
- Check severity levels
- Verify confidence scores
- Ensure findings are CRITICAL/HIGH

False Positives

Improve accuracy by:
- Providing more context
- Using higher confidence thresholds
- Customizing decision rules

Performance

Analysis is slow:
- Reduce number of workflows analyzed
- Use caching for repeated analyses
- Run in parallel for multiple repos

Advanced Configuration

Custom Decision Rules

Modify sentinelci/autonomous_engine.py:

self.rules = {
    "secrets": {
        "CRITICAL": {
            "action": ActionType.BLOCK_PIPELINE,
            "secondary": ActionType.CREATE_PR,
            "reason": "Custom reason",
        },
    },
}

Custom AI Prompts

Modify sentinelci/ai_analyzer.py:

prompt = f"""Custom analysis prompt:
{context}
Look for specific patterns...
"""

Export Formats

JSON (default):
- Machine-readable
- Full detail
- Easy to parse

Terminal:
- Human-readable
- Color-coded
- Interactive

Markdown:
- Documentation
- Reports
- Sharing

Limitations

1. AI Analysis
   - Requires API key
   - Network connectivity needed
   - Rate limits apply

2. Autonomous Decisions
   - Rule-based (not ML)
   - May need tuning
   - Context-dependent

3. Automated Fixes
   - Not always applicable
   - Requires review
   - May need customization

Future Enhancements

- Machine learning for decision rules
- Historical trend analysis
- Custom rule engine
- Integration with more CI/CD platforms
- Automated PR creation
- Issue tracking integration
- Slack/Teams notifications

Support

For issues or questions:
1. Check this documentation
2. Review examples
3. Check API key configuration
4. Verify repository access

See Also

- README_GITHUB.md - GitHub integration
- COMMANDS_REFERENCE.md - All commands
- ARCHITECTURE.md - System design
