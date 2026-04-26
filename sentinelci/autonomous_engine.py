"""
Autonomous decision engine for security response
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime


class ActionType(Enum):
    """Types of autonomous actions"""
    WARN_ONLY = "warn_only"
    BLOCK_PIPELINE = "block_pipeline"
    REQUIRE_APPROVAL = "require_approval"
    SUGGEST_FIX = "suggest_fix"
    OPEN_ISSUE = "open_issue"
    CREATE_PR = "create_pr"


@dataclass
class Decision:
    """Represents an autonomous decision"""
    action: ActionType
    reason: str
    explanation: str
    confidence: float
    severity: str
    finding_id: str
    automated_fix: Optional[str] = None
    pr_title: Optional[str] = None
    pr_body: Optional[str] = None
    issue_title: Optional[str] = None
    issue_body: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["action"] = self.action.value
        return result


@dataclass
class SimulationResult:
    """Result of autonomous simulation"""
    repository: str
    timestamp: str
    decisions: List[Decision]
    overall_action: ActionType
    explanation: str
    blocked: bool
    requires_approval: bool
    fixes_suggested: int
    issues_to_open: int
    prs_to_create: int

    def to_dict(self) -> Dict[str, Any]:
        result = asdict(self)
        result["decisions"] = [d.to_dict() for d in self.decisions]
        result["overall_action"] = self.overall_action.value
        return result


class RuleEngine:
    """Rule-based decision engine"""

    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> Dict[str, Any]:
        """Initialize decision rules"""
        return {
            "secrets": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Exposed secrets pose immediate security risk",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.SUGGEST_FIX,
                    "reason": "Potential secret exposure requires review",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Possible secret pattern detected",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Low confidence secret detection",
                },
            },
            "outbound_calls": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Suspicious outbound call to untrusted domain",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.SUGGEST_FIX,
                    "reason": "Unverified external API call detected",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "External call should be reviewed",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "External call to known domain",
                },
            },
            "dependencies": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Critical dependency vulnerability or hash mismatch",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "High severity dependency issue",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Dependency should be updated or pinned",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Minor dependency concern",
                },
            },
            "privilege_escalation": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Dangerous privilege escalation detected",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.SUGGEST_FIX,
                    "reason": "Unnecessary elevated privileges",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Privilege usage should be reviewed",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Minor privilege concern",
                },
            },
            "token_permissions": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Severely over-permissioned token",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Token permissions exceed requirements",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.SUGGEST_FIX,
                    "reason": "Token permissions should be restricted",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Minor permission concern",
                },
            },
            "third_party_actions": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Untrusted or malicious third-party action",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.CREATE_PR,
                    "reason": "Unpinned or unverified third-party action",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.SUGGEST_FIX,
                    "reason": "Third-party action should be pinned",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Minor third-party action concern",
                },
            },
            "supply_chain": {
                "CRITICAL": {
                    "action": ActionType.BLOCK_PIPELINE,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Critical supply chain security gap",
                },
                "HIGH": {
                    "action": ActionType.REQUIRE_APPROVAL,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Supply chain verification missing",
                },
                "MEDIUM": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": ActionType.OPEN_ISSUE,
                    "reason": "Supply chain security should be improved",
                },
                "LOW": {
                    "action": ActionType.WARN_ONLY,
                    "secondary": None,
                    "reason": "Minor supply chain concern",
                },
            },
        }

    def decide(self, finding: Dict[str, Any]) -> Decision:
        """
        Make autonomous decision for a finding

        Args:
            finding: Security finding dict

        Returns:
            Decision object
        """
        category = finding.get("category", "unknown")
        severity = finding.get("severity", "LOW")
        confidence = finding.get("confidence", 0.5)

        # Get rule for this category and severity
        rule = self.rules.get(category, {}).get(severity, {
            "action": ActionType.WARN_ONLY,
            "secondary": None,
            "reason": "Unknown issue type",
        })

        primary_action = rule["action"]
        secondary_action = rule.get("secondary")
        reason = rule["reason"]

        # Generate explanation
        explanation = self._generate_explanation(
            finding, primary_action, secondary_action, reason, confidence
        )

        # Generate automated fix if applicable
        automated_fix = None
        pr_title = None
        pr_body = None
        issue_title = None
        issue_body = None

        if primary_action == ActionType.CREATE_PR or secondary_action == ActionType.CREATE_PR:
            automated_fix = self._generate_fix(finding)
            pr_title, pr_body = self._generate_pr_content(finding, automated_fix)

        if primary_action == ActionType.SUGGEST_FIX or secondary_action == ActionType.SUGGEST_FIX:
            automated_fix = self._generate_fix(finding)

        if primary_action == ActionType.OPEN_ISSUE or secondary_action == ActionType.OPEN_ISSUE:
            issue_title, issue_body = self._generate_issue_content(finding)

        return Decision(
            action=primary_action,
            reason=reason,
            explanation=explanation,
            confidence=confidence,
            severity=severity,
            finding_id=finding.get("title", "unknown"),
            automated_fix=automated_fix,
            pr_title=pr_title,
            pr_body=pr_body,
            issue_title=issue_title,
            issue_body=issue_body,
        )

    def _generate_explanation(
        self,
        finding: Dict[str, Any],
        primary_action: ActionType,
        secondary_action: Optional[ActionType],
        reason: str,
        confidence: float,
    ) -> str:
        """Generate human-readable explanation"""
        parts = []

        # Primary action explanation
        if primary_action == ActionType.BLOCK_PIPELINE:
            parts.append(f"🚫 BLOCKING pipeline execution because: {reason}")
            parts.append(f"This is a {finding.get('severity')} severity issue that poses immediate risk.")
        elif primary_action == ActionType.REQUIRE_APPROVAL:
            parts.append(f"⏸️  REQUIRING manual approval because: {reason}")
            parts.append(f"This {finding.get('severity')} severity issue needs human review before proceeding.")
        elif primary_action == ActionType.WARN_ONLY:
            parts.append(f"WARNING: {reason}")
            parts.append(f"This {finding.get('severity')} severity issue should be reviewed but won't block execution.")

        # Secondary action explanation
        if secondary_action == ActionType.CREATE_PR:
            parts.append("📝 Will create a pull request with automated fix.")
        elif secondary_action == ActionType.SUGGEST_FIX:
            parts.append("SUGGESTION: Automated fix suggestion available.")
        elif secondary_action == ActionType.OPEN_ISSUE:
            parts.append("TRACKING: Will open a security issue for tracking.")

        # Confidence note
        if confidence < 0.7:
            parts.append(f"⚡ Confidence: {confidence:.0%} - May require verification.")

        return " ".join(parts)

    def _generate_fix(self, finding: Dict[str, Any]) -> str:
        """Generate automated fix suggestion"""
        category = finding.get("category", "")
        remediation = finding.get("remediation", "")

        if remediation:
            return remediation

        # Category-specific fix templates
        if category == "secrets":
            return """# Remove hardcoded secret and use GitHub Secrets instead

