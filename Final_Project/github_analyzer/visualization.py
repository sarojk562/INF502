"""
Visualization module for GitHub repository analysis.
"""

from typing import List, Optional
import matplotlib.pyplot as plt
import pandas as pd
from .github_analyzer import RepoSummary


def plot_pr_status_distribution(summaries: List[RepoSummary], save_path: Optional[str] = None) -> None:
    """
    Create a bar chart comparing open vs closed PRs per repo.
    
    Args:
        summaries: List of RepoSummary objects
        save_path: Optional file path to save the figure
        
    Example:
        >>> from github_analyzer import plot_pr_status_distribution
        >>> plot_pr_status_distribution(analyzer.repo_summaries, "pr_status.png")
    """
    if not summaries:
        print("No summaries to plot")
        return
    
    repos = [s.repo for s in summaries]
    open_counts = [s.open_prs for s in summaries]
    closed_counts = [s.closed_prs for s in summaries]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Set bar width and positions
    x = range(len(repos))
    width = 0.35
    
    # Create bars
    bars1 = ax.bar([i - width/2 for i in x], open_counts, width, label='Open', color='#2ecc71', alpha=0.8)
    bars2 = ax.bar([i + width/2 for i in x], closed_counts, width, label='Closed', color='#3498db', alpha=0.8)
    
    # Customize plot
    ax.set_xlabel('Repository', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Pull Requests', fontsize=12, fontweight='bold')
    ax.set_title('Pull Request Status Distribution by Repository', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(repos, rotation=45, ha='right')
    ax.legend(fontsize=10)
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}',
                   ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_unique_users(summaries: List[RepoSummary], save_path: Optional[str] = None) -> None:
    """
    Create a bar chart of number of unique users per repo.
    
    Args:
        summaries: List of RepoSummary objects
        save_path: Optional file path to save the figure
        
    Example:
        >>> from github_analyzer import plot_unique_users
        >>> plot_unique_users(analyzer.repo_summaries, "unique_users.png")
    """
    if not summaries:
        print("No summaries to plot")
        return
    
    repos = [s.repo for s in summaries]
    user_counts = [s.unique_users for s in summaries]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create bars with gradient colors
    colors = plt.cm.viridis([i/len(repos) for i in range(len(repos))])
    bars = ax.bar(repos, user_counts, color=colors, alpha=0.8, edgecolor='black', linewidth=1.2)
    
    # Customize plot
    ax.set_xlabel('Repository', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Unique Contributors', fontsize=12, fontweight='bold')
    ax.set_title('Unique Contributors by Repository', fontsize=14, fontweight='bold', pad=20)
    ax.set_xticklabels(repos, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
               f'{int(height)}',
               ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_prs_over_time(time_series_df: pd.DataFrame, save_path: Optional[str] = None) -> None:
    """
    Create a line chart showing PR counts over time per repo.
    
    Args:
        time_series_df: DataFrame with columns ['repo', 'date', 'pr_count']
        save_path: Optional file path to save the figure
        
    Example:
        >>> ts = analyzer.build_time_series()
        >>> plot_prs_over_time(ts, "pr_timeline.png")
    """
    if time_series_df.empty:
        print("No time series data to plot")
        return
    
    # Create figure
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot each repository
    repos = time_series_df['repo'].unique()
    colors = plt.cm.tab10(range(len(repos)))
    
    for i, repo in enumerate(repos):
        repo_data = time_series_df[time_series_df['repo'] == repo].copy()
        repo_data = repo_data.sort_values('date')
        
        # Resample to monthly for cleaner visualization
        repo_data.set_index('date', inplace=True)
        monthly = repo_data['pr_count'].resample('M').sum()
        
        ax.plot(monthly.index, monthly.values, marker='o', linewidth=2, 
               markersize=4, label=repo, color=colors[i], alpha=0.8)
    
    # Customize plot
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Pull Requests (Monthly)', fontsize=12, fontweight='bold')
    ax.set_title('Pull Request Activity Over Time', fontsize=14, fontweight='bold', pad=20)
    ax.legend(fontsize=10, loc='best')
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Rotate x-axis labels
    plt.xticks(rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_comparison_trend(time_series_df: pd.DataFrame, repos: List[str], 
                         save_path: Optional[str] = None) -> None:
    """
    Create a focused comparison of trends between a subset of repos.
    
    Args:
        time_series_df: DataFrame with columns ['repo', 'date', 'pr_count']
        repos: List of repository names to compare
        save_path: Optional file path to save the figure
        
    Example:
        >>> ts = analyzer.build_time_series()
        >>> plot_comparison_trend(ts, ["numpy/numpy", "pandas-dev/pandas"], "comparison.png")
    """
    if time_series_df.empty:
        print("No time series data to plot")
        return
    
    # Filter for selected repos
    filtered_df = time_series_df[time_series_df['repo'].isin(repos)]
    
    if filtered_df.empty:
        print(f"No data found for repos: {repos}")
        return
    
    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
    
    colors = plt.cm.Set2(range(len(repos)))
    
    # Plot 1: Daily activity
    for i, repo in enumerate(repos):
        repo_data = filtered_df[filtered_df['repo'] == repo].copy()
        repo_data = repo_data.sort_values('date')
        
        ax1.plot(repo_data['date'], repo_data['pr_count'], 
                marker='o', linewidth=1.5, markersize=3, 
                label=repo, color=colors[i], alpha=0.7)
    
    ax1.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax1.set_ylabel('Daily PR Count', fontsize=11, fontweight='bold')
    ax1.set_title('Daily Pull Request Activity Comparison', fontsize=13, fontweight='bold', pad=15)
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3, linestyle='--')
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Plot 2: Cumulative activity
    for i, repo in enumerate(repos):
        repo_data = filtered_df[filtered_df['repo'] == repo].copy()
        repo_data = repo_data.sort_values('date')
        
        # Calculate cumulative sum
        repo_data['cumulative'] = repo_data['pr_count'].cumsum()
        
        ax2.plot(repo_data['date'], repo_data['cumulative'], 
                linewidth=2.5, label=repo, color=colors[i], alpha=0.8)
    
    ax2.set_xlabel('Date', fontsize=11, fontweight='bold')
    ax2.set_ylabel('Cumulative PR Count', fontsize=11, fontweight='bold')
    ax2.set_title('Cumulative Pull Request Growth Comparison', fontsize=13, fontweight='bold', pad=15)
    ax2.legend(fontsize=10)
    ax2.grid(True, alpha=0.3, linestyle='--')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved plot to {save_path}")
    
    plt.show()


def plot_comprehensive_dashboard(summaries: List[RepoSummary], time_series_df: pd.DataFrame,
                                 save_path: Optional[str] = None) -> None:
    """
    Create a comprehensive dashboard with multiple subplots.
    
    Args:
        summaries: List of RepoSummary objects
        time_series_df: DataFrame with time series data
        save_path: Optional file path to save the figure
        
    Example:
        >>> plot_comprehensive_dashboard(analyzer.repo_summaries, ts, "dashboard.png")
    """
    if not summaries or time_series_df.empty:
        print("Insufficient data for dashboard")
        return
    
    fig = plt.figure(figsize=(16, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.3, wspace=0.3)
    
    repos = [s.repo for s in summaries]
    colors = plt.cm.tab10(range(len(repos)))
    
    # Subplot 1: PR Status Distribution (Stacked Bar)
    ax1 = fig.add_subplot(gs[0, 0])
    open_counts = [s.open_prs for s in summaries]
    closed_counts = [s.closed_prs for s in summaries]
    
    ax1.bar(repos, open_counts, label='Open', color='#2ecc71', alpha=0.8)
    ax1.bar(repos, closed_counts, bottom=open_counts, label='Closed', color='#3498db', alpha=0.8)
    ax1.set_title('PR Status Distribution', fontweight='bold', fontsize=12)
    ax1.set_ylabel('Number of PRs', fontweight='bold')
    ax1.legend()
    ax1.tick_params(axis='x', rotation=45)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
    ax1.grid(axis='y', alpha=0.3)
    
    # Subplot 2: Unique Contributors
    ax2 = fig.add_subplot(gs[0, 1])
    user_counts = [s.unique_users for s in summaries]
    ax2.bar(repos, user_counts, color=colors, alpha=0.8, edgecolor='black')
    ax2.set_title('Unique Contributors', fontweight='bold', fontsize=12)
    ax2.set_ylabel('Number of Users', fontweight='bold')
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right', fontsize=9)
    ax2.grid(axis='y', alpha=0.3)
    
    # Subplot 3: Timeline
    ax3 = fig.add_subplot(gs[1, :])
    for i, repo in enumerate(time_series_df['repo'].unique()):
        repo_data = time_series_df[time_series_df['repo'] == repo].copy()
        repo_data = repo_data.sort_values('date')
        repo_data.set_index('date', inplace=True)
        monthly = repo_data['pr_count'].resample('M').sum()
        
        ax3.plot(monthly.index, monthly.values, marker='o', linewidth=2, 
                markersize=4, label=repo, color=colors[i], alpha=0.8)
    
    ax3.set_title('PR Activity Over Time (Monthly)', fontweight='bold', fontsize=12)
    ax3.set_xlabel('Date', fontweight='bold')
    ax3.set_ylabel('Monthly PR Count', fontweight='bold')
    ax3.legend(fontsize=9, loc='best')
    ax3.grid(True, alpha=0.3)
    plt.setp(ax3.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    fig.suptitle('GitHub Repository Analysis Dashboard', fontsize=16, fontweight='bold', y=0.995)
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"Saved dashboard to {save_path}")
    
    plt.show()
