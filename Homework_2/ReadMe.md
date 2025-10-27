# Homework 2
In this homework, you will bring together Python functions, file handling, error handling, modules, and data science. Specifically, you are tasked with reading in disparate datasets, data taken from two different wearable technologies and those in a "note" format.  Once loaded in a Pandas DataFrame, you will need to perform a regression to model the observations from one device using measures from the other.

## The Data
In the data directory, you should find three more directories:
* actigraph
* clinical
* fitbit

You will find a data dictionary for the Actigraph data in that folder.

The clinical data is a basic text file, which you should be able to parse.

The Fitbit data is formatted such that each file includes a single measurement variable, with each row corresponding to an hour, and each column is the corresponding minute.  See the header to get a better understanding of this format.

## The task
You will do an analysis on the data to see if you can predict the Actigraph step count using the inputs of Fitbit metrics, which includes step counts.  To do so though, we first need to identify how well these correlate, and what the typical errors might be.  It will be easiest to have all Actigraph and Fitbit data in a single DataFrame.  Please generate some plots to visualize the data, and to show the difference between your model, y_pred = f(X_fitbit), and the Fitbit step count.

Once you have a model in hand, use this model to correct the Fitbit step counts, and then identify bouts of activity.  Bouts of activity are typically defined by elevated activity levels (use steps here though) that are sustained for several minutes, with some tolerance for reduced activity in some epoch.  Think about what it takes for you to walk to your car, another part of campus, or even home.  You can probably walk for a few minutes (or longer) uninterrupted, but eventually have to stop and wait for a crosswalk signal, or traffic, or maybe even to catch the bus.  I want you to think about how long of an epoch would be appropriate in estimating if someone is walking further than from class to the bathroom, and think about what kind of tolerance would be appropriate.

Identify the bouts, and store this into a dictionary (or dictionary of dictionary, dictionary of lists, etc) so that you can then also compute the duration of these bouts and the total steps taken.  With a collection of bouts in hand, AND the clinical information such as age , I want you to generate a plot that will allow you to assess the hypothesis that the number of steps (or bouts) that one takes in a day, or week, is predictable.

## Solution Requirements
I want you to develop the habit of writing extensible code.  Sure, you could to this entire project with a single script, but that's _not_ an approach that would make it easy to change the dataset, change the analysis, or to even just open one single file.  You can do better than a single script.

I have outline what I think will be required modules and a few of what I think will be required functions to complete this task.  For a few steps, I have also provided you with some example code that you should be able to use as-is, or should be able to use as a springboard to writing the code you actually need.  Specifically, I want you to format your code to follow these signatures:

```python
fitbit_dataframe = loadFitbit(file_or_directory_name, 
                              [file_search_term])

actigraph_dataframe = loadActigraph(file_or_directory_name, 
                                    [file_search_term])
```
These two functions, loadFitbit() and loadActigraph(), should live in the same file.  You probably want to put a function to load the clinical data in there too.

loadFitbit() and loadActigraph() must both return a Pandas DataFrame.  You will need to join these in a way that preserves subject number and measurement time - you want to know that for each row, you have all measures from both devices at the same minute.

```python
subsets, duration = findBouts(dataFrame, 
                              column_name_for_analysis, 
                              minimum_threshold, 
                              minimum_duration_in_minutes, 
                              tolerance)
```
Where the subsets variable needs to be either a dictionary of dataframes, or a list of dataframes where said dataframes contain the original data for the bout.  The duration variable needs to follow a similar design.  Store these into a larger dictionary such that the keys in that dictionary are subject IDs.

In this dictionary, you should be able to reference a subject by key, and then reference characteristics, such as the set of bouts, the properties of bouts, and the clinical descriptors, by keys.

## Special Notes
This exercise is intended to flex your skills that you have developed over the past few weeks; it is not intended to test your statistical analysis knowledge.  I do not expect you to use ANY advanced methods.  While _not_ the right approach, you can use a basic linear regression.  Here's an example:

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X, y)
model.score(X, y)
y_pred = model.predict(X)
```

And if you want to do something closer to appropriate with your model, you can subsample from your observations to create a training set and a testing set.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=0)
model = LinearRegression()
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
```