1. Remove the hardcoded value from the file
2. Add the secret to GitHub repository secrets
3. Reference it using: ${{ secrets.SECRET_NAME }}

Example:
- api_key: "hardcoded_key"  # REMOVE THIS
+ api_key: ${{ secrets.API_KEY }}  # USE THIS"""

        elif category == "dependencies":
            return """# Pin dependency versions with integrity hashes

1. Specify exact versions instead of ranges
2. Add integrity hashes for verification
3. Use lock files (package-lock.json, yarn.lock, etc.)

Example:
- "package": "^1.0.0"  # AVOID THIS
+ "package": "1.2.3"   # USE THIS"""

        elif category == "token_permissions":
            return """# Restrict token permissions to minimum required

Add permissions block to workflow:

permissions:
  contents: read  # Only what's needed
  pull-requests: write  # If PR comments needed

Avoid using:
permissions: write-all  # TOO BROAD"""

        elif category == "third_party_actions":
            return """# Pin third-party actions to commit SHA

- uses: actions/checkout@v3  # AVOID TAG
+ uses: actions/checkout@8e5e7e5ab8b370d6c329ec480221332ada57f0ab  # USE SHA"""

        return "See remediation guidance in finding details."

    def _generate_pr_content(self, finding: Dict[str, Any], fix: str) -> tuple[str, str]:
        """Generate PR title and body"""
        title = f"Security Fix: {finding.get('title', 'Security Issue')}"

        body = f"""## Security Issue

**Category:** {finding.get('category', 'Unknown')}
**Severity:** {finding.get('severity', 'MEDIUM')}
**Location:** {finding.get('location', 'Unknown')}

## Description

{finding.get('description', 'Security issue detected by automated analysis.')}

## Evidence

{finding.get('evidence', 'See analysis report for details.')}

## Proposed Fix

{fix}

## Remediation

{finding.get('remediation', 'Apply the suggested fix above.')}

---

*This PR was automatically generated by SentinelCI security analysis.*
*Please review carefully before merging.*
"""

        return title, body

    def _generate_issue_content(self, finding: Dict[str, Any]) -> tuple[str, str]:
        """Generate issue title and body"""
        title = f"Security: {finding.get('title', 'Security Issue')}"

        body = f"""## Security Finding

**Category:** {finding.get('category', 'Unknown')}
**Severity:** {finding.get('severity', 'MEDIUM')}
**Confidence:** {finding.get('confidence', 0.7):.0%}
**Location:** {finding.get('location', 'Unknown')}

## Description

{finding.get('description', 'Security issue detected by automated analysis.')}

## Evidence

```
{finding.get('evidence', 'See analysis report for details.')}
```

## Remediation Steps

{finding.get('remediation', 'Review the security finding and apply appropriate fixes.')}

## Impact

This {finding.get('severity', 'MEDIUM')} severity issue should be addressed to maintain security posture.

---

*This issue was automatically created by SentinelCI security analysis.*
*Labels: security, automated*
"""

        return title, body


