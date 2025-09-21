# Odd Even Filter
## Python Program to Separate Odd and Even Numbers

**This program filters a list of integers and separates them into even and odd numbers.**

1. The program iterates through each number in the input list.
2. Use the function `odd_even_filter(numbers)` to separate the numbers into two lists.

## Problem

**Write a function with the following signature:** `odd_even_filter(numbers)`.

```python
# Example usage
input_list = [10, 21, 4, 45, 66, 93, 11, 70]
result = odd_even_filter(input_list)
print("Even numbers:", result[0])
print("Odd numbers:", result[1])
# Output: Even numbers: [10, 4, 66, 70]
# Output: Odd numbers: [21, 45, 93, 11]
```