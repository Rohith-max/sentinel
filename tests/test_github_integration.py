"""
Tests for GitHub integration modules
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sentinelci.github_auth import GitHubAuth, GitHubAuthError
from sentinelci.github_repos import GitHubRepoManager
from sentinelci.github_security import GitHubSecurityAnalyzer


class TestGitHubAuth:
    """Test GitHub authentication"""

    def test_has_pat_returns_false_when_no_pat(self):
        """Test PAT detection when none configured"""
        with patch.object(GitHubAuth, 'get_pat', return_value=None):
            auth = GitHubAuth()
            assert auth.has_pat() is False

    def test_has_pat_returns_true_when_pat_exists(self):
        """Test PAT detection when configured"""
        with patch.object(GitHubAuth, 'get_pat', return_value='ghp_test123'):
            auth = GitHubAuth()
            assert auth.has_pat() is True

    @patch('sentinelci.github_auth.requests.get')
    def test_validate_pat_success(self, mock_get):
        """Test successful PAT validation"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'login': 'testuser',
            'name': 'Test User',
            'email': 'test@example.com'
        }
        mock_get.return_value = mock_response

        auth = GitHubAuth()
        result = auth.validate_pat('ghp_test123')

        assert result['login'] == 'testuser'
        assert result['name'] == 'Test User'

    @patch('sentinelci.github_auth.requests.get')
    def test_validate_pat_invalid(self, mock_get):
        """Test invalid PAT validation"""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_get.return_value = mock_response

        auth = GitHubAuth()
        
        with pytest.raises(GitHubAuthError, match="Invalid or expired"):
            auth.validate_pat('ghp_invalid')

    @patch('sentinelci.github_auth.requests.get')
    def test_get_user_organizations(self, mock_get):
        """Test fetching user organizations"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'login': 'org1', 'id': 1},
            {'login': 'org2', 'id': 2}
        ]
        mock_get.return_value = mock_response

        with patch.object(GitHubAuth, 'get_pat', return_value='ghp_test123'):
            auth = GitHubAuth()
            orgs = auth.get_user_organizations()

            assert len(orgs) == 2
            assert orgs[0]['login'] == 'org1'


class TestGitHubRepoManager:
    """Test GitHub repository management"""

    @patch('sentinelci.github_repos.requests.get')
    def test_fetch_repositories(self, mock_get):
        """Test fetching repositories"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'name': 'repo1',
                'full_name': 'user/repo1',
                'owner': {'login': 'user'},
                'private': False,
                'default_branch': 'main',
                'description': 'Test repo',
                'updated_at': '2024-01-01T00:00:00Z',
                'pushed_at': '2024-01-01T00:00:00Z',
                'stargazers_count': 10,
                'forks_count': 5,
                'language': 'Python',
                'html_url': 'https://github.com/user/repo1',
                'clone_url': 'https://github.com/user/repo1.git',
                'ssh_url': 'git@github.com:user/repo1.git'
            }
        ]
        mock_get.return_value = mock_response

        with patch.object(GitHubRepoManager, '_get_open_pr_count', return_value=2):
            with patch('sentinelci.github_repos.GitHubAuth') as mock_auth:
                mock_auth_instance = Mock()
                mock_auth_instance.get_pat.return_value = 'ghp_test123'
                mock_auth_instance.ensure_authenticated.return_value = None
                mock_auth.return_value = mock_auth_instance

                manager = GitHubRepoManager()
                repos = manager.fetch_all_repositories()

                assert len(repos) == 1
                assert repos[0]['name'] == 'repo1'
                assert repos[0]['visibility'] == 'public'
                assert repos[0]['open_prs'] == 2

    def test_filter_repositories_by_search(self):
        """Test filtering repositories by search term"""
        repos = [
            {'name': 'test-api', 'description': 'API service', 'visibility': 'public', 'language': 'Python'},
            {'name': 'web-app', 'description': 'Web application', 'visibility': 'private', 'language': 'JavaScript'},
            {'name': 'api-client', 'description': 'Client library', 'visibility': 'public', 'language': 'Python'}
        ]

        manager = GitHubRepoManager()
        filtered = manager.filter_repositories(repos, search='api')

        assert len(filtered) == 2
        assert all('api' in r['name'].lower() or 'api' in r['description'].lower() for r in filtered)

    def test_filter_repositories_by_visibility(self):
        """Test filtering repositories by visibility"""
        repos = [
            {'name': 'repo1', 'description': '', 'visibility': 'public', 'language': 'Python'},
            {'name': 'repo2', 'description': '', 'visibility': 'private', 'language': 'Python'},
            {'name': 'repo3', 'description': '', 'visibility': 'public', 'language': 'Python'}
        ]

        manager = GitHubRepoManager()
        filtered = manager.filter_repositories(repos, visibility='private')

        assert len(filtered) == 1
        assert filtered[0]['name'] == 'repo2'

    def test_filter_repositories_by_language(self):
        """Test filtering repositories by language"""
        repos = [
            {'name': 'repo1', 'description': '', 'visibility': 'public', 'language': 'Python'},
            {'name': 'repo2', 'description': '', 'visibility': 'public', 'language': 'JavaScript'},
            {'name': 'repo3', 'description': '', 'visibility': 'public', 'language': 'Python'}
        ]

        manager = GitHubRepoManager()
        filtered = manager.filter_repositories(repos, language='Python')

        assert len(filtered) == 2
        assert all(r['language'] == 'Python' for r in filtered)


