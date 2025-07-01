# Educational Callout Usage Guide

## Overview

This guide explains how to use the 8 educational callout types in your Quarto documents. Each callout serves a specific pedagogical purpose and follows accessibility standards (6:1 contrast ratio minimum).

## The 8 Callout Types

Our callout system is organized into **4 semantic tiers** for clear educational structure:

### 📚 **INFORMATION TIER** (Understanding)
- 📖 **`note`** - General information and context
- 📚 **`definition`** - Formal definitions and terminology

### 🎯 **ACTION TIER** (Doing)  
- ✏️ **`exercise`** - In-class practice activities
- 📝 **`homework`** - Take-home assignments
- 🤖 **`prompt`** - AI/LLM prompting guidance

### 💡 **ADVISORY TIER** (Guidance)
- ⭐ **`tip`** - Helpful advice and pro tips
- ⚠️ **`warning`** - Important cautions and alerts

### 🎓 **META TIER** (Learning Structure)
- 🎯 **`objective`** - Learning goals and outcomes

---

# Quick Reference

## Basic Syntax
```markdown
::: {.callout-type}
Your content here.
:::
```

## With Custom Title
```markdown
::: {.callout-type title="Your Custom Title"}
Your content here.
:::
```

---

# Detailed Usage Guide

## 📖 Note Callouts
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

## 📚 Definition Callouts
**Purpose**: Present formal definitions, terminology, and key concepts.

**When to use**:
- Introducing new technical terms
- Providing formal definitions from academic sources
- Creating glossary-like references

**Examples**:
```markdown
::: {.callout-definition}
**Version Control**: A system that tracks changes to files over time, allowing you to recall specific versions and collaborate safely.
:::

::: {.callout-definition title="Machine Learning"}
A subset of artificial intelligence that enables computers to learn from experience without being explicitly programmed for every task.
:::
```

## ⭐ Tip Callouts
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

## ⚠️ Warning Callouts
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

## ✏️ Exercise Callouts
**Purpose**: Present in-class practice activities and hands-on tasks.

**When to use**:
- Interactive coding exercises
- Step-by-step tutorials
- Activities that reinforce current lesson content

**Examples**:
```markdown
::: {.callout-exercise}
**Practice: Your First Python Script**

1. Create a new file called `hello.py`
2. Add this code: `print("Hello, World!")`
3. Run it with `python3 hello.py`
4. Modify the message to include your name
:::

::: {.callout-exercise title="Git Practice"}
Try this sequence:
1. `git status` - Check current state
2. `git add .` - Stage all changes  
3. `git commit -m "Your message"`
4. `git log --oneline` - See history
:::
```

## 📝 Homework Callouts
**Purpose**: Assign take-home work and longer projects.

**When to use**:
- Multi-step projects requiring time outside class
- Research assignments
- Portfolio pieces

**Examples**:
```markdown
::: {.callout-homework}
**Week 3 Assignment: Personal Website**

Create a portfolio website using Quarto:
1. Set up a new Quarto website project
2. Include an About page with your background
3. Add 2+ project pages
4. Deploy to GitHub Pages
5. Submit repository link by Friday, 11:59 PM
:::

::: {.callout-homework title="Reading Assignment"}
Before next class, read Chapter 4 of "Python Crash Course" and complete the practice exercises.
:::
```

## 🤖 Prompt Callouts
**Purpose**: Guide students in effective AI/LLM prompting and AI-assisted learning.

**When to use**:
- Teaching prompt engineering techniques
- Providing specific prompts to try
- Demonstrating AI tool usage

**Examples**:
```markdown
::: {.callout-prompt}
**Try This Debugging Prompt**

"I'm learning Python and have a bug. Here's what I'm trying to do: [goal]. Here's my code: [code]. Here's the error: [error]. Can you explain what's wrong and suggest a fix?"
:::

::: {.callout-prompt title="Code Explanation"}
"You are a patient coding instructor. Explain this Python code line by line in simple terms: [paste code]. Focus on what each part does and why it's necessary."
:::
```

