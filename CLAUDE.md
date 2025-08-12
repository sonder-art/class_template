# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a GitHub Class Template Framework - a Hugo-based educational platform that creates self-contained class websites with authentication, grading, and content management. It supports both professors and students with automated synchronization and deployment.

## Core Architecture

**Directory Structure:**
- `professor/` - Source/base project containing all framework components and class content
- `students/` - Student workspaces, each user gets their own subdirectory (e.g., `students/username/`)
- `dna.yml` - Framework metadata and operational settings (repository root)

**Configuration Hierarchy:**
- `dna.yml` - Framework meta-process control (sync mode, CI/CD, operational flags)
- `config.yml` - Per-directory rendering preferences (theme, visual settings)
- `course.yml` - Class-specific metadata (course info, professor details, branding)

**Framework Principles:**
- Each directory is self-contained for rendering (no shared dependencies)
- Non-destructive synchronization (student work never overwritten)
- Automated index generation based on file naming conventions
- Content preservation using `<!-- KEEP:START -->` / `<!-- KEEP:END -->` blocks

## CRITICAL: Framework Architecture Understanding

**Static Site Generation Model:**
- This is a STATIC SITE framework - Hugo builds HTML/CSS/JS files only
- NO server-side execution after build - everything runs in the browser
- Python scripts are PRE-BUILD processors (config generation, validation, sync)
- Backend interactions happen via JavaScript calling external APIs (Supabase)

**File Organization Principles:**
- `framework_code/sql/` - Database schemas and migrations
- `framework_code/supabase/` - Supabase Edge Functions and backend configurations
- `framework_code/scripts/` - Python pre-build processors
- `framework_code/assets/js/` - Frontend JavaScript (runtime code)
- `framework_code/css/` - Framework styles
- `framework_code/themes/*/` - Theme-specific overrides
- `framework_code/protected_pages/` - Protected content pages
- `framework_code/auth/` - Authentication flow pages
- `framework_code/hugo_generated/` - Hugo output (never edit)

**Content Documentation Structure:**
- `framework_documentation/` - Technical docs about framework internals
- `framework_tutorials/` - How-to guides for using the framework
- `class_notes/` - Course content from professor
- Follow naming: `01_chapter/01_section.md` with frontmatter metadata

## Development Commands

**Main Management Script:**
```bash
# From professor/ or students/username/ directory
./manage.sh [options]

# Or directly:
python3 framework_code/scripts/manage.py [options]
```

**Core Commands:**
- `--build` - Full build pipeline (validate + generate + hugo build)
- `--dev` - Start Hugo development server (professor: port 1313, student: port 1314)
- `--status` - Show current framework status and recent changes
- `--validate` - Run validation and content generation only
- `--sync` - Sync framework updates (students only)
- `--deploy` - Build for production deployment
- `--clean` - Remove generated files

**Command Combinations:**
- `--build --dev` - Build and start development server
- `--sync --build` - Sync updates and build (students)
- `--build --force` - Skip confirmation prompts

**Student Initialization:**
```bash
# From students/ directory (one-time setup)
./start.sh [username]
```

## Framework Scripts

**Key Python Scripts (in `framework_code/scripts/`):**
- `manage.py` - Unified management interface
- `generate_hugo_config.py` - Auto-generate Hugo configuration from templates
- `generate_indices.py` - Create navigation indices from content structure
- `sync_student.py` - Synchronize professor updates to student directories
- `validate_content.py` - Validate content structure and metadata

**Script Dependencies:**
- Python 3.x required
- Dependencies in `requirements.txt`: rich, pyyaml, jinja2

## Content Structure & Naming

**Naming Conventions:**
- Chapters: `01_chapter_name/` (zero-padded numbers)
- Sections: `01_section_name.md`
- Code files: `01_a_code_file.py`, `01_b_code_file.py` (letter suffixes)
- Homework: `hw_01.md`, `hw_01_a_solution.py`
- Appendices: `A_advanced_topics/` (capital letters)
- Indices: `00_index.md` (auto-generated), `00_master_index.md`

