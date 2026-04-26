"""
Intelligent Commit Splitter
Analyzes large commits and splits them into logical, readable chunks
"""

import subprocess
import re
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class FileChange:
    """Represents a file change"""
    path: str
    status: str  # A=added, M=modified, D=deleted
    additions: int
    deletions: int
    diff: str


@dataclass
class CommitGroup:
    """Represents a logical group of changes"""
    name: str
    description: str
    files: List[FileChange]
    priority: int  # Lower = commit first


class CommitSplitter:
    """Intelligently split large commits into logical chunks"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
    
    def analyze_staged_changes(self) -> List[FileChange]:
        """Get all staged changes"""
        result = subprocess.run(
            ["git", "diff", "--cached", "--numstat"],
            cwd=self.repo_path,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=30
        )
        
        if result.returncode != 0:
            return []
        
        changes = []
        for line in result.stdout.strip().split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) < 3:
                continue
            
            additions = int(parts[0]) if parts[0] != "-" else 0
            deletions = int(parts[1]) if parts[1] != "-" else 0
            file_path = parts[2]
            
            # Get diff for this file
            diff_result = subprocess.run(
                ["git", "diff", "--cached", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            
            # Determine status
            status_result = subprocess.run(
                ["git", "status", "--porcelain", file_path],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            
            status = "M"
            if status_result.stdout:
                status_code = status_result.stdout[0]
                if status_code == "A":
                    status = "A"
                elif status_code == "D":
                    status = "D"
            
            changes.append(FileChange(
                path=file_path,
                status=status,
                additions=additions,
                deletions=deletions,
                diff=diff_result.stdout
            ))
        
        return changes
    
    def categorize_changes(self, changes: List[FileChange]) -> List[CommitGroup]:
        """Categorize changes into logical groups"""
        groups = []
        
        # Group by category
        config_files = []
        test_files = []
        doc_files = []
        frontend_files = []
        backend_files = []
        database_files = []
        ci_cd_files = []
        dependency_files = []
        feature_files = defaultdict(list)
        
        for change in changes:
            path = change.path.lower()
            
            # Configuration files
            if any(cfg in path for cfg in [".env", "config", ".yml", ".yaml", ".json", ".toml", ".ini"]):
                if "package.json" in path or "requirements.txt" in path or "pyproject.toml" in path:
                    dependency_files.append(change)
                elif ".github/workflows" in path or "ci" in path or "cd" in path:
                    ci_cd_files.append(change)
                else:
                    config_files.append(change)
            
            # Test files
            elif any(test in path for test in ["test_", "_test.", "spec.", ".test.", "__tests__", "tests/"]):
                test_files.append(change)
            
            # Documentation
            elif any(doc in path for doc in [".md", "readme", "docs/", "documentation"]):
                doc_files.append(change)
            
            # Database
            elif any(db in path for db in ["migration", "schema", "models/", "entities/"]):
                database_files.append(change)
            
            # Frontend
            elif any(fe in path for fe in [".tsx", ".jsx", ".vue", ".svelte", "components/", "pages/", "app/"]):
                # Try to group by feature
                feature = self._extract_feature_name(change.path)
                if feature:
                    feature_files[f"frontend_{feature}"].append(change)
                else:
                    frontend_files.append(change)
            
            # Backend
            elif any(be in path for be in [".py", ".go", ".java", ".rs", "api/", "server/", "backend/"]):
                feature = self._extract_feature_name(change.path)
                if feature:
                    feature_files[f"backend_{feature}"].append(change)
                else:
                    backend_files.append(change)
            
            else:
                # Try to group by directory
                feature = self._extract_feature_name(change.path)
                if feature:
                    feature_files[feature].append(change)
        
        # Create commit groups with priorities
        if dependency_files:
            groups.append(CommitGroup(
                name="chore: Update dependencies",
                description="Update project dependencies and package files",
                files=dependency_files,
                priority=1
            ))
        
        if config_files:
            groups.append(CommitGroup(
                name="chore: Update configuration",
                description="Update configuration files",
                files=config_files,
                priority=2
            ))
        
        if database_files:
            groups.append(CommitGroup(
                name="feat: Database schema changes",
                description="Update database schema and migrations",
                files=database_files,
                priority=3
            ))
        
        if backend_files:
            groups.append(CommitGroup(
                name="feat: Backend implementation",
                description="Implement backend logic and API endpoints",
                files=backend_files,
                priority=4
            ))
        
        if frontend_files:
            groups.append(CommitGroup(
                name="feat: Frontend implementation",
                description="Implement frontend components and UI",
                files=frontend_files,
                priority=5
            ))
        
        # Feature-specific groups
        for feature_name, feature_changes in feature_files.items():
            groups.append(CommitGroup(
                name=f"feat: {feature_name.replace('_', ' ').title()}",
                description=f"Implement {feature_name.replace('_', ' ')} feature",
                files=feature_changes,
                priority=6
            ))
        
        if test_files:
            groups.append(CommitGroup(
                name="test: Add tests",
                description="Add test coverage for new features",
                files=test_files,
                priority=7
            ))
        
        if ci_cd_files:
            groups.append(CommitGroup(
                name="ci: Update CI/CD pipeline",
                description="Update continuous integration and deployment configuration",
                files=ci_cd_files,
                priority=8
            ))
        
        if doc_files:
            groups.append(CommitGroup(
                name="docs: Update documentation",
                description="Update project documentation",
                files=doc_files,
                priority=9
            ))
        
        # Sort by priority
        groups.sort(key=lambda g: g.priority)
        
        return groups
    
    def _extract_feature_name(self, file_path: str) -> str:
        """Extract feature name from file path"""
        path = Path(file_path)
        
        # Try to get feature from directory name
        parts = path.parts
        
        # Skip common directories
        skip_dirs = {"src", "lib", "app", "components", "pages", "api", "server", "client", "frontend", "backend"}
        
        for part in parts:
            if part not in skip_dirs and not part.startswith("."):
                # Clean up the name
                feature = re.sub(r"[_-]", " ", part)
                feature = re.sub(r"\.(py|js|ts|tsx|jsx)$", "", feature)
                return feature.lower()
        
        return ""
    
    def create_commits(self, groups: List[CommitGroup], dry_run: bool = False) -> List[str]:
        """Create individual commits for each group"""
        commit_shas = []
        
        for group in groups:
            if not group.files:
                continue
            
            print(f"\n📝 Creating commit: {group.name}")
            print(f"   Files: {len(group.files)}")
            
            if dry_run:
                print(f"   [DRY RUN] Would commit:")
                for f in group.files:
                    print(f"     - {f.path}")
                continue
            
            # Stage only these files
            for file_change in group.files:
                subprocess.run(
                    ["git", "add", file_change.path],
                    cwd=self.repo_path,
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30
                )
            
            # Create commit
            commit_message = f"{group.name}\n\n{group.description}\n\nFiles changed: {len(group.files)}"
            
            result = subprocess.run(
                ["git", "commit", "-m", commit_message],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
            
            if result.returncode == 0:
                # Get commit SHA
                sha_result = subprocess.run(
                    ["git", "rev-parse", "HEAD"],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=30
                )
                commit_sha = sha_result.stdout.strip()
                commit_shas.append(commit_sha)
                print(f"   ✅ Committed: {commit_sha[:7]}")
            else:
                print(f"   ❌ Failed: {result.stderr}")
        
        return commit_shas
    
    def split_current_commit(self, dry_run: bool = False) -> Dict:
        """Split currently staged changes into multiple commits"""
        print("🔍 Analyzing staged changes...")
        
        changes = self.analyze_staged_changes()
        
        if not changes:
            return {
                "success": False,
                "error": "No staged changes found",
                "groups": 0,
                "commits": []
            }
        
        print(f"📊 Found {len(changes)} changed files")
        
        # Categorize
        groups = self.categorize_changes(changes)
        
        print(f"📦 Organized into {len(groups)} logical commits:")
        for i, group in enumerate(groups, 1):
            print(f"   {i}. {group.name} ({len(group.files)} files)")
        
        if not dry_run:
            # Unstage all first
            subprocess.run(
                ["git", "reset", "HEAD"],
                cwd=self.repo_path,
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=30
            )
        
        # Create commits
        commit_shas = self.create_commits(groups, dry_run)
        
        return {
            "success": True,
            "groups": len(groups),
            "commits": commit_shas,
            "dry_run": dry_run
        }


def split_commits(repo_path: str = ".", dry_run: bool = False) -> Dict:
    """
    Split large staged commits into logical chunks
    
    Args:
        repo_path: Path to git repository
        dry_run: Preview without creating commits
    
    Returns:
        Dictionary with split results
    """
    splitter = CommitSplitter(repo_path)
    return splitter.split_current_commit(dry_run)