## 🎯 Objective Callouts
**Purpose**: Clearly state learning goals and expected outcomes.

**When to use**:
- Beginning of lessons or modules
- Setting clear expectations
- Helping students track progress

**Examples**:
```markdown
::: {.callout-objective}
**Learning Objectives: Git Basics**

By the end of this lesson, you will be able to:
1. Explain what version control is and why it's important
2. Initialize a new Git repository
3. Stage and commit changes to files
4. Connect your local repository to GitHub
:::

::: {.callout-objective title="Module Goals"}
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

## Accessibility
- ✅ All callouts automatically meet 6:1 contrast ratio
- ✅ Font sizes optimized for classroom presentations  
- ✅ Icons and colors work across all themes
- ✅ Content structure supports screen readers

## Common Patterns

### Lesson Structure
```markdown
::: {.callout-objective}
Today's goals...
:::

::: {.callout-note}
Background information...
:::

::: {.callout-definition}
Key terms...
:::

::: {.callout-exercise}
Practice activity...
:::

::: {.callout-homework}
Assignment for next week...
:::
```

### AI-Enhanced Learning
```markdown
::: {.callout-prompt}
Try this prompt with your AI assistant...
:::

::: {.callout-tip}
When the AI response isn't clear, ask follow-up questions...
:::

::: {.callout-exercise}  
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

*For theme creation guidance, see [THEME_SYSTEM.md](THEME_SYSTEM.md)*

---

# Detailed Usage Guide

## 📖 Note Callouts
**Purpose**: Provide general information, context, or background knowledge.

**When to use**:
- Explaining concepts that aren't formal definitions
- Providing historical context
- Offering additional information that supports understanding
- Clarifying complex topics

**Tone**: Informative, neutral, explanatory

### Examples:

```markdown
::: {.callout-note}
Python was created by Guido van Rossum and first released in 1991. The name comes from the British comedy series "Monty Python's Flying Circus," not the snake.
:::

::: {.callout-note title="How Git Works"}
Git tracks changes to files by creating "snapshots" of your entire project at different points in time. Each snapshot is called a "commit."
:::
```

**Best Practices**:
- Keep notes focused and relevant to the current topic
- Use when students need context but not a formal definition
- Ideal for "good to know" information

---

## 📚 Definition Callouts
**Purpose**: Present formal definitions, terminology, and key concepts.

**When to use**:
- Introducing new technical terms
- Providing formal definitions from academic sources
- Explaining jargon or domain-specific language
- Creating a glossary-like reference

**Tone**: Precise, formal, authoritative

### Examples:

```markdown
::: {.callout-definition}
**Version Control**: A system that tracks changes to files over time, allowing you to recall specific versions, compare changes, and collaborate with others safely.
:::

::: {.callout-definition title="Machine Learning"}
A subset of artificial intelligence (AI) that enables computers to learn and improve from experience without being explicitly programmed for every task.
:::
```

**Best Practices**:
- Start with the term in **bold**
- Use clear, concise language
- Include the essential characteristics that distinguish the term
- Avoid circular definitions

---

## ⭐ Tip Callouts
**Purpose**: Share helpful advice, shortcuts, best practices, and pro tips.

**When to use**:
- Teaching efficiency techniques
- Sharing keyboard shortcuts
- Providing tool-specific advice
- Offering troubleshooting suggestions
- Highlighting best practices

**Tone**: Friendly, helpful, experienced

### Examples:

```markdown
::: {.callout-tip}
Use `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (Mac) to open the command palette in VS Code. This gives you access to every feature without memorizing menus.
:::

::: {.callout-tip title="Terminal Time-Saver"}
Use the `Tab` key to auto-complete file and folder names in the terminal. Type the first few letters and press Tab – it will complete the name or show you options.
:::

