"""
Unit tests for GitHubClient class.
"""

import unittest
from unittest.mock import patch, Mock, MagicMock
import json
from github_analyzer.github_client import (
    GitHubClient, 
    GitHubAPIError, 
    RateLimitError,
    parse_user_profile
)


class TestGitHubClient(unittest.TestCase):
    """Test cases for GitHubClient class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.token = "test_token_12345"
        self.client = GitHubClient(self.token)
    
    def test_client_initialization(self):
        """Test client is initialized with correct attributes."""
        self.assertEqual(self.client.token, self.token)
        self.assertEqual(self.client.base_url, "https://api.github.com")
        self.assertIn("Authorization", self.client.session.headers)
        self.assertEqual(
            self.client.session.headers["Authorization"], 
            f"token {self.token}"
        )
    
    @patch('requests.Session.get')
    def test_get_repo_metadata_success(self, mock_get):
        """Test successful repository metadata retrieval."""
        # Mock response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "numpy",
            "full_name": "numpy/numpy",
            "stargazers_count": 25000,
            "forks_count": 8000,
            "description": "The fundamental package for scientific computing with Python"
        }
        mock_get.return_value = mock_response
        
        # Call method
        result = self.client.get_repo_metadata("numpy/numpy")
        
        # Assertions
        self.assertEqual(result["name"], "numpy")
        self.assertEqual(result["stargazers_count"], 25000)
        mock_get.assert_called_once()
    
    @patch('requests.Session.get')
    def test_get_repo_metadata_not_found(self, mock_get):
        """Test handling of 404 errors."""
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        with self.assertRaises(GitHubAPIError) as context:
            self.client.get_repo_metadata("nonexistent/repo")
        
        self.assertIn("not found", str(context.exception).lower())
    
    @patch('requests.Session.get')
    def test_rate_limit_error(self, mock_get):
        """Test handling of rate limit errors."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.headers = {
            "X-RateLimit-Remaining": "0",
            "X-RateLimit-Reset": "1234567890"
        }
        mock_get.return_value = mock_response
        
        with self.assertRaises(RateLimitError) as context:
            self.client.get_repo_metadata("numpy/numpy")
        
        self.assertIn("rate limit", str(context.exception).lower())
    
    @patch('requests.Session.get')
    def test_get_pull_requests_pagination(self, mock_get):
        """Test pull request pagination handling."""
        # Mock first page
        mock_response_1 = Mock()
        mock_response_1.status_code = 200
        mock_response_1.json.return_value = [
            {"number": 1, "title": "PR 1", "state": "open"},
            {"number": 2, "title": "PR 2", "state": "closed"}
        ]
        mock_response_1.headers = {
            "Link": '<https://api.github.com/repos/test/test/pulls?page=2>; rel="next"'
        }
        
        # Mock second page (last page)
        mock_response_2 = Mock()
        mock_response_2.status_code = 200
        mock_response_2.json.return_value = [
            {"number": 3, "title": "PR 3", "state": "open"}
        ]
        mock_response_2.headers = {"Link": ""}
        
        # Set up mock to return different responses
        mock_get.side_effect = [mock_response_1, mock_response_2]
        
        # Call method
        result = self.client.get_pull_requests("test/test", state="all")
        
        # Assertions
        self.assertEqual(len(result), 3)
        self.assertEqual(result[0]["number"], 1)
        self.assertEqual(result[2]["number"], 3)
        self.assertEqual(mock_get.call_count, 2)
    
    @patch('requests.Session.get')
    def test_get_pull_requests_empty(self, mock_get):
        """Test handling of repositories with no pull requests."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = []
        mock_response.headers = {"Link": ""}
        mock_get.return_value = mock_response
        
        result = self.client.get_pull_requests("test/test")
        
        self.assertEqual(result, [])
    
    @patch('requests.Session.get')
    def test_get_contributors_success(self, mock_get):
        """Test successful contributors retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"login": "user1", "contributions": 100},
            {"login": "user2", "contributions": 50}
        ]
        mock_response.headers = {"Link": ""}
        mock_get.return_value = mock_response
        
        result = self.client.get_contributors("test/test")
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["login"], "user1")
    
    @patch('requests.get')
    def test_get_user_profile_html_success(self, mock_get):
        """Test successful user profile HTML retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Profile Page</body></html>"
        mock_get.return_value = mock_response
        
        result = self.client.get_user_profile_html("testuser")
        
        self.assertIn("Profile Page", result)
        mock_get.assert_called_once()
    
    @patch('requests.get')
    def test_get_user_profile_html_error(self, mock_get):
        """Test handling of errors when fetching user profile."""
        mock_get.side_effect = Exception("Connection error")
        
        with self.assertRaises(GitHubAPIError):
            self.client.get_user_profile_html("testuser")


class TestParseUserProfile(unittest.TestCase):
    """Test cases for parse_user_profile function."""
    
    def test_parse_user_profile_basic(self):
        """Test parsing a basic user profile."""
        html = """
        <html>
        <body>
            <span class="p-name">John Doe</span>
            <div class="p-note">Python developer</div>
            <span class="p-label">San Francisco</span>
        </body>
        </html>
        """
        
        result = parse_user_profile(html)
        
        self.assertEqual(result["display_name"], "John Doe")
        self.assertEqual(result["bio"], "Python developer")
        self.assertEqual(result["location"], "San Francisco")
    
    def test_parse_user_profile_missing_fields(self):
        """Test parsing profile with missing fields."""
        html = "<html><body></body></html>"
        
        result = parse_user_profile(html)
        
        # Should return dict with None values for missing fields
        self.assertIsNone(result["display_name"])
        self.assertIsNone(result["bio"])
        self.assertIsNone(result["location"])
    
    def test_parse_user_profile_malformed_html(self):
        """Test handling of malformed HTML."""
        html = "<<<not valid html>>>"
        
        # Should not raise exception
        result = parse_user_profile(html)
        
        # Should return dict with expected keys
        self.assertIn("display_name", result)
        self.assertIn("bio", result)


if __name__ == '__main__':
    unittest.main()
