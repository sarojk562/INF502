"""
GitHub Repository Analyzer Package

A modular Python application for collecting, analyzing, and visualizing
GitHub repository data using the GitHub REST API.
"""

__version__ = "1.0.0"
__author__ = "GitHub Analyzer Team"

from .github_client import GitHubClient
from .github_analyzer import GitHubRepoAnalyzer, RepoSummary
from .visualization import (
    plot_pr_status_distribution,
    plot_unique_users,
    plot_prs_over_time,
    plot_comparison_trend
)

__all__ = [
    "GitHubClient",
    "GitHubRepoAnalyzer",
    "RepoSummary",
    "plot_pr_status_distribution",
    "plot_unique_users",
    "plot_prs_over_time",
    "plot_comparison_trend"
]
