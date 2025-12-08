#!/usr/bin/env python3
"""
Main demonstration script for GitHub Repository Analyzer.

This script demonstrates two use cases:
1. Collecting fresh data from GitHub API, analyzing it, and saving to pickle
2. Loading previously saved data from pickle and performing analysis

Usage:
    export GITHUB_TOKEN='your_token_here'
    python main.py [repo1] [repo2] [repo3] ...
    
    If no repos are provided, uses default set of popular repositories.
"""

import sys
import os
from tabulate import tabulate
import pandas as pd

from github_analyzer import (
    GitHubClient,
    GitHubRepoAnalyzer,
    plot_pr_status_distribution,
    plot_unique_users,
    plot_prs_over_time,
    plot_comparison_trend
)
from github_analyzer.config import get_github_token
from github_analyzer.visualization import plot_comprehensive_dashboard


def print_section_header(title: str) -> None:
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def format_summaries_table(summaries) -> str:
    """Format repo summaries as a nice table."""
    if not summaries:
        return "No summaries available."
    
    headers = ["Repository", "Open PRs", "Closed PRs", "Total PRs", 
               "Unique Users", "Oldest PR Date"]
    
    rows = []
    for summary in summaries:
        total = summary.open_prs + summary.closed_prs
        oldest = summary.oldest_pr_date.strftime("%Y-%m-%d") if pd.notna(summary.oldest_pr_date) else "N/A"
        rows.append([
            summary.repo,
            summary.open_prs,
            summary.closed_prs,
            total,
            summary.unique_users,
            oldest
        ])
    
    return tabulate(rows, headers=headers, tablefmt="grid")


def use_case_1_fresh_data(repos: list[str], token: str) -> None:
    """
    USE CASE 1: Collect fresh data from GitHub API.
    
    Demonstrates:
    - Creating analyzer with live GitHub client
    - Collecting data from API
    - Saving to pickle
    - Preprocessing and analysis
    - Generating visualizations
    """
    print_section_header("USE CASE 1: Collecting Fresh Data from GitHub API")
    
    print(f"Repositories to analyze: {', '.join(repos)}")
    print(f"Total repositories: {len(repos)}\n")
    
    # Create client and analyzer
    print("Step 1: Initializing GitHub client...")
    client = GitHubClient(token)
    analyzer = GitHubRepoAnalyzer(repos, client)
    print("✓ Client initialized\n")
    
    # Collect data
    print("Step 2: Collecting data from GitHub API...")
    print("(This may take a few minutes depending on repository size)\n")
    try:
        analyzer.collect_data(max_users_to_scrape=10)
        print("\n✓ Data collection complete\n")
    except Exception as e:
        print(f"\n✗ Error during data collection: {e}")
        print("Please check your GITHUB_TOKEN and internet connection.")
        sys.exit(1)
    
    # Save to pickle
    print("Step 3: Saving raw data to pickle file...")
    pickle_path = "github_data.pkl"
    analyzer.to_pickle(pickle_path)
    print(f"✓ Data saved to {pickle_path}\n")
    
    # Preprocess
    print("Step 4: Preprocessing data...")
    analyzer.preprocess()
    print("✓ Preprocessing complete\n")
    
    # Compute summaries
    print("Step 5: Computing repository summaries...")
    summaries = analyzer.compute_summaries()
    print("✓ Summaries computed\n")
    
    # Display summaries
    print_section_header("Repository Summary Statistics")
    print(format_summaries_table(summaries))
    
    # Build time series
    print("\nStep 6: Building time series data...")
    time_series = analyzer.build_time_series()
    print("✓ Time series built\n")
    
    # Trend analysis
    print_section_header("Temporal Trend Analysis")
    trends = analyzer.describe_trends(time_series)
    print(trends)
    
    # Generate visualizations
    print_section_header("Generating Visualizations")
    
    print("Creating visualizations...")
    
    try:
        # Create output directory for plots
        os.makedirs("output", exist_ok=True)
        
        print("\n1. PR Status Distribution...")
        plot_pr_status_distribution(summaries, save_path="output/pr_status_distribution.png")
        
        print("\n2. Unique Contributors...")
        plot_unique_users(summaries, save_path="output/unique_users.png")
        
        print("\n3. PR Activity Over Time...")
        plot_prs_over_time(time_series, save_path="output/pr_timeline.png")
        
        if len(repos) >= 2:
            print(f"\n4. Comparison Trend ({repos[0]} vs {repos[1]})...")
            plot_comparison_trend(time_series, repos[:2], save_path="output/comparison_trend.png")
        
        print("\n5. Comprehensive Dashboard...")
        plot_comprehensive_dashboard(summaries, time_series, save_path="output/dashboard.png")
        
        print("\n✓ All visualizations saved to 'output/' directory")
        
    except Exception as e:
        print(f"\n⚠ Warning: Some visualizations may not have been generated: {e}")
    
    print("\n" + "=" * 80)
    print("  USE CASE 1 COMPLETE")
    print("=" * 80)


