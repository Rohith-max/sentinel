"""
Advanced AI-powered security analysis for repositories
"""

import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import asyncio

from groq import Groq


@dataclass
class SecurityFinding:
    """Represents a security finding from AI analysis"""
    category: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    title: str
    description: str
    location: str
    evidence: str
    remediation: str
    confidence: float
    cwe_id: Optional[str] = None
    cvss_score: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class AnalysisResult:
    """Complete analysis result"""
    repository: str
    timestamp: str
    risk_score: int  # 0-100
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    findings: List[SecurityFinding]
    summary: str
    recommendations: List[str]
    audit_explanation: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "repository": self.repository,
            "timestamp": self.timestamp,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "findings": [f.to_dict() for f in self.findings],
            "summary": self.summary,
            "recommendations": self.recommendations,
            "audit_explanation": self.audit_explanation,
        }


class AISecurityAnalyzer:
    """Advanced AI-powered security analyzer"""

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    async def analyze_repository(
        self,
        repo_name: str,
        metadata: Dict[str, Any],
        workflows: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
        pipeline_data: Dict[str, Any],
    ) -> AnalysisResult:
        """
        Comprehensive AI security analysis

        Args:
            repo_name: Repository full name
            metadata: Repository metadata
            workflows: GitHub Actions workflows
            dependencies: Dependency information
            pipeline_data: CI/CD pipeline data

        Returns:
            AnalysisResult with findings and recommendations
        """
        # Prepare analysis context
        context = self._prepare_context(repo_name, metadata, workflows, dependencies, pipeline_data)

        # Run parallel analyses
        tasks = [
            self._analyze_secrets(context),
            self._analyze_outbound_calls(context),
            self._analyze_dependencies(context),
            self._analyze_privilege_escalation(context),
            self._analyze_token_permissions(context),
            self._analyze_third_party_actions(context),
            self._analyze_supply_chain(context),
        ]

        results = await asyncio.gather(*tasks)

        # Combine findings
        all_findings = []
        for finding_list in results:
            all_findings.extend(finding_list)

        # Calculate risk score
        risk_score = self._calculate_risk_score(all_findings)
        risk_level = self._determine_risk_level(risk_score)

        # Generate summary and recommendations
        summary = await self._generate_summary(all_findings, risk_score)
        recommendations = self._generate_recommendations(all_findings)
        audit_explanation = await self._generate_audit_explanation(
            repo_name, all_findings, risk_score, context
        )

        return AnalysisResult(
            repository=repo_name,
            timestamp=datetime.utcnow().isoformat(),
            risk_score=risk_score,
            risk_level=risk_level,
            findings=all_findings,
            summary=summary,
            recommendations=recommendations,
            audit_explanation=audit_explanation,
        )

    def _prepare_context(
        self,
        repo_name: str,
        metadata: Dict[str, Any],
        workflows: List[Dict[str, Any]],
        dependencies: List[Dict[str, Any]],
        pipeline_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare analysis context"""
        return {
            "repository": repo_name,
            "metadata": metadata,
            "workflows": workflows,
            "dependencies": dependencies,
            "pipeline_data": pipeline_data,
        }

    async def _analyze_secrets(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze for hardcoded secrets exposure"""
        findings = []

        prompt = f"""Analyze this repository for hardcoded secrets exposure:

Repository: {context['repository']}
Workflows: {json.dumps(context['workflows'], indent=2)}

Look for:
1. Hardcoded API keys, tokens, passwords
2. Secrets in environment variables without proper masking
3. Credentials in workflow files
4. Exposed secrets in logs
5. Insecure secret storage

Return findings in JSON format:
[{{"category": "secrets", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            
            # Extract JSON from response
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "secrets"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception as e:
            print(f"WARNING: Secrets analysis error: {str(e)}")

        return findings

    async def _analyze_outbound_calls(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze for suspicious outbound calls"""
        findings = []

        prompt = f"""Analyze this repository for suspicious outbound network calls:

Repository: {context['repository']}
Workflows: {json.dumps(context['workflows'], indent=2)}

Look for:
1. Calls to unknown or suspicious domains
2. Data exfiltration attempts
3. Unverified external API calls
4. Insecure HTTP connections
5. Calls to IP addresses instead of domains

Return findings in JSON format:
[{{"category": "outbound_calls", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "outbound_calls"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    async def _analyze_dependencies(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze dependency hash mismatch risks"""
        findings = []

        dependencies = context.get("dependencies", [])
        if not dependencies:
            return findings

        prompt = f"""Analyze these dependencies for security risks:

Repository: {context['repository']}
Dependencies: {json.dumps(dependencies, indent=2)}

Look for:
1. Missing or mismatched dependency hashes
2. Unpinned versions
3. Known vulnerable packages
4. Suspicious package names (typosquatting)
5. Lack of integrity checks

Return findings in JSON format:
[{{"category": "dependencies", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "dependencies"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    async def _analyze_privilege_escalation(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze for privilege escalation in workflows"""
        findings = []

        workflows = context.get("workflows", [])
        if not workflows:
            return findings

        prompt = f"""Analyze these workflows for privilege escalation risks:

Repository: {context['repository']}
Workflows: {json.dumps(workflows, indent=2)}

Look for:
1. Unnecessary sudo usage
2. Running as root
3. Privilege escalation commands
4. Insecure permission changes
5. Unrestricted script execution

Return findings in JSON format:
[{{"category": "privilege_escalation", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "privilege_escalation"),
                        severity=f.get("severity", "HIGH"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    async def _analyze_token_permissions(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze over-permissioned GitHub Actions tokens"""
        findings = []

        workflows = context.get("workflows", [])
        if not workflows:
            return findings

        prompt = f"""Analyze these workflows for over-permissioned tokens:

Repository: {context['repository']}
Workflows: {json.dumps(workflows, indent=2)}

Look for:
1. Overly broad token permissions
2. Write permissions when read is sufficient
3. Missing permission restrictions
4. Unnecessary repo-wide access
5. Tokens with admin privileges

Return findings in JSON format:
[{{"category": "token_permissions", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "token_permissions"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    async def _analyze_third_party_actions(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze untrusted third-party actions"""
        findings = []

        workflows = context.get("workflows", [])
        if not workflows:
            return findings

        prompt = f"""Analyze these workflows for untrusted third-party actions:

Repository: {context['repository']}
Workflows: {json.dumps(workflows, indent=2)}

Look for:
1. Actions from unknown publishers
2. Unpinned action versions
3. Actions without commit SHA pinning
4. Suspicious action names
5. Actions with excessive permissions

Return findings in JSON format:
[{{"category": "third_party_actions", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "third_party_actions"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    async def _analyze_supply_chain(self, context: Dict[str, Any]) -> List[SecurityFinding]:
        """Analyze supply chain risks"""
        findings = []

        prompt = f"""Analyze this repository for supply chain security risks:

Repository: {context['repository']}
Dependencies: {json.dumps(context.get('dependencies', []), indent=2)}
Workflows: {json.dumps(context.get('workflows', []), indent=2)}

Look for:
1. Lack of dependency verification
2. Missing SBOM (Software Bill of Materials)
3. No provenance attestation
4. Unsigned artifacts
5. Insecure build processes

Return findings in JSON format:
[{{"category": "supply_chain", "severity": "CRITICAL|HIGH|MEDIUM|LOW", "title": "...", "description": "...", "location": "...", "evidence": "...", "remediation": "...", "confidence": 0.0-1.0}}]

If no issues found, return empty array []."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=2048,
            )

            content = response.choices[0].message.content or "[]"
            json_start = content.find("[")
            json_end = content.rfind("]") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                findings_data = json.loads(json_str)
                
                for f in findings_data:
                    findings.append(SecurityFinding(
                        category=f.get("category", "supply_chain"),
                        severity=f.get("severity", "MEDIUM"),
                        title=f.get("title", ""),
                        description=f.get("description", ""),
                        location=f.get("location", ""),
                        evidence=f.get("evidence", ""),
                        remediation=f.get("remediation", ""),
                        confidence=f.get("confidence", 0.7),
                    ))

        except Exception:
            pass

        return findings

    def _calculate_risk_score(self, findings: List[SecurityFinding]) -> int:
        """Calculate overall risk score (0-100)"""
        if not findings:
            return 0

        severity_weights = {
            "CRITICAL": 25,
            "HIGH": 15,
            "MEDIUM": 8,
            "LOW": 3,
        }

        total_score = 0
        for finding in findings:
            weight = severity_weights.get(finding.severity, 3)
            confidence_factor = finding.confidence
            total_score += weight * confidence_factor

        return min(int(total_score), 100)

    def _determine_risk_level(self, risk_score: int) -> str:
        """Determine risk level from score"""
        if risk_score >= 70:
            return "CRITICAL"
        elif risk_score >= 45:
            return "HIGH"
        elif risk_score >= 20:
            return "MEDIUM"
        else:
            return "LOW"

    async def _generate_summary(self, findings: List[SecurityFinding], risk_score: int) -> str:
        """Generate executive summary"""
        if not findings:
            return "No significant security issues detected. Repository follows security best practices."

        severity_counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
        for finding in findings:
            severity_counts[finding.severity] = severity_counts.get(finding.severity, 0) + 1

        summary_parts = [
            f"Security analysis identified {len(findings)} issue(s) with a risk score of {risk_score}/100."
        ]

        if severity_counts["CRITICAL"] > 0:
            summary_parts.append(f"{severity_counts['CRITICAL']} CRITICAL issue(s) require immediate attention.")
        if severity_counts["HIGH"] > 0:
            summary_parts.append(f"{severity_counts['HIGH']} HIGH severity issue(s) should be addressed promptly.")

        return " ".join(summary_parts)

    def _generate_recommendations(self, findings: List[SecurityFinding]) -> List[str]:
        """Generate prioritized recommendations"""
        recommendations = []

        # Group by category
        by_category = {}
        for finding in findings:
            if finding.category not in by_category:
                by_category[finding.category] = []
            by_category[finding.category].append(finding)

        # Generate category-specific recommendations
        for category, category_findings in by_category.items():
            if category == "secrets":
                recommendations.append("Implement GitHub secret scanning and remove hardcoded credentials")
            elif category == "dependencies":
                recommendations.append("Pin dependency versions with integrity hashes")
            elif category == "privilege_escalation":
                recommendations.append("Apply principle of least privilege to workflow permissions")
            elif category == "token_permissions":
                recommendations.append("Restrict GitHub Actions token permissions to minimum required")
            elif category == "third_party_actions":
                recommendations.append("Pin third-party actions to specific commit SHAs")
            elif category == "supply_chain":
                recommendations.append("Implement SBOM generation and artifact signing")

        return recommendations[:10]  # Top 10 recommendations

    async def _generate_audit_explanation(
        self,
        repo_name: str,
        findings: List[SecurityFinding],
        risk_score: int,
        context: Dict[str, Any],
    ) -> str:
        """Generate plain English audit explanation"""
        prompt = f"""Generate a plain English security audit explanation for this repository:

Repository: {repo_name}
Risk Score: {risk_score}/100
Number of Findings: {len(findings)}

Findings Summary:
{json.dumps([f.to_dict() for f in findings[:5]], indent=2)}

Write a clear, non-technical explanation that:
1. Explains what was analyzed
2. Describes the key security concerns found
3. Explains why these issues matter
4. Provides context for the risk score
5. Suggests next steps

Keep it concise (3-4 paragraphs) and accessible to non-security experts."""

        try:
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1024,
            )

            return response.choices[0].message.content or "Audit explanation unavailable."

        except Exception:
            return f"Security audit of {repo_name} identified {len(findings)} issue(s) with a risk score of {risk_score}/100. Review the detailed findings for specific remediation steps."
