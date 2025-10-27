# this is just the start for you.  You will need at least the following libraries, so let's do the import
import pandas
from datetime import datetime
from datetime import timedelta
import os
import numpy as np

# we can start by defining the loadFitbit function.
def loadFitbit(path, measures=['METs', 'Steps', 'Calories', 'Intensities']):
    # by using measures=[] above, we are setting some default values.  If you provide a second input, those will overwrite the default here.
    try:
        os.scandir(path) #  let's figure out if the user passed in a directory, or a single file name.
    except NotADirectoryError:
        # it wasn't a directory that was passed in
        # but this doesn't yet test if the file exists, fix that!
        if os.path.isfile(path):
            # Determine measure from filename
            filename = os.path.basename(path)
            for measure in measures:
                if measure in filename:
                    merged = loadFitbitFile(path, measure)
                    break
            else:
                raise ValueError(f"Cannot determine measure type from filename: {filename}")
        else:
            raise FileNotFoundError(f"File does not exist: {path}")
    else:
        # it was a directory that was passed in, so let's make use of it
        print('Directory name passed in')
        merged = None
        
        # for each of the measures, we want to find all of the files with those measures, and load them.
        for this_measure in measures:
            print(f"Processing {this_measure}")
            paths = [f.path for f in os.scandir(path) if (f.is_file() and (this_measure in f.name))]
            
            if not paths:
                print(f"No files found for measure: {this_measure}")
                continue
                
            # Concatenate all files for this measure
            measure_data_frames = []
            for this_file in paths:
                data = loadFitbitFile(this_file, this_measure)
                measure_data_frames.append(data)
            
            # Concatenate all data for this measure
            concatenated_data = pandas.concat(measure_data_frames, ignore_index=True)
            
            # Merge with previously processed measures
            if merged is None:
                merged = concatenated_data
            else:
                merged = pandas.merge(merged, concatenated_data, on=['Subject', 'DateTime'], how='outer')
                
    return merged

def loadFitbitFile(this_file, measure):
    date_format = '%m/%d/%Y %I:%M:%S %p'
    delta = timedelta(minutes=1)
    filename = os.path.basename(this_file)
    
    # Extract subject number from filename (e.g., "101_minuteSteps_20141021_20141123.csv" -> 101)
    subject_id = filename.split('_')[0]
    
    # Read the CSV file
    df = pandas.read_csv(this_file)
    
    # Map measure names to actual column prefixes in the files
    measure_mapping = {
        'METs': 'MET',
        'Steps': 'Steps', 
        'Calories': 'Calories',
        'Intensities': 'Intensity'
    }
    
    column_prefix = measure_mapping.get(measure, measure)
    
    # Initialize lists to store reshaped data
    subjects = []
    datetimes = []
    values = []
    
    # Process each row (hour)
    for _, row in df.iterrows():
        # Extract the datetime string from ActivityHour column
        datetime_in_string_format = row['ActivityHour']
        date_object = datetime.strptime(datetime_in_string_format, date_format)
        
        # Generate all 60 minutes for this hour
        this_hour = [date_object + (delta * i) for i in range(60)]
        
        # Extract values for each minute (Steps00, Steps01, ..., Steps59)
        for i in range(60):
            minute_col = f"{column_prefix}{i:02d}"  # e.g., "Steps00", "MET00"
            subjects.append(subject_id)
            datetimes.append(this_hour[i])
            values.append(row[minute_col])
    
    # Create DataFrame
    single_file_worth_of_data = pandas.DataFrame({
        'Subject': subjects,
        'DateTime': datetimes,
        measure: values
    })
    
    return single_file_worth_of_data

def loadActigraph(path):
    try:
        os.scandir(path)
    except NotADirectoryError:
        # it wasn't a directory that was passed in
        print('Filename provided')
        if os.path.isfile(path):
            return loadActigraphFile(path)
        else:
            raise FileNotFoundError(f"File does not exist: {path}")
    else:
        # it was a directory that was passed in
        print('Directory name passed in')
        
        # Find all CSV files in the directory (excluding dataDictionary.txt)
        csv_files = [f.path for f in os.scandir(path) 
                    if f.is_file() and f.name.endswith('.csv')]
        
        if not csv_files:
            raise ValueError(f"No CSV files found in directory: {path}")
        
        # Load and concatenate all files
        all_data = []
        for csv_file in csv_files:
            data = loadActigraphFile(csv_file)
            all_data.append(data)
        
        # Concatenate all data
        merged_data = pandas.concat(all_data, ignore_index=True)
        
        return merged_data