::: {.callout-tip title="Git Best Practice"}
Write commit messages in the present tense: "Add user authentication" instead of "Added user authentication." This matches Git's own convention.
:::
```

**Best Practices**:
- Focus on actionable advice
- Include specific examples when possible
- Use descriptive titles for complex tips
- Test your tips to ensure they work

---

## ⚠️ Warning Callouts
**Purpose**: Alert students to important cautions, common mistakes, and critical information.

**When to use**:
- Highlighting dangerous operations (deleting files, etc.)
- Pointing out common errors students make
- Explaining consequences of incorrect actions
- Noting when something might not work as expected

**Tone**: Serious, direct, protective

### Examples:

```markdown
::: {.callout-warning}
Be extremely careful with `rm -rf` commands. This will permanently delete files and folders with no way to recover them. Always double-check the path before pressing Enter.
:::

::: {.callout-warning title="Common Git Mistake"}
Never commit sensitive information like passwords, API keys, or personal data. Once committed to Git, this information becomes part of your project's permanent history.
:::

::: {.callout-warning title="Version Compatibility"}
This tutorial assumes Python 3.8 or higher. If you're using an older version, some code examples may not work correctly.
:::
```

**Best Practices**:
- Be specific about what could go wrong
- Explain the consequences clearly
- Offer alternatives or solutions when possible
- Use strong, clear language

---

## ✏️ Exercise Callouts
**Purpose**: Present in-class practice activities and hands-on tasks.

**When to use**:
- Interactive coding exercises
- Step-by-step tutorials
- Practice problems to solve immediately
- Activities that reinforce current lesson content

**Tone**: Engaging, instructional, encouraging

### Examples:

```markdown
::: {.callout-exercise}
**Practice: Your First Python Script**

1. Create a new file called `hello.py`
2. Add this code: `print("Hello, World!")`
3. Run it with `python3 hello.py`
4. Modify the message to include your name

What output do you see?
:::

::: {.callout-exercise title="Git Practice"}
Try this sequence of Git commands in your project:

1. `git status` - What files are changed?
2. `git add .` - Stage all changes
3. `git commit -m "Your message here"`
4. `git log --oneline` - See your commit history
:::
```

**Best Practices**:
- Provide clear, numbered steps
- Include expected outcomes
- Make exercises achievable in class time
- Build on previous knowledge

---

## 📝 Homework Callouts
**Purpose**: Assign take-home work and longer projects.

**When to use**:
- Multi-step projects that require time outside class
- Research assignments
- Portfolio pieces
- Preparation for next class

**Tone**: Clear, structured, motivating

### Examples:

```markdown
::: {.callout-homework}
**Week 3 Assignment: Personal Website**

Create a personal portfolio website using Quarto:

1. Set up a new Quarto website project
2. Include an About page with your background
3. Add at least 2 project pages showcasing your work
4. Deploy your site to GitHub Pages
5. Submit the GitHub repository link by Friday, 11:59 PM

**Evaluation criteria**: Design clarity, content quality, working deployment
:::

::: {.callout-homework title="Reading Assignment"}
**Before next class**, read Chapter 4 of "Python Crash Course" and complete the practice exercises at the end. We'll discuss your solutions in our next session.
:::
```

**Best Practices**:
- Include clear deliverables
- Specify due dates and submission methods
- Provide evaluation criteria
- Break complex assignments into steps

---

## 🤖 Prompt Callouts
**Purpose**: Guide students in effective AI/LLM prompting and AI-assisted learning.

**When to use**:
- Teaching prompt engineering techniques
- Providing specific prompts to try
- Demonstrating AI tool usage
- Showing how to get better AI responses

**Tone**: Instructional, strategic, empowering

### Examples:

```markdown
::: {.callout-prompt}
**Try This Prompt for Debugging**

When your code isn't working, try this prompt structure:

"I'm learning Python and have a bug in my code. Here's what I'm trying to do: [explain your goal]. Here's my code: [paste code]. Here's the error message: [paste error]. Can you explain what's wrong and suggest a fix?"
:::

