# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a **GitHub Class Template Framework** - a production-ready Hugo-based educational platform that creates self-contained class websites with authentication, grading, and content management. It supports both professors and students with automated synchronization, token-based enrollment, and comprehensive grade tracking.

**Current Status**: Production-ready framework with complete implementation. All core features are functional including authentication, grading system, content management, and multi-user workflows.

## Core Architecture

**Root Directory Structure:**
```
/home/uumami/sonder/class_template/
├── framework/                    # Framework components and logic
├── class_template/              # Class metadata and configuration
├── professor/                   # Professor workspace
├── students/                    # Student workspaces (students/username/)
├── framework_wiki/              # Documentation and tutorials
├── hugo_generated/              # Hugo build output
├── dna.yml                      # Framework meta-process control
├── build.yml                    # Build target configuration
├── manage.sh                    # Root orchestrator script
└── requirements.txt             # Python dependencies
```

**Configuration Hierarchy:**
- `dna.yml` - Framework operational settings (sync mode, meta-process control)
- `build.yml` - Build target configuration (professor vs student builds)
- `class_template/course.yml` - Class metadata (course info, professor details, Supabase config)
- `professor/config.yml` & `students/*/config.yml` - Rendering preferences (theme, visual settings)

**Framework Principles:**
- Each workspace is self-contained for rendering (no shared dependencies)
- Non-destructive synchronization (student work never overwritten)
- Automated index generation based on file naming conventions
- Content preservation using `<!-- KEEP:START -->` / `<!-- KEEP:END -->` blocks
- Token-based enrollment with role management

## CRITICAL: Framework Architecture Understanding

**Static Site Generation Model:**
- This is a STATIC SITE framework - Hugo builds HTML/CSS/JS files only
- NO server-side execution after build - everything runs in the browser
- Python scripts are PRE-BUILD processors (config generation, validation, sync)
- Backend interactions happen via JavaScript calling external APIs (Supabase Edge Functions)

**Current Directory Organization:**
- `framework/sql/00_current.sql` - **Current production database schema** (exported from Supabase)
- `framework/sql/legacy/` - **Historical SQL migrations and development files**
- `framework/supabase/functions/` - Deno Edge Functions (11 deployed functions)
- `framework/scripts/` - Python pre-build processors and management tools
- `framework/assets/js/` - Frontend JavaScript (runtime auth, grading, submissions)
- `framework/css/` - Framework styles and component CSS
- `framework/themes/*/` - Theme-specific overrides (Evangelion theme active)
- `framework/auth/` - Authentication flow pages
- `framework/protected_pages/` - Dashboard, grading, enrollment interfaces
- `hugo_generated/` - Hugo build output with static assets

**Content Structure:**
- `framework_wiki/framework_documentation/` - Technical docs about framework internals
- `framework_wiki/framework_tutorials/` - How-to guides for using the framework
- `professor/class_notes/` & `students/*/class_notes/` - Course content
- Follow naming: `01_chapter/01_section.md` with frontmatter metadata

## Development Commands

**Main Management Script:**
```bash
# From repository root - automatically detects build target
./manage.sh [options]

# Direct Python execution (from any directory)
python3 framework/scripts/manage.py [options]
```

**Core Commands:**
- `--build` - Full build pipeline (validate + generate + hugo build)
- `--dev` - Start Hugo development server (professor: port 1313, student: port 1314)
- `--status` - Show current framework status and recent changes
- `--validate` - Run validation and content generation only
- `--sync` - Sync framework updates (students only)
- `--deploy` - Build for production deployment
- `--publish` - Complete build + deploy pipeline
- `--clean` - Remove generated files

**Command Combinations:**
- `--build --dev` - Build and start development server
- `--sync --build` - Sync updates and build (students)
- `--build --force` - Skip confirmation prompts
- `--publish` - Same as `--build --deploy`

**Student Initialization:**
```bash
# From students/ directory (one-time setup)
./start.sh [username]
```

## Framework Scripts

**Key Python Scripts (in `framework/scripts/`):**
- `manage.py` - Unified management interface with modular architecture
- `generate_hugo_config.py` - Auto-generate Hugo configuration from templates
- `generate_indices.py` - Create navigation indices from content structure
- `sync_student.py` - Synchronize professor updates to student directories
- `validate_content.py` - Validate content structure and metadata
- `parse_grading_data.py` - Process grading configurations and generate JSON
- `inject_class_context.py` - Inject class metadata into build process

