#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 20:39:39 2025

@author: sarojk
"""

# Function definition to manipulate a list of integers
# Parameter: list of integers (list_in)
# Returns: new list with manipulated values
def list_mangler(list_in):
    result = []
    for num in list_in:
        if num % 2 == 0:  # even check for multiplication by 2
            result.append(num * 2)
        else:  # odd check for multiplication by 3
            result.append(num * 3)
    return result

# Example usage of the function
input_list = [1, 2, 3, 4, 5]
output_list = list_mangler(input_list)
print(f"Input List: {input_list}")
print(f"Output List: {output_list}")