import math

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Sep 20 20:20:11 2025

@author: sarojk
"""
import math

# Function definition to calculate the length of the hypotenuse of a right triangle using the Pythagorean theorem
# Parameters: lengths of the two sides (length_of_a and length_of_b)
# Returns: length of the hypotenuse
def pythagoreanTheorem(length_of_a, length_of_b):
    return math.hypot(length_of_a, length_of_b)

# Example usage of the function
side_a = 3
side_b = 4

hypotenuse = pythagoreanTheorem(side_a, side_b)
print(f"The length of the hypotenuse is: {hypotenuse}")