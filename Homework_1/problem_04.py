#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 21:22:49 2025

@author: sarojk
"""

# Function definition to filter odd and even numbers from a list
# Parameters: list of integers
# Returns: list containing two lists - first with even numbers, second with odd numbers
def odd_even_filter(numbers):
    even_numbers = []
    odd_numbers = []
    
    for num in numbers:
        if num % 2 == 0: # Check if the number is even
            even_numbers.append(num)
        else: # If the number is odd
            odd_numbers.append(num)
    
    return [even_numbers, odd_numbers]

# Example usage
input_list = [10, 21, 4, 45, 66, 93, 11, 70]
result = odd_even_filter(input_list)
print("Even numbers:", result[0])
print("Odd numbers:", result[1])