class TestGitHubSecurityAnalyzer:
    """Test GitHub security analysis"""

    def test_calculate_risk_score_no_protection(self):
        """Test risk score with no branch protection"""
        analysis = {
            'branch_protection': {'enabled': False},
            'vulnerability_alerts': {'enabled': True},
            'dependabot': [],
            'secret_scanning': [],
            'failed_workflows': [],
            'permissions': {'visibility': 'private', 'allow_forking': False}
        }

        analyzer = GitHubSecurityAnalyzer()
        risk = analyzer.calculate_risk_score(analysis)

        assert risk['score'] >= 20
        assert 'No branch protection' in risk['factors']

    def test_calculate_risk_score_with_secrets(self):
        """Test risk score with exposed secrets"""
        analysis = {
            'branch_protection': {'enabled': True},
            'vulnerability_alerts': {'enabled': True},
            'dependabot': [],
            'secret_scanning': [
                {'number': 1, 'secret_type': 'api_key', 'state': 'open'}
            ],
            'failed_workflows': [],
            'permissions': {'visibility': 'private', 'allow_forking': False}
        }

        analyzer = GitHubSecurityAnalyzer()
        risk = analyzer.calculate_risk_score(analysis)

        assert risk['score'] >= 15
        assert any('exposed secret' in f for f in risk['factors'])

    def test_calculate_risk_score_critical_dependabot(self):
        """Test risk score with critical Dependabot alerts"""
        analysis = {
            'branch_protection': {'enabled': True},
            'vulnerability_alerts': {'enabled': True},
            'dependabot': [
                {'severity': 'critical', 'package': 'test-pkg'},
                {'severity': 'high', 'package': 'another-pkg'}
            ],
            'secret_scanning': [],
            'failed_workflows': [],
            'permissions': {'visibility': 'private', 'allow_forking': False}
        }

        analyzer = GitHubSecurityAnalyzer()
        risk = analyzer.calculate_risk_score(analysis)

        assert risk['score'] >= 15
        assert any('Dependabot' in f for f in risk['factors'])

    def test_calculate_risk_level_critical(self):
        """Test critical risk level calculation"""
        analysis = {
            'branch_protection': {'enabled': False},
            'vulnerability_alerts': {'enabled': False},
            'dependabot': [
                {'severity': 'critical', 'package': 'pkg1'},
                {'severity': 'critical', 'package': 'pkg2'},
                {'severity': 'critical', 'package': 'pkg3'}
            ],
            'secret_scanning': [
                {'number': 1, 'secret_type': 'api_key'}
            ],
            'failed_workflows': [],
            'permissions': {'visibility': 'public', 'allow_forking': True}
        }

        analyzer = GitHubSecurityAnalyzer()
        risk = analyzer.calculate_risk_score(analysis)

        assert risk['level'] == 'CRITICAL'
        assert risk['score'] >= 50


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
