"""
Direct GitHub Repository Fixer
Makes changes directly via GitHub API without local cloning
"""

import base64
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import requests
from rich.console import Console
from rich.panel import Panel
from rich import box

console = Console()


@dataclass
class GitHubFile:
    """Represents a file in GitHub repository"""
    path: str
    content: str
    sha: str
    encoding: str = "base64"


@dataclass
class FixAction:
    """Represents a fix action to apply"""
    file_path: str
    original_content: str
    fixed_content: str
    description: str
    finding_type: str


class GitHubDirectFixer:
    """Fix vulnerabilities directly in GitHub repositories via API"""
    
    def __init__(self, github_token: str):
        self.token = github_token
        self.headers = {
            "Authorization": f"token {github_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.base_url = "https://api.github.com"
    
    def get_file_content(self, owner: str, repo: str, file_path: str, branch: str = "main") -> Optional[GitHubFile]:
        """Get file content from GitHub"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        params = {"ref": branch}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            
            if response.status_code == 404:
                return None
            
            response.raise_for_status()
            data = response.json()
            
            # Decode base64 content
            content = base64.b64decode(data["content"]).decode("utf-8")
            
            return GitHubFile(
                path=file_path,
                content=content,
                sha=data["sha"],
                encoding=data.get("encoding", "base64")
            )
        
        except Exception as e:
            console.print(f"[red]Failed to get file {file_path}: {str(e)}[/red]")
            return None
    
    def update_file(
        self,
        owner: str,
        repo: str,
        file_path: str,
        content: str,
        message: str,
        sha: str,
        branch: str = "main"
    ) -> bool:
        """Update file content in GitHub"""
        url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}"
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
        
        data = {
            "message": message,
            "content": encoded_content,
            "sha": sha,
            "branch": branch,
        }
        
        try:
            response = requests.put(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            return True
        
        except Exception as e:
            console.print(f"[red]Failed to update file {file_path}: {str(e)}[/red]")
            return False
    
    def create_branch(self, owner: str, repo: str, branch_name: str, from_branch: str = "main") -> bool:
        """Create a new branch"""
        try:
            # Get the SHA of the base branch
            ref_url = f"{self.base_url}/repos/{owner}/{repo}/git/ref/heads/{from_branch}"
            response = requests.get(ref_url, headers=self.headers, timeout=30)
            response.raise_for_status()
            base_sha = response.json()["object"]["sha"]
            
            # Check if branch already exists
            check_url = f"{self.base_url}/repos/{owner}/{repo}/git/ref/heads/{branch_name}"
            check_response = requests.get(check_url, headers=self.headers, timeout=30)
            
            if check_response.status_code == 200:
                # Branch exists, delete it first
                console.print(f"[yellow]Branch {branch_name} already exists, deleting...[/yellow]")
                delete_url = f"{self.base_url}/repos/{owner}/{repo}/git/refs/heads/{branch_name}"
                requests.delete(delete_url, headers=self.headers, timeout=30)
            
            # Create new branch
            create_url = f"{self.base_url}/repos/{owner}/{repo}/git/refs"
            data = {
                "ref": f"refs/heads/{branch_name}",
                "sha": base_sha,
            }
            
            response = requests.post(create_url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 422:
                # Branch might still exist, try with timestamp
                import time
                branch_name_new = f"{branch_name}-{int(time.time())}"
                console.print(f"[yellow]Retrying with branch name: {branch_name_new}[/yellow]")
                data["ref"] = f"refs/heads/{branch_name_new}"
                response = requests.post(create_url, headers=self.headers, json=data, timeout=30)
            
            response.raise_for_status()
            return True
        
        except Exception as e:
            console.print(f"[red]Failed to create branch {branch_name}: {str(e)}[/red]")
            if hasattr(e, 'response') and e.response is not None:
                console.print(f"[red]Response: {e.response.text}[/red]")
            return False
    
    def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head_branch: str,
        base_branch: str = "main"
    ) -> Optional[str]:
        """Create a pull request"""
        url = f"{self.base_url}/repos/{owner}/{repo}/pulls"
        
        data = {
            "title": title,
            "body": body,
            "head": head_branch,
            "base": base_branch,
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=data, timeout=30)
            response.raise_for_status()
            pr_data = response.json()
            return pr_data["html_url"]
        
        except Exception as e:
            console.print(f"[red]Failed to create PR: {str(e)}[/red]")
            return None
    
    def extract_secrets_from_content(self, content: str, file_path: str) -> List[Dict[str, Any]]:
        """Extract hardcoded secrets from file content"""
        secrets = []
        
        # Only detect actual hardcoded secrets with real values
        patterns = [
            # Specific API key formats
            (r'\bAKIA[0-9A-Z]{16}\b', "AWS Access Key"),
            (r'\bghp_[A-Za-z0-9]{36,}\b', "GitHub Token"),
            (r'\bsk_live_[A-Za-z0-9]{24,}\b', "Stripe Secret Key"),
            (r'\bsk-[A-Za-z0-9]{48,}\b', "OpenAI API Key"),
            (r'\bgsk_[A-Za-z0-9]{52,}\b', "Groq API Key"),
            (r'\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b', "SendGrid API Key"),
            # Only match actual hardcoded values (minimum 32 chars, high complexity)
            (r'(?i)(?:api[_-]?key|apikey)["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{32,})["\']', "API Key"),
            (r'(?i)(?:password|passwd)["\']?\s*[:=]\s*["\']([A-Za-z0-9!@#$%^&*()_+\-=\[\]{};:,.<>?]{16,})["\']', "Password"),
            (r'(?i)(?:auth[_-]?token|access[_-]?token)["\']?\s*[:=]\s*["\']([A-Za-z0-9_-]{32,})["\']', "Token"),
        ]
        
        lines = content.splitlines()
        for line_num, line in enumerate(lines, 1):
            # Skip JSX/React component lines
            if any(jsx in line for jsx in ["<Text", "<TextInput", "<Input", "<Button", "placeholder=", "style=", "value={"]):
                continue
            
            # Skip environment variable references without values
            if "process.env." in line and "=" not in line.split("process.env.")[0][-20:]:
                continue
            
            for pattern, secret_type in patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    if match.groups():
                        secret_value = match.group(1)
                    else:
                        secret_value = match.group(0)
                    
                    # Skip obvious placeholders
                    if any(p in secret_value.lower() for p in ["example", "placeholder", "your_", "xxx", "test", "demo", "sample"]):
                        continue
                    
                    # Skip UI property names
                    if secret_value.lower() in ["placeholder", "label", "title", "description", "text", "value", "name"]:
                        continue
                    
                    # Require minimum complexity
                    if len(secret_value) < 16:
                        continue
                    
                    # Check entropy for generic patterns
                    if secret_type in ["API Key", "Password", "Token"]:
                        unique_chars = len(set(secret_value))
                        if unique_chars < 8:  # Require at least 8 different characters
                            continue
                    
                    secrets.append({
                        "line": line_num,
                        "var_name": secret_type.upper().replace(" ", "_"),
                        "value": secret_value,
                        "type": secret_type,
                        "original_line": line,
                    })
        
        return secrets
    
    def fix_secrets_in_content(self, content: str, file_path: str) -> tuple[str, List[str]]:
        """Fix hardcoded secrets in content"""
        secrets = self.extract_secrets_from_content(content, file_path)
        
        if not secrets:
            return content, []
        
        fixed_content = content
        env_vars = []
        
        # Determine file type
        is_python = file_path.endswith(".py")
        is_js = file_path.endswith((".js", ".ts", ".jsx", ".tsx"))
        is_yaml = file_path.endswith((".yml", ".yaml"))
        
        for secret in secrets:
            var_name = secret["var_name"]
            original_line = secret["original_line"]
            
            # Generate replacement based on file type
            if is_python:
                replacement = f'{var_name} = os.getenv("{var_name}")'
                if "import os" not in fixed_content:
                    fixed_content = "import os\n" + fixed_content
            elif is_js:
                replacement = f'const {var_name} = process.env.{var_name}'
            elif is_yaml:
                replacement = f'{var_name}: ${{{{ secrets.{var_name} }}}}'
            else:
                replacement = f'{var_name} = ENV["{var_name}"]'
            
            # Replace the line
            fixed_content = fixed_content.replace(original_line, replacement)
            
            # Add to env vars list
            env_vars.append(f'{var_name}={secret["value"]}')
        
        return fixed_content, env_vars
    
    def fix_workflow_permissions(self, content: str) -> str:
        """Fix excessive workflow permissions"""
        # Replace write-all with minimal permissions
        fixed = re.sub(
            r'permissions:\s*write-all',
            'permissions:\n  contents: read\n  pull-requests: write',
            content
        )
        
        return fixed
    
    def fix_unpinned_actions(self, content: str) -> str:
        """Fix unpinned actions (basic - pins to latest stable)"""
        # This is a simplified version - in production, you'd fetch actual commit SHAs
        replacements = {
            '@main': '@v4',
            '@master': '@v4',
        }
        
        fixed = content
        for old, new in replacements.items():
            fixed = fixed.replace(old, new)
        
        return fixed
    
    def analyze_and_fix_repository(
        self,
        owner: str,
        repo: str,
        findings: List[Dict[str, Any]],
        base_branch: str = "main",
        auto_commit: bool = True
    ) -> Dict[str, Any]:
        """Analyze findings and fix directly in GitHub"""
        
        console.print(Panel(
            f"[bold cyan]Direct GitHub Fixer[/bold cyan]\n"
            f"Repository: {owner}/{repo}\n"
            f"Findings: {len(findings)}",
            border_style="cyan",
            box=box.ROUNDED
        ))
        
        # Group findings by file
        files_to_fix = {}
        for finding in findings:
            file_path = finding.get("file", "")
            if not file_path:
                continue
            
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(finding)
        
        console.print(f"\n[cyan]Files to fix: {len(files_to_fix)}[/cyan]")
        
        # Create new branch
        branch_name = f"security/auto-fix-{len(findings)}-issues"
        console.print(f"\n[cyan]Creating branch: {branch_name}[/cyan]")
        
        if not self.create_branch(owner, repo, branch_name, base_branch):
            # Try with timestamp if failed
            import time
            branch_name = f"security/auto-fix-{int(time.time())}"
            console.print(f"[yellow]Retrying with: {branch_name}[/yellow]")
            if not self.create_branch(owner, repo, branch_name, base_branch):
                return {"success": False, "error": "Failed to create branch"}
        
        # Fix each file
        fixed_files = []
        env_vars_all = []
        
        for file_path, file_findings in files_to_fix.items():
            console.print(f"\n[cyan]Processing: {file_path}[/cyan]")
            
            # Get file content
            github_file = self.get_file_content(owner, repo, file_path, branch_name)
            if not github_file:
                console.print(f"[yellow]Skipping {file_path} - not found[/yellow]")
                continue
            
            original_content = github_file.content
            fixed_content = original_content
            
            # Apply fixes based on finding types
            for finding in file_findings:
                finding_type = finding.get("type", "")
                
                if "secret" in finding_type.lower() or "api key" in finding_type.lower():
                    fixed_content, env_vars = self.fix_secrets_in_content(fixed_content, file_path)
                    env_vars_all.extend(env_vars)
                
                elif "permission" in finding_type.lower():
                    fixed_content = self.fix_workflow_permissions(fixed_content)
                
                elif "unpinned" in finding_type.lower():
                    fixed_content = self.fix_unpinned_actions(fixed_content)
            
            # Update file if changed
            if fixed_content != original_content:
                commit_message = f"fix: Security fixes for {file_path}\n\nFixed {len(file_findings)} issue(s)"
                
                if self.update_file(owner, repo, file_path, fixed_content, commit_message, github_file.sha, branch_name):
                    fixed_files.append(file_path)
                    console.print(f"[green]✓ Fixed {file_path}[/green]")
                else:
                    console.print(f"[red]✗ Failed to fix {file_path}[/red]")
        
        # Create .env.example if we have env vars
        if env_vars_all:
            env_content = "\n".join(env_vars_all)
            console.print(f"\n[cyan]Creating .env.example with {len(env_vars_all)} variables[/cyan]")
            
            # Check if .env.example exists
            env_file = self.get_file_content(owner, repo, ".env.example", branch_name)
            
            if env_file:
                # Append to existing
                new_content = env_file.content + "\n\n# Auto-generated secrets\n" + env_content
                self.update_file(owner, repo, ".env.example", new_content, "chore: Add extracted secrets", env_file.sha, branch_name)
            else:
                # Create new file (requires different API call)
                console.print("[yellow]Note: .env.example creation requires manual step[/yellow]")
        
        # Create pull request
        if fixed_files and auto_commit:
            console.print(f"\n[cyan]Creating pull request...[/cyan]")
            
            pr_body = f"""## 🔒 Automated Security Fixes

This PR was created automatically by SentinelCI to fix security vulnerabilities.

### Fixed Issues
- Total findings: {len(findings)}
- Files modified: {len(fixed_files)}

### Changes Made
"""
            for file_path in fixed_files:
                pr_body += f"- ✅ {file_path}\n"
            
            if env_vars_all:
                pr_body += f"\n### Environment Variables\n"
                pr_body += f"Created/updated `.env.example` with {len(env_vars_all)} variables.\n"
                pr_body += f"**Action Required:** Add these to your GitHub Secrets or environment configuration.\n"
            
            pr_body += f"\n### Review Required\n"
            pr_body += f"Please review the changes and test before merging.\n"
            
            pr_url = self.create_pull_request(
                owner,
                repo,
                f"🔒 Security: Auto-fix {len(findings)} issue(s)",
                pr_body,
                branch_name,
                base_branch
            )
            
            if pr_url:
                console.print(f"\n[green]✓ Pull request created: {pr_url}[/green]")
            
            return {
                "success": True,
                "branch": branch_name,
                "fixed_files": fixed_files,
                "pr_url": pr_url,
                "env_vars": len(env_vars_all),
            }
        
        return {
            "success": True,
            "branch": branch_name,
            "fixed_files": fixed_files,
            "env_vars": len(env_vars_all),
        }


def fix_github_repository_direct(
    owner: str,
    repo: str,
    findings: List[Dict[str, Any]],
    github_token: str,
    base_branch: str = "main",
    auto_commit: bool = True
) -> Dict[str, Any]:
    """
    Fix vulnerabilities directly in GitHub repository
    
    Args:
        owner: Repository owner
        repo: Repository name
        findings: List of security findings
        github_token: GitHub Personal Access Token
        base_branch: Base branch to create PR against
        auto_commit: Whether to auto-commit and create PR
    
    Returns:
        Dictionary with fix results
    """
    fixer = GitHubDirectFixer(github_token)
    return fixer.analyze_and_fix_repository(owner, repo, findings, base_branch, auto_commit)
