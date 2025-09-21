# Grade Calculator
## Python Program to Calculate Letter Grade After Dropping Lowest Scores

**This program calculates a letter grade by dropping the lowest grades and computing the average of the remaining scores.**

1. The program sorts the grades and removes the specified number of lowest grades.
2. Use the function `grade_calc(grades_in, to_drop)` to calculate the final letter grade.

## Problem

**Write a function with the following signature:** `grade_calc(grades_in, to_drop)`.

```python
# Example usage
grades = [88, 92, 79, 85, 95]
num_to_drop = 2
letter_grade = grade_calc(grades, num_to_drop)
print(f"The letter grade after dropping the lowest {num_to_drop} grades is: {letter_grade}")
# Output: The letter grade after dropping the lowest 2 grades is: A
```