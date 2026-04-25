"""
GitHub repository security analysis and risk dashboard
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import requests

from sentinelci.github_auth import GitHubAuth, GitHubAuthError


class GitHubSecurityAnalyzer:
    """Analyzes GitHub repository security configuration"""

    def __init__(self):
        self.auth = GitHubAuth()
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated request headers"""
        pat = self.auth.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        return {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }

    def analyze_repository(self, full_name: str) -> Dict[str, Any]:
        """
        Comprehensive security analysis of a repository

        Args:
            full_name: Repository full name (owner/repo)

        Returns:
            Dict with all security findings
        """
        self.auth.ensure_authenticated()

        analysis = {
            "repository": full_name,
            "timestamp": datetime.utcnow().isoformat(),
            "webhooks": self._get_webhooks(full_name),
            "workflows": self._get_workflows(full_name),
            "ci_cd_files": self._detect_ci_cd_files(full_name),
            "branch_protection": self._get_branch_protection(full_name),
            "secret_scanning": self._get_secret_scanning_alerts(full_name),
            "dependabot": self._get_dependabot_alerts(full_name),
            "security_advisories": self._get_security_advisories(full_name),
            "failed_workflows": self._get_failed_workflow_runs(full_name),
            "permissions": self._get_repository_permissions(full_name),
            "vulnerability_alerts": self._check_vulnerability_alerts_enabled(full_name),
        }

        return analysis

    def _get_webhooks(self, full_name: str) -> List[Dict[str, Any]]:
        """Get configured webhooks"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/hooks",
                headers=self._get_headers(),
                timeout=10,
            )

            if response.status_code == 200:
                hooks = response.json()
                return [
                    {
                        "id": hook["id"],
                        "name": hook.get("name", "web"),
                        "url": hook["config"].get("url", ""),
                        "events": hook.get("events", []),
                        "active": hook.get("active", False),
                        "created_at": hook.get("created_at", ""),
                    }
                    for hook in hooks
                ]
            elif response.status_code == 404:
                return []
            else:
                return [{"error": f"Failed to fetch webhooks: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _get_workflows(self, full_name: str) -> List[Dict[str, Any]]:
        """Get GitHub Actions workflows"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/actions/workflows",
                headers=self._get_headers(),
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                workflows = data.get("workflows", [])
                return [
                    {
                        "id": wf["id"],
                        "name": wf["name"],
                        "path": wf["path"],
                        "state": wf["state"],
                        "created_at": wf.get("created_at", ""),
                        "updated_at": wf.get("updated_at", ""),
                    }
                    for wf in workflows
                ]
            elif response.status_code == 404:
                return []
            else:
                return [{"error": f"Failed to fetch workflows: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _detect_ci_cd_files(self, full_name: str) -> Dict[str, bool]:
        """Detect CI/CD configuration files"""
        ci_files = {
            ".github/workflows": False,
            "Jenkinsfile": False,
            ".gitlab-ci.yml": False,
            ".circleci/config.yml": False,
            ".travis.yml": False,
            "azure-pipelines.yml": False,
            "bitbucket-pipelines.yml": False,
        }

        for file_path in ci_files.keys():
            try:
                response = requests.get(
                    f"{self.base_url}/repos/{full_name}/contents/{file_path}",
                    headers=self._get_headers(),
                    timeout=5,
                )
                ci_files[file_path] = response.status_code == 200
            except Exception:
                pass

        return ci_files

    def _get_branch_protection(self, full_name: str) -> Dict[str, Any]:
        """Get branch protection rules for default branch"""
        try:
            repo_response = requests.get(
                f"{self.base_url}/repos/{full_name}",
                headers=self._get_headers(),
                timeout=10,
            )

            if repo_response.status_code != 200:
                return {"error": "Failed to fetch repository info"}

            default_branch = repo_response.json().get("default_branch", "main")

            protection_response = requests.get(
                f"{self.base_url}/repos/{full_name}/branches/{default_branch}/protection",
                headers=self._get_headers(),
                timeout=10,
            )

            if protection_response.status_code == 200:
                protection = protection_response.json()
                return {
                    "enabled": True,
                    "branch": default_branch,
                    "required_status_checks": protection.get("required_status_checks"),
                    "enforce_admins": protection.get("enforce_admins", {}).get("enabled", False),
                    "required_pull_request_reviews": protection.get("required_pull_request_reviews"),
                    "restrictions": protection.get("restrictions"),
                    "required_signatures": protection.get("required_signatures", {}).get("enabled", False),
                }
            elif protection_response.status_code == 404:
                return {
                    "enabled": False,
                    "branch": default_branch,
                    "message": "No branch protection configured",
                }
            else:
                return {"error": f"Failed to fetch branch protection: {protection_response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _get_secret_scanning_alerts(self, full_name: str) -> List[Dict[str, Any]]:
        """Get secret scanning alerts"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/secret-scanning/alerts",
                headers={**self._get_headers(), "Accept": "application/vnd.github+json"},
                params={"state": "open"},
                timeout=10,
            )

            if response.status_code == 200:
                alerts = response.json()
                return [
                    {
                        "number": alert["number"],
                        "secret_type": alert.get("secret_type", ""),
                        "state": alert.get("state", ""),
                        "created_at": alert.get("created_at", ""),
                        "url": alert.get("html_url", ""),
                    }
                    for alert in alerts
                ]
            elif response.status_code == 404:
                return [{"message": "Secret scanning not available or not enabled"}]
            elif response.status_code == 403:
                return [{"message": "Secret scanning requires GitHub Advanced Security"}]
            else:
                return [{"error": f"Failed to fetch secret scanning alerts: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _get_dependabot_alerts(self, full_name: str) -> List[Dict[str, Any]]:
        """Get Dependabot vulnerability alerts"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/dependabot/alerts",
                headers={**self._get_headers(), "Accept": "application/vnd.github+json"},
                params={"state": "open"},
                timeout=10,
            )

            if response.status_code == 200:
                alerts = response.json()
                return [
                    {
                        "number": alert["number"],
                        "state": alert.get("state", ""),
                        "severity": alert.get("security_advisory", {}).get("severity", ""),
                        "package": alert.get("security_vulnerability", {}).get("package", {}).get("name", ""),
                        "summary": alert.get("security_advisory", {}).get("summary", ""),
                        "created_at": alert.get("created_at", ""),
                        "url": alert.get("html_url", ""),
                    }
                    for alert in alerts
                ]
            elif response.status_code == 404:
                return [{"message": "Dependabot alerts not available"}]
            elif response.status_code == 403:
                return [{"message": "Insufficient permissions to access Dependabot alerts"}]
            else:
                return [{"error": f"Failed to fetch Dependabot alerts: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _get_security_advisories(self, full_name: str) -> List[Dict[str, Any]]:
        """Get repository security advisories"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/security-advisories",
                headers={**self._get_headers(), "Accept": "application/vnd.github+json"},
                timeout=10,
            )

            if response.status_code == 200:
                advisories = response.json()
                return [
                    {
                        "ghsa_id": adv.get("ghsa_id", ""),
                        "summary": adv.get("summary", ""),
                        "severity": adv.get("severity", ""),
                        "state": adv.get("state", ""),
                        "published_at": adv.get("published_at", ""),
                        "url": adv.get("html_url", ""),
                    }
                    for adv in advisories
                ]
            elif response.status_code == 404:
                return []
            else:
                return [{"error": f"Failed to fetch security advisories: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _get_failed_workflow_runs(self, full_name: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent failed workflow runs"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/actions/runs",
                headers=self._get_headers(),
                params={"status": "failure", "per_page": limit},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                runs = data.get("workflow_runs", [])
                return [
                    {
                        "id": run["id"],
                        "name": run.get("name", ""),
                        "status": run.get("status", ""),
                        "conclusion": run.get("conclusion", ""),
                        "created_at": run.get("created_at", ""),
                        "updated_at": run.get("updated_at", ""),
                        "url": run.get("html_url", ""),
                    }
                    for run in runs
                ]
            elif response.status_code == 404:
                return []
            else:
                return [{"error": f"Failed to fetch workflow runs: {response.status_code}"}]

        except Exception as e:
            return [{"error": str(e)}]

    def _get_repository_permissions(self, full_name: str) -> Dict[str, Any]:
        """Get repository permissions model"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}",
                headers=self._get_headers(),
                timeout=10,
            )

            if response.status_code == 200:
                repo = response.json()
                return {
                    "visibility": "private" if repo.get("private") else "public",
                    "has_issues": repo.get("has_issues", False),
                    "has_projects": repo.get("has_projects", False),
                    "has_wiki": repo.get("has_wiki", False),
                    "has_downloads": repo.get("has_downloads", False),
                    "allow_forking": repo.get("allow_forking", False),
                    "is_template": repo.get("is_template", False),
                    "archived": repo.get("archived", False),
                    "disabled": repo.get("disabled", False),
                }
            else:
                return {"error": f"Failed to fetch repository info: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def _check_vulnerability_alerts_enabled(self, full_name: str) -> Dict[str, Any]:
        """Check if vulnerability alerts are enabled"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/vulnerability-alerts",
                headers={**self._get_headers(), "Accept": "application/vnd.github+json"},
                timeout=10,
            )

            if response.status_code == 204:
                return {"enabled": True}
            elif response.status_code == 404:
                return {"enabled": False}
            else:
                return {"error": f"Failed to check vulnerability alerts: {response.status_code}"}

        except Exception as e:
            return {"error": str(e)}

    def calculate_risk_score(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate risk score based on security analysis

        Args:
            analysis: Security analysis dict

        Returns:
            Risk score and breakdown
        """
        risk_score = 0
        risk_factors = []

        if not analysis.get("branch_protection", {}).get("enabled"):
            risk_score += 20
            risk_factors.append("No branch protection on default branch")

        if not analysis.get("vulnerability_alerts", {}).get("enabled"):
            risk_score += 15
            risk_factors.append("Vulnerability alerts disabled")

        dependabot_alerts = analysis.get("dependabot", [])
        if dependabot_alerts and not any("error" in a or "message" in a for a in dependabot_alerts):
            critical_count = sum(1 for a in dependabot_alerts if a.get("severity") == "critical")
            high_count = sum(1 for a in dependabot_alerts if a.get("severity") == "high")
            
            risk_score += critical_count * 10
            risk_score += high_count * 5
            
            if critical_count > 0:
                risk_factors.append(f"{critical_count} critical Dependabot alert(s)")
            if high_count > 0:
                risk_factors.append(f"{high_count} high severity Dependabot alert(s)")

        secret_alerts = analysis.get("secret_scanning", [])
        if secret_alerts and not any("error" in a or "message" in a for a in secret_alerts):
            risk_score += len(secret_alerts) * 15
            risk_factors.append(f"{len(secret_alerts)} exposed secret(s)")

        failed_workflows = analysis.get("failed_workflows", [])
        if failed_workflows and not any("error" in w for w in failed_workflows):
            risk_score += min(len(failed_workflows) * 2, 10)
            risk_factors.append(f"{len(failed_workflows)} recent failed workflow(s)")

        permissions = analysis.get("permissions", {})
        if permissions.get("visibility") == "public" and permissions.get("allow_forking"):
            risk_score += 5
            risk_factors.append("Public repository with forking enabled")

        risk_level = "LOW"
        if risk_score >= 50:
            risk_level = "CRITICAL"
        elif risk_score >= 30:
            risk_level = "HIGH"
        elif risk_score >= 15:
            risk_level = "MEDIUM"

        return {
            "score": min(risk_score, 100),
            "level": risk_level,
            "factors": risk_factors,
        }
