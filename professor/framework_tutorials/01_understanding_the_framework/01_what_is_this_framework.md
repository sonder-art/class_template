---
author: Framework Team
date: '2024-01-15'
difficulty: easy
estimated_time: 5
slug: 2024-01-15-tutorial-what-is-this-framework
slug_locked: true
slug_source: creation_context
summary: Introduction to the class template framework and its core principles
tags:
- introduction
- overview
- philosophy
title: What is this Framework?
type: tutorial
---


This GitHub Class Template Repository framework solves a fundamental problem in educational content delivery: how to create a consistent, automated, and flexible system for professors to distribute course materials while allowing students to maintain their own independent work environments.

## The Problem We Solve

Traditional course websites require either:
- **Static sites** that are hard to update and customize
- **Complex LMS systems** that lock you into specific platforms
- **Manual file sharing** that becomes chaotic with multiple students

Our framework provides a **third option**: a structured, automated system that gives professors full control over content while giving students their own customizable workspace.

## Core Philosophy

The framework is built on three key principles from `core.md`:

1. **Professor as Source of Truth** - All authoritative content lives in `/professor`
2. **Student Independence** - Each student works in `/students/<username>` with full autonomy
3. **Automation First** - Everything that can be automated, will be automated

## How It Works

The framework uses a **template repository** approach where:

- Professors maintain the master template with all course content
- Students fork the repository and work in their own directories
- A smart sync system keeps student directories updated without overwriting their work
- Each directory generates its own independent website

This approach scales from a single student to hundreds of students while maintaining clean separation and avoiding conflicts.

## What You Get

When properly set up, you'll have:
- **Your own course website** built automatically from your content
- **Sync system** that pulls updates from your professor safely
- **Professional theme** optimized for educational content
- **Self-contained setup** that works independently

The next tutorial will explain exactly how this sync and independence model works in practice. 