---
title: "Homework {{ .Name | replaceRE `hw_(\d+).*` `$1` }}: {{ replace (.Name | replaceRE `hw_\d+_?(.*)` `$1`) "-" " " | title }}"
type: "homework"
date: {{ .Date }}
author: "{{ .Site.Params.professor_name }}"
summary: "Homework assignment with practical exercises"
draft: false

# Homework-specific metadata
difficulty: "medium"     # easy | medium | hard
estimated_time: 60      # minutes
due_date: ""            # YYYY-MM-DD format
points: 100             # total points
submission_format: "notebook"  # notebook | markdown | code | mixed

# Optional metadata fields
prerequisites: []       # array of slugs for required knowledge
tags: []               # list of tags
resources: []          # list of helpful resources
---

# Homework {{ .Name | replaceRE `hw_(\d+).*` `$1` }}: {{ replace (.Name | replaceRE `hw_\d+_?(.*)` `$1`) "-" " " | title }}

## Assignment Overview

Brief description of what this homework covers and learning objectives.

### Learning Objectives
- Objective 1
- Objective 2
- Objective 3

### Due Date
**Due:** [Insert due date]

### Points
**Total Points:** {{ .Params.points }}

## Instructions

Detailed instructions for completing this assignment.

### Setup

Any setup instructions or requirements.

### Part 1: [Task Name]

Description of the first part of the assignment.

### Part 2: [Task Name]

Description of the second part of the assignment.

## Submission Requirements

- List submission requirements
- File formats expected
- Naming conventions
- What to include

## Grading Rubric

| Criteria | Points | Description |
|----------|---------|-------------|
| Criterion 1 | XX | Description |
| Criterion 2 | XX | Description |
| Code Quality | XX | Clean, well-commented code |
| Documentation | XX | Clear explanations and documentation |

## Resources

- [Helpful Resource 1](url)
- [Helpful Resource 2](url)

## Getting Help

If you need help with this assignment:
- Office hours: {{ .Site.Params.office_hours }}
- Email: {{ .Site.Params.email }}
- [Course discussion forum/repository]({{ .Site.Params.github_repo }}) 