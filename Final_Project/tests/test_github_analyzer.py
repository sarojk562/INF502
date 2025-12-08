"""
Unit tests for GitHubRepoAnalyzer class.
"""

import unittest
from unittest.mock import Mock, MagicMock, patch
import pandas as pd
from datetime import datetime
from github_analyzer.github_analyzer import GitHubRepoAnalyzer, RepoSummary
from github_analyzer.github_client import GitHubClient


class TestGitHubRepoAnalyzer(unittest.TestCase):
    """Test cases for GitHubRepoAnalyzer class."""
    
    def setUp(self):
        """Set up test fixtures with fake data."""
        # Create mock client
        self.mock_client = Mock(spec=GitHubClient)
        
        # Set up test repos
        self.test_repos = ["test/repo1", "test/repo2"]
        
        # Create analyzer instance
        self.analyzer = GitHubRepoAnalyzer(self.test_repos, self.mock_client)
        
        # Create fake PR data
        self.fake_prs_repo1 = [
            {
                "number": 1,
                "title": "Add feature A",
                "state": "open",
                "user": {"login": "alice"},
                "created_at": "2024-01-15T10:00:00Z",
                "updated_at": "2024-01-16T10:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "comments": 5,
                "commits": 3,
                "additions": 100,
                "deletions": 20
            },
            {
                "number": 2,
                "title": "Fix bug B",
                "state": "closed",
                "user": {"login": "bob"},
                "created_at": "2024-01-10T10:00:00Z",
                "updated_at": "2024-01-12T10:00:00Z",
                "closed_at": "2024-01-12T10:00:00Z",
                "merged_at": "2024-01-12T10:00:00Z",
                "comments": 2,
                "commits": 1,
                "additions": 10,
                "deletions": 5
            },
            {
                "number": 3,
                "title": "Update docs",
                "state": "closed",
                "user": {"login": "alice"},
                "created_at": "2024-01-05T10:00:00Z",
                "updated_at": "2024-01-06T10:00:00Z",
                "closed_at": "2024-01-06T10:00:00Z",
                "merged_at": None,
                "comments": 0,
                "commits": 1,
                "additions": 50,
                "deletions": 0
            }
        ]
        
        self.fake_prs_repo2 = [
            {
                "number": 1,
                "title": "Initial commit",
                "state": "open",
                "user": {"login": "charlie"},
                "created_at": "2024-02-01T10:00:00Z",
                "updated_at": "2024-02-01T10:00:00Z",
                "closed_at": None,
                "merged_at": None,
                "comments": 0,
                "commits": 1,
                "additions": 200,
                "deletions": 0
            }
        ]
        
        # Store fake data for use in tests (but don't assign to analyzer yet)
        self.fake_raw_data = {
            "test/repo1": {
                "metadata": {"name": "repo1", "stargazers_count": 100},
                "pull_requests": self.fake_prs_repo1,
                "contributors": [{"login": "alice"}, {"login": "bob"}]
            },
            "test/repo2": {
                "metadata": {"name": "repo2", "stargazers_count": 50},
                "pull_requests": self.fake_prs_repo2,
                "contributors": [{"login": "charlie"}]
            }
        }
    
    def test_initialization(self):
        """Test analyzer is initialized correctly."""
        self.assertEqual(self.analyzer.repo_full_names, self.test_repos)
        self.assertEqual(self.analyzer.client, self.mock_client)
        self.assertEqual(self.analyzer.raw_data, {})
        self.assertEqual(self.analyzer.pr_data, {})
        self.assertEqual(self.analyzer.user_profiles, {})
        self.assertEqual(self.analyzer.repo_summaries, [])
    
    def test_preprocess(self):
        """Test preprocessing converts raw data to DataFrames correctly."""
        # Set up raw data for this test
        self.analyzer.raw_data = self.fake_raw_data
        self.analyzer.preprocess()
        
        # Check that pr_data contains DataFrames
        self.assertIn("test/repo1", self.analyzer.pr_data)
        self.assertIn("test/repo2", self.analyzer.pr_data)
        
        # Check repo1 DataFrame
        df1 = self.analyzer.pr_data["test/repo1"]
        self.assertIsInstance(df1, pd.DataFrame)
        self.assertEqual(len(df1), 3)
        
        # Check that datetime columns are parsed (handle both timezone-aware and naive)
        self.assertIn("datetime64", str(df1["created_at"].dtype))
        
        # Check that usernames are normalized
        self.assertTrue(all(df1["user_login"].str.islower()))
        
        # Check repo2 DataFrame
        df2 = self.analyzer.pr_data["test/repo2"]
        self.assertEqual(len(df2), 1)
    
    def test_compute_summaries(self):
        """Test summary computation gives correct counts."""
        # Set up raw data
        self.analyzer.raw_data = self.fake_raw_data
        
        # First preprocess the data
        self.analyzer.preprocess()
        
        # Compute summaries
        summaries = self.analyzer.compute_summaries()
        
        # Check we got summaries for both repos
        self.assertEqual(len(summaries), 2)
        
        # Check repo1 summary
        repo1_summary = next(s for s in summaries if s.repo == "test/repo1")
        self.assertEqual(repo1_summary.open_prs, 1)
        self.assertEqual(repo1_summary.closed_prs, 2)
        self.assertEqual(repo1_summary.unique_users, 2)  # alice and bob
        
        # Check oldest PR date for repo1
        expected_oldest = pd.Timestamp("2024-01-05T10:00:00Z")
        self.assertEqual(repo1_summary.oldest_pr_date, expected_oldest)
        
        # Check repo2 summary
        repo2_summary = next(s for s in summaries if s.repo == "test/repo2")
        self.assertEqual(repo2_summary.open_prs, 1)
        self.assertEqual(repo2_summary.closed_prs, 0)
        self.assertEqual(repo2_summary.unique_users, 1)  # charlie
    
    def test_build_time_series(self):
        """Test time series construction."""
        # Set up raw data
        self.analyzer.raw_data = self.fake_raw_data
        
        # First preprocess the data
        self.analyzer.preprocess()
        
        # Build time series
        ts = self.analyzer.build_time_series()
        
        # Check it's a DataFrame with correct columns
        self.assertIsInstance(ts, pd.DataFrame)
        self.assertIn("repo", ts.columns)
        self.assertIn("date", ts.columns)
        self.assertIn("pr_count", ts.columns)
        
        # Check we have data for both repos
        repos_in_ts = ts["repo"].unique()
        self.assertIn("test/repo1", repos_in_ts)
        self.assertIn("test/repo2", repos_in_ts)
        
        # Check counts are correct (repo1 has 3 PRs on different dates)
        repo1_data = ts[ts["repo"] == "test/repo1"]
        self.assertEqual(len(repo1_data), 3)  # 3 different dates
        self.assertTrue(all(repo1_data["pr_count"] == 1))  # 1 PR per date
    
    def test_build_time_series_empty(self):
        """Test time series with no data."""
        # Create analyzer with no raw data
        empty_analyzer = GitHubRepoAnalyzer([], self.mock_client)
        ts = empty_analyzer.build_time_series()
        
        # Should return empty DataFrame with correct columns
        self.assertTrue(ts.empty)
        self.assertIn("repo", ts.columns)
        self.assertIn("date", ts.columns)
        self.assertIn("pr_count", ts.columns)
    
    def test_describe_trends(self):
        """Test trend analysis produces text output."""
        # Set up raw data
        self.analyzer.raw_data = self.fake_raw_data
        
        # Preprocess and build time series
        self.analyzer.preprocess()
        ts = self.analyzer.build_time_series()
        
        # Get trend description
        trends = self.analyzer.describe_trends(ts)
        
        # Check it returns a string
        self.assertIsInstance(trends, str)
        
        # Check it contains key information
        self.assertIn("test/repo1", trends)
        self.assertIn("test/repo2", trends)
        self.assertIn("TREND", trends.upper())
    
    def test_describe_trends_empty(self):
        """Test trend analysis with empty data."""
        empty_df = pd.DataFrame(columns=["repo", "date", "pr_count"])
        trends = self.analyzer.describe_trends(empty_df)
        
        self.assertIn("No time series data", trends)
    
    @patch('builtins.open', create=True)
    @patch('pickle.dump')
    def test_to_pickle(self, mock_pickle_dump, mock_open):
        """Test saving data to pickle file."""
        # Set up raw data
        self.analyzer.raw_data = self.fake_raw_data
        
        # Set up some data
        self.analyzer.preprocess()
        
        # Save to pickle
        self.analyzer.to_pickle("test.pkl")
        
        # Check that file was opened and pickle.dump was called
        mock_open.assert_called_once_with("test.pkl", "wb")
        mock_pickle_dump.assert_called_once()
    
    @patch('builtins.open', create=True)
    @patch('pickle.load')
    def test_from_pickle(self, mock_pickle_load, mock_open):
        """Test loading data from pickle file."""
        # Set up mock pickle data
        mock_pickle_load.return_value = {
            "repo_full_names": self.test_repos,
            "raw_data": self.fake_raw_data,
            "user_profiles": {},
            "pr_data": {},
            "repo_summaries": []
        }
        
        # Load from pickle
        loaded_analyzer = GitHubRepoAnalyzer.from_pickle("test.pkl", self.mock_client)
        
        # Check data was loaded correctly
        self.assertEqual(loaded_analyzer.repo_full_names, self.test_repos)
        self.assertEqual(len(loaded_analyzer.raw_data), 2)
        mock_open.assert_called_once_with("test.pkl", "rb")


class TestRepoSummary(unittest.TestCase):
    """Test cases for RepoSummary dataclass."""
    
    def test_repo_summary_creation(self):
        """Test creating a RepoSummary instance."""
        summary = RepoSummary(
            repo="test/repo",
            open_prs=10,
            closed_prs=50,
            unique_users=15,
            oldest_pr_date=pd.Timestamp("2023-01-01")
        )
        
        self.assertEqual(summary.repo, "test/repo")
        self.assertEqual(summary.open_prs, 10)
        self.assertEqual(summary.closed_prs, 50)
        self.assertEqual(summary.unique_users, 15)
        self.assertIsInstance(summary.oldest_pr_date, pd.Timestamp)


if __name__ == '__main__':
    unittest.main()
