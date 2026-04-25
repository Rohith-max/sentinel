"""
GitHub authentication and PAT management
"""

import os
import sys
from typing import Optional, Dict, Any
from pathlib import Path
import requests
from datetime import datetime

from sentinelci.config import get_config


class GitHubAuthError(Exception):
    """GitHub authentication error"""
    pass


class GitHubAuth:
    """Manages GitHub authentication and PAT validation"""

    def __init__(self):
        self.config = get_config()
        self.base_url = "https://api.github.com"
        self._cached_user: Optional[Dict[str, Any]] = None

    def get_pat(self) -> Optional[str]:
        """Get PAT from config or environment"""
        return self.config.get_github_pat()

    def has_pat(self) -> bool:
        """Check if PAT exists in config or environment"""
        return self.get_pat() is not None

    def validate_pat(self, pat: str) -> Dict[str, Any]:
        """
        Validate PAT against GitHub API

        Args:
            pat: GitHub Personal Access Token

        Returns:
            User information dict if valid

        Raises:
            GitHubAuthError: If PAT is invalid or expired
        """
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
        """
        Store PAT in config after validation

        Args:
            pat: GitHub Personal Access Token

        Raises:
            GitHubAuthError: If PAT is invalid
        """
        self.validate_pat(pat)
        self.config.set("git", "github_pat", pat)
        self._cached_user = None

    def prompt_and_store_pat(self) -> str:
        """
        Prompt user for PAT, validate, and store

        Returns:
            The validated PAT

        Raises:
            GitHubAuthError: If validation fails
        """
        print("\n🔑 GitHub Personal Access Token Setup")
        print("\nTo create a PAT:")
        print("1. Go to: https://github.com/settings/tokens/new")
        print("2. Select scopes: repo, read:org, read:user, workflow")
        print("3. Generate token and copy it\n")

        if sys.stdin.isatty():
            import getpass
            pat = getpass.getpass("Enter GitHub PAT: ").strip()
        else:
            pat = input("Enter GitHub PAT: ").strip()

        if not pat:
            raise GitHubAuthError("PAT cannot be empty")

        print("🔍 Validating PAT...")
        user_info = self.validate_pat(pat)
        
        self.config.set("git", "github_pat", pat)
        self._cached_user = user_info
        
        print(f"✅ PAT validated and stored for user: {user_info.get('login')}")
        return pat

    def get_authenticated_user(self) -> Dict[str, Any]:
        """
        Get authenticated user information

        Returns:
            User information dict

        Raises:
            GitHubAuthError: If not authenticated or PAT invalid
        """
        if self._cached_user:
            return self._cached_user

        pat = self.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        self._cached_user = self.validate_pat(pat)
        return self._cached_user

    def get_user_organizations(self) -> list[Dict[str, Any]]:
        """
        Get organizations for authenticated user

        Returns:
            List of organization dicts

        Raises:
            GitHubAuthError: If not authenticated
        """
        pat = self.get_pat()
        if not pat:
            raise GitHubAuthError("No GitHub PAT configured")

        headers = {
            "Authorization": f"token {pat}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            response = requests.get(
                f"{self.base_url}/user/orgs",
                headers=headers,
                timeout=10,
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise GitHubAuthError(f"Failed to fetch organizations: {response.status_code}")

        except requests.exceptions.RequestException as e:
            raise GitHubAuthError(f"Network error: {str(e)}")

    def check_auth_status(self) -> Dict[str, Any]:
        """
        Check authentication status and return details

        Returns:
            Dict with auth status, user info, and organizations
        """
        status = {
            "authenticated": False,
            "user": None,
            "organizations": [],
            "error": None,
        }

        try:
            if not self.has_pat():
                status["error"] = "No PAT configured"
                return status

            user = self.get_authenticated_user()
            orgs = self.get_user_organizations()

            status["authenticated"] = True
            status["user"] = user
            status["organizations"] = orgs

        except GitHubAuthError as e:
            status["error"] = str(e)

        return status

    def ensure_authenticated(self) -> None:
        """
        Ensure user is authenticated, prompt if not

        Raises:
            GitHubAuthError: If authentication fails
        """
        if not self.has_pat():
            self.prompt_and_store_pat()
        else:
            try:
                self.get_authenticated_user()
            except GitHubAuthError:
                print("⚠️  Stored PAT is invalid or expired")
                self.prompt_and_store_pat()
