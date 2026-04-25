"""
AI-powered security analysis agent
"""

import asyncio
import json
from groq import Groq


# System prompt for security analysis
SYSTEM_PROMPT = """You are SCI, an expert security analyst. Your role is to analyze security threats detected in code and provide clear, actionable remediation advice.

You have access to tools that allow you to:
1. Analyze threats and assess their risk
2. Suggest remediation steps

When given a list of security findings, you should:
1. Analyze each threat with context
2. Provide risk assessment based on type and location
3. Suggest practical remediation steps
4. Prioritize critical findings
5. Provide code examples when possible

Be concise but thorough. Focus on actionable advice that developers can immediately implement."""


def _handle_suggest_remediation(threat_type: str, component: str, details: str) -> str:
    """Tool handler for remediation suggestions"""
    remediation_steps = {
        "secret": f"""
**Remediation Steps for {component}:**

1. Immediate Actions:
   - Revoke/rotate the exposed secret
   - Change passwords and API keys
   - Check logs for unauthorized access

2. Code Cleanup:
   - Remove the secret from code history (use git-filter-branch or BFG Repo-Cleaner)
   - Update your .gitignore to prevent future leaks
   - Use environment variables for sensitive values

3. Example Fix:
   # Before (WRONG):
   api_key = "sk-abc123def456"
   
   # After (CORRECT):
   import os
   api_key = os.getenv("API_KEY")

4. Prevention:
   - Use secrets management tools (AWS Secrets Manager, HashiCorp Vault)
   - Enable pre-commit hooks with trufflehog
   - Regular secret scanning in CI/CD pipeline
""",
        "homograph": f"""
**Remediation Steps for {component}:**

1. Verify Domain Legitimacy:
   - Check domain ownership and DNS records
   - Verify with legitimate service providers
   - Review recent changes to domain configuration

2. Code Changes:
   - Replace suspicious domain with verified legitimate domain
   - Use hardcoded whitelists for critical domains
   - Implement domain verification in configuration

3. Example Fix:
   # Before:
   api_url = "https://api-cdn.com"  # Unicode characters hidden
   
   # After:
   api_url = "https://api-cdn.com"  # Verified ASCII domain

4. Prevention:
   - Use code review to catch unusual Unicode
   - Implement domain pinning for critical services
   - Regular security audits of external URLs
""",
        "cve": f"""
**Remediation Steps for {component}:**

1. Assess Impact:
   - Determine if component is actually exploitable in your context
   - Check if vulnerable code path is used in your application

2. Update Component:
   - Upgrade to patched version if available
   - Test thoroughly in staging environment
   - Deploy updates following your release process

3. Temporary Mitigations (if update not available):
   - Disable vulnerable features if possible
   - Restrict access to vulnerable functionality
   - Monitor for exploitation attempts

4. Follow-up:
   - Subscribe to security advisories for {component}
   - Include dependency scanning in CI/CD
   - Regular vulnerability assessments
""",
    }

    threat_remediation = remediation_steps.get(threat_type, "Review security advisories and apply patches.")
    return f"**{component} - {threat_type.upper()} Remediation**" + threat_remediation


async def analyze_findings(findings: list, use_streaming: bool = False) -> str:
    """
    Use AI analysis to review security findings

    Args:
        findings: List of security findings (dict format)
        use_streaming: Whether to stream responses

    Returns:
        Analysis summary from AI
    """
    from sentinelci.config import get_config

    config = get_config()
    api_key = config.get_api_key()

    if not api_key:
        raise ValueError("AI API key not configured")

    client = Groq(api_key=api_key)

    # Format findings for Claude
    findings_text = json.dumps(findings, indent=2)
    user_message = f"""Please analyze these security findings and provide recommendations:

{findings_text}

For each finding, analyze the threat and suggest remediation steps."""

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    def _request_analysis() -> str:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            max_tokens=2048,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content or ""

    try:
        return await asyncio.to_thread(_request_analysis)
    except Exception:
        # Fall back to deterministic advice so scans still complete when AI calls fail.
        sections = []
        for finding in findings[:10]:
            sections.append(
                _handle_suggest_remediation(
                    threat_type=str(finding.get("type", "unknown")).lower(),
                    component=str(finding.get("tool", finding.get("location", "component"))),
                    details=str(finding.get("details", "")),
                )
            )
        return "\n\n".join(sections) if sections else "No actionable findings to analyze."


def get_threat_advice(threat_type: str, details: str) -> str:
    """
    Get quick advice for a specific threat without full agentic loop

    Args:
        threat_type: Type of threat
        details: Threat details

    Returns:
        Advice string
    """
    if threat_type == "secret":
        return _handle_suggest_remediation("secret", "exposed_secret", details)
    elif threat_type == "homograph":
        return _handle_suggest_remediation("homograph", "suspicious_url", details)
    elif threat_type == "cve":
        return _handle_suggest_remediation("cve", "vulnerable_component", details)
    else:
        return "Unknown threat type. Please review security best practices."
