"""
GitHub repository fetching and selection
"""

import sys
from typing import List, Dict, Any, Optional
from datetime import datetime
import requests

from sentinelci.github_auth import GitHubAuth, GitHubAuthError


class GitHubRepoManager:
    """Manages GitHub repository operations"""

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

    def fetch_repositories_paginated(self, page: int = 1, per_page: int = 6, include_orgs: bool = True) -> tuple[List[Dict[str, Any]], bool]:
        """
        Fetch repositories page by page for faster loading

        Args:
            page: Page number (1-indexed)
            per_page: Number of repos per page
            include_orgs: Include organization repositories

        Returns:
            Tuple of (list of repository dicts, has_more_pages)
        """
        self.auth.ensure_authenticated()

        try:
            response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self._get_headers(),
                params={
                    "per_page": per_page,
                    "page": page,
                    "sort": "updated",
                    "affiliation": "owner,collaborator,organization_member" if include_orgs else "owner",
                },
                timeout=15,
            )

            if response.status_code != 200:
                raise GitHubAuthError(f"Failed to fetch repositories: {response.status_code}")

            batch = response.json()
            has_more = len(batch) == per_page
            
            return self._enrich_repositories(batch), has_more

        except requests.exceptions.RequestException as e:
            raise GitHubAuthError(f"Network error: {str(e)}")

    def fetch_all_repositories(self, include_orgs: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch all repositories accessible by authenticated user

        Args:
            include_orgs: Include organization repositories

        Returns:
            List of repository dicts with metadata
        """
        self.auth.ensure_authenticated()
        repos = []

        try:
            page = 1
            per_page = 100

            while True:
                response = requests.get(
                    f"{self.base_url}/user/repos",
                    headers=self._get_headers(),
                    params={
                        "per_page": per_page,
                        "page": page,
                        "sort": "updated",
                        "affiliation": "owner,collaborator,organization_member" if include_orgs else "owner",
                    },
                    timeout=15,
                )

                if response.status_code != 200:
                    raise GitHubAuthError(f"Failed to fetch repositories: {response.status_code}")

                batch = response.json()
                if not batch:
                    break

                repos.extend(batch)
                page += 1

                if len(batch) < per_page:
                    break

        except requests.exceptions.RequestException as e:
            raise GitHubAuthError(f"Network error: {str(e)}")

        return self._enrich_repositories(repos)

    def _enrich_repositories(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich repository data with additional metadata

        Args:
            repos: List of repository dicts from GitHub API

        Returns:
            Enriched repository list
        """
        enriched = []

        for repo in repos:
            try:
                pr_count = self._get_open_pr_count(repo["full_name"])
            except Exception:
                pr_count = 0

            enriched_repo = {
                "name": repo["name"],
                "full_name": repo["full_name"],
                "owner": repo["owner"]["login"],
                "visibility": "private" if repo["private"] else "public",
                "default_branch": repo.get("default_branch", "main"),
                "description": repo.get("description", ""),
                "last_updated": repo.get("updated_at", ""),
                "last_pushed": repo.get("pushed_at", ""),
                "open_prs": pr_count,
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "language": repo.get("language", ""),
                "url": repo["html_url"],
                "clone_url": repo["clone_url"],
                "ssh_url": repo["ssh_url"],
            }

            enriched.append(enriched_repo)

        return enriched

    def _get_open_pr_count(self, full_name: str) -> int:
        """Get count of open pull requests for a repository"""
        try:
            response = requests.get(
                f"{self.base_url}/repos/{full_name}/pulls",
                headers=self._get_headers(),
                params={"state": "open", "per_page": 1},
                timeout=5,
            )

            if response.status_code == 200:
                link_header = response.headers.get("Link", "")
                if "last" in link_header:
                    import re
                    match = re.search(r'page=(\d+)>; rel="last"', link_header)
                    if match:
                        return int(match.group(1))
                return len(response.json())

        except Exception:
            pass

        return 0

    def select_repositories_interactive_lazy(
        self,
        multi_select: bool = False,
        search: str = None,
        visibility: str = None,
        language: str = None,
    ) -> List[Dict[str, Any]]:
        """
        Interactive repository selection with lazy loading (fetch page by page)
        Navigate with arrow keys: ← Previous, → Next, Esc to cancel

        Args:
            multi_select: Allow multiple selection
            search: Filter by name
            visibility: Filter by visibility (public/private)
            language: Filter by language

        Returns:
            List of selected repositories
        """
        try:
            import questionary
            from questionary import Choice
            from prompt_toolkit.keys import Keys
            from prompt_toolkit.key_binding import KeyBindings
        except ImportError:
            print("⚠️  questionary not installed. Install with: pip install questionary")
            return []

        current_page = 1
        per_page = 6
        
        # Create custom key bindings for arrow navigation
        bindings = KeyBindings()
        page_action = {"action": None}
        
        @bindings.add(Keys.Right)
        def _(event):
            """Navigate to next page"""
            page_action["action"] = "next"
            event.app.exit(result="__navigate__")
        
        @bindings.add(Keys.Left)
        def _(event):
            """Navigate to previous page"""
            page_action["action"] = "prev"
            event.app.exit(result="__navigate__")
        
        while True:
            # Fetch current page
            print(f"\n🔍 Loading page {current_page}...")
            repos, has_more = self.fetch_repositories_paginated(
                page=current_page,
                per_page=per_page
            )
            
            if not repos:
                print("No repositories found")
                return []
            
            # Apply filters
            if search or visibility or language:
                repos = self.filter_repositories(
                    repos,
                    search=search,
                    visibility=visibility,
                    language=language
                )
            
            if not repos:
                if has_more:
                    print("No matches on this page, loading next...")
                    current_page += 1
                    continue
                else:
                    print("No repositories match the filters")
                    return []
            
            # Clear screen and show header
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            nav_hint = []
            if current_page > 1:
                nav_hint.append("← Prev")
            if has_more:
                nav_hint.append("→ Next")
            nav_hint.append("Esc to cancel")
            
            print(f"\n📚 Repositories (Page {current_page}) - {' | '.join(nav_hint)}")
            print(f"   Showing {len(repos)} repositories\n")
            
            # Build choices for current page
            choices = []
            for repo in repos:
                last_update = self._format_date(repo["last_pushed"])
                pr_info = f" ({repo['open_prs']} PRs)" if repo['open_prs'] > 0 else ""
                
                label = (
                    f"{repo['full_name']:<50} "
                    f"[{repo['visibility']:<7}] "
                    f"{repo['default_branch']:<15} "
                    f"Updated: {last_update:<12}"
                    f"{pr_info}"
                )

                choices.append(Choice(title=label, value=repo))

            try:
                if multi_select:
                    selected = questionary.checkbox(
                        "Select repositories (Space to select, Enter to confirm):",
                        choices=choices,
                        key_bindings=bindings
                    ).ask()
                    
                    if selected == "__navigate__":
                        if page_action["action"] == "next" and has_more:
                            current_page += 1
                            continue
                        elif page_action["action"] == "prev" and current_page > 1:
                            current_page -= 1
                            continue
                    
                    if not selected:
                        return []
                    
                    # Return selected repos immediately
                    return selected if isinstance(selected, list) else []
                else:
                    selected = questionary.select(
                        "Select a repository:",
                        choices=choices,
                        key_bindings=bindings
                    ).ask()
                    
                    # Handle navigation
                    if selected == "__navigate__":
                        if page_action["action"] == "next" and has_more:
                            current_page += 1
                            continue
                        elif page_action["action"] == "prev" and current_page > 1:
                            current_page -= 1
                            continue
                    
                    if selected is None:
                        return []
                    
                    # Return selected repo immediately (stop fetching)
                    return [selected] if selected else []

            except KeyboardInterrupt:
                print("\n❌ Selection cancelled")
                return []

    def select_repositories_interactive(
        self,
        repos: List[Dict[str, Any]],
        multi_select: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Interactive repository selection using questionary with pagination

        Args:
            repos: List of repositories to choose from
            multi_select: Allow multiple selection

        Returns:
            List of selected repositories
        """
        try:
            import questionary
            from questionary import Choice
        except ImportError:
            print("⚠️  questionary not installed. Install with: pip install questionary")
            return self._fallback_selection(repos, multi_select)

        if not repos:
            print("No repositories found")
            return []

        # Pagination settings
        page_size = 6
        total_pages = (len(repos) + page_size - 1) // page_size
        current_page = 0
        
        while True:
            # Calculate page boundaries
            start_idx = current_page * page_size
            end_idx = min(start_idx + page_size, len(repos))
            page_repos = repos[start_idx:end_idx]
            
            # Clear screen and show header
            import os
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print(f"\n📚 Repositories (Page {current_page + 1}/{total_pages})")
            print(f"   Showing {start_idx + 1}-{end_idx} of {len(repos)} repositories\n")
            
            # Build choices for current page
            choices = []
            for repo in page_repos:
                last_update = self._format_date(repo["last_pushed"])
                pr_info = f" ({repo['open_prs']} PRs)" if repo['open_prs'] > 0 else ""
                
                label = (
                    f"{repo['full_name']:<50} "
                    f"[{repo['visibility']:<7}] "
                    f"{repo['default_branch']:<15} "
                    f"Updated: {last_update:<12}"
                    f"{pr_info}"
                )

                choices.append(Choice(title=label, value=repo))
            
            # Add navigation options
            nav_choices = []
            if current_page > 0:
                nav_choices.append(Choice(title="← Previous Page", value="__prev__"))
            if current_page < total_pages - 1:
                nav_choices.append(Choice(title="→ Next Page", value="__next__"))
            nav_choices.append(Choice(title="❌ Cancel", value="__cancel__"))
            
            all_choices = choices + [Choice(title="---", value="__separator__")] + nav_choices

            try:
                if multi_select:
                    selected = questionary.checkbox(
                        "Select repositories (Space to select, Enter to confirm):",
                        choices=all_choices,
                    ).ask()
                else:
                    selected = questionary.select(
                        "Select a repository:",
                        choices=all_choices,
                    ).ask()
                
                # Handle navigation
                if selected == "__prev__":
                    current_page -= 1
                    continue
                elif selected == "__next__":
                    current_page += 1
                    continue
                elif selected == "__cancel__" or selected is None:
                    return []
                elif selected == "__separator__":
                    continue
                
                # Handle multi-select navigation
                if multi_select and isinstance(selected, list):
                    # Filter out navigation items
                    actual_repos = [s for s in selected if isinstance(s, dict)]
                    nav_items = [s for s in selected if isinstance(s, str)]
                    
                    if "__prev__" in nav_items:
                        current_page -= 1
                        continue
                    elif "__next__" in nav_items:
                        current_page += 1
                        continue
                    elif "__cancel__" in nav_items:
                        return []
                    
                    return actual_repos if actual_repos else []
                
                # Single selection
                return [selected] if selected else []

            except KeyboardInterrupt:
                print("\n❌ Selection cancelled")
                return []

    def _fallback_selection(
        self,
        repos: List[Dict[str, Any]],
        multi_select: bool = False,
    ) -> List[Dict[str, Any]]:
        """Fallback selection when questionary is not available"""
        print("\n📋 Available Repositories:\n")

        for idx, repo in enumerate(repos, 1):
            last_update = self._format_date(repo["last_pushed"])
            pr_info = f" ({repo['open_prs']} PRs)" if repo['open_prs'] > 0 else ""
            
            print(
                f"{idx:3}. {repo['full_name']:<50} "
                f"[{repo['visibility']:<7}] "
                f"{repo['default_branch']:<15} "
                f"Updated: {last_update:<12}"
                f"{pr_info}"
            )

        print()

        if multi_select:
            selection = input("Enter repository numbers (comma-separated, e.g., 1,3,5): ").strip()
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(",") if x.strip()]
                return [repos[i] for i in indices if 0 <= i < len(repos)]
            except (ValueError, IndexError):
                print("❌ Invalid selection")
                return []
        else:
            selection = input("Enter repository number: ").strip()
            try:
                idx = int(selection) - 1
                if 0 <= idx < len(repos):
                    return [repos[idx]]
            except ValueError:
                pass

            print("❌ Invalid selection")
            return []

    def filter_repositories(
        self,
        repos: List[Dict[str, Any]],
        search: Optional[str] = None,
        visibility: Optional[str] = None,
        language: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Filter repositories by criteria

        Args:
            repos: List of repositories
            search: Search term for name/description
            visibility: Filter by public/private
            language: Filter by programming language

        Returns:
            Filtered repository list
        """
        filtered = repos

        if search:
            search_lower = search.lower()
            filtered = [
                r for r in filtered
                if search_lower in r["name"].lower()
                or search_lower in r.get("description", "").lower()
            ]

        if visibility:
            filtered = [r for r in filtered if r["visibility"] == visibility.lower()]

        if language:
            filtered = [
                r for r in filtered
                if r.get("language", "").lower() == language.lower()
            ]

        return filtered

    def _format_date(self, date_str: str) -> str:
        """Format ISO date string to relative time"""
        if not date_str:
            return "Unknown"

        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            now = datetime.now(date.tzinfo)
            delta = now - date

            if delta.days == 0:
                return "Today"
            elif delta.days == 1:
                return "Yesterday"
            elif delta.days < 7:
                return f"{delta.days}d ago"
            elif delta.days < 30:
                return f"{delta.days // 7}w ago"
            elif delta.days < 365:
                return f"{delta.days // 30}mo ago"
            else:
                return f"{delta.days // 365}y ago"

        except Exception:
            return date_str[:10]