**Management Module Architecture:**
- `manage_modules/operation_sequencer.py` - Operation workflow management
- `manage_modules/environment_manager.py` - Environment detection and setup
- `manage_modules/subprocess_runner.py` - Safe subprocess execution
- `manage_modules/message_orchestrator.py` - User communication and logging
- `manage_modules/user_experience.py` - Rich console interface

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
- Generated from `framework/hugo_config/hugo.toml.j2` template
- Merged with values from `course.yml` and `config.yml`
- Output directory: `hugo_generated/`
- Multi-target builds with automatic detection

**Content Processing:**
1. Environment detection (professor vs student workspace)
2. Validate directory structure and naming conventions
3. Generate indices and navigation components
4. Process configuration templates with Jinja2
5. Inject class context and grading data
6. Mount content and assets using Hugo modules
7. Build static site with Hugo

**Theme System:**
- Base framework CSS: `framework/css/`
- Theme-specific styles: `framework/themes/{theme}/css/`
- Active theme: Evangelion (configurable in `config.yml`)
- Component-based CSS architecture

## Authentication & Backend

**Supabase Integration:**
- **Production URL**: `https://levybxqsltedfjtnkntm.supabase.co`
- **Class ID**: `df6b6665-d793-445d-8514-f1680ff77369`
- GitHub OAuth authentication
- PostgreSQL with Row Level Security (RLS)
- File storage for submissions
- 11 deployed Edge Functions for API endpoints

**Edge Functions:**
- `/me` - User profile and enrollment status
- `/enroll` - Token-based class enrollment
- `/generate-token`, `/generate-token-v2`, `/generate-token-simple` - Token management
- `/manage-tokens` - Token administration
- `/class-roster` - Class membership management
- `/student-grades` - Grade retrieval
- `/submit-item` - Assignment submission
- `/professor-grade-item`, `/professor-add-manual-item` - Grading tools

**Database Schema:**
- Multi-class support with fine-grained permissions
- **Grading hierarchy**: Modules → Constituents → Items → Submissions
- User profiles with GitHub integration
- Enrollment tokens with SHA-256 hashing
- Submission tracking with version history
- Grade adjustments and policy engine
- Complete Row Level Security policies

## Grading System

**Hierarchical Structure:**
- **Modules**: High-level course components (e.g., "Authentication", "Databases")
- **Constituents**: Module subdivisions (e.g., "Basic Auth", "OAuth")
- **Items**: Individual graded elements (homework, quizzes, projects)
- **Submissions**: Student work submitted for grading

**Content Integration:**
- Hugo shortcodes: `{{< item-inline >}}` for embedding grading elements
- Automatic item parsing from markdown content
- Grade sync between database and static site
- Professor grading interfaces with rich UI

**Configuration Files:**
- `class_template/modules.yml` - Module definitions and weights
- `class_template/constituents.yml` - Constituent configurations
- `class_template/grading_data_parsed.json` - Generated grading structure

## Testing & Validation

**Validation System:**
- Framework validation: `./manage.sh --validate`
- Content validation: Built-in checks for required frontmatter and naming
- Hugo build success indicates configuration validity
- Python script validation for syntax and imports

**No Specific Test Framework:**
- Validation through build process success
- Content structure verification
- Configuration file validation
- Database schema integrity checks

**Lint/Type Checking:**
- No specific linting commands configured
- Python code follows standard conventions
- YAML/Markdown validated during build process
- JavaScript follows ES6+ standards

## Development Guidelines

**File Modification Rules:**
- Students only work in their own `students/username/` directory
- Never modify `framework/` directly - updates come through sync
- Use preservation blocks for custom content that should survive updates
- Follow naming conventions for automatic index generation

**Configuration Priority:**
- `dna.yml` - Framework operational settings only (never rendering preferences)
- `build.yml` - Build target configuration and port settings
- `config.yml` - All visual/rendering preferences (theme, colors, layout)
- `course.yml` - Class metadata (course name, professor info, semester, Supabase config)

**Sync Strategy:**
- Additive by default (new files added, existing files preserved)
- Smart exclusions prevent syncing build artifacts or auto-generated content
- Forced updates preserve content in `<!-- KEEP -->` blocks
- Non-destructive updates maintain student customizations

## Common Operations

**Professor Workflow:**
1. Modify content in `professor/`
2. Run `./manage.sh --build --dev` to build and preview
3. Students sync updates with `./manage.sh --sync --build`
4. Deploy with `./manage.sh --publish`

