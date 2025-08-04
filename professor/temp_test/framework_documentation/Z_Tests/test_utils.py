"""
Test utilities for JupyterLite integration testing
This file should be visible and importable from notebooks in the same directory.
"""

def greet_student(name):
    """Greet a student with a framework message."""
    return f"Hello {name}! Welcome to the GitHub Class Template Framework! 🎓"

def calculate_simple(a, b):
    """Simple calculation to test function imports."""
    return a + b

def get_framework_info():
    """Return information about the framework environment."""
    return {
        "framework": "GitHub Class Template",
        "python_env": "JupyterLite + Pyodide",
        "features": ["Inline execution", "Full lab environment", "File imports"]
    }

def demonstrate_data_processing():
    """Show a simple data processing example."""
    # Simulate some data processing
    data = [1, 2, 3, 4, 5]
    processed = [x * 2 for x in data]
    return {
        "original": data,
        "processed": processed,
        "sum": sum(processed)
    }

# Test constants
FRAMEWORK_VERSION = "1.0.0"
TEST_STATUS = "Active"

if __name__ == "__main__":
    print("🧪 Test utilities loaded successfully!")
    print(f"Framework version: {FRAMEWORK_VERSION}")
    print(f"Test status: {TEST_STATUS}") 