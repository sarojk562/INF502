#!/usr/bin/env python3
"""
Test script for Homework 2 functions
This script tests individual functions to ensure they work correctly
"""

from loadData import *
import pandas as pd

def test_functions():
    print("Testing individual functions...")
    
    # Test 1: Load a single Fitbit file
    print("\n1. Testing loadFitbitFile...")
    fitbit_file = "data/fitbit/101_minuteSteps_20141021_20141123.csv"
    try:
        steps_data = loadFitbitFile(fitbit_file, "Steps")
        print(f"✓ Successfully loaded {len(steps_data)} rows from Steps file")
        print(f"  Subject: {steps_data['Subject'].iloc[0]}")
        print(f"  Date range: {steps_data['DateTime'].min()} to {steps_data['DateTime'].max()}")
        print(f"  Steps range: {steps_data['Steps'].min()} to {steps_data['Steps'].max()}")
    except Exception as e:
        print(f"✗ Error loading Fitbit file: {e}")
    
    # Test 2: Load a single Actigraph file  
    print("\n2. Testing loadActigraphFile...")
    actigraph_file = "data/actigraph/101_week1.csv"
    try:
        acti_data = loadActigraphFile(actigraph_file)
        print(f"✓ Successfully loaded {len(acti_data)} rows from Actigraph file")
        print(f"  Subject: {acti_data['Subject'].iloc[0]}")
        print(f"  Date range: {acti_data['DateTime'].min()} to {acti_data['DateTime'].max()}")
        print(f"  Steps range: {acti_data['Steps'].min()} to {acti_data['Steps'].max()}")
    except Exception as e:
        print(f"✗ Error loading Actigraph file: {e}")
    
    # Test 3: Load a single clinical file
    print("\n3. Testing loadClinicalFile...")
    clinical_file = "data/clinical/101_clinical.txt"
    try:
        clinical_data = loadClinicalFile(clinical_file)
        print(f"✓ Successfully loaded clinical data")
        print(f"  Subject: {clinical_data['Subject'].iloc[0]}")
        print(f"  Age: {clinical_data['age'].iloc[0]}")
        print(f"  Sex: {clinical_data['sex'].iloc[0]}")
        print(f"  Mass: {clinical_data['mass'].iloc[0]}")
    except Exception as e:
        print(f"✗ Error loading clinical file: {e}")
    
    # Test 4: Test findBouts function with sample data
    print("\n4. Testing findBouts function...")
    try:
        # Create sample data for testing
        test_data = pd.DataFrame({
            'Subject': ['101'] * 20,
            'DateTime': pd.date_range('2014-10-21 10:00', periods=20, freq='1min'),
            'Steps': [0, 0, 15, 20, 25, 18, 5, 22, 19, 16, 
                     0, 0, 0, 30, 25, 20, 18, 22, 15, 0]
        })
        
        bouts, durations = findBouts(test_data, 'Steps', 
                                   minimum_threshold=10, 
                                   minimum_duration_in_minutes=3, 
                                   tolerance=1)
        
        subject_bouts = bouts['101']
        subject_durations = durations['101']
        
        print(f"✓ Found {len(subject_bouts)} bouts for test subject")
        if subject_bouts:
            print(f"  First bout duration: {subject_durations[0]} minutes")
            print(f"  First bout steps: {subject_bouts[0]['Steps'].sum()}")
        
    except Exception as e:
        print(f"✗ Error in findBouts function: {e}")
    
    print("\n5. Testing directory loading...")
    try:
        # Test loading Fitbit directory with just Steps
        fitbit_steps = loadFitbit("data/fitbit", measures=['Steps'])
        print(f"✓ Loaded Fitbit Steps from directory: {len(fitbit_steps)} rows")
        
        # Test loading Actigraph directory
        actigraph_all = loadActigraph("data/actigraph")
        print(f"✓ Loaded Actigraph from directory: {len(actigraph_all)} rows")
        
        # Test loading Clinical directory
        clinical_all = loadClinical("data/clinical")
        print(f"✓ Loaded Clinical from directory: {len(clinical_all)} rows")
        
    except Exception as e:
        print(f"✗ Error in directory loading: {e}")
    
    print("\n✓ All tests completed!")

if __name__ == "__main__":
    test_functions()