::: {.callout-prompt title="Code Explanation Prompt"}
**Getting Code Explanations**

"You are a patient coding instructor. Please explain this Python code line by line in simple terms, as if teaching a beginner:

[paste your code here]

Focus on what each part does and why it's necessary."
:::

::: {.callout-prompt title="Advanced: Prompt Refinement"}
Start with: "Explain Python functions to a beginner"

Then refine to: "You are a coding instructor. Explain Python functions using cooking analogies. Include: what functions are, why they're useful, how to create them, and a simple example. Make it engaging for someone who's never programmed before."

Notice how the refined prompt is more specific and contextual?
:::
```

**Best Practices**:
- Provide complete, copy-paste ready prompts
- Explain why the prompt works
- Show before/after examples of prompt refinement
- Teach prompt engineering as a skill

---

## 🎯 Objective Callouts
**Purpose**: Clearly state learning goals and expected outcomes.

**When to use**:
- Beginning of lessons or modules
- Outlining what students will achieve
- Setting clear expectations
- Helping students track their progress

**Tone**: Clear, measurable, motivating

### Examples:

```markdown
::: {.callout-objective}
**Learning Objectives: Introduction to Git**

By the end of this lesson, you will be able to:

1. Explain what version control is and why it's important
2. Initialize a new Git repository
3. Stage and commit changes to files
4. View your project's commit history
5. Connect your local repository to GitHub
:::

::: {.callout-objective title="Module 2 Goals"}
**What You'll Master**

- Create and manipulate Python lists and dictionaries
- Write and use custom functions
- Handle errors gracefully with try/except blocks
- Read and write data to files
- Build a simple command-line tool
:::
```

**Best Practices**:
- Use measurable verbs (create, explain, demonstrate, analyze)
- Keep objectives achievable within the lesson timeframe
- Align with assessment criteria
- Review objectives at lesson end

---

# Implementation Syntax

## Basic Syntax
```markdown
::: {.callout-type}
Your content here.
:::
```

## With Custom Title
```markdown
::: {.callout-type title="Your Custom Title"}
Your content here.
:::
```

## Available Types
- `note` - 📖 General information
- `definition` - 📚 Formal definitions  
- `tip` - ⭐ Helpful advice
- `warning` - ⚠️ Important cautions
- `exercise` - ✏️ In-class activities
- `homework` - 📝 Take-home assignments
- `prompt` - 🤖 AI prompting guidance
- `objective` - 🎯 Learning goals

---

# Content Guidelines

## Writing Style

### Length
- **Short callouts** (1-3 sentences): Note, tip, warning
- **Medium callouts** (1-2 paragraphs): Definition, exercise
- **Long callouts** (multiple sections): Homework, objective

### Tone by Type
- **Informational** (note, definition): Neutral, clear, factual
- **Advisory** (tip, warning): Friendly but authoritative
- **Interactive** (exercise, homework, prompt): Engaging, instructional
- **Structural** (objective): Clear, measurable, motivating

### Formatting
- Use **bold** for key terms and important points
- Include `code snippets` when relevant
- Use numbered lists for step-by-step instructions
- Use bullet points for feature lists or criteria

## Accessibility Standards

### Contrast Requirements
All callouts automatically meet WCAG AA+ standards (6:1+ contrast ratio):
- ✅ **Tested**: All color combinations verified for accessibility
- ✅ **Responsive**: Font sizes optimized for classroom presentations
- ✅ **Universal**: Icons and colors work across all themes

### Screen Reader Support
- Callouts include semantic markup for screen readers
- Icons have appropriate alt text
- Content structure is logically organized

---

# Common Patterns

## Lesson Structure Pattern
```markdown
::: {.callout-objective}
**Today's Goals**: Learn Git basics and create your first repository.
:::

::: {.callout-note}
Version control is like a time machine for your code...
:::

::: {.callout-definition}
**Git**: A distributed version control system...
:::

::: {.callout-tip}
Use `git status` frequently to see what's happening...
:::

