"""
Configuration module for GitHub API authentication.
"""

import os
from typing import Optional


def get_github_token() -> str:
    """
    Returns the GitHub token from the environment variable GITHUB_TOKEN.
    
    Returns:
        str: The GitHub personal access token
        
    Raises:
        ValueError: If the GITHUB_TOKEN environment variable is not set
        
    Example:
        >>> token = get_github_token()
        >>> # Use token for API authentication
    """
    token: Optional[str] = os.environ.get("GITHUB_TOKEN")
    
    if not token:
        raise ValueError(
            "GitHub token not found. Please set the GITHUB_TOKEN environment variable.\n"
            "You can create a personal access token at: https://github.com/settings/tokens\n"
            "Then set it in your environment:\n"
            "  export GITHUB_TOKEN='your_token_here'  # Linux/macOS\n"
            "  set GITHUB_TOKEN=your_token_here       # Windows CMD\n"
            "  $env:GITHUB_TOKEN='your_token_here'    # Windows PowerShell"
        )
    
    return token


def get_config() -> dict:
    """
    Returns configuration settings for the GitHub analyzer.
    
    Returns:
        dict: Configuration dictionary with API settings
    """
    return {
        "base_url": "https://api.github.com",
        "api_version": "2022-11-28",
        "per_page": 100,
        "max_users_to_scrape": 10,  # Limit scraping to avoid rate limits
        "timeout": 30,  # Request timeout in seconds
    }
