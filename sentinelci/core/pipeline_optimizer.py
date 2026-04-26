"""
Pipeline optimization based on commit analysis
"""

import re
from typing import Dict, List, Set
from dataclasses import dataclass


@dataclass
class PipelineOptimization:
    """Optimization recommendations for CI/CD pipeline"""
    skip_tests: List[str]
    run_tests: List[str]
    skip_builds: List[str]
    run_builds: List[str]
    parallel_jobs: List[List[str]]
    cache_keys: List[str]
    estimated_time_saved: int  # seconds


class PipelineOptimizer:
    """Analyzes commits and suggests pipeline optimizations"""
    
    def __init__(self):
        self.commit_patterns = {
            "docs": r"^(docs|documentation|readme|md):",
            "tests": r"^(test|tests|spec):",
            "deps": r"^(deps|dependencies|chore\(deps\)):",
            "ci": r"^(ci|pipeline|workflow):",
            "frontend": r"^(feat|fix|refactor)\((ui|frontend|components|styles)\):",
            "backend": r"^(feat|fix|refactor)\((api|backend|server|database)\):",
            "config": r"^(chore|config):",
        }
    
    def analyze_commit(self, commit_message: str, changed_files: List[str]) -> Dict[str, any]:
        """Analyze a single commit to determine its type and impact"""
        commit_type = self._detect_commit_type(commit_message)
        file_categories = self._categorize_files(changed_files)
        
        return {
            "type": commit_type,
            "categories": file_categories,
            "is_docs_only": file_categories == {"docs"},
            "is_tests_only": file_categories == {"tests"},
            "is_config_only": file_categories == {"config"},
            "has_frontend": "frontend" in file_categories,
            "has_backend": "backend" in file_categories,
            "has_dependencies": "dependencies" in file_categories,
        }
    
    def _detect_commit_type(self, message: str) -> str:
        """Detect commit type from conventional commit message"""
        for commit_type, pattern in self.commit_patterns.items():
            if re.match(pattern, message, re.IGNORECASE):
                return commit_type
        return "general"
    
    def _categorize_files(self, files: List[str]) -> Set[str]:
        """Categorize changed files"""
        categories = set()
        
        for file_path in files:
            # Documentation
            if any(ext in file_path.lower() for ext in [".md", "readme", "docs/"]):
                categories.add("docs")
            
            # Tests
            elif any(pattern in file_path.lower() for pattern in ["test", "spec", "__tests__"]):
                categories.add("tests")
            
            # Dependencies
            elif any(file in file_path.lower() for file in [
                "package.json", "requirements.txt", "pyproject.toml", 
                "go.mod", "cargo.toml", "pom.xml"
            ]):
                categories.add("dependencies")
            
            # CI/CD
            elif ".github/workflows" in file_path or ".gitlab-ci" in file_path:
                categories.add("ci")
            
            # Frontend
            elif any(ext in file_path for ext in [
                ".jsx", ".tsx", ".vue", ".svelte", ".css", ".scss", ".sass"
            ]) or "frontend/" in file_path or "ui/" in file_path:
                categories.add("frontend")
            
            # Backend
            elif any(pattern in file_path for pattern in [
                "backend/", "api/", "server/", "services/"
            ]) or any(ext in file_path for ext in [".go", ".rs", ".java"]):
                categories.add("backend")
            
            # Config
            elif any(ext in file_path for ext in [
                ".yml", ".yaml", ".toml", ".ini", ".env", ".config"
            ]):
                categories.add("config")
            
            # Database
            elif any(pattern in file_path for pattern in [
                "migrations/", "schema/", ".sql"
            ]):
                categories.add("database")
        
        return categories
    
    def optimize_pipeline(self, commits: List[Dict]) -> PipelineOptimization:
        """Generate pipeline optimization based on commit analysis"""
        skip_tests = []
        run_tests = []
        skip_builds = []
        run_builds = []
        parallel_jobs = []
        cache_keys = []
        time_saved = 0
        
        # Analyze all commits
        has_docs_only = all(c.get("is_docs_only") for c in commits)
        has_tests_only = all(c.get("is_tests_only") for c in commits)
        has_frontend = any(c.get("has_frontend") for c in commits)
        has_backend = any(c.get("has_backend") for c in commits)
        has_dependencies = any(c.get("has_dependencies") for c in commits)
        
        # Documentation-only commits
        if has_docs_only:
            skip_tests = ["unit", "integration", "e2e"]
            skip_builds = ["frontend", "backend", "docker"]
            time_saved += 300  # 5 minutes
        
        # Test-only commits
        elif has_tests_only:
            skip_builds = ["docker", "production"]
            run_tests = ["unit", "integration"]
            time_saved += 120  # 2 minutes
        
        # Selective testing based on changes
        else:
            if not has_frontend:
                skip_tests.append("frontend-tests")
                skip_builds.append("frontend-build")
                time_saved += 60
            else:
                run_tests.append("frontend-tests")
                run_builds.append("frontend-build")
            
            if not has_backend:
                skip_tests.append("backend-tests")
                skip_builds.append("backend-build")
                time_saved += 90
            else:
                run_tests.append("backend-tests")
                run_builds.append("backend-build")
        
        # Parallel execution opportunities
        if has_frontend and has_backend:
            parallel_jobs.append(["frontend-build", "backend-build"])
            parallel_jobs.append(["frontend-tests", "backend-tests"])
            time_saved += 60  # Parallelization saves time
        
        # Cache optimization
        if has_dependencies:
            cache_keys.append("dependencies-${{ hashFiles('**/package-lock.json', '**/requirements.txt') }}")
        else:
            cache_keys.append("dependencies-stable")
            time_saved += 30  # Faster cache restore
        
        return PipelineOptimization(
            skip_tests=skip_tests,
            run_tests=run_tests,
            skip_builds=skip_builds,
            run_builds=run_builds,
            parallel_jobs=parallel_jobs,
            cache_keys=cache_keys,
            estimated_time_saved=time_saved
        )
    
    def generate_optimized_workflow(self, optimization: PipelineOptimization) -> str:
        """Generate optimized GitHub Actions workflow YAML"""
        workflow = """name: Optimized CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  analyze:
    name: Analyze Changes
    runs-on: ubuntu-latest
    outputs:
      skip_tests: ${{ steps.analyze.outputs.skip_tests }}
      run_tests: ${{ steps.analyze.outputs.run_tests }}
      skip_builds: ${{ steps.analyze.outputs.skip_builds }}
      run_builds: ${{ steps.analyze.outputs.run_builds }}
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0
      
      - name: Analyze commit changes
        id: analyze
        run: |
          # Get changed files
          CHANGED_FILES=$(git diff --name-only ${{ github.event.before }} ${{ github.sha }})
          
          # Check if only docs changed
          if echo "$CHANGED_FILES" | grep -qvE '\\.(md|txt|rst)$'; then
            echo "skip_tests=false" >> $GITHUB_OUTPUT
          else
            echo "skip_tests=true" >> $GITHUB_OUTPUT
          fi
"""
        
        # Add conditional jobs based on optimization
        if optimization.run_builds:
            for build in optimization.run_builds:
                workflow += f"""
  {build}:
    name: {build.replace('-', ' ').title()}
    runs-on: ubuntu-latest
    needs: analyze
    if: needs.analyze.outputs.run_builds contains '{build}'
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup cache
        uses: actions/cache@v4
        with:
          path: |
            ~/.cache
            node_modules
          key: {optimization.cache_keys[0] if optimization.cache_keys else 'cache-${{ runner.os }}'}
      
      - name: Build {build}
        run: |
          echo "Building {build}..."
          # Add your build commands here
"""
        
        # Add parallel jobs
        if optimization.parallel_jobs:
            workflow += """
  parallel-execution:
    name: Parallel Jobs
    runs-on: ubuntu-latest
    needs: analyze
    strategy:
      matrix:
        job: """
            workflow += str(optimization.parallel_jobs[0])
            workflow += """
    steps:
      - uses: actions/checkout@v4
      - name: Run ${{ matrix.job }}
        run: echo "Running ${{ matrix.job }}"
"""
        
        return workflow
    
    def generate_optimization_report(self, optimization: PipelineOptimization) -> str:
        """Generate human-readable optimization report"""
        report = "🚀 Pipeline Optimization Report\n\n"
        
        if optimization.skip_tests:
            report += f"⏭️  Skip Tests: {', '.join(optimization.skip_tests)}\n"
        
        if optimization.run_tests:
            report += f"✅ Run Tests: {', '.join(optimization.run_tests)}\n"
        
        if optimization.skip_builds:
            report += f"⏭️  Skip Builds: {', '.join(optimization.skip_builds)}\n"
        
        if optimization.run_builds:
            report += f"🔨 Run Builds: {', '.join(optimization.run_builds)}\n"
        
        if optimization.parallel_jobs:
            report += f"\n⚡ Parallel Execution:\n"
            for i, jobs in enumerate(optimization.parallel_jobs, 1):
                report += f"   Group {i}: {', '.join(jobs)}\n"
        
        if optimization.cache_keys:
            report += f"\n💾 Cache Strategy: {optimization.cache_keys[0]}\n"
        
        report += f"\n⏱️  Estimated Time Saved: {optimization.estimated_time_saved}s "
        report += f"({optimization.estimated_time_saved // 60}m {optimization.estimated_time_saved % 60}s)\n"
        
        return report