**Required Frontmatter:**
```yaml
---
title: "Content Title"
type: note|homework|tutorial|documentation
date: 2025-01-01
author: "Author Name"
summary: "Brief description for indices and search"
---
```

## Build Process

**Hugo Configuration:**
- Generated from `framework_code/hugo_config/hugo.toml.j2` template
- Merged with values from `course.yml` and `config.yml`
- Output directory: `framework_code/hugo_generated/`

**Content Processing:**
1. Validate directory structure and naming conventions
2. Generate indices and navigation components
3. Process configuration templates with Jinja2
4. Mount content and assets using Hugo modules
5. Build static site with Hugo

**Theme System:**
- Base framework CSS: `framework_code/css/`
- Theme-specific styles: `framework_code/themes/{theme}/css/`
- Active theme selected in `config.yml`, not `dna.yml`

## Authentication & Backend

**Supabase Integration:**
- GitHub OAuth authentication
- PostgreSQL with RLS (Row Level Security)
- File storage for submissions
- Edge Functions for API endpoints

**Database Schema:**
- Multi-class support with fine-grained permissions
- Grading system: Modules → Constituents → Items
- Submission tracking with version history
- Grade adjustments and policy engine

## Testing & Validation

**No specific test framework** - validation happens through:
- Framework validation: `./manage.sh --validate`
- Content validation: Built-in checks for required frontmatter and naming
- Hugo build success indicates configuration validity

**Lint/Type Checking:**
- No specific linting commands configured
- Python code follows standard conventions
- YAML/Markdown validated during build process

## Development Guidelines

**File Modification Rules:**
- Students only work in their own `students/username/` directory
- Never modify `framework_code/` directly - updates come through sync
- Use preservation blocks for custom content that should survive updates
- Follow naming conventions for automatic index generation

**Configuration Priority:**
- `dna.yml` - Framework operational settings only (never rendering preferences)
- `config.yml` - All visual/rendering preferences (theme, colors, layout)
- `course.yml` - Class metadata (course name, professor info, semester)

**Sync Strategy:**
- Additive by default (new files added, existing files preserved)
- Smart exclusions prevent syncing build artifacts or auto-generated content
- Forced updates preserve content in `<!-- KEEP -->` blocks

## Common Operations

**Professor Workflow:**
1. Modify content in `professor/`
2. Run `./manage.sh --build --dev` to build and preview
3. Students sync updates with `./manage.sh --sync --build`

**Student Workflow:**
1. Initial setup: `students/start.sh username`
2. Regular sync: `./manage.sh --sync`
3. Local development: `./manage.sh --build --dev`
4. Add personal content in `class_notes/`, `homework/`, `personal_projects/`

**Deployment:**
- GitHub Pages deployment configured
- Run `./manage.sh --deploy` for production builds
- Site served at `{domain}/{repo_name}/`

## Framework Features

**Authentication System:**
- Supabase Auth with GitHub provider
- Protected pages: dashboard, upload areas
- JWT-based session management
- Frontend auth state management in JavaScript
- **Token-based enrollment system** with professor/student role management
- **Role-based dashboard UI** with prominent enrollment interface
- **Secure token hashing** using SHA-256 (Deno Edge Functions compatible)

**Content Features:**
- LaTeX math rendering via MathJax/KaTeX
- JupyterLite integration for Python notebooks
- Syntax highlighting for code blocks
- Automatic table of contents generation
- Discussion system integration (Giscus)

**Accessibility:**
- Font options (including OpenDyslexic)
- High contrast mode
- Keyboard navigation
- Screen reader optimization

This framework emphasizes automation, consistency, and safe collaboration between professors and students while maintaining flexibility for customization.

## Related Documents

- `IMPLEMENTATION_PLAN.md` - Current authentication implementation roadmap
- `AUTHENTICATION_SETUP.md` - Authentication configuration guide
- `DESIGN.md` - Complete authentication system design specification