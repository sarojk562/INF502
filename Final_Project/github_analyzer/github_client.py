"""
GitHub API client for fetching repository data and user profiles.
"""

import time
from typing import Optional
import requests
from bs4 import BeautifulSoup


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors."""
    pass


class RateLimitError(GitHubAPIError):
    """Exception raised when GitHub API rate limit is exceeded."""
    pass


class GitHubClient:
    """
    Client for interacting with the GitHub REST API and scraping user profiles.
    
    Attributes:
        token (str): GitHub personal access token for authentication
        base_url (str): Base URL for GitHub API (default: https://api.github.com)
        session (requests.Session): HTTP session for making requests
    """
    
    def __init__(self, token: str, base_url: str = "https://api.github.com"):
        """
        Initialize the GitHub client.
        
        Args:
            token: GitHub personal access token
            base_url: Base URL for GitHub API
        """
        self.token = token
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
            "X-GitHub-Api-Version": "2022-11-28"
        })
    
    def _make_request(self, endpoint: str, params: Optional[dict] = None) -> requests.Response:
        """
        Make an authenticated request to the GitHub API.
        
        Args:
            endpoint: API endpoint (e.g., '/repos/owner/repo')
            params: Query parameters
            
        Returns:
            Response object
            
        Raises:
            RateLimitError: If rate limit is exceeded
            GitHubAPIError: For other API errors
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.get(url, params=params, timeout=30)
            
            # Check for rate limiting
            if response.status_code == 403:
                remaining = response.headers.get("X-RateLimit-Remaining", "0")
                if remaining == "0":
                    reset_time = response.headers.get("X-RateLimit-Reset", "unknown")
                    raise RateLimitError(
                        f"GitHub API rate limit exceeded. "
                        f"Rate limit resets at timestamp: {reset_time}. "
                        f"Please wait before making more requests."
                    )
            
            # Check for other errors
            if response.status_code == 404:
                raise GitHubAPIError(f"Resource not found: {url}")
            elif response.status_code >= 400:
                error_msg = response.json().get("message", "Unknown error") if response.text else "Unknown error"
                raise GitHubAPIError(
                    f"GitHub API error (status {response.status_code}): {error_msg}"
                )
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            raise GitHubAPIError(f"Request failed: {str(e)}")
    
    def get_repo_metadata(self, full_name: str) -> dict:
        """
        Return repository metadata for 'owner/repo'.
        
        Args:
            full_name: Repository in format 'owner/repo' (e.g., 'numpy/numpy')
            
        Returns:
            dict: Repository metadata including name, description, stars, forks, etc.
            
        Example:
            >>> client = GitHubClient(token)
            >>> metadata = client.get_repo_metadata("numpy/numpy")
            >>> print(metadata['name'], metadata['stargazers_count'])
        """
        endpoint = f"/repos/{full_name}"
        response = self._make_request(endpoint)
        return response.json()
    
    def get_pull_requests(self, full_name: str, state: str = "all") -> list[dict]:
        """
        Return a list of pull requests for a repo with pagination handling.
        
        Args:
            full_name: Repository in format 'owner/repo'
            state: Filter by state ('open', 'closed', or 'all')
            
        Returns:
            list[dict]: List of all pull requests
            
        Example:
            >>> client = GitHubClient(token)
            >>> prs = client.get_pull_requests("django/django", state="all")
            >>> print(f"Total PRs: {len(prs)}")
        """
        endpoint = f"/repos/{full_name}/pulls"
        all_prs = []
        page = 1
        per_page = 100
        
        while True:
            params = {
                "state": state,
                "per_page": per_page,
                "page": page,
                "sort": "created",
                "direction": "desc"
            }
            
            response = self._make_request(endpoint, params=params)
            prs = response.json()
            
            if not prs:
                break
            
            all_prs.extend(prs)
            
            # Check if there are more pages
            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break
            
            page += 1
            
            # Small delay to be respectful to the API
            time.sleep(0.1)
        
        return all_prs
    
    def get_contributors(self, full_name: str) -> list[dict]:
        """
        Return contributors for the repo.
        
        Args:
            full_name: Repository in format 'owner/repo'
            
        Returns:
            list[dict]: List of contributors with their contributions
            
        Example:
            >>> client = GitHubClient(token)
            >>> contributors = client.get_contributors("pandas-dev/pandas")
        """
        endpoint = f"/repos/{full_name}/contributors"
        all_contributors = []
        page = 1
        per_page = 100
        
        while True:
            params = {
                "per_page": per_page,
                "page": page
            }
            
            response = self._make_request(endpoint, params=params)
            contributors = response.json()
            
            if not contributors:
                break
            
            all_contributors.extend(contributors)
            
            # Check if there are more pages
            link_header = response.headers.get("Link", "")
            if 'rel="next"' not in link_header:
                break
            
            page += 1
            time.sleep(0.1)
        
        return all_contributors
    
    def get_user_profile_html(self, username: str) -> str:
        """
        Fetch raw HTML for a user's GitHub profile page.
        This is for minimal scraping of additional social info.
        
        Args:
            username: GitHub username
            
        Returns:
            str: Raw HTML content of the user's profile page
            
        Example:
            >>> client = GitHubClient(token)
            >>> html = client.get_user_profile_html("torvalds")
            >>> profile_data = parse_user_profile(html)
        """
        url = f"https://github.com/{username}"
        
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            raise GitHubAPIError(f"Failed to fetch profile for {username}: {str(e)}")


def parse_user_profile(html: str) -> dict:
    """
    Parse the GitHub profile HTML and extract simple fields.
    
    Args:
        html: Raw HTML content from a GitHub profile page
        
    Returns:
        dict: Parsed profile information including:
            - display_name: User's display name
            - bio: User's bio/description
            - location: User's location
            - followers: Number of followers (as string)
            - following: Number of people following
            - repos: Number of public repositories
            
    Example:
        >>> html = client.get_user_profile_html("octocat")
        >>> profile = parse_user_profile(html)
        >>> print(profile['display_name'], profile['location'])
    """
    soup = BeautifulSoup(html, 'html.parser')
    
    profile_data = {
        "display_name": None,
        "bio": None,
        "location": None,
        "followers": None,
        "following": None,
        "repos": None
    }
    
    try:
        # Try to extract display name
        name_elem = soup.find("span", {"class": "p-name"})
        if name_elem:
            profile_data["display_name"] = name_elem.get_text(strip=True)
        
        # Try to extract bio
        bio_elem = soup.find("div", {"class": "p-note"})
        if bio_elem:
            profile_data["bio"] = bio_elem.get_text(strip=True)
        
        # Try to extract location
        location_elem = soup.find("span", {"class": "p-label"})
        if location_elem:
            profile_data["location"] = location_elem.get_text(strip=True)
        
        # Try to extract follower stats
        # Look for links with specific text patterns
        links = soup.find_all("a", {"class": "Link--secondary"})
        for link in links:
            text = link.get_text(strip=True).lower()
            if "followers" in text:
                # Extract number from text like "1.2k followers"
                number = text.split()[0]
                profile_data["followers"] = number
            elif "following" in text:
                number = text.split()[0]
                profile_data["following"] = number
        
        # Try to extract repository count
        repo_counter = soup.find("span", {"class": "Counter"})
        if repo_counter:
            profile_data["repos"] = repo_counter.get_text(strip=True)
            
    except Exception:
        # If scraping fails for any element, return what we have
        pass
    
    return profile_data