def use_case_2_from_pickle(pickle_path: str, token: str) -> None:
    """
    USE CASE 2: Load data from pickle file.
    
    Demonstrates:
    - Loading analyzer from saved pickle
    - Analyzing without hitting API
    - Generating alternative visualizations
    """
    print_section_header("USE CASE 2: Loading Data from Pickle File")
    
    if not os.path.exists(pickle_path):
        print(f"✗ Pickle file not found: {pickle_path}")
        print("Please run USE CASE 1 first to generate the pickle file.")
        return
    
    print(f"Loading data from: {pickle_path}\n")
    
    # Create client (won't be used for API calls)
    client = GitHubClient(token)
    
    # Load from pickle
    print("Step 1: Loading analyzer from pickle...")
    analyzer = GitHubRepoAnalyzer.from_pickle(pickle_path, client)
    print("✓ Data loaded successfully\n")
    
    # Preprocess (in case it wasn't done before pickling)
    print("Step 2: Preprocessing data...")
    analyzer.preprocess()
    print("✓ Preprocessing complete\n")
    
    # Compute summaries
    print("Step 3: Computing summaries...")
    summaries = analyzer.compute_summaries()
    print("✓ Summaries computed\n")
    
    # Display summaries in different format
    print_section_header("Repository Summary (Loaded from Pickle)")
    print(format_summaries_table(summaries))
    
    # Build time series
    print("\nStep 4: Building time series...")
    time_series = analyzer.build_time_series()
    print("✓ Time series built\n")
    
    # Show some additional statistics
    print_section_header("Additional Statistics")
    
    for repo, df in analyzer.pr_data.items():
        print(f"\n{repo}:")
        print(f"  Total PRs: {len(df)}")
        print(f"  Date range: {df['created_at'].min().date()} to {df['created_at'].max().date()}")
        print(f"  Average comments per PR: {df['comments'].mean():.2f}")
        print(f"  Average commits per PR: {df['commits'].mean():.2f}")
        
        # Calculate merge rate
        merged = df['merged_at'].notna().sum()
        merge_rate = (merged / len(df) * 100) if len(df) > 0 else 0
        print(f"  Merge rate: {merge_rate:.1f}%")
    
    # Generate one more visualization
    print_section_header("Additional Visualization")
    
    try:
        print("Creating comprehensive dashboard...")
        plot_comprehensive_dashboard(summaries, time_series, save_path="output/dashboard_from_pickle.png")
        print("✓ Dashboard saved to output/dashboard_from_pickle.png")
    except Exception as e:
        print(f"⚠ Warning: Could not generate dashboard: {e}")
    
    print("\n" + "=" * 80)
    print("  USE CASE 2 COMPLETE")
    print("=" * 80)


def main():
    """Main entry point."""
    print("\n" + "=" * 80)
    print("  GitHub Repository Analyzer")
    print("  A comprehensive tool for analyzing GitHub repository pull requests")
    print("=" * 80)
    
    # Get GitHub token
    try:
        token = get_github_token()
    except ValueError as e:
        print(f"\n✗ Error: {e}\n")
        sys.exit(1)
    
    # Determine which repos to analyze
    if len(sys.argv) > 1:
        # Use repos from command line
        repos = sys.argv[1:]
    else:
        # Use default repos
        repos = [
            "numpy/numpy",
            "pandas-dev/pandas",
            "django/django"
        ]
        print("\nNo repositories specified. Using default set:")
        for repo in repos:
            print(f"  - {repo}")
    
    # RUN USE CASE 1: Fresh data collection
    try:
        use_case_1_fresh_data(repos, token)
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error in USE CASE 1: {e}")
        import traceback
        traceback.print_exc()
    
    # Small pause
    print("\n" + "-" * 80)
    input("\nPress ENTER to continue to USE CASE 2 (load from pickle)...")
    print("-" * 80)
    
    # RUN USE CASE 2: Load from pickle
    try:
        use_case_2_from_pickle("github_data.pkl", token)
    except KeyboardInterrupt:
        print("\n\n✗ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error in USE CASE 2: {e}")
        import traceback
        traceback.print_exc()
    
    # Final message
    print_section_header("All Demonstrations Complete!")
    print("Generated files:")
    print("  - github_data.pkl (raw and processed data)")
    print("  - output/pr_status_distribution.png")
    print("  - output/unique_users.png")
    print("  - output/pr_timeline.png")
    print("  - output/comparison_trend.png")
    print("  - output/dashboard.png")
    print("  - output/dashboard_from_pickle.png")
    print("\nThank you for using GitHub Repository Analyzer!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
