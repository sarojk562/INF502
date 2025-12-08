"""
Core analyzer class for GitHub repository analysis.
"""

import pickle
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import pandas as pd
from .github_client import GitHubClient, parse_user_profile


@dataclass
class RepoSummary:
    """
    Summary statistics for a GitHub repository.
    
    Attributes:
        repo: Full repository name (owner/repo)
        open_prs: Number of pull requests in open state
        closed_prs: Number of pull requests in closed state
        unique_users: Number of unique users (PR authors)
        oldest_pr_date: Date of the oldest pull request
    """
    repo: str
    open_prs: int
    closed_prs: int
    unique_users: int
    oldest_pr_date: pd.Timestamp


class GitHubRepoAnalyzer:
    """
    Main class for analyzing GitHub repositories.
    
    Orchestrates data collection, preprocessing, analysis, and visualization
    of GitHub repository pull request data.
    
    Attributes:
        repo_full_names: List of repository names in 'owner/repo' format
        client: GitHubClient instance for API calls
        raw_data: Dictionary storing raw API responses
        pr_data: Dictionary of pandas DataFrames with preprocessed PR data
        user_profiles: Dictionary of scraped user profile information
        repo_summaries: List of RepoSummary objects with analysis results
    """
    
    def __init__(self, repo_full_names: List[str], client: GitHubClient):
        """
        Initialize the GitHub repository analyzer.
        
        Args:
            repo_full_names: List like ["numpy/numpy", "pandas-dev/pandas", "django/django"]
            client: GitHubClient instance for making API calls
            
        Example:
            >>> from github_analyzer import GitHubClient, GitHubRepoAnalyzer
            >>> from github_analyzer.config import get_github_token
            >>> 
            >>> token = get_github_token()
            >>> client = GitHubClient(token)
            >>> repos = ["numpy/numpy", "pandas-dev/pandas"]
            >>> analyzer = GitHubRepoAnalyzer(repos, client)
        """
        self.repo_full_names = repo_full_names
        self.client = client
        self.raw_data: Dict[str, Dict[str, Any]] = {}
        self.pr_data: Dict[str, pd.DataFrame] = {}
        self.user_profiles: Dict[str, Dict[str, Any]] = {}
        self.repo_summaries: List[RepoSummary] = []
    
    def collect_data(self, max_users_to_scrape: int = 10) -> None:
        """
        Collect data from GitHub API for each repository.
        
        For each repo:
        - Fetch repo metadata
        - Fetch all pull requests (state='all')
        - Fetch contributors
        - Extract usernames from PRs and scrape basic user profile info
        
        Args:
            max_users_to_scrape: Maximum number of user profiles to scrape per repo
            
        Example:
            >>> analyzer.collect_data(max_users_to_scrape=5)
            Collecting data for numpy/numpy...
            Collecting data for pandas-dev/pandas...
        """
        for repo in self.repo_full_names:
            print(f"Collecting data for {repo}...")
            
            try:
                # Fetch repository metadata
                repo_metadata = self.client.get_repo_metadata(repo)
                
                # Fetch all pull requests
                print(f"  Fetching pull requests...")
                pull_requests = self.client.get_pull_requests(repo, state="all")
                
                # Fetch contributors
                print(f"  Fetching contributors...")
                contributors = self.client.get_contributors(repo)
                
                # Store raw data
                self.raw_data[repo] = {
                    "metadata": repo_metadata,
                    "pull_requests": pull_requests,
                    "contributors": contributors
                }
                
                # Extract unique usernames from PRs
                usernames = set()
                for pr in pull_requests:
                    if pr.get("user") and pr["user"].get("login"):
                        usernames.add(pr["user"]["login"])
                
                # Scrape user profiles (limited to avoid rate limits)
                print(f"  Scraping user profiles (max {max_users_to_scrape})...")
                scraped_count = 0
                for username in list(usernames)[:max_users_to_scrape]:
                    if username not in self.user_profiles:
                        try:
                            html = self.client.get_user_profile_html(username)
                            self.user_profiles[username] = parse_user_profile(html)
                            scraped_count += 1
                        except Exception as e:
                            print(f"    Warning: Could not scrape profile for {username}: {e}")
                
                print(f"  ✓ Collected {len(pull_requests)} PRs, {len(contributors)} contributors, "
                      f"{scraped_count} user profiles")
                
            except Exception as e:
                print(f"  ✗ Error collecting data for {repo}: {e}")
                raise
    
    def to_pickle(self, path: str) -> None:
        """
        Save raw data and processed data to a pickle file.
        
        Args:
            path: File path for the pickle file
            
        Example:
            >>> analyzer.to_pickle("github_data.pkl")
        """
        data_to_save = {
            "repo_full_names": self.repo_full_names,
            "raw_data": self.raw_data,
            "user_profiles": self.user_profiles,
            "pr_data": self.pr_data,
            "repo_summaries": self.repo_summaries
        }
        
        with open(path, "wb") as f:
            pickle.dump(data_to_save, f)
        
        print(f"Data saved to {path}")
    
    @classmethod
    def from_pickle(cls, path: str, client: GitHubClient) -> "GitHubRepoAnalyzer":
        """
        Load previously saved data from a pickle file.
        
        Constructs an analyzer instance without hitting the API.
        
        Args:
            path: File path to the pickle file
            client: GitHubClient instance (for potential future API calls)
            
        Returns:
            GitHubRepoAnalyzer: New instance with loaded data
            
        Example:
            >>> analyzer = GitHubRepoAnalyzer.from_pickle("github_data.pkl", client)
        """
        with open(path, "rb") as f:
            data = pickle.load(f)
        
        # Create new instance
        instance = cls(data["repo_full_names"], client)
        
        # Load saved data
        instance.raw_data = data["raw_data"]
        instance.user_profiles = data["user_profiles"]
        instance.pr_data = data.get("pr_data", {})
        instance.repo_summaries = data.get("repo_summaries", [])
        
        print(f"Data loaded from {path}")
        print(f"  Repositories: {len(instance.repo_full_names)}")
        print(f"  User profiles: {len(instance.user_profiles)}")
        
        return instance
    
    def preprocess(self) -> None:
        """
        Convert raw PR lists into pandas DataFrames and clean/normalize fields.
        
        Processing steps:
        - Parse 'created_at' and 'closed_at' as datetime
        - Normalize username fields
        - Extract relevant columns
        - Handle missing values
        
        Stores per-repo PR dataframes in self.pr_data.
        
        Example:
            >>> analyzer.preprocess()
            >>> print(analyzer.pr_data['numpy/numpy'].columns)
        """
        print("Preprocessing data...")
        
        for repo, data in self.raw_data.items():
            prs = data.get("pull_requests", [])
            
            if not prs:
                print(f"  No PRs found for {repo}")
                continue
            
            # Extract relevant fields from each PR
            pr_records = []
            for pr in prs:
                record = {
                    "number": pr.get("number"),
                    "title": pr.get("title"),
                    "state": pr.get("state"),
                    "user_login": pr.get("user", {}).get("login") if pr.get("user") else None,
                    "created_at": pr.get("created_at"),
                    "updated_at": pr.get("updated_at"),
                    "closed_at": pr.get("closed_at"),
                    "merged_at": pr.get("merged_at"),
                    "comments": pr.get("comments", 0),
                    "commits": pr.get("commits", 0),
                    "additions": pr.get("additions", 0),
                    "deletions": pr.get("deletions", 0),
                }
                pr_records.append(record)
            
            # Create DataFrame
            df = pd.DataFrame(pr_records)
            
            # Convert datetime columns
            datetime_cols = ["created_at", "updated_at", "closed_at", "merged_at"]
            for col in datetime_cols:
                df[col] = pd.to_datetime(df[col], errors="coerce")
            
            # Normalize username
            df["user_login"] = df["user_login"].str.lower().str.strip()
            
            # Sort by created_at
            df = df.sort_values("created_at").reset_index(drop=True)
            
            self.pr_data[repo] = df
            print(f"  ✓ Preprocessed {len(df)} PRs for {repo}")
    
    def compute_summaries(self) -> List[RepoSummary]:
        """
        Compute summary statistics for each repository.
        
        For each repo, computes:
        - open_prs: count of PRs with state == 'open'
        - closed_prs: count of PRs with state == 'closed'
        - unique_users: number of unique PR authors
        - oldest_pr_date: min 'created_at'
        
        Returns:
            List[RepoSummary]: List of summary objects
            
        Example:
            >>> summaries = analyzer.compute_summaries()
            >>> for summary in summaries:
            ...     print(f"{summary.repo}: {summary.open_prs} open, {summary.closed_prs} closed")
        """
        print("Computing summaries...")
        self.repo_summaries = []
        
        for repo, df in self.pr_data.items():
            if df.empty:
                continue
            
            # Count by state
            open_prs = len(df[df["state"] == "open"])
            closed_prs = len(df[df["state"] == "closed"])
            
            # Count unique users
            unique_users = df["user_login"].nunique()
            
            # Find oldest PR date
            oldest_pr_date = df["created_at"].min()
            
            summary = RepoSummary(
                repo=repo,
                open_prs=open_prs,
                closed_prs=closed_prs,
                unique_users=unique_users,
                oldest_pr_date=oldest_pr_date
            )
            
            self.repo_summaries.append(summary)
            print(f"  ✓ {repo}: {open_prs} open, {closed_prs} closed, "
                  f"{unique_users} unique users")
        
        return self.repo_summaries
    
    def build_time_series(self) -> pd.DataFrame:
        """
        Construct a time series DataFrame of PR creation over time.
        
        Returns:
            pd.DataFrame: DataFrame with columns ['repo', 'date', 'pr_count']
                        where pr_count is number of PRs created on that date per repo
                        
        Example:
            >>> ts = analyzer.build_time_series()
            >>> print(ts.head())
        """
        print("Building time series data...")
        
        all_series = []
        
        for repo, df in self.pr_data.items():
            if df.empty:
                continue
            
            # Extract date (without time) from created_at
            df_copy = df.copy()
            df_copy["date"] = df_copy["created_at"].dt.date
            
            # Group by date and count PRs
            daily_counts = df_copy.groupby("date").size().reset_index(name="pr_count")
            daily_counts["repo"] = repo
            
            all_series.append(daily_counts)
        
        if not all_series:
            return pd.DataFrame(columns=["repo", "date", "pr_count"])
        
        # Combine all repositories
        time_series = pd.concat(all_series, ignore_index=True)
        time_series["date"] = pd.to_datetime(time_series["date"])
        
        print(f"  ✓ Built time series with {len(time_series)} data points")
        
        return time_series
    
    def describe_trends(self, time_series_df: pd.DataFrame) -> str:
        """
        Analyze trends in the time-series data.
        
        Analyzes:
        - Which repo shows increasing PR activity over time
        - Which repo has more stable or declining activity
        - Comparison between repos
        
        Args:
            time_series_df: DataFrame from build_time_series()
            
        Returns:
            str: Human-readable multi-line summary of trends
            
        Example:
            >>> ts = analyzer.build_time_series()
            >>> trends = analyzer.describe_trends(ts)
            >>> print(trends)
        """
        if time_series_df.empty:
            return "No time series data available for trend analysis."
        
        analysis = ["=" * 60, "TEMPORAL TREND ANALYSIS", "=" * 60, ""]
        
        # Analyze each repository
        repo_stats = {}
        for repo in time_series_df["repo"].unique():
            repo_df = time_series_df[time_series_df["repo"] == repo].copy()
            repo_df = repo_df.sort_values("date")
            
            # Calculate statistics
            total_prs = repo_df["pr_count"].sum()
            avg_daily = repo_df["pr_count"].mean()
            max_daily = repo_df["pr_count"].max()
            
            # Calculate trend (simple linear regression on counts)
            repo_df["day_num"] = (repo_df["date"] - repo_df["date"].min()).dt.days
            if len(repo_df) > 1:
                correlation = repo_df["day_num"].corr(repo_df["pr_count"])
            else:
                correlation = 0
            
            # Split into early and late periods
            mid_point = len(repo_df) // 2
            if mid_point > 0:
                early_avg = repo_df.iloc[:mid_point]["pr_count"].mean()
                late_avg = repo_df.iloc[mid_point:]["pr_count"].mean()
                change_pct = ((late_avg - early_avg) / early_avg * 100) if early_avg > 0 else 0
            else:
                change_pct = 0
            
            repo_stats[repo] = {
                "total": total_prs,
                "avg_daily": avg_daily,
                "max_daily": max_daily,
                "correlation": correlation,
                "change_pct": change_pct
            }
            
            # Add to analysis
            analysis.append(f"Repository: {repo}")
            analysis.append(f"  Total PRs analyzed: {total_prs}")
            analysis.append(f"  Average daily PRs: {avg_daily:.2f}")
            analysis.append(f"  Peak daily PRs: {max_daily}")
            
            # Interpret trend
            if correlation > 0.3:
                trend = "INCREASING activity over time"
            elif correlation < -0.3:
                trend = "DECLINING activity over time"
            else:
                trend = "STABLE activity over time"
            
            analysis.append(f"  Trend: {trend} (correlation: {correlation:.3f})")
            analysis.append(f"  Change from early to late period: {change_pct:+.1f}%")
            analysis.append("")
        
        # Comparative analysis
        if len(repo_stats) > 1:
            analysis.append("COMPARATIVE ANALYSIS:")
            analysis.append("")
            
            # Sort by total activity
            sorted_repos = sorted(repo_stats.items(), key=lambda x: x[1]["total"], reverse=True)
            
            most_active = sorted_repos[0][0]
            least_active = sorted_repos[-1][0]
            
            analysis.append(f"Most active repository: {most_active}")
            analysis.append(f"  ({repo_stats[most_active]['total']} total PRs)")
            analysis.append("")
            analysis.append(f"Least active repository: {least_active}")
            analysis.append(f"  ({repo_stats[least_active]['total']} total PRs)")
            analysis.append("")
            
            # Find repo with strongest growth
            growing_repos = [(r, s["change_pct"]) for r, s in repo_stats.items() if s["change_pct"] > 0]
            if growing_repos:
                fastest_growing = max(growing_repos, key=lambda x: x[1])
                analysis.append(f"Fastest growing: {fastest_growing[0]} ({fastest_growing[1]:+.1f}%)")
            
            declining_repos = [(r, s["change_pct"]) for r, s in repo_stats.items() if s["change_pct"] < 0]
            if declining_repos:
                fastest_declining = min(declining_repos, key=lambda x: x[1])
                analysis.append(f"Fastest declining: {fastest_declining[0]} ({fastest_declining[1]:+.1f}%)")
        
        analysis.append("")
        analysis.append("=" * 60)
        
        return "\n".join(analysis)