class AutonomousEngine:
    """Autonomous decision and action engine"""

    def __init__(self):
        self.rule_engine = RuleEngine()

    def simulate(
        self,
        repository: str,
        findings: List[Dict[str, Any]],
    ) -> SimulationResult:
        """
        Simulate autonomous decisions for findings

        Args:
            repository: Repository name
            findings: List of security findings

        Returns:
            SimulationResult with all decisions
        """
        decisions = []

        for finding in findings:
            decision = self.rule_engine.decide(finding)
            decisions.append(decision)

        # Determine overall action
        overall_action = self._determine_overall_action(decisions)

        # Calculate statistics
        blocked = any(d.action == ActionType.BLOCK_PIPELINE for d in decisions)
        requires_approval = any(d.action == ActionType.REQUIRE_APPROVAL for d in decisions)
        fixes_suggested = sum(1 for d in decisions if d.automated_fix is not None)
        issues_to_open = sum(1 for d in decisions if d.issue_title is not None)
        prs_to_create = sum(1 for d in decisions if d.pr_title is not None)

        # Generate overall explanation
        explanation = self._generate_overall_explanation(
            decisions, overall_action, blocked, requires_approval
        )

        return SimulationResult(
            repository=repository,
            timestamp=datetime.utcnow().isoformat(),
            decisions=decisions,
            overall_action=overall_action,
            explanation=explanation,
            blocked=blocked,
            requires_approval=requires_approval,
            fixes_suggested=fixes_suggested,
            issues_to_open=issues_to_open,
            prs_to_create=prs_to_create,
        )

    def _determine_overall_action(self, decisions: List[Decision]) -> ActionType:
        """Determine overall action from all decisions"""
        if any(d.action == ActionType.BLOCK_PIPELINE for d in decisions):
            return ActionType.BLOCK_PIPELINE
        elif any(d.action == ActionType.REQUIRE_APPROVAL for d in decisions):
            return ActionType.REQUIRE_APPROVAL
        elif any(d.action == ActionType.CREATE_PR for d in decisions):
            return ActionType.CREATE_PR
        elif any(d.action == ActionType.OPEN_ISSUE for d in decisions):
            return ActionType.OPEN_ISSUE
        elif any(d.action == ActionType.SUGGEST_FIX for d in decisions):
            return ActionType.SUGGEST_FIX
        else:
            return ActionType.WARN_ONLY

    def _generate_overall_explanation(
        self,
        decisions: List[Decision],
        overall_action: ActionType,
        blocked: bool,
        requires_approval: bool,
    ) -> str:
        """Generate overall explanation"""
        parts = []

        if blocked:
            critical_count = sum(1 for d in decisions if d.severity == "CRITICAL")
            parts.append(f"🚫 Pipeline BLOCKED due to {critical_count} CRITICAL issue(s).")
            parts.append("Immediate remediation required before proceeding.")
        elif requires_approval:
            high_count = sum(1 for d in decisions if d.severity == "HIGH")
            parts.append(f"⏸️  Manual approval REQUIRED due to {high_count} HIGH severity issue(s).")
            parts.append("Security review needed before proceeding.")
        else:
            parts.append("SUCCESS: No blocking issues detected.")
            parts.append("Warnings and suggestions provided for review.")

        return " ".join(parts)

    def export_decisions(self, result: SimulationResult, output_file: str) -> None:
        """Export decisions to JSON file"""
        with open(output_file, "w") as f:
            json.dump(result.to_dict(), f, indent=2)
