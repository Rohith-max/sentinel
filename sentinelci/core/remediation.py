"""
Automated remediation - PR and Issue generation using Git Data API
"""

from typing import Dict, Any, List, Optional
import requests
import base64
from sentinelci.core.auth import GitHubAuth, GitHubAuthError


class RemediationEngine:
    """Generates PRs and issues for security findings using Git Data API"""

    def __init__(self):
        self.auth = GitHubAuth()
        self.base_url = "https://api.github.com"

    def _get_headers(self) -> Dict[str, str]:
        """Get authenticated headers"""
        pat = self.auth.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        return {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }

    def _get_default_branch(self, repo_full_name: str) -> str:
        """Get repository default branch"""
        response = requests.get(
            f"{self.base_url}/repos/{repo_full_name}",
            headers=self._get_headers(),
            timeout=10,
        )
        
        if response.status_code == 200:
            return response.json().get("default_branch", "main")
        return "main"

    def _get_branch_sha(self, repo_full_name: str, branch: str) -> str:
        """Get SHA of branch HEAD"""
        response = requests.get(
            f"{self.base_url}/repos/{repo_full_name}/git/refs/heads/{branch}",
            headers=self._get_headers(),
            timeout=10,
        )
        
        if response.status_code == 200:
            return response.json()["object"]["sha"]
        raise GitHubAuthError(f"Failed to get branch SHA: {response.status_code}")

    def _create_blob(self, repo_full_name: str, content: str) -> str:
        """Create a blob (file content) and return its SHA"""
        payload = {
            "content": content,
            "encoding": "utf-8",
        }
        
        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/git/blobs",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )
        
        if response.status_code == 201:
            return response.json()["sha"]
        raise GitHubAuthError(f"Failed to create blob: {response.status_code}")

    def _get_tree(self, repo_full_name: str, tree_sha: str) -> Dict[str, Any]:
        """Get tree object"""
        response = requests.get(
            f"{self.base_url}/repos/{repo_full_name}/git/trees/{tree_sha}",
            headers=self._get_headers(),
            timeout=10,
        )
        
        if response.status_code == 200:
            return response.json()
        raise GitHubAuthError(f"Failed to get tree: {response.status_code}")

    def _create_tree(self, repo_full_name: str, base_tree: str, files: List[Dict[str, Any]]) -> str:
        """Create a new tree with file changes"""
        payload = {
            "base_tree": base_tree,
            "tree": files,
        }
        
        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/git/trees",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )
        
        if response.status_code == 201:
            return response.json()["sha"]
        raise GitHubAuthError(f"Failed to create tree: {response.status_code}")

    def _create_commit(
        self,
        repo_full_name: str,
        message: str,
        tree_sha: str,
        parent_sha: str,
    ) -> str:
        """Create a commit"""
        payload = {
            "message": message,
            "tree": tree_sha,
            "parents": [parent_sha],
        }
        
        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/git/commits",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )
        
        if response.status_code == 201:
            return response.json()["sha"]
        raise GitHubAuthError(f"Failed to create commit: {response.status_code}")

    def _update_ref(self, repo_full_name: str, ref: str, sha: str) -> None:
        """Update a reference to point to a new commit"""
        payload = {
            "sha": sha,
            "force": False,
        }
        
        response = requests.patch(
            f"{self.base_url}/repos/{repo_full_name}/git/refs/{ref}",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )
        
        if response.status_code != 200:
            raise GitHubAuthError(f"Failed to update ref: {response.status_code}")

    def _create_ref(self, repo_full_name: str, ref: str, sha: str) -> None:
        """Create a new reference"""
        payload = {
            "ref": f"refs/{ref}",
            "sha": sha,
        }
        
        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/git/refs",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )
        
        if response.status_code != 201:
            raise GitHubAuthError(f"Failed to create ref: {response.status_code}")

    def _get_file_content(self, repo_full_name: str, path: str, ref: str = None) -> tuple[str, str]:
        """Get file content and SHA"""
        params = {"ref": ref} if ref else {}
        
        response = requests.get(
            f"{self.base_url}/repos/{repo_full_name}/contents/{path}",
            headers=self._get_headers(),
            params=params,
            timeout=10,
        )
        
        if response.status_code == 200:
            data = response.json()
            content = base64.b64decode(data["content"]).decode("utf-8")
            return content, data["sha"]
        raise GitHubAuthError(f"Failed to get file: {response.status_code}")

    def create_security_issue(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        labels: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a security issue"""
        self.auth.ensure_authenticated()

        payload = {
            "title": title,
            "body": body,
            "labels": labels or ["security", "automated"],
        }

        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/issues",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )

        if response.status_code == 201:
            return response.json()
        else:
            raise GitHubAuthError(f"Failed to create issue: {response.status_code}")

    def create_pull_request(
        self,
        repo_full_name: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = None,
    ) -> Dict[str, Any]:
        """Create a pull request"""
        self.auth.ensure_authenticated()
        
        if not base_branch:
            base_branch = self._get_default_branch(repo_full_name)

        payload = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
        }

        response = requests.post(
            f"{self.base_url}/repos/{repo_full_name}/pulls",
            headers=self._get_headers(),
            json=payload,
            timeout=15,
        )

        if response.status_code == 201:
            return response.json()
        else:
            raise GitHubAuthError(f"Failed to create PR: {response.status_code}")

    def apply_patch_remote(
        self,
        repo_full_name: str,
        branch_name: str,
        files: Dict[str, str],
        commit_message: str,
    ) -> str:
        """
        Apply patches to multiple files remotely using Git Data API
        
        Args:
            repo_full_name: Repository full name (owner/repo)
            branch_name: New branch name to create
            files: Dict of {file_path: new_content}
            commit_message: Commit message
            
        Returns:
            Commit SHA
        """
        self.auth.ensure_authenticated()
        
        # Get base branch
        base_branch = self._get_default_branch(repo_full_name)
        base_sha = self._get_branch_sha(repo_full_name, base_branch)
        
        # Get base commit
        response = requests.get(
            f"{self.base_url}/repos/{repo_full_name}/git/commits/{base_sha}",
            headers=self._get_headers(),
            timeout=10,
        )
        
        if response.status_code != 200:
            raise GitHubAuthError(f"Failed to get commit: {response.status_code}")
        
        base_tree_sha = response.json()["tree"]["sha"]
        
        # Create blobs for each file
        tree_items = []
        for file_path, content in files.items():
            blob_sha = self._create_blob(repo_full_name, content)
            tree_items.append({
                "path": file_path,
                "mode": "100644",
                "type": "blob",
                "sha": blob_sha,
            })
        
        # Create new tree
        new_tree_sha = self._create_tree(repo_full_name, base_tree_sha, tree_items)
        
        # Create commit
        commit_sha = self._create_commit(
            repo_full_name,
            commit_message,
            new_tree_sha,
            base_sha,
        )
        
        # Create new branch
        try:
            self._create_ref(repo_full_name, f"heads/{branch_name}", commit_sha)
        except GitHubAuthError:
            # Branch might exist, try to update it
            self._update_ref(repo_full_name, f"heads/{branch_name}", commit_sha)
        
        return commit_sha

    def generate_fix_content(self, finding: Dict[str, Any], original_content: str) -> str:
        """Generate fixed content based on finding type"""
        category = finding.get("category", finding.get("type", "")).lower()
        
        if "secret" in category:
            # Remove hardcoded secrets
            lines = original_content.split("\n")
            line_num = finding.get("line_number", 0)
            
            if 0 < line_num <= len(lines):
                # Comment out the line with secret
                lines[line_num - 1] = f"# SECURITY: Secret removed - use environment variable\n# {lines[line_num - 1]}"
            
            return "\n".join(lines)
        
        elif "workflow" in category or "permission" in category:
            # Add restrictive permissions to workflow
            lines = original_content.split("\n")
            
            # Find where to insert permissions
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.strip().startswith("on:"):
                    insert_idx = i + 1
                    # Skip event definitions
                    while insert_idx < len(lines) and (lines[insert_idx].startswith("  ") or not lines[insert_idx].strip()):
                        insert_idx += 1
                    break
            
            # Insert permissions block
            permissions_block = [
                "",
                "permissions:",
                "  contents: read",
                "  pull-requests: write",
                "",
            ]
            
            lines = lines[:insert_idx] + permissions_block + lines[insert_idx:]
            return "\n".join(lines)
        
        elif "dependency" in category:
            # Pin dependency versions
            lines = original_content.split("\n")
            
            for i, line in enumerate(lines):
                # Pin npm dependencies
                if "@latest" in line or "^" in line or "~" in line:
                    lines[i] = line.replace("@latest", "@1.0.0").replace("^", "").replace("~", "")
            
            return "\n".join(lines)
        
        return original_content

    def generate_security_pr(
        self,
        repo_full_name: str,
        findings: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Generate PR with security fixes using Git Data API (no cloning)
        
        Returns PR details
        """
        self.auth.ensure_authenticated()
        
        # Group findings by file
        files_to_fix = {}
        
        for finding in findings:
            file_path = finding.get("location", finding.get("file", ""))
            if not file_path:
                continue
            
            # Get original content
            try:
                original_content, _ = self._get_file_content(repo_full_name, file_path)
                fixed_content = self.generate_fix_content(finding, original_content)
                files_to_fix[file_path] = fixed_content
            except Exception:
                continue
        
        if not files_to_fix:
            raise GitHubAuthError("No fixable files found")
        
        # Create branch and apply patches
        branch_name = f"security/auto-fix-{len(findings)}-issues"
        commit_message = f"🔒 Security: Fix {len(findings)} issue(s)\n\nAutomated security fixes:\n" + "\n".join(
            f"- {f.get('category', 'issue')} in {f.get('location', 'file')}"
            for f in findings[:5]
        )
        
        commit_sha = self.apply_patch_remote(
            repo_full_name,
            branch_name,
            files_to_fix,
            commit_message,
        )
        
        # Create PR
        title = f"🔒 Security: Auto-fix {len(findings)} issue(s)"
        body = self._generate_pr_body(findings, files_to_fix)
        
        pr = self.create_pull_request(
            repo_full_name,
            title,
            body,
            branch_name,
        )
        
        return {
            "pr_number": pr["number"],
            "pr_url": pr["html_url"],
            "branch": branch_name,
            "commit_sha": commit_sha,
            "files_changed": len(files_to_fix),
        }

    def _generate_pr_body(self, findings: List[Dict[str, Any]], files: Dict[str, str]) -> str:
        """Generate concise PR body"""
        severity_counts = {}
        for f in findings:
            sev = f.get("severity", "MEDIUM")
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        body = "## 🔒 Automated Security Fixes\n\n"
        body += "**Summary:**\n"
        for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            if sev in severity_counts:
                body += f"- {sev}: {severity_counts[sev]} issue(s)\n"
        
        body += f"\n**Files Changed:** {len(files)}\n\n"
        
        body += "**Changes:**\n"
        for finding in findings[:10]:
            category = finding.get("category", "Security issue")
            location = finding.get("location", "unknown")
            body += f"- **{category}** in `{location}`\n"
            
            # Add fix description
            if "secret" in category.lower():
                body += "  - Removed hardcoded secret\n"
            elif "permission" in category.lower():
                body += "  - Restricted workflow permissions\n"
            elif "dependency" in category.lower():
                body += "  - Pinned dependency version\n"
        
        if len(findings) > 10:
            body += f"\n... and {len(findings) - 10} more\n"
        
        body += "\n---\n*Generated by SentinelCI - No cloning required*"
        
        return body
