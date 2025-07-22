# Educational Callout Usage Guide

## Overview

This guide explains how to use the 8 educational callout types in your Quarto documents. Each callout serves a specific pedagogical purpose and follows accessibility standards (6:1 contrast ratio minimum).

**⚠️ IMPORTANT**: Custom callouts require the `quarto-custom-callout` extension. See [Installation](#installation) section below.

## Installation

### Step 1: Install the Extension
Run this command in your project directory:
```bash
quarto add coatless-quarto/custom-callout
```

### Step 2: Configure in _quarto.yml
The extension is already configured in this project's `_quarto.yml` with:
- 🤖 **prompt** - AI prompting guidance (teal #00B894)
- ✏️ **exercise** - In-class activities (amber #F39C12)  
- 📝 **homework** - Take-home assignments (coral #E17055)
- 🎯 **objective** - Learning goals (blue #4A90E2)
- 📚 **definition** - Formal definitions (purple #6C5CE7)

### Step 3: Add Filter to Format
The filter is automatically included via the global `_quarto.yml` configuration.

## The 8 Callout Types

Our callout system is organized into **4 semantic tiers** for clear educational structure:

### 📚 **INFORMATION TIER** (Understanding)
- 📖 **`note`** - General information and context (built-in)
- 📚 **`definition`** - Formal definitions and terminology (custom)

### 🎯 **ACTION TIER** (Doing)  
- ✏️ **`exercise`** - In-class practice activities (custom)
- 📝 **`homework`** - Take-home assignments (custom)
- 🤖 **`prompt`** - AI/LLM prompting guidance (custom)

### 💡 **ADVISORY TIER** (Guidance)
- ⭐ **`tip`** - Helpful advice and pro tips (built-in)
- ⚠️ **`warning`** - Important cautions and alerts (built-in)

### 🎓 **META TIER** (Learning Structure)
- 🎯 **`objective`** - Learning goals and outcomes (custom)

---

# Quick Reference

## Built-in Callouts (Standard Quarto)
```markdown
::: {.callout-note}
Your content here.
:::
```

## Custom Callouts (Extension Required)
```markdown
::: {.prompt}
Your content here.
:::
```

## With Custom Title
```markdown
::: {.prompt title="Your Custom Title"}
Your content here.
:::
```

---

# Detailed Usage Guide

## 📖 Note Callouts (Built-in)
**Purpose**: Provide general information, context, or background knowledge.

**When to use**:
- Explaining concepts that aren't formal definitions
- Providing historical context
- Offering additional information that supports understanding

**Examples**:
```markdown
::: {.callout-note}
Python was created by Guido van Rossum and first released in 1991. The name comes from the British comedy series "Monty Python's Flying Circus."
:::

::: {.callout-note title="How Git Works"}
Git tracks changes by creating "snapshots" of your project at different points in time. Each snapshot is called a "commit."
:::
```

## 📚 Definition Callouts (Custom)
**Purpose**: Present formal definitions, terminology, and key concepts.

**When to use**:
- Introducing new technical terms
- Providing formal definitions from academic sources
- Creating glossary-like references

**Examples**:
```markdown
::: {.definition}
**Version Control**: A system that tracks changes to files over time, allowing you to recall specific versions and collaborate safely.
:::

::: {.definition title="Machine Learning"}
A subset of artificial intelligence that enables computers to learn from experience without being explicitly programmed for every task.
:::
```

## ⭐ Tip Callouts (Built-in)
**Purpose**: Share helpful advice, shortcuts, best practices, and pro tips.

**When to use**:
- Teaching efficiency techniques
- Sharing keyboard shortcuts
- Providing tool-specific advice
- Highlighting best practices

**Examples**:
```markdown
::: {.callout-tip}
Use `Ctrl+Shift+P` in VS Code to open the command palette and access every feature without memorizing menus.
:::

::: {.callout-tip title="Terminal Time-Saver"}
Use the `Tab` key to auto-complete file and folder names. Type the first few letters and press Tab.
:::
```

## ⚠️ Warning Callouts (Built-in)
**Purpose**: Alert students to important cautions, common mistakes, and critical information.

**When to use**:
- Highlighting dangerous operations
- Pointing out common errors
- Explaining consequences of incorrect actions

**Examples**:
```markdown
::: {.callout-warning}
Be extremely careful with `rm -rf` commands. This permanently deletes files with no way to recover them.
:::

::: {.callout-warning title="Git Security"}
Never commit passwords, API keys, or personal data. Once committed, this information becomes part of your project's permanent history.
:::
```

## ✏️ Exercise Callouts (Custom)
**Purpose**: Present in-class practice activities and hands-on tasks.

**When to use**:
- Interactive coding exercises
- Step-by-step tutorials
- Activities that reinforce current lesson content

**Examples**:
```markdown
::: {.exercise}
**Practice: Your First Python Script**

1. Create a new file called `hello.py`
2. Add this code: `print("Hello, World!")`
3. Run it with `python3 hello.py`
4. Modify the message to include your name
:::

::: {.exercise title="Git Practice"}
Try this sequence:
1. `git status` - Check current state
2. `git add .` - Stage all changes  
3. `git commit -m "Your message"`
4. `git log --oneline` - See history
:::
```

## 📝 Homework Callouts (Custom)
**Purpose**: Assign take-home work and longer projects.

**When to use**:
- Multi-step projects requiring time outside class
- Research assignments
- Portfolio pieces

**Examples**:
```markdown
::: {.homework}
**Week 3 Assignment: Personal Website**

Create a portfolio website using Quarto:
1. Set up a new Quarto website project
2. Include an About page with your background
3. Add 2+ project pages
4. Deploy to GitHub Pages
5. Submit repository link by Friday, 11:59 PM
:::

::: {.homework title="Reading Assignment"}
Before next class, read Chapter 4 of "Python Crash Course" and complete the practice exercises.
:::
```

## 🤖 Prompt Callouts (Custom)
**Purpose**: Guide students in effective AI/LLM prompting and AI-assisted learning.

**When to use**:
- Teaching prompt engineering techniques
- Providing specific prompts to try
- Demonstrating AI tool usage

**Examples**:
```markdown
::: {.prompt}
**Try This Debugging Prompt**

"I'm learning Python and have a bug. Here's what I'm trying to do: [goal]. Here's my code: [code]. Here's the error: [error]. Can you explain what's wrong and suggest a fix?"
:::

::: {.prompt title="Code Explanation"}
"You are a patient coding instructor. Explain this Python code line by line in simple terms: [paste code]. Focus on what each part does and why it's necessary."
:::
```

## 🎯 Objective Callouts (Custom)
**Purpose**: Clearly state learning goals and expected outcomes.

**When to use**:
- Beginning of lessons or modules
- Setting clear expectations
- Helping students track progress

**Examples**:
```markdown
::: {.objective}
**Learning Objectives: Git Basics**

By the end of this lesson, you will be able to:
1. Explain what version control is and why it's important
2. Initialize a new Git repository
3. Stage and commit changes to files
4. Connect your local repository to GitHub
:::

::: {.objective title="Module Goals"}
**What You'll Master**
- Create Python lists and dictionaries
- Write custom functions
- Handle errors with try/except blocks
- Build a simple command-line tool
:::
```

---

# Best Practices

## Content Guidelines
- **Keep focused**: Each callout should have one clear purpose
- **Use appropriate length**: Tips are short, exercises can be longer
- **Write clearly**: Avoid jargon unless defined elsewhere
- **Test examples**: Ensure all code and instructions work

## Syntax Guidelines
- **Built-in callouts**: Use `.callout-type` format (note, tip, warning, important, caution)
- **Custom callouts**: Use `.type` format (prompt, exercise, homework, objective, definition)
- **Always test**: Render your document to verify callouts display correctly

## Accessibility
- ✅ All callouts automatically meet 6:1 contrast ratio
- ✅ Font sizes optimized for classroom presentations  
- ✅ Icons and colors work across all themes
- ✅ Content structure supports screen readers

## Common Patterns

### Lesson Structure
```markdown
::: {.objective}
Today's goals...
:::

::: {.callout-note}
Background information...
:::

::: {.definition}
Key terms...
:::

::: {.exercise}
Practice activity...
:::

::: {.homework}
Assignment for next week...
:::
```

### AI-Enhanced Learning
```markdown
::: {.prompt}
Try this prompt with your AI assistant...
:::

::: {.callout-tip}
When the AI response isn't clear, ask follow-up questions...
:::

::: {.exercise}  
Practice using the prompt above...
:::
```

---

# Theme Compatibility

All callouts work consistently across themes:
- **Evangelion**: Dark sci-fi with high contrast
- **Cyberpunk**: Neon colors with maintained readability  
- **Academic**: Professional traditional styling
- **Custom themes**: Automatically inherit your color palette

The system ensures educational content remains accessible and effective regardless of visual styling.

---

# Troubleshooting

## Extension Not Working
If custom callouts aren't rendering properly:

1. **Check installation**: Run `quarto add coatless-quarto/custom-callout`
2. **Verify configuration**: Ensure `_quarto.yml` includes the filter
3. **Test syntax**: Use `.prompt` not `.callout-prompt`
4. **Re-render**: Run `quarto render` to refresh

## Styling Issues
- Custom callouts inherit theme colors automatically
- The extension handles icons and structure
- Your CSS should focus on general improvements, not custom callout specifics

---

*For theme creation guidance, see [THEME_SYSTEM.md](THEME_SYSTEM.md)* 