def loadActigraphFile(this_file):
    date_format = '%m/%d/%Y %H:%M:%S' # the time format is a bit different in the actigraph.  Use this one.
    delta = timedelta(minutes=1)
    
    # Extract subject ID from filename
    filename = os.path.basename(this_file)
    subject_id = filename.split('_')[0]
    
    # Read the header to extract start date and time
    start_date = None
    start_time = None
    
    with open(this_file, 'r') as file:
        for i in range(10):  # Read first 10 lines for header info
            line = file.readline().strip()
            if line.startswith('Start Time'):
                start_time = line.split(' ', 2)[2]  # Get time part after "Start Time "
            elif line.startswith('Start Date'):
                start_date = line.split(' ', 2)[2]  # Get date part after "Start Date "
    
    # Combine date and time
    start_datetime_str = f"{start_date} {start_time}"
    start_datetime = datetime.strptime(start_datetime_str, date_format)
    
    # Read the data starting from line 11 (skip header)
    column_names = ['Axis1', 'Axis2', 'Axis3', 'Steps', 'Lux', 
                   'InclinometerOff', 'InclinometerStanding', 
                   'InclinometerSitting', 'InclinometerLying']
    
    data = pandas.read_csv(this_file, skiprows=10, header=None, names=column_names)
    
    # Generate datetime for each row (each minute)
    num_rows = len(data)
    datetimes = [start_datetime + (delta * i) for i in range(num_rows)]
    
    # Add subject and datetime columns
    data['Subject'] = subject_id
    data['DateTime'] = datetimes
    
    return data

def loadClinical(path):
    """Load clinical data from file or directory"""
    try:
        os.scandir(path)
    except NotADirectoryError:
        # Single file
        if os.path.isfile(path):
            return loadClinicalFile(path)
        else:
            raise FileNotFoundError(f"File does not exist: {path}")
    else:
        # Directory
        txt_files = [f.path for f in os.scandir(path) 
                    if f.is_file() and f.name.endswith('.txt')]
        
        if not txt_files:
            raise ValueError(f"No .txt files found in directory: {path}")
        
        # Load all clinical files
        all_clinical_data = []
        for txt_file in txt_files:
            clinical_data = loadClinicalFile(txt_file)
            all_clinical_data.append(clinical_data)
        
        # Concatenate all clinical data
        merged_clinical = pandas.concat(all_clinical_data, ignore_index=True)
        return merged_clinical

def loadClinicalFile(this_file):
    """Load a single clinical file"""
    filename = os.path.basename(this_file)
    subject_id = filename.split('_')[0]
    
    clinical_data = {'Subject': subject_id}
    
    with open(this_file, 'r') as file:
        for line in file:
            line = line.strip()
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert to appropriate type
                try:
                    # Try to convert to number
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    # Keep as string
                    pass
                
                clinical_data[key] = value
    
    return pandas.DataFrame([clinical_data])

def findBouts(dataFrame, column_name_for_analysis, minimum_threshold, 
              minimum_duration_in_minutes, tolerance):
    """
    Find activity bouts in the data
    
    Parameters:
    - dataFrame: DataFrame with activity data
    - column_name_for_analysis: column to analyze (e.g., 'Steps')
    - minimum_threshold: minimum value to consider as active
    - minimum_duration_in_minutes: minimum duration for a bout
    - tolerance: number of minutes below threshold allowed within a bout
    
    Returns:
    - subsets: dictionary with subject IDs as keys, containing bout DataFrames
    - durations: dictionary with subject IDs as keys, containing bout durations
    """
    
    # Group by subject
    subjects = dataFrame['Subject'].unique()
    subsets = {}
    durations = {}
    
    for subject in subjects:
        subject_data = dataFrame[dataFrame['Subject'] == subject].copy()
        subject_data = subject_data.sort_values('DateTime').reset_index(drop=True)
        
        # Identify active periods (above threshold)
        subject_data['Active'] = subject_data[column_name_for_analysis] >= minimum_threshold
        
        # Find bouts
        bouts = []
        bout_durations = []
        
        i = 0
        while i < len(subject_data):
            if subject_data.loc[i, 'Active']:
                # Start of potential bout
                bout_start = i
                active_count = 1
                inactive_count = 0
                
                j = i + 1
                while j < len(subject_data):
                    if subject_data.loc[j, 'Active']:
                        active_count += 1
                        inactive_count = 0  # Reset inactive counter
                    else:
                        inactive_count += 1
                        if inactive_count > tolerance:
                            # End of bout
                            break
                    j += 1
                
                bout_end = j - inactive_count  # Don't include the tolerance period
                bout_duration = bout_end - bout_start
                
                # Check if bout meets minimum duration
                if bout_duration >= minimum_duration_in_minutes:
                    bout_data = subject_data.iloc[bout_start:bout_end].copy()
                    bouts.append(bout_data)
                    bout_durations.append(bout_duration)
                    i = bout_end
                else:
                    i += 1
            else:
                i += 1
        
        subsets[subject] = bouts
        durations[subject] = bout_durations
    
    return subsets, durations