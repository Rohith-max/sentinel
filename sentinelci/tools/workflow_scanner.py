"""
GitHub Actions workflow security scanner
Detects security issues in CI/CD pipelines
"""

import re
import yaml
from pathlib import Path
from typing import List, Dict, Any


def scan_workflows(path: str) -> List[Dict[str, Any]]:
    """
    Scan GitHub Actions workflows for security issues
    
    Args:
        path: File or directory path
    
    Returns:
        List of workflow security findings
    """
    findings = []
    path_obj = Path(path)
    
    if path_obj.is_file() and path_obj.suffix in [".yml", ".yaml"]:
        findings.extend(_scan_workflow_file(path_obj))
    elif path_obj.is_dir():
        # Scan .github/workflows directory
        workflows_dir = path_obj / ".github" / "workflows"
        if workflows_dir.exists():
            for workflow_file in workflows_dir.glob("*.yml"):
                findings.extend(_scan_workflow_file(workflow_file))
            for workflow_file in workflows_dir.glob("*.yaml"):
                findings.extend(_scan_workflow_file(workflow_file))
    
    return findings


def _scan_workflow_file(file_path: Path) -> List[Dict[str, Any]]:
    """Scan a single workflow file for security issues"""
    findings = []
    
    try:
        content = file_path.read_text()
        
        # Parse YAML
        try:
            workflow = yaml.safe_load(content)
        except yaml.YAMLError:
            return findings
        
        if not isinstance(workflow, dict):
            return findings
        
        # Check for script injection vulnerabilities
        findings.extend(_check_script_injection(file_path, content, workflow))
        
        # Check for excessive permissions
        findings.extend(_check_permissions(file_path, workflow))
        
        # Check for pull_request_target misuse
        findings.extend(_check_pull_request_target(file_path, workflow))
        
        # Check for hardcoded secrets in workflow
        findings.extend(_check_hardcoded_secrets(file_path, content))
        
        # Check for unpinned actions
        findings.extend(_check_unpinned_actions(file_path, content))
        
    except Exception:
        pass
    
    return findings


def _check_script_injection(file_path: Path, content: str, workflow: dict) -> List[Dict[str, Any]]:
    """Check for script injection vulnerabilities"""
    findings = []
    
    # Dangerous patterns that use untrusted input
    dangerous_patterns = [
        r"\$\{\{\s*github\.event\.issue\.title\s*\}\}",
        r"\$\{\{\s*github\.event\.issue\.body\s*\}\}",
        r"\$\{\{\s*github\.event\.pull_request\.title\s*\}\}",
        r"\$\{\{\s*github\.event\.pull_request\.body\s*\}\}",
        r"\$\{\{\s*github\.event\.comment\.body\s*\}\}",
        r"\$\{\{\s*github\.event\.review\.body\s*\}\}",
        r"\$\{\{\s*github\.event\.pages\.\*\.page_name\s*\}\}",
        r"\$\{\{\s*github\.head_ref\s*\}\}",
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, content):
            findings.append({
                "type": "Script Injection Risk",
                "severity": "CRITICAL",
                "file": str(file_path),
                "line_number": 0,
                "description": "Workflow uses untrusted input in run command which can lead to script injection",
                "remediation": "Use environment variables to pass untrusted input instead of direct interpolation",
            })
            break
    
    return findings


def _check_permissions(file_path: Path, workflow: dict) -> List[Dict[str, Any]]:
    """Check for excessive permissions"""
    findings = []
    
    # Check top-level permissions
    permissions = workflow.get("permissions")
    if permissions == "write-all" or (isinstance(permissions, dict) and "write-all" in str(permissions)):
        findings.append({
            "type": "Excessive Permissions",
            "severity": "HIGH",
            "file": str(file_path),
            "line_number": 0,
            "description": "Workflow has write-all permissions which grants excessive access",
            "remediation": "Use least privilege principle and specify only required permissions",
        })
    
    # Check job-level permissions
    jobs = workflow.get("jobs", {})
    for job_name, job_config in jobs.items():
        if isinstance(job_config, dict):
            job_perms = job_config.get("permissions")
            if job_perms == "write-all":
                findings.append({
                    "type": "Excessive Permissions",
                    "severity": "HIGH",
                    "file": str(file_path),
                    "line_number": 0,
                    "description": f"Job '{job_name}' has write-all permissions",
                    "remediation": "Specify only required permissions for this job",
                })
    
    return findings


def _check_pull_request_target(file_path: Path, workflow: dict) -> List[Dict[str, Any]]:
    """Check for pull_request_target misuse"""
    findings = []
    
    on_config = workflow.get("on", {})
    if isinstance(on_config, dict) and "pull_request_target" in on_config:
        # Check if workflow checks out PR code
        jobs = workflow.get("jobs", {})
        for job_name, job_config in jobs.items():
            if isinstance(job_config, dict):
                steps = job_config.get("steps", [])
                for step in steps:
                    if isinstance(step, dict):
                        uses = step.get("uses", "")
                        if "actions/checkout" in uses:
                            with_config = step.get("with", {})
                            ref = with_config.get("ref", "")
                            if "github.event.pull_request" in str(ref):
                                findings.append({
                                    "type": "Unsafe pull_request_target",
                                    "severity": "CRITICAL",
                                    "file": str(file_path),
                                    "line_number": 0,
                                    "description": "Workflow uses pull_request_target and checks out PR code, allowing code execution from forks",
                                    "remediation": "Use pull_request trigger instead or avoid checking out PR code",
                                })
    
    return findings


def _check_hardcoded_secrets(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Check for hardcoded secrets in workflow"""
    findings = []
    
    # Look for potential hardcoded secrets (not using secrets context)
    secret_patterns = [
        (r"(?i)(api[_-]?key|token|password|secret)\s*:\s*['\"]([^'\"]{20,})['\"]", "Hardcoded Secret"),
        (r"(?i)GITHUB_TOKEN\s*:\s*['\"]ghp_[A-Za-z0-9]{36}['\"]", "Hardcoded GitHub Token"),
    ]
    
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        # Skip lines that properly use secrets
        if "secrets." in line or "${{ secrets." in line:
            continue
        
        for pattern, secret_type in secret_patterns:
            if re.search(pattern, line):
                findings.append({
                    "type": secret_type,
                    "severity": "CRITICAL",
                    "file": str(file_path),
                    "line_number": line_num,
                    "description": f"Workflow contains hardcoded secret instead of using GitHub Secrets",
                    "remediation": "Move secret to GitHub Secrets and reference with ${{ secrets.SECRET_NAME }}",
                })
    
    return findings


def _check_unpinned_actions(file_path: Path, content: str) -> List[Dict[str, Any]]:
    """Check for unpinned third-party actions"""
    findings = []
    
    lines = content.splitlines()
    for line_num, line in enumerate(lines, 1):
        # Match action usage
        match = re.search(r"uses:\s*([^@\s]+)@([^\s]+)", line)
        if match:
            action_name, version = match.groups()
            
            # Skip official GitHub actions
            if action_name.startswith("actions/"):
                continue
            
            # Check if version is a branch name (not a commit SHA or tag)
            if version in ["main", "master", "develop", "dev"]:
                findings.append({
                    "type": "Unpinned Action",
                    "severity": "MEDIUM",
                    "file": str(file_path),
                    "line_number": line_num,
                    "description": f"Action '{action_name}' is pinned to branch '{version}' instead of commit SHA",
                    "remediation": "Pin to specific commit SHA for supply chain security",
                })
    
    return findings
