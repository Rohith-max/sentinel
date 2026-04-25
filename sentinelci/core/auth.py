"""
GitHub authentication module
"""

import os
from typing import Optional, Dict, Any
from pathlib import Path
import requests
from sentinelci.config import get_config


class GitHubAuthError(Exception):
    """GitHub authentication error"""
    pass


class GitHubAuth:
    """Manages GitHub authentication"""

    def __init__(self):
        self.config = get_config()
        self.base_url = "https://api.github.com"
        self._cached_user: Optional[Dict[str, Any]] = None

    def get_pat(self) -> Optional[str]:
        """Get PAT from config or environment"""
        return self.config.get_github_pat()

    def has_pat(self) -> bool:
        """Check if PAT exists"""
        return self.get_pat() is not None

    def validate_pat(self, pat: str) -> Dict[str, Any]:
        """Validate PAT against GitHub API"""
        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                raise GitHubAuthError("Invalid or expired GitHub PAT")
            elif response.status_code == 403:
                raise GitHubAuthError("GitHub PAT lacks required permissions")
            else:
                raise GitHubAuthError(f"GitHub API error: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise GitHubAuthError(f"Network error: {str(e)}")

    def store_pat(self, pat: str) -> None:
        """Store PAT after validation"""
        self.validate_pat(pat)
        self.config.set("git", "github_pat", pat)
        self._cached_user = None

    def get_authenticated_user(self) -> Dict[str, Any]:
        """Get authenticated user information"""
        if self._cached_user:
            return self._cached_user

        pat = self.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        self._cached_user = self.validate_pat(pat)
        return self._cached_user

    def ensure_authenticated(self) -> None:
        """Ensure user is authenticated"""
        if not self.has_pat():
            raise GitHubAuthError("No GitHub PAT configured. Run: sci github setup")
        
        try:
            self.get_authenticated_user()
        except GitHubAuthError:
            raise GitHubAuthError("Stored PAT is invalid. Run: sci github setup")

    def get_token_scopes(self) -> list[str]:
        """Get the scopes/permissions of the current PAT"""
        pat = self.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                # GitHub returns scopes in the X-OAuth-Scopes header
                scopes_header = response.headers.get("X-OAuth-Scopes", "")
                if scopes_header:
                    return [s.strip() for s in scopes_header.split(",")]
                return []
            else:
                raise GitHubAuthError(f"Failed to get token scopes: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise GitHubAuthError(f"Network error: {str(e)}")

    def check_required_scopes(self, required_scopes: list[str]) -> tuple[bool, list[str]]:
        """
        Check if PAT has required scopes
        
        Returns:
            (has_all_scopes, missing_scopes)
        """
        try:
            current_scopes = self.get_token_scopes()
            missing = []
            
            for required in required_scopes:
                if required not in current_scopes:
                    missing.append(required)
            
            return (len(missing) == 0, missing)
        except GitHubAuthError:
            return (False, required_scopes)