**Student Workflow:**
1. Initial setup: `students/start.sh username`
2. Regular sync: `./manage.sh --sync`
3. Local development: `./manage.sh --build --dev`
4. Add personal content in `class_notes/`, `homework/`, `personal_projects/`

**Deployment:**
- GitHub Pages deployment configured
- Run `./manage.sh --deploy` or `./manage.sh --publish` for production builds
- Site served at configured baseURL

## Framework Features

**Authentication System:**
- Supabase Auth with GitHub provider
- Protected pages: dashboard, upload areas, grading interfaces
- JWT-based session management
- Frontend auth state management in JavaScript
- **Token-based enrollment system** with professor/student role management
- **Role-based dashboard UI** with prominent enrollment interface
- **Secure token hashing** using SHA-256 (Deno Edge Functions compatible)
- **Class roster management** with enrollment status tracking

**Grading Features:**
- **4-Level Hierarchical Structure**: Items (raw points) → Constituents (normalized %) → Modules (5-rule policy) → Final (weighted %)
- **Production-Verified SQL Functions**:
  - `calculate_module_grades(student_id, class_id)` - Module calculations with 5-rule policy
  - `calculate_constituent_grades(student_id, class_id)` - Constituent normalization to 0-10 scale
  - `get_item_grades(student_id, class_id)` - Individual item scores and percentages
  - `calculate_grade_summary(student_id, class_id)` - Overall grade summary and statistics
  - `apply_grading_policy(module_id, class_id, grades[])` - 5-rule policy application engine
- **5-Rule Grading Policy System**: All > 9.0 → 10.0; All > 8.0 → bonus; etc.
- **Ground Truth Sync**: Web-based sync at `/grading-sync/` (not CLI)
- **In-content grading elements** via Hugo shortcodes
- **Submission tracking** in `student_submissions` table with JSONB data

**Content Features:**
- LaTeX math rendering via MathJax/KaTeX
- JupyterLite integration for Python notebooks
- Syntax highlighting for code blocks
- Automatic table of contents generation
- Discussion system integration (Giscus)
- Automatic index generation from file structure

**Accessibility:**
- Font options (including OpenDyslexic)
- High contrast mode
- Keyboard navigation
- Screen reader optimization
- WCAG compliance considerations

**Advanced Features:**
- **Multi-class support** - Database designed for multiple class instances
- **Theme system** - Pluggable themes with component overrides
- **Content preservation** - Student work protected during framework updates
- **Smart synchronization** - Additive updates without data loss
- **Rich development tools** - Comprehensive CLI with progress indicators

## Production Configuration

**Current Class Instance:**
- **Class Name**: "GitHub Class Template Example"
- **Course Code**: "TMPL101"
- **Semester**: "Template 2025"
- **Professor**: uumami (uumami@sonder.art)
- **Theme**: Evangelion
- **Base URL**: https://www.sonder.art/class_template/

**Active Integrations:**
- **Supabase Project**: levybxqsltedfjtnkntm
- **GitHub OAuth**: Configured and functional
- **Edge Functions**: All 11 functions deployed
- **Database**: Complete schema with RLS policies
- **File Storage**: Configured for submissions

This framework represents a sophisticated, production-ready educational platform that could serve real educational institutions with enterprise-level features like token-based enrollment, comprehensive grading systems, and multi-user authentication.

## Database Schema & Testing

### **Current Production Schema**
- **Location**: `framework/sql/00_current.sql` - Complete production database schema exported from Supabase
- **Legacy Files**: `framework/sql/legacy/` - Historical development migrations and experiments

### **Key Database Tables**
- **`student_submissions`** - Student work with required `submission_data` JSONB field
- **`modules`** - Course modules with `is_current` state management
- **`constituents`** - Module components with normalization weights
- **`items`** - Individual graded elements linked to constituents
- **`grading_policies`** - 5-rule policy engine configuration stored as JSONB

### **Production Testing**
- **Test User ID**: `385dd2ab-a193-483d-9df9-d5a2cca2cea3` (verified working)
- **Class ID**: `df6b6665-d793-445d-8514-f1680ff77369`
- **Verified Functions**: All grading calculations tested and working in production
- **Sync Verification**: Ground truth sync via `/grading-sync/` web interface confirmed functional

## Related Documents

- **`GRADING_HIERARCHY_IMPLEMENTATION_V2.md`** - Complete grading system implementation guide with production-verified details
- `AUTHENTICATION_SETUP.md` - Authentication configuration guide
- `SEED.md` - Framework setup and initialization guide
- `framework_wiki/` - Comprehensive framework documentation
- `class_template/grading_policies/` - Grading policy configurations