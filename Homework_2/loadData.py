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
        merged = loadFitbitFile(path, measures[0])
    else:
        # it was a directory that was passed in, so let's make use of it
        print('Directory name passed in')
        # for each of the measures, we want to find all of the files with those measures, and load them.
        for this_measure in measures:
            print(this_measure)
            paths = [f.path for f in os.scandir(path) if (f.is_file() and (this_measure in f.name))]

            for this_file in paths:
                data = loadFitbitFile(this_file, this_measure)
                # the above will call your loadFitbitFile() function
                # and that will return some data.
                # you will want to concat this data with any existing data - OF THE SAME MEASURE
                # concatenated_data = pandas.concat([df1, df2], ignore_index=True)

            # but what about once you have loaded all the files for that measure, then it's time to merge those with
            # the other data from other measures, right?
            # merged_data = pandas.merge(previously_merged, concatenated_data, on=['Subject', 'DateTime'], how='inner')
            # but I am skipping a few steps here, which you'll need to fill in.
    return merged_data

def loadFitbitFile(this_file, measure):
    date_format = '%m/%d/%Y %I:%M:%S %p'
    delta = timedelta(minutes=1)
    filename = os.path.basename(this_file)
    # okay, so we have the filename, how do we find what subject number this is for?

    # open the file
    # how can we read this file line by line?
    # do we need that first line?
    # you need to extract the datetime info, in string format.  This will convert that string into a working datatime format
    date_object = datetime.strptime(datetime_in_string_format, date_format)
    # and this will fill out all the minutes for that hour
    this_hour = date_object + (delta*np.arange(60))

    # don't forget to close the file!
    file_handler.close()
    return single_file_worth_of_data

def loadActigraph(path):
    try:
        os.scandir(path)
    except NotADirectoryError:
        # it wasn't a directory that was passed in
        print('Filename provided')
    # you can fill in the rest, I know you can.
    # do watch out for the funkyness of the actigraph files though.
    # how can you skip some number of lines when reading in a csv to a DataFrame?
    # dang it, those columns aren't labeled!  So ... how can you specify column names on that load as well?

def loadActigraphFile(this_file):
    date_format = '%m/%d/%Y %H:%M:%S' # the time format is a bit different in the actigraph.  Use this one.
    delta = timedelta(minutes=1)
    # maybe you need to read N lines of the file, and look for clues as to the start date and start time?