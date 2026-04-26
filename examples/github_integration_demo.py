"""
Demo script for GitHub integration features
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sentinelci.github_auth import GitHubAuth, GitHubAuthError
from sentinelci.github_repos import GitHubRepoManager
from sentinelci.github_security import GitHubSecurityAnalyzer
from sentinelci.output.github_dashboard import render_github_dashboard


def demo_authentication():
    """Demo GitHub authentication"""
    print("\n" + "="*60)
    print("DEMO 1: GitHub Authentication")
    print("="*60 + "\n")

    auth = GitHubAuth()
    
    try:
        status = auth.check_auth_status()
        
        if status["authenticated"]:
            user = status["user"]
            orgs = status["organizations"]
            
            print(f"SUCCESS: Authenticated as: {user['login']}")
            print(f"   Name: {user.get('name', 'N/A')}")
            print(f"   Email: {user.get('email', 'N/A')}")
            print(f"   Public Repos: {user.get('public_repos', 0)}")
            print(f"   Followers: {user.get('followers', 0)}")
            
            if orgs:
                print(f"\nOrganizations ({len(orgs)}):")
                for org in orgs[:5]:
                    print(f"   • {org['login']}")
            
            return True
        else:
            print(f"FAILED: Not authenticated: {status['error']}")
            print("\nTo setup authentication, run:")
            print("  sci github setup")
            return False
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def demo_repository_listing():
    """Demo repository listing and filtering"""
    print("\n" + "="*60)
    print("DEMO 2: Repository Listing")
    print("="*60 + "\n")

    try:
        manager = GitHubRepoManager()
        
        print("LOADING: Fetching repositories...")
        repos = manager.fetch_all_repositories()
        
        print(f"SUCCESS: Found {len(repos)} repositories\n")
        
        print("Sample repositories:")
        for repo in repos[:5]:
            print(f"\n  REPO: {repo['full_name']}")
            print(f"     Visibility: {repo['visibility']}")
            print(f"     Language: {repo.get('language', 'N/A')}")
            print(f"     Stars: {repo['stars']}")
            print(f"     Open PRs: {repo['open_prs']}")
            print(f"     Last updated: {repo['last_updated'][:10]}")
        
        if len(repos) > 5:
            print(f"\n  ... and {len(repos) - 5} more repositories")
        
        print("\n\nFilter examples:")
        
        private_repos = manager.filter_repositories(repos, visibility="private")
        print(f"  • Private repositories: {len(private_repos)}")
        
        python_repos = manager.filter_repositories(repos, language="Python")
        print(f"  • Python repositories: {len(python_repos)}")
        
        return repos
        
    except GitHubAuthError as e:
        print(f"ERROR: {str(e)}")
        return []
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return []


def demo_security_analysis(repo_full_name: str):
    """Demo security analysis for a repository"""
    print("\n" + "="*60)
    print("DEMO 3: Security Analysis")
    print("="*60 + "\n")

    try:
        analyzer = GitHubSecurityAnalyzer()
        
        print(f"ANALYZING: repository: {repo_full_name}\n")
        
        analysis = analyzer.analyze_repository(repo_full_name)
        risk_score = analyzer.calculate_risk_score(analysis)
        
        render_github_dashboard(analysis, risk_score)
        
        return True
        
    except GitHubAuthError as e:
        print(f"ERROR: {str(e)}")
        return False
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return False


def main():
    """Run all demos"""
    print("\n" + "="*60)
    print("GitHub Integration Demo")
    print("="*60)
    
    authenticated = demo_authentication()
    
    if not authenticated:
        print("\nWARNING: Authentication required to continue demos")
        print("Run: sci github setup")
        return
    
    repos = demo_repository_listing()
    
    if repos:
        print("\n\nWould you like to analyze a repository? (y/n): ", end="")
        try:
            choice = input().strip().lower()
            
            if choice == 'y':
                print("\nEnter repository full name (owner/repo): ", end="")
                repo_name = input().strip()
                
                if repo_name:
                    demo_security_analysis(repo_name)
                else:
                    print("Using first repository from list...")
                    demo_security_analysis(repos[0]['full_name'])
        except KeyboardInterrupt:
            print("\n\nCANCELLED: Demo cancelled")
    
    print("\n" + "="*60)
    print("Demo Complete!")
    print("="*60)
    print("\nNext steps:")
    print("  • sci github auth          - Check authentication status")
    print("  • sci github repos         - List and select repositories")
    print("  • sci github analyze REPO  - Analyze repository security")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
