---
title: "JupyterLite Integration Test"
type: "documentation"
date: "2025-01-20"
author: "Framework Team"
summary: "Test of JupyterLite integration with natural markdown content"
difficulty: "medium"
estimated_time: 5
tags: ["jupyter", "python", "interactive", "testing", "ux-ui"]
---

# JupyterLite Integration Test

This document tests the **two-tier JupyterLite integration** with **natural markdown content**.

## Tier 1: Inline Python Execution Tests

### Test 1: Pure Code Layout (Full Width)

Simple Python execution taking the full available width:

{{< python-editor >}}
print("🔥 Hello from full-width Python!")
print("This editor uses the complete available space")

# Test basic operations
numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
total = sum(numbers)
average = total / len(numbers)

print(f"Numbers: {numbers}")
print(f"Total: {total}")
print(f"Average: {average}")

# Test a function
def calculate_factorial(n):
    if n <= 1:
        return 1
    return n * calculate_factorial(n - 1)

print(f"Factorial of 5: {calculate_factorial(5)}")
{{< /python-editor >}}

### Test 2: Two-Column Layout (Code + Explanation)

{{< python-lesson >}}
  {{< lesson-explanation >}}
  ## Python List Comprehensions Tutorial

  This example demonstrates **list comprehensions** and **functional programming** concepts. The code editor appears alongside this explanation, making it perfect for tutorial-style content.

  ### 🎯 Try These Modifications:
  - Change the numbers in the range: `range(1, 20)`
  - Modify the filtering condition: `x % 3 == 0` (multiples of 3)
  - Try different operations: `x**3` (cubes), `x*2+1` (linear transform)
  - Add your own comprehensions

  ### 📚 Learning Objectives:
  - **List Comprehensions**: `[expression for item in iterable if condition]`
  - **Filter Conditions**: Using modulo `%` for even/odd detection
  - **Mathematical Operations**: Squares, transformations, aggregations
  - **Functional Programming**: Clean, readable code patterns

  ### 🧮 Mathematical Context:
  The sum of squares formula: $\sum_{i=1}^{n} i^2 = \frac{n(n+1)(2n+1)}{6}$

  For the first 5 odd numbers: $1^2 + 3^2 + 5^2 + 7^2 + 9^2 = 165$
  {{< /lesson-explanation >}}
  
  {{< python-editor layout="constrained" >}}
# List comprehensions and functional programming
print("🐍 Python List Comprehensions Demo")

# Generate numbers and apply operations
numbers = list(range(1, 11))
print(f"Original numbers: {numbers}")

# Even numbers only
evens = [x for x in numbers if x % 2 == 0]
print(f"Even numbers: {evens}")

# Squares of odd numbers
odd_squares = [x**2 for x in numbers if x % 2 == 1]
print(f"Odd squares: {odd_squares}")

# More complex operations
processed = [x * 2 + 1 for x in evens]
print(f"Processed evens: {processed}")

# Summary statistics
print(f"\nSummary:")
print(f"Total evens: {len(evens)}")
print(f"Sum of odd squares: {sum(odd_squares)}")
  {{< /python-editor >}}
{{< /python-lesson >}}




### What to Test:

1. **Full Width Layout**: Verify the first example uses complete available width with proper sizing
2. **Two-Column Layout**: Check that explanation appears left, Python editor right with equal heights
3. **Eva Theme Styling**: Confirm consistent purple accent colors and syntax highlighting
4. **Responsive Design**: Test on different screen sizes (mobile should stack vertically)
5. **Keyboard Shortcuts**: Try Ctrl+Enter to run code in both layouts
6. **Button Readability**: Ensure Run/Clear buttons are visible and accessible in constrained layout
7. **Output Formatting**: Check that Python output is properly formatted and colored
8. **Lab Environment**: Click "Launch Lab Environment" to open JupyterLite

### Expected Results:
- ✅ Unified component system with consistent Eva theme styling
- ✅ Full width editor expands properly for longer code
- ✅ Two-column layout maintains equal heights and proper alignment
- ✅ Syntax highlighting using Eva theme colors (purple, green, blue, orange)
- ✅ Mobile layout stacks vertically with proper spacing
- ✅ Keyboard shortcuts (Ctrl+Enter) work in both layouts
- ✅ Output area shows/hides dynamically with proper formatting
- ✅ Lab environment opens with local file access

---

**Test Status**: If all layout modes and auto-detection work correctly, the integration is successful! 🎉 