::: {.callout-exercise}
Let's practice: Create your first Git repository...
:::

::: {.callout-warning}
Never commit passwords or sensitive data...
:::

::: {.callout-homework}
For next week, complete the Git tutorial...
:::
```

## AI-Enhanced Learning Pattern
```markdown
::: {.callout-prompt title="Getting Started with AI"}
"You are a Python tutor. Help me understand variables by explaining them using real-world analogies. Include examples."
:::

::: {.callout-tip}
When the AI explains something you don't understand, ask follow-up questions like "Can you explain that differently?" or "Show me an example."
:::

::: {.callout-exercise}
Try the prompt above, then ask the AI to create practice problems for you to solve.
:::
```

## Troubleshooting Pattern
```markdown
::: {.callout-warning}
If you see "command not found" errors, Python might not be installed correctly.
:::

::: {.callout-tip title="Quick Fix"}
Try `python3 --version` to check if Python is installed. If not, revisit the installation guide.
:::

::: {.callout-prompt}
"I'm getting a 'command not found' error when trying to run Python. I'm on [your operating system]. What should I check and how can I fix this?"
:::
```

---

# Quality Checklist

## Before Publishing
- [ ] **Purpose**: Does each callout serve a clear educational purpose?
- [ ] **Type**: Is the correct callout type used for the content?
- [ ] **Length**: Is the content appropriately sized for the type?
- [ ] **Clarity**: Will students understand the message immediately?
- [ ] **Action**: Do interactive callouts have clear next steps?
- [ ] **Relevance**: Does the callout connect to the current lesson goals?

## Content Review
- [ ] **Accuracy**: Is all technical information correct?
- [ ] **Completeness**: Are step-by-step instructions complete?
- [ ] **Tone**: Does the tone match the callout type?
- [ ] **Grammar**: Is the writing clear and error-free?
- [ ] **Formatting**: Are important terms highlighted appropriately?

## Accessibility Check
- [ ] **Contrast**: All callouts automatically meet 6:1 ratio
- [ ] **Structure**: Content is logically organized
- [ ] **Language**: Clear, jargon-free when possible
- [ ] **Alternative text**: Any embedded images have descriptions

---

# Advanced Usage

## Nested Content
Callouts can contain complex content:

```markdown
::: {.callout-exercise title="Complete Git Workflow"}
**Practice the full Git workflow:**

1. **Initialize**: `git init`
2. **Create**: Make a new file called `README.md`
3. **Stage**: `git add README.md`
4. **Commit**: `git commit -m "Add README"`
5. **Check**: `git log --oneline`

**Expected result**: You should see your commit in the log.

**If something goes wrong**: Use `git status` to see what Git thinks is happening.
:::
```

## Combining Types
Use multiple callouts to create rich learning experiences:

```markdown
::: {.callout-definition}
**API (Application Programming Interface)**: A set of rules that allows different software applications to communicate with each other.
:::

::: {.callout-tip}
Think of an API like a restaurant menu – it shows you what you can order (request) and what you'll get back (response), but you don't need to know how the kitchen (server) actually makes the food.
:::

::: {.callout-prompt}
"Explain APIs using the restaurant analogy but for a weather app. How does the app get weather data?"
:::
```

---

# Theme Compatibility

## Universal Design
All callouts work consistently across all themes:
- **Evangelion theme**: Dark backgrounds with high contrast
- **Cyberpunk theme**: Neon colors with maintained readability
- **Academic theme**: Professional styling with traditional colors
- **Forest theme**: Nature colors with earth tones
- **Ocean theme**: Blue palettes with wave effects

## Custom Themes
When creating new themes, callouts automatically:
- ✅ Inherit your theme's color palette
- ✅ Maintain 6:1+ contrast ratio
- ✅ Scale properly for presentations
- ✅ Work on all screen sizes

---

*This system ensures that educational content remains accessible and effective regardless of visual styling, putting learning first while maintaining beautiful design.* 