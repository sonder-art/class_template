---
title: "JupyterLite Integration Test"
type: "documentation"
date: "2025-01-20"
author: "Framework Team"
summary: "Simple test of JupyterLite browser-based notebook integration"
difficulty: "medium"
estimated_time: 5
tags: ["jupyter", "python", "interactive", "testing"]
---

# JupyterLite Integration Test

This document tests the **two-tier JupyterLite integration** capabilities.

## Tier 1: Inline Python Execution Test

Simple Python execution directly in the documentation:

{{< python-exec >}}
print(" Hello from inline Python!")
print("This executes directly in the browser!")
x = 5 + 3
print(f"Simple calculation: 5 + 3 = {x}")

# Test a simple function
def greet(name):
    return f"Hello {name}!"

print(greet("Framework User"))
{{< /python-exec >}}

## Tier 2: Full Lab Environment Test

Launch the complete JupyterLite lab environment:

{{< jupyterlite-lab root="framework_documentation/Z_Tests/" title="Test Lab Environment" >}}

### What to Test:

1. **Inline Python**: Click "Run Python" on the code block above
2. **Lab Environment**: Click "Launch Lab Environment" to open JupyterLite
3. **Test Notebook**: In the lab, open `test_environment.ipynb` and run the cells
4. **File Access**: Verify the notebook can import from `test_utils.py`

### Expected Results:
- ✅ Inline code executes and shows output immediately  
- ✅ Lab environment opens in the browser
- ✅ Test notebook runs successfully
- ✅ Files in the directory are visible and importable

---

**Test Status**: If both features work, the JupyterLite integration is successful! 🎉 