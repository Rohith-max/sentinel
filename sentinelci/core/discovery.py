"""
Repository discovery and organization scanning
"""

from typing import List, Dict, Any, Optional
import requests
from sentinelci.core.auth import GitHubAuth, GitHubAuthError


class RepositoryDiscovery:
    """Discovers and filters repositories"""

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

    def fetch_user_repositories(self) -> List[Dict[str, Any]]:
        """Fetch all user repositories"""
        self.auth.ensure_authenticated()
        repos = []
        page = 1

        while True:
            response = requests.get(
                f"{self.base_url}/user/repos",
                headers=self._get_headers(),
                params={
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                    "affiliation": "owner,collaborator,organization_member",
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

            if len(batch) < 100:
                break

        return self._normalize_repositories(repos)

    def fetch_organization_repositories(self, org_name: str) -> List[Dict[str, Any]]:
        """Fetch all repositories in an organization"""
        self.auth.ensure_authenticated()
        repos = []
        page = 1

        while True:
            response = requests.get(
                f"{self.base_url}/orgs/{org_name}/repos",
                headers=self._get_headers(),
                params={
                    "per_page": 100,
                    "page": page,
                    "sort": "updated",
                },
                timeout=15,
            )

            if response.status_code != 200:
                raise GitHubAuthError(f"Failed to fetch org repositories: {response.status_code}")

            batch = response.json()
            if not batch:
                break

            repos.extend(batch)
            page += 1

            if len(batch) < 100:
                break

        return self._normalize_repositories(repos)

    def get_user_organizations(self) -> List[Dict[str, Any]]:
        """Get user's organizations"""
        self.auth.ensure_authenticated()

        response = requests.get(
            f"{self.base_url}/user/orgs",
            headers=self._get_headers(),
            timeout=10,
        )

        if response.status_code == 200:
            return response.json()
        else:
            raise GitHubAuthError(f"Failed to fetch organizations: {response.status_code}")

    def _normalize_repositories(self, repos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize repository data"""
        normalized = []

        for repo in repos:
            normalized.append({
                "name": repo["name"],
                "full_name": repo["full_name"],
                "owner": repo["owner"]["login"],
                "visibility": "private" if repo["private"] else "public",
                "default_branch": repo.get("default_branch", "main"),
                "description": repo.get("description", ""),
                "language": repo.get("language", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "updated_at": repo.get("updated_at", ""),
                "url": repo["html_url"],
                "clone_url": repo["clone_url"],
            })

        return normalized

    def filter_repositories(
        self,
        repos: List[Dict[str, Any]],
        search: Optional[str] = None,
        visibility: Optional[str] = None,
        language: Optional[str] = None,
        min_stars: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Filter repositories by criteria"""
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

        if min_stars is not None:
            filtered = [r for r in filtered if r.get("stars", 0) >= min_stars]

        return filtered
