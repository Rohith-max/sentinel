"""
End-to-end pipeline error detection and automated fixing
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re

from sentinelci.output.clean import (
    console, print_header, print_success, print_error,
    print_warning, print_info, print_step, print_table, confirm
)


class ErrorCategory(Enum):
    """Pipeline error categories"""
    WORKFLOW_PERMISSIONS = "workflow_permissions"
    SECRET_EXPOSURE = "secret_exposure"
    DEPENDENCY_VULNERABILITY = "dependency_vulnerability"
    INSECURE_ACTION = "insecure_action"
    MISSING_SECURITY_CHECKS = "missing_security_checks"
    BRANCH_PROTECTION = "branch_protection"
    CODE_INJECTION = "code_injection"
    SUPPLY_CHAIN = "supply_chain"


@dataclass
class PipelineError:
    """Represents a detected pipeline error"""
    category: ErrorCategory
    severity: str
    file_path: str
    line_number: Optional[int]
    description: str
    current_value: str
    recommended_fix: str
    auto_fixable: bool
    fix_confidence: float  # 0.0 to 1.0


@dataclass
class FixResult:
    """Result of applying a fix"""
    success: bool
    error_id: str
    file_path: str
    changes_made: str
    error_message: Optional[str] = None


class PipelineErrorDetector:
    """Detects security errors in CI/CD pipelines"""
    
    def __init__(self):
        self.errors: List[PipelineError] = []
    
    def analyze_workflow(self, file_path: str, content: str) -> List[PipelineError]:
        """Analyze GitHub Actions workflow for errors"""
        errors = []
        
        # Check for excessive permissions
        errors.extend(self._check_permissions(file_path, content))
        
        # Check for secret exposure
        errors.extend(self._check_secrets(file_path, content))
        
        # Check for insecure actions
        errors.extend(self._check_actions(file_path, content))
        
        # Check for code injection vulnerabilities
        errors.extend(self._check_code_injection(file_path, content))
        
        # Check for missing security checks
        errors.extend(self._check_security_checks(file_path, content))
        
        return errors
    
    def _check_permissions(self, file_path: str, content: str) -> List[PipelineError]:
        """Check for excessive workflow permissions"""
        errors = []
        lines = content.split('\n')
        
        # Check for write-all or overly broad permissions
        for i, line in enumerate(lines, 1):
            if 'permissions:' in line:
                # Check next few lines for write-all
                for j in range(i, min(i + 10, len(lines))):
                    if 'write-all' in lines[j]:
                        errors.append(PipelineError(
                            category=ErrorCategory.WORKFLOW_PERMISSIONS,
                            severity="CRITICAL",
                            file_path=file_path,
                            line_number=j + 1,
                            description="Workflow has write-all permissions",
                            current_value="write-all",
                            recommended_fix="Use minimal required permissions (contents: read, pull-requests: write)",
                            auto_fixable=True,
                            fix_confidence=0.95
                        ))
                        break
        
        # Check if permissions block is missing entirely
        if 'permissions:' not in content and 'on:' in content:
            errors.append(PipelineError(
                category=ErrorCategory.WORKFLOW_PERMISSIONS,
                severity="HIGH",
                file_path=file_path,
                line_number=None,
                description="Workflow missing permissions block (defaults to write-all)",
                current_value="<missing>",
                recommended_fix="Add restrictive permissions block",
                auto_fixable=True,
                fix_confidence=0.90
            ))
        
        return errors
    
    def _check_secrets(self, file_path: str, content: str) -> List[PipelineError]:
        """Check for exposed secrets"""
        errors = []
        lines = content.split('\n')
        
        # Patterns that indicate potential secret exposure
        secret_patterns = [
            (r'echo\s+\$\{\{\s*secrets\.', 'Secret printed to logs'),
            (r'curl.*\$\{\{\s*secrets\.', 'Secret passed in URL'),
            (r'--token\s+\$\{\{\s*secrets\.', 'Secret in command line'),
        ]
        
        for i, line in enumerate(lines, 1):
            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    errors.append(PipelineError(
                        category=ErrorCategory.SECRET_EXPOSURE,
                        severity="CRITICAL",
                        file_path=file_path,
                        line_number=i,
                        description=description,
                        current_value=line.strip(),
                        recommended_fix="Use environment variables or secure secret handling",
                        auto_fixable=False,
                        fix_confidence=0.70
                    ))
        
        return errors
    
    def _check_actions(self, file_path: str, content: str) -> List[PipelineError]:
        """Check for insecure or unpinned actions"""
        errors = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for unpinned actions (using @main, @master, @latest)
            if 'uses:' in line:
                if re.search(r'@(main|master|latest|HEAD)', line):
                    action_name = line.split('uses:')[1].strip()
                    errors.append(PipelineError(
                        category=ErrorCategory.INSECURE_ACTION,
                        severity="HIGH",
                        file_path=file_path,
                        line_number=i,
                        description=f"Action not pinned to specific commit: {action_name}",
                        current_value=action_name,
                        recommended_fix="Pin to specific commit SHA",
                        auto_fixable=False,
                        fix_confidence=0.60
                    ))
        
        return errors
    
    def _check_code_injection(self, file_path: str, content: str) -> List[PipelineError]:
        """Check for code injection vulnerabilities"""
        errors = []
        lines = content.split('\n')
        
        # Check for unsafe use of github context in run commands
        injection_patterns = [
            r'\$\{\{\s*github\.event\.issue\.title\s*\}\}',
            r'\$\{\{\s*github\.event\.pull_request\.title\s*\}\}',
            r'\$\{\{\s*github\.event\.comment\.body\s*\}\}',
            r'\$\{\{\s*github\.head_ref\s*\}\}',
        ]
        
        for i, line in enumerate(lines, 1):
            if 'run:' in line or ('|' in line and i > 0 and 'run:' in lines[i-2]):
                for pattern in injection_patterns:
                    if re.search(pattern, line):
                        errors.append(PipelineError(
                            category=ErrorCategory.CODE_INJECTION,
                            severity="CRITICAL",
                            file_path=file_path,
                            line_number=i,
                            description="Potential code injection from untrusted input",
                            current_value=line.strip(),
                            recommended_fix="Use environment variables with proper escaping",
                            auto_fixable=True,
                            fix_confidence=0.85
                        ))
        
        return errors
    
    def _check_security_checks(self, file_path: str, content: str) -> List[PipelineError]:
        """Check for missing security checks"""
        errors = []
        
        # Check if workflow has any security scanning
        has_security_scan = any([
            'security' in content.lower(),
            'codeql' in content.lower(),
            'snyk' in content.lower(),
            'trivy' in content.lower(),
        ])
        
        if not has_security_scan and 'on: push' in content:
            errors.append(PipelineError(
                category=ErrorCategory.MISSING_SECURITY_CHECKS,
                severity="MEDIUM",
                file_path=file_path,
                line_number=None,
                description="Workflow missing security scanning step",
                current_value="<missing>",
                recommended_fix="Add security scanning (CodeQL, Snyk, or similar)",
                auto_fixable=False,
                fix_confidence=0.50
            ))
        
        return errors


class PipelineFixer:
    """Automatically fixes detected pipeline errors"""
    
    def __init__(self):
        self.fixes_applied: List[FixResult] = []
    
    def fix_permissions(self, content: str, error: PipelineError) -> Tuple[str, bool]:
        """Fix workflow permissions"""
        lines = content.split('\n')
        
        if error.current_value == "write-all":
            # Replace write-all with minimal permissions
            for i, line in enumerate(lines):
                if 'write-all' in line:
                    indent = len(line) - len(line.lstrip())
                    lines[i] = ' ' * indent + 'contents: read'
                    # Add pull-requests: write if needed
                    if i + 1 < len(lines):
                        lines.insert(i + 1, ' ' * indent + 'pull-requests: write')
                    return '\n'.join(lines), True
        
        elif error.current_value == "<missing>":
            # Add permissions block after 'on:' section
            for i, line in enumerate(lines):
                if line.strip().startswith('on:'):
                    # Find end of 'on:' section
                    j = i + 1
                    while j < len(lines) and (lines[j].startswith('  ') or not lines[j].strip()):
                        j += 1
                    
                    # Insert permissions block
                    permissions_block = [
                        '',
                        'permissions:',
                        '  contents: read',
                        '  pull-requests: write',
                        ''
                    ]
                    lines = lines[:j] + permissions_block + lines[j:]
                    return '\n'.join(lines), True
        
        return content, False
    
    def fix_code_injection(self, content: str, error: PipelineError) -> Tuple[str, bool]:
        """Fix code injection vulnerabilities"""
        lines = content.split('\n')
        
        if error.line_number:
            line_idx = error.line_number - 1
            if line_idx < len(lines):
                line = lines[line_idx]
                
                # Replace direct context usage with environment variable
                # Example: ${{ github.event.issue.title }} -> $ISSUE_TITLE
                replacements = {
                    r'\$\{\{\s*github\.event\.issue\.title\s*\}\}': '$ISSUE_TITLE',
                    r'\$\{\{\s*github\.event\.pull_request\.title\s*\}\}': '$PR_TITLE',
                    r'\$\{\{\s*github\.event\.comment\.body\s*\}\}': '$COMMENT_BODY',
                    r'\$\{\{\s*github\.head_ref\s*\}\}': '$HEAD_REF',
                }
                
                modified = False
                for pattern, replacement in replacements.items():
                    if re.search(pattern, line):
                        lines[line_idx] = re.sub(pattern, replacement, line)
                        modified = True
                        
                        # Add env block before the run command
                        # Find the 'run:' line
                        for k in range(max(0, line_idx - 5), line_idx):
                            if 'run:' in lines[k]:
                                indent = len(lines[k]) - len(lines[k].lstrip())
                                env_lines = [
                                    ' ' * indent + 'env:',
                                    ' ' * (indent + 2) + f'{replacement.strip("$")}: ${{{{ github.event.issue.title }}}}'
                                ]
                                lines = lines[:k] + env_lines + lines[k:]
                                break
                
                if modified:
                    return '\n'.join(lines), True
        
        return content, False
    
    def apply_fix(self, content: str, error: PipelineError) -> FixResult:
        """Apply fix for a specific error"""
        if not error.auto_fixable:
            return FixResult(
                success=False,
                error_id=f"{error.category.value}_{error.line_number}",
                file_path=error.file_path,
                changes_made="",
                error_message="Error not auto-fixable"
            )
        
        fixed_content = content
        success = False
        
        if error.category == ErrorCategory.WORKFLOW_PERMISSIONS:
            fixed_content, success = self.fix_permissions(content, error)
        elif error.category == ErrorCategory.CODE_INJECTION:
            fixed_content, success = self.fix_code_injection(content, error)
        
        if success:
            return FixResult(
                success=True,
                error_id=f"{error.category.value}_{error.line_number}",
                file_path=error.file_path,
                changes_made=error.recommended_fix,
                error_message=None
            )
        else:
            return FixResult(
                success=False,
                error_id=f"{error.category.value}_{error.line_number}",
                file_path=error.file_path,
                changes_made="",
                error_message="Fix could not be applied"
            )


def analyze_and_fix_pipeline(
    file_path: str,
    content: str,
    auto_fix: bool = False,
    interactive: bool = True
) -> Tuple[List[PipelineError], List[FixResult], str]:
    """
    Analyze pipeline file and optionally fix errors
    
    Returns:
        (errors_found, fixes_applied, fixed_content)
    """
    print_header("Pipeline Security Analysis", f"Analyzing: {file_path}")
    
    # Detect errors
    detector = PipelineErrorDetector()
    errors = detector.analyze_workflow(file_path, content)
    
    if not errors:
        print_success("No pipeline security issues detected")
        return [], [], content
    
    # Display errors
    print_warning(f"Found {len(errors)} pipeline security issue(s)")
    console.print()
    
    # Create error table
    rows = []
    for i, error in enumerate(errors, 1):
        severity_color = {
            "CRITICAL": "[red]CRITICAL[/red]",
            "HIGH": "[yellow]HIGH[/yellow]",
            "MEDIUM": "[blue]MEDIUM[/blue]",
            "LOW": "[dim]LOW[/dim]",
        }.get(error.severity, error.severity)
        
        fixable = "[green]Yes[/green]" if error.auto_fixable else "[dim]No[/dim]"
        
        rows.append([
            str(i),
            severity_color,
            error.category.value.replace('_', ' ').title(),
            error.description[:50] + "..." if len(error.description) > 50 else error.description,
            fixable
        ])
    
    print_table(
        "Detected Issues",
        ["#", "Severity", "Category", "Description", "Auto-Fix"],
        rows
    )
    
    # Apply fixes
    fixes_applied = []
    fixed_content = content
    
    if auto_fix or (interactive and confirm("Apply automatic fixes?", default=True)):
        print_header("Applying Fixes")
        
        fixer = PipelineFixer()
        for i, error in enumerate(errors, 1):
            if error.auto_fixable:
                print_step(i, len([e for e in errors if e.auto_fixable]), f"Fixing: {error.description}")
                
                result = fixer.apply_fix(fixed_content, error)
                fixes_applied.append(result)
                
                if result.success:
                    fixed_content = result.changes_made
                    print_success(f"Applied: {error.recommended_fix}")
                else:
                    print_error(f"Failed: {result.error_message}")
        
        console.print()
        print_success(f"Applied {len([f for f in fixes_applied if f.success])} fix(es)")
    
    return errors, fixes_applied, fixed_content
