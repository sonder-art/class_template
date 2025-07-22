---
title: "Content Creation Guide"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Learn how to create and organize educational content using the framework conventions"
difficulty: "easy"
estimated_time: 20
tags: ["tutorial", "content-creation", "markdown", "metadata"]
---

# Content Creation Guide

This guide teaches you how to create well-structured educational content using the GitHub Class Template Repository framework.

## What You'll Learn

- How to structure your content hierarchically
- Writing effective metadata (YAML front matter)
- Organizing files with naming conventions
- Creating different types of content (notes, homework, code)

## Content Structure Basics

### The Three-Level Hierarchy

The framework uses a three-level structure:

1. **Categories** - Top-level organization (e.g., `class_notes/`)
2. **Chapters** - Major topics (e.g., `01_introduction/`)
3. **Sections** - Individual content files (e.g., `01_welcome.md`)

### Example Structure

```
professor/class_notes/
├── 01_introduction/
│   ├── 01_course_overview.md
│   ├── 01_a_setup_code.py
│   ├── 02_expectations.md
│   └── hw_01.md
├── 02_fundamentals/
│   ├── 01_basic_concepts.md
│   ├── 02_practical_examples.md
│   └── 02_a_example_code.py
└── A_advanced_topics/
    ├── 01_advanced_concepts.md
    └── 01_a_advanced_code.py
```

## File Naming Conventions

### Primary Content Files

Use numbers for main content:
- `01_introduction.md` - First section
- `02_basics.md` - Second section
- `03_advanced.md` - Third section

### Associated Code Files

Use letters after the number:
- `01_a_intro_code.py` - Code for section 01
- `01_b_more_intro_code.py` - More code for section 01
- `02_a_basic_examples.py` - Code for section 02

### Homework Files

Use `hw_` prefix:
- `hw_01.md` - First homework assignment
- `hw_01_a_starter_code.py` - Starter code for homework 01
- `hw_02.md` - Second homework assignment

### Chapter Directories

- **Regular chapters**: `01_introduction/`, `02_basics/`
- **Appendix chapters**: `A_advanced_topics/`, `B_references/`

## Writing Effective Metadata

### Required Fields

Every content file needs YAML front matter:

```yaml
---
title: "Your Content Title"
type: "note"
date: 2025-01-21
author: "Your Name"
summary: "Brief description of the content"
---
```

### Optional But Recommended Fields

```yaml
---
title: "Advanced Python Concepts"
type: "note"
date: 2025-01-21
author: "Dr. Jane Doe"
summary: "Exploring advanced Python features and best practices"
difficulty: "medium"        # easy, medium, hard
estimated_time: 30         # minutes
tags: ["python", "advanced", "programming"]
prerequisites: ["01_python_basics"]
---
```

### Homework-Specific Fields

```yaml
---
title: "Homework 2: Data Analysis"
type: "homework"
date: 2025-01-21
author: "Dr. Jane Doe"
summary: "Analyze datasets using Python and pandas"
difficulty: "medium"
estimated_time: 90
due_date: "2025-02-01"
points: 150
submission_format: "notebook"
---
```

## Content Types

### Regular Notes

Standard educational content:

```markdown
---
title: "Introduction to Variables"
type: "note"
summary: "Learn about variables and data types"
---

# Introduction to Variables

Variables are fundamental building blocks...

## What are Variables?

A variable is a named storage location...

## Examples

Here are some examples:
```

### Homework Assignments

Structured assignments with clear requirements:

```markdown
---
title: "Homework 1: Python Basics"
type: "homework"
points: 100
due_date: "2025-02-01"
---

# Homework 1: Python Basics

## Assignment Overview

This homework covers...

## Instructions

1. Complete the following exercises
2. Submit your code files
3. Include documentation

## Exercise 1 (25 points)

Write a function that...
```

### Code Files

Well-documented code examples:

```python
"""
Example code for Section 01: Introduction to Functions

This file demonstrates basic function concepts
and provides examples students can run and modify.
"""

def greet_student(name):
    """
    Greet a student by name.
    
    Args:
        name (str): The student's name
        
    Returns:
        str: A greeting message
    """
    return f"Hello, {name}! Welcome to the course."

# Example usage
if __name__ == "__main__":
    # Test the function
    message = greet_student("Alice")
    print(message)
```

## Best Practices

### Writing Clear Content

1. **Start with overview** - Explain what the content covers
2. **Use clear headings** - Structure content logically
3. **Include examples** - Show concepts in action
4. **Add summaries** - Reinforce key points

### Organizing Files

1. **Keep chapters focused** - One major topic per chapter
2. **Order logically** - Build concepts progressively
3. **Group related content** - Keep code with relevant sections
4. **Use consistent naming** - Follow conventions strictly

### Creating Metadata

1. **Write descriptive titles** - Make content discoverable
2. **Add helpful summaries** - Enable quick scanning
3. **Include realistic time estimates** - Help students plan
4. **Use consistent tags** - Enable search and filtering

## Validation Tools

### Check Your Work

Always validate your content structure:

```bash
# Check naming conventions
cd professor/framework_code/validation
python3 naming_conventions.py

# Check directory structure
python3 chapter_structure.py
```

### Common Validation Errors

- **Missing metadata**: All files need YAML front matter
- **Wrong naming**: Files must follow number/letter conventions
- **Missing index**: Chapters need `00_index.md` (auto-generated)
- **Broken sequences**: Numbers should be consecutive (01, 02, 03)

## Mathematical Content

### Inline Math

Use single dollar signs for inline equations:
```markdown
The formula for area is $A = \pi r^2$ where r is the radius.
```

### Block Math

Use double dollar signs for displayed equations:
```markdown
$$
E = mc^2
$$
```

### Complex Equations

```markdown
$$
\int_{-\infty}^{\infty} \frac{1}{\sqrt{2\pi\sigma^2}} e^{-\frac{(x-\mu)^2}{2\sigma^2}} dx = 1
$$
```

## Code Integration

### Syntax Highlighting

The framework supports many languages:

````markdown
```python
def example_function():
    return "Hello, World!"
```

```javascript
function greet() {
    console.log("Hello from JavaScript!");
}
```

```bash
# Shell commands
cd my_directory
ls -la
```
````

### Code References

Link to associated code files:
```markdown
See the complete implementation in [example_code.py](01_a_example_code.py).
```

## Testing Your Content

### Preview with Hugo

1. Set up Hugo preview (see Quick Start Guide)
2. Check that content renders correctly
3. Verify navigation works
4. Test math rendering
5. Validate links and references

### Content Checklist

Before publishing, verify:
- [ ] All files have proper naming
- [ ] Metadata is complete and accurate
- [ ] Content is well-structured with clear headings
- [ ] Code examples work and are well-documented
- [ ] Math equations render correctly
- [ ] Validation tools pass without errors

## Next Steps

- Explore [theme customization](../03_customizing_themes/)
- Learn about [advanced features](../../framework_documentation/)
- Check out example content in the repository

Remember: Good content takes time to create, but following these conventions makes it easier to maintain and helps students learn more effectively! 