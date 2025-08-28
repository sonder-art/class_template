# GitHub Class Template Framework

Welcome to the **GitHub Class Template Framework** - a foundational system for creating educational repositories with automated content management, Hugo-powered rendering, and student-professor synchronization.

## 🎯 Framework Overview

This repository serves as a **template** for classes, providing:

- **Automated Structure**: Consistent content organization with naming conventions
- **Hugo Integration**: Static site generation with themes and components  
- **Student Workspace**: Self-contained student directories with sync capabilities
- **Accessibility First**: Built-in support for diverse learning needs
- **Agent-Ready**: Structured for easy consumption by coding assistants

## 📁 Directory Structure

```
professor/                          # Source of truth for course content
├── class_notes/                   # Main instructional content
├── framework_code/                # Technical infrastructure
│   ├── components/               # Functional UI components
│   ├── themes/                   # Visual themes (current: evangelion)
│   ├── scripts/                  # Automation tools
│   ├── css/                      # Baseline styles
│   └── hugo_config/              # Hugo configuration templates
├── framework_documentation/       # Technical documentation
└── framework_tutorials/           # Student-facing tutorials

students/                          # Student workspace system
├── _template/                     # Template for new students
└── <username>/                    # Individual student directories
```

## 🚀 Quick Start

1. **Configure the Framework**
   - Edit `dna.yml` in the repository root for framework settings
   - Customize `professor/course.yml` for class metadata
   - Adjust `professor/config.yml` for visual preferences

2. **Generate Site Configuration**
   ```bash
   ./professor/framework_code/scripts/generate_hugo_config.py
   ```

3. **Create Content**
   - Add chapters to `professor/class_notes/` following naming conventions
   - Use numbered directories (`01_intro/`) and files (`01_topic.md`)
   - Associate code files with letter suffixes (`01_a_code.py`)

4. **Build and Deploy**
   - Hugo will automatically detect the generated configuration
   - GitHub Pages renders student directories when they exist

## 🎓 Join This Class

**Students:** Ready to join this class? You'll need an enrollment token from your instructor.

<div style="background: var(--elevated-color, #f8f9fa); border: 2px solid var(--eva-green-primary, #00d084); border-radius: 8px; padding: 20px; margin: 20px 0;">
<h3 style="color: var(--eva-green-primary, #00d084); margin-top: 0;">Quick Enrollment</h3>
<p><strong>Have a token?</strong> Click below to join:</p>
<a href="/enroll/" style="display: inline-block; background: var(--eva-green-primary, #00d084); color: var(--bg-color, #ffffff); padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">🎓 Join Class</a>
<p style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;"><strong>No token yet?</strong> Contact {{ .Site.Params.professor_name }} at {{ .Site.Params.professor_email }}</p>
</div>

## 🎨 Current Theme: Evangelion

The active theme provides a dark, modern interface inspired by Evangelion aesthetics:
- **Deep blue backgrounds** with high contrast text
- **Accessibility features** including font switching and high contrast mode
- **Responsive design** with collapsible navigation for mobile

## 📋 Core Principles

1. **Keep root minimal** - Only high-level control files at repository root
2. **Professor as source-of-truth** - All course assets under `/professor`
3. **Automation first** - Generate configs, indices, and navigation automatically
4. **Non-destructive sync** - Student work is never overwritten
5. **Agent compatibility** - Structure is easily parseable and actionable

---

*This framework begins as a GitHub template repository and evolves into a comprehensive educational content management system.* 