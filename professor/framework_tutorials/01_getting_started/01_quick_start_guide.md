---
title: "Quick Start Guide"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Step-by-step guide to get started with the GitHub Class Template Repository framework"
difficulty: "easy"
estimated_time: 15
tags: ["tutorial", "getting-started", "setup"]
---

# Quick Start Guide

Welcome to the GitHub Class Template Repository framework! This guide will help you get started with creating and managing your class content.

## What You'll Learn

- How to fork and set up the template repository
- Understanding the directory structure
- Creating your first content files
- Using the built-in validation tools

## Prerequisites

- GitHub account
- Basic knowledge of Git
- Text editor (VS Code, Cursor, etc.)

## Step 1: Fork the Repository

1. **Visit the template repository** on GitHub
2. **Click "Fork"** to create your own copy
3. **Clone your fork** to your local machine:
   ```bash
   git clone https://github.com/YOUR_USERNAME/class_template.git
   cd class_template
   ```

## Step 2: Update Configuration

### Update DNA Configuration

Edit `dna.yml` in the repository root:

```yaml
professor_profile: YOUR_GITHUB_USERNAME
theme: default
search_mode: simple
index_generation: true
```

### Update Course Information

Edit `professor/course.yml`:

```yaml
course_name: "Your Course Name"
course_code: "CS101"
semester: "Fall 2025"
professor:
  name: "Your Name"
  email: "your.email@university.edu"
  office_hours: "Mon 2-4pm"
  office_location: "Room 123"
```

## Step 3: Understand the Structure

Your repository has this structure:

```
class_template/
├── dna.yml                 # Framework configuration
├── professor/              # Your content directory
│   ├── course.yml         # Course metadata
│   ├── class_notes/       # Main content
│   └── framework_code/    # Theme and tools
└── students/              # Student work areas
```

## Step 4: Create Your First Content

### Create a Chapter

```bash
mkdir professor/class_notes/01_introduction
```

### Create a Section

Create `professor/class_notes/01_introduction/01_welcome.md`:

```markdown
---
title: "Welcome to the Course"
type: "note"
date: 2025-01-21
author: "Your Name"
summary: "Introduction to the course and expectations"
difficulty: "easy"
tags: ["introduction", "welcome"]
---

# Welcome to the Course

This is your first content file! 

## Course Overview

Add your course overview here.

## What You'll Learn

- Topic 1
- Topic 2
- Topic 3
```

### Create Associated Code

Create `professor/class_notes/01_introduction/01_a_example_code.py`:

```python
# Example Python code for the introduction
print("Hello, class!")

def welcome_message(name):
    return f"Welcome to the course, {name}!"

# Test the function
print(welcome_message("Student"))
```

## Step 5: Create Homework

Create `professor/class_notes/01_introduction/hw_01.md`:

```markdown
---
title: "Homework 1: Getting Started"
type: "homework"
date: 2025-01-21
author: "Your Name"
summary: "First homework assignment"
difficulty: "easy"
estimated_time: 30
due_date: "2025-01-28"
points: 100
---

# Homework 1: Getting Started

## Overview

This homework helps you get familiar with the course tools.

## Instructions

1. Set up your development environment
2. Complete the exercises below
3. Submit your work via GitHub

## Exercise 1

Write a Python function that does X.

## Exercise 2

Answer the following questions about Y.
```

## Step 6: Validate Your Structure

Test that your content follows the naming conventions:

```bash
cd professor/framework_code/validation
python3 naming_conventions.py
python3 chapter_structure.py
```

## Step 7: Preview Your Site

1. **Install Hugo** (if not already installed)
2. **Set up the site**:
   ```bash
   cd professor/framework_code/hugo_config
   npm install
   hugo new site preview_site --config hugo.toml
   ```
3. **Copy your content** to the Hugo site
4. **Start the preview**:
   ```bash
   cd preview_site
   hugo server
   ```

## What's Next?

- **Add more content** following the naming conventions
- **Customize your theme** by copying `framework_code/themes/default/`
- **Set up GitHub Pages** for automatic publishing
- **Explore advanced features** like math rendering and search

## Getting Help

- **Check the validation output** if something isn't working
- **Review the framework documentation** for technical details
- **Look at the example content** for patterns to follow

## Common Patterns

### File Naming
- Sections: `01_introduction.md`, `02_basics.md`
- Code files: `01_a_intro_code.py`, `01_b_more_code.py`
- Homework: `hw_01.md`, `hw_01_a_solution.py`

### Chapter Organization
- Each chapter gets its own directory
- Use numbers for regular chapters: `01_`, `02_`, `03_`
- Use capital letters for appendices: `A_`, `B_`, `C_`

### Content Structure
- Always include YAML front matter
- Use descriptive titles and summaries
- Add appropriate tags and metadata

You're now ready to start creating amazing educational content with the framework! 