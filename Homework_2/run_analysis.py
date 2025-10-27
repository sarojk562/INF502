# let's use a script to call the functions in your module that you have written.
from loadData import * # this will import ALL defined functions from your loadData.py file
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for non-GUI environment
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import numpy as np

def main():
    print("Starting Homework 2 Analysis...")
    
    # Define data paths
    fitbit_path = "data/fitbit"
    actigraph_path = "data/actigraph" 
    clinical_path = "data/clinical"
    
    print("\n1. Loading Fitbit data...")
    fitbit_data = loadFitbit(fitbit_path)
    print(f"Fitbit data shape: {fitbit_data.shape}")
    print(f"Fitbit columns: {list(fitbit_data.columns)}")
    print(f"Unique subjects in Fitbit: {sorted(fitbit_data['Subject'].unique())}")
    
    print("\n2. Loading Actigraph data...")
    actigraph_data = loadActigraph(actigraph_path)
    print(f"Actigraph data shape: {actigraph_data.shape}")
    print(f"Actigraph columns: {list(actigraph_data.columns)}")
    print(f"Unique subjects in Actigraph: {sorted(actigraph_data['Subject'].unique())}")
    
    print("\n3. Loading Clinical data...")
    clinical_data = loadClinical(clinical_path)
    print(f"Clinical data shape: {clinical_data.shape}")
    print(f"Clinical columns: {list(clinical_data.columns)}")
    print(f"Unique subjects in Clinical: {sorted(clinical_data['Subject'].unique())}")
    
    print("\n4. Merging datasets...")
    # Merge Fitbit and Actigraph data on Subject and DateTime
    merged_data = pandas.merge(fitbit_data, actigraph_data, 
                              on=['Subject', 'DateTime'], 
                              how='inner', suffixes=('_fitbit', '_actigraph'))
    
    print(f"Merged data shape: {merged_data.shape}")
    print(f"Date range: {merged_data['DateTime'].min()} to {merged_data['DateTime'].max()}")
    
    # Remove rows with missing values
    merged_data = merged_data.dropna()
    print(f"After removing NaN values: {merged_data.shape}")
    
    print("\n5. Exploring data correlations...")
    # Calculate correlation between Fitbit and Actigraph steps
    correlation = merged_data['Steps_fitbit'].corr(merged_data['Steps_actigraph'])
    print(f"Correlation between Fitbit and Actigraph steps: {correlation:.3f}")
    
    # Create correlation plot
    plt.figure(figsize=(12, 8))
    
    plt.subplot(2, 2, 1)
    plt.scatter(merged_data['Steps_fitbit'], merged_data['Steps_actigraph'], 
               alpha=0.5, s=1)
    plt.xlabel('Fitbit Steps')
    plt.ylabel('Actigraph Steps')
    plt.title(f'Fitbit vs Actigraph Steps (r={correlation:.3f})')
    plt.plot([0, merged_data['Steps_fitbit'].max()], 
             [0, merged_data['Steps_fitbit'].max()], 'r--', alpha=0.5)
    
    print("\n6. Building regression model...")
    # Prepare features for regression
    feature_cols = ['Steps_fitbit', 'METs', 'Calories', 'Intensities']
    X = merged_data[feature_cols]
    y = merged_data['Steps_actigraph']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Make predictions
    y_pred_train = model.predict(X_train)
    y_pred_test = model.predict(X_test)
    
    # Calculate metrics
    train_r2 = r2_score(y_train, y_pred_train)
    test_r2 = r2_score(y_test, y_pred_test)
    train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
    test_rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    
    print(f"Training R²: {train_r2:.3f}, RMSE: {train_rmse:.2f}")
    print(f"Testing R²: {test_r2:.3f}, RMSE: {test_rmse:.2f}")
    
    # Plot model performance
    plt.subplot(2, 2, 2)
    plt.scatter(y_test, y_pred_test, alpha=0.5, s=1)
    plt.xlabel('Actual Actigraph Steps')
    plt.ylabel('Predicted Actigraph Steps')
    plt.title(f'Model Prediction (Test R²={test_r2:.3f})')
    plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'r--', alpha=0.5)
    
    # Plot residuals
    plt.subplot(2, 2, 3)
    residuals = y_test - y_pred_test
    plt.scatter(y_pred_test, residuals, alpha=0.5, s=1)
    plt.xlabel('Predicted Steps')
    plt.ylabel('Residuals')
    plt.title('Residual Plot')
    plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
    
    # Feature importance
    plt.subplot(2, 2, 4)
    feature_importance = abs(model.coef_)
    plt.bar(feature_cols, feature_importance)
    plt.title('Feature Importance (|Coefficient|)')
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig('fitbit_actigraph_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()  # Close instead of show for non-GUI environment
    
    print("\n7. Correcting Fitbit steps using model...")
    # Apply model to correct all Fitbit steps
    X_all = merged_data[feature_cols]
    corrected_steps = model.predict(X_all)
    merged_data['Steps_corrected'] = corrected_steps
    
    print("\n8. Finding activity bouts...")
    # Parameters for bout analysis
    minimum_threshold = 10  # steps per minute (reasonable walking pace)
    minimum_duration = 5    # 5 minutes minimum bout
    tolerance = 2          # allow 2 minutes of low activity within bout
    
    # Find bouts using corrected steps
    bouts, bout_durations = findBouts(merged_data, 'Steps_corrected', 
                                     minimum_threshold, minimum_duration, tolerance)
    
    # Calculate bout statistics for each subject
    bout_stats = {}
    for subject in bouts.keys():
        subject_bouts = bouts[subject]
        subject_durations = bout_durations[subject]
        
        total_bouts = len(subject_bouts)
        total_bout_time = sum(subject_durations) if subject_durations else 0
        total_bout_steps = sum([bout['Steps_corrected'].sum() for bout in subject_bouts])
        avg_bout_duration = np.mean(subject_durations) if subject_durations else 0
        
        bout_stats[subject] = {
            'total_bouts': total_bouts,
            'total_bout_time': total_bout_time,
            'total_bout_steps': total_bout_steps,
            'avg_bout_duration': avg_bout_duration
        }
    
    print(f"Bout analysis completed for {len(bout_stats)} subjects")
    for subject, stats in list(bout_stats.items())[:5]:  # Show first 5 subjects
        print(f"Subject {subject}: {stats['total_bouts']} bouts, "
              f"{stats['total_bout_time']} min total, "
              f"{stats['total_bout_steps']:.0f} steps")
    
    print("\n9. Analyzing relationship with clinical data...")
    # Create bout summary DataFrame
    bout_summary = pandas.DataFrame.from_dict(bout_stats, orient='index')
    bout_summary['Subject'] = bout_summary.index
    bout_summary = bout_summary.reset_index(drop=True)
    
    # Merge with clinical data
    final_data = pandas.merge(bout_summary, clinical_data, on='Subject', how='inner')
    print(f"Final analysis data shape: {final_data.shape}")
    
    # Create final visualization
    plt.figure(figsize=(15, 10))
    
    # Plot 1: Age vs Total Bouts
    plt.subplot(2, 3, 1)
    plt.scatter(final_data['age'], final_data['total_bouts'])
    plt.xlabel('Age')
    plt.ylabel('Total Daily Bouts')
    plt.title('Age vs Total Activity Bouts')
    
    # Plot 2: Age vs Total Bout Steps
    plt.subplot(2, 3, 2) 
    plt.scatter(final_data['age'], final_data['total_bout_steps'])
    plt.xlabel('Age')
    plt.ylabel('Total Bout Steps')
    plt.title('Age vs Total Steps in Bouts')
    
    # Plot 3: Mass vs Total Bouts
    plt.subplot(2, 3, 3)
    plt.scatter(final_data['mass'], final_data['total_bouts'])
    plt.xlabel('Mass (kg)')
    plt.ylabel('Total Daily Bouts')
    plt.title('Body Mass vs Activity Bouts')
    
    # Plot 4: Sex differences
    plt.subplot(2, 3, 4)
    sex_groups = final_data.groupby('sex')['total_bouts'].mean()
    plt.bar(sex_groups.index, sex_groups.values)
    plt.xlabel('Sex')
    plt.ylabel('Average Daily Bouts')
    plt.title('Sex Differences in Activity Bouts')
    
    # Plot 5: Distribution of bout durations
    plt.subplot(2, 3, 5)
    plt.hist(final_data['avg_bout_duration'], bins=15, alpha=0.7)
    plt.xlabel('Average Bout Duration (min)')
    plt.ylabel('Frequency')
    plt.title('Distribution of Bout Durations')
    
    # Plot 6: Correlation matrix
    plt.subplot(2, 3, 6)
    numeric_cols = ['age', 'mass', 'total_bouts', 'total_bout_steps', 'avg_bout_duration']
    corr_matrix = final_data[numeric_cols].corr()
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0)
    plt.title('Correlation Matrix')
    
    plt.tight_layout()
    plt.savefig('clinical_bout_analysis.png', dpi=300, bbox_inches='tight')
    plt.close()  # Close instead of show for non-GUI environment
    
    print("\n10. Summary Statistics...")
    print("\nBout Analysis Summary:")
    print(f"Average bouts per person: {final_data['total_bouts'].mean():.1f} ± {final_data['total_bouts'].std():.1f}")
    print(f"Average bout duration: {final_data['avg_bout_duration'].mean():.1f} ± {final_data['avg_bout_duration'].std():.1f} minutes")
    print(f"Average steps per bout: {(final_data['total_bout_steps']/final_data['total_bouts']).mean():.1f}")
    
    print("\nClinical Correlations:")
    age_bout_corr = final_data['age'].corr(final_data['total_bouts'])
    mass_bout_corr = final_data['mass'].corr(final_data['total_bouts'])
    print(f"Age vs Total Bouts: r = {age_bout_corr:.3f}")
    print(f"Body Mass vs Total Bouts: r = {mass_bout_corr:.3f}")
    
    print("\nAnalysis complete! Check generated plots for visualizations.")
    
    return merged_data, final_data, model

if __name__ == "__main__":
    merged_data, final_data, model = main()