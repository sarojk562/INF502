#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 21:16:55 2025

@author: sarojk
"""

# Function definition to calculate letter grade after dropping lowest grades
# Parameters: list of integer grades (grades_in) and number of lowest grades to drop (to_drop)
# Returns: letter grade as a string
def grade_calc(grades_in, to_drop):
    if len(grades_in) <= to_drop:
        return 'F'
    
    # Sort grades and drop the lowest ones
    sorted_grades = sorted(grades_in)
    remaining_grades = sorted_grades[to_drop:]
    
    # Calculate average
    average = sum(remaining_grades) / len(remaining_grades)
    
    # Convert to letter grade
    if average >= 90:
        return 'A'
    elif average >= 80:
        return 'B'
    elif average >= 70:
        return 'C'
    elif average >= 60:
        return 'D'
    else:
        return 'F'
    
# Example usage
grades = [88, 92, 79, 85, 95]
num_to_drop = 2
letter_grade = grade_calc(grades, num_to_drop)
print(f"The letter grade after dropping the lowest {num_to_drop} grades is: {letter_grade}")