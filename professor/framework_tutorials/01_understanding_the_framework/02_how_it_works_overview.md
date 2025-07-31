---
title: "How the Framework Works"
type: "overview"
date: "2024-01-15"
author: "Framework Team"
summary: "Overview of the professor-to-student sync system and directory independence"
difficulty: "easy"
estimated_time: 7
tags: ["sync", "architecture", "workflow"]
---


The framework operates on a simple but powerful model: **professor as source of truth** with **smart synchronization** to student directories. This tutorial explains how this works in practice.

## Directory Structure

The framework uses a two-directory model:

```
repository/
├── professor/          # Source of truth - all authoritative content
│   ├── class_notes/
│   ├── framework_code/
│   └── config files
└── students/
    ├── alice/          # Alice's independent workspace
    ├── bob/            # Bob's independent workspace
    └── charlie/        # Charlie's independent workspace
```

## The Sync Process

The magic happens through `sync_student.py`, our smart synchronization system:

### 1. **Non-Destructive Updates**
- **Never overwrites** student-modified files
- **Only adds new files** or updates unchanged professor files
- **Preserves student work** completely

### 2. **Smart Exclusions**
The sync system automatically excludes:
- Auto-generated files (`hugo.toml`, `00_index.md`)
- Build artifacts (`hugo_generated/`)
- Student personal work
- Development cache files

### 3. **Framework Updates**
Students get:
- New course content from professor
- Framework improvements and bug fixes
- Theme updates and new features
- Configuration updates (when appropriate)

## Self-Contained Operation

Each student directory is **completely independent**:

- **Own configuration files** (`config.yml`, `course.yml`)
- **Own Hugo site generation** - no dependencies on professor directory
- **Own theme customization** - can modify colors, fonts, layout
- **Own content organization** - can add personal notes and projects

## Example Workflow

1. **Professor creates content** in `/professor/class_notes/02_new_topic/`
2. **Student runs sync**: `python3 professor/framework_code/scripts/sync_student.py`
3. **New content appears** in student's directory automatically
4. **Student's existing work** remains completely untouched
5. **Student builds site**: `hugo` in their directory

## Benefits of This Model

- **Scale infinitely** - works with 1 or 1000 students
- **No conflicts** - each student has their own space
- **Easy updates** - professor changes propagate automatically
- **Student freedom** - full control over their own environment
- **Backup built-in** - student work lives in their own Git repository

This architecture enables the automated, friction-free educational experience that makes the framework powerful for both professors and students. 