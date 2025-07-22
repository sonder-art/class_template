# PROJECT SPECIFICATION: Quarto Educational Content Management System - COMPREHENSIVE REFERENCE

> **📚 COMPREHENSIVE SYSTEM DOCUMENTATION**: This document provides complete system understanding including existing patterns, technical details, and content examples. For implementation-focused specification, see PROJECT_SPECIFICATION.md (the main document for coding agents).

## TODO: Implementation Status

### Phase 1: Infrastructure Setup ⏳
- [ ] Create `uumami/quarto_code/` directory structure
- [ ] Move existing components: `uumami/components/` → `uumami/quarto_code/components/`
- [ ] Move existing styles: `uumami/styles/` → `uumami/quarto_code/styles/`
- [ ] Move extensions: `uumami/_extensions/` → `uumami/quarto_code/_extensions/`
- [ ] Create `uumami/legacy/` and preserve existing content
- [ ] Update all relative paths in YAML headers and includes
- [ ] Verify extension dependencies are maintained

### Phase 2: Automation Scripts ⏳
- [ ] `scan_structure.py` - Content discovery with current naming patterns
- [ ] `validate_structure.py` - Naming convention enforcement
- [ ] `generate_navigation.py` - Auto-generate `_quarto.yml` navbar
- [ ] `update_nav_components.py` - Generate enhanced `_nav.qmd` files
- [ ] `generate_site.py` - Master orchestrator script
- [ ] `create_chapter.py` - Interactive content creation wizard

### Phase 3: Development Framework ⏳
- [ ] Create `uumami/quarto_development/` structure
- [ ] Migrate `uumami/ACCESSIBILITY_SETUP.md` → `quarto_development/02_accessibility_features/`
- [ ] Split `uumami/styles/THEME_SYSTEM.md` → `quarto_development/00_theme_system/`
- [ ] Split `uumami/styles/CALLOUT_GUIDE.md` → `quarto_development/01_callout_system/`
- [ ] Create script usage documentation
- [ ] Update main navigation to include development section

### Phase 4: Enhanced Navigation ⏳
- [ ] Enhance `_nav.qmd` with collapsible sections (based on current dropdown pattern)
- [ ] Implement automatic breadcrumb generation
- [ ] Add section overview with expandable subsections
- [ ] Maintain current JavaScript prev/next functionality
- [ ] Add navigation scope configuration

### Phase 5: Testing & Validation ⏳
- [ ] Test automation scripts with sample content structure
- [ ] Validate student sync mechanism with new paths
- [ ] Test accessibility features with new structure
- [ ] Verify theme system compatibility
- [ ] Performance testing with large content structures

## Executive Summary

This project implements a sophisticated, semi-automated educational content management system using Quarto for a programming class. The system features **JavaScript-powered navigation**, **CSS variable theming**, **custom callout extensions**, **accessibility integration**, and **automated student distribution**. All components are designed for classroom presentation with WCAG AA+ accessibility compliance.

## Project Architecture Overview

### Core Technical Principles
- **JavaScript Navigation System**: Hardcoded pages arrays with automatic prev/next detection
- **CSS Variable Theming**: Unlimited themes via CSS custom properties with universal readability
- **Extension-Based Callouts**: `coatless-quarto/custom-callout` for educational content structure
- **Relative Path Architecture**: All paths relative to file location for portability
- **Component Inclusion System**: Global `_quarto.yml` includes + local `{{< include >}}` patterns
- **Semi-Automated Generation**: Scripts handle structure, humans create content

### Current Directory Structure (ACTUAL EXISTING FILES)
```
class_template/
├── uumami/                                    # Main instructor content (EXISTING)
│   ├── components/                           # CURRENT LOCATION - TO MOVE
│   │   ├── accessibility-auto.html           # Auto-injected accessibility (WORKING)
│   │   ├── accessibility-bar.html            # Legacy accessibility template  
│   │   └── accessibility-test.qmd            # Test page for accessibility
│   ├── styles/                               # CURRENT LOCATION - TO MOVE
│   │   ├── main.css                          # Core structure (WORKING - NEVER EDIT)
│   │   ├── THEME_SYSTEM.md                   # 1016 lines - Complete theme guide (EXISTING)
│   │   ├── CALLOUT_GUIDE.md                  # 350 lines - Callout usage guide (EXISTING)
│   │   └── themes/                           # Theme collection (EXISTING)
│   │       ├── _template.css                 # Base template (WORKING)
│   │       ├── evangelion.css                # Default dark theme (WORKING)
│   │       └── cyberpunk.css                 # Neon example theme (WORKING)
│   ├── _extensions/                          # CURRENT LOCATION - TO MOVE
│   │   └── coatless-quarto/                  # Custom callout system (CRITICAL)
│   │       └── custom-callout/               # Extension files (WORKING)
│   │           ├── _extension.yml            # Extension configuration
│   │           ├── customcallout.lua         # Lua filter for callouts
│   │           └── fa.lua                    # Font Awesome icons
│   ├── a_intro_appendix/                     # EXISTING WORKING CONTENT - TO PRESERVE
│   │   ├── _nav.qmd                          # 107 lines - Sophisticated navigation (REFERENCE PATTERN)
│   │   ├── 01_creating_llm_accounts.qmd      # Working content example
│   │   ├── 02_how_to_get_help.qmd            # Working content example
│   │   ├── [... 7 more sections ...]        # Complete working chapter
│   │   └── a_wsl2.qmd                        # Appendix example
│   ├── c_quarto_appendix/                    # EXISTING TUTORIALS - TO MIGRATE
│   │   ├── 00_index.qmd                      # Quarto crash course intro
│   │   ├── 01_the_language_of_quarto.qmd     # Markdown/YAML tutorial
│   │   ├── 02_executable_documents.qmd       # Code execution guide
│   │   ├── 03_the_project_workflow.qmd       # Professional workflow
│   │   └── 04_style_and_layout.qmd           # Styling guidance
│   ├── notas/                                # NEW STRUCTURE - PARTIALLY STARTED
│   │   └── 00_intro/                         # Chapter 0 skeleton
│   │       ├── _nav.qmd                      # Basic navigation (NEEDS ENHANCEMENT)
│   │       ├── 00_index.qmd                  # Chapter landing page
│   │       └── [subdirectories with letter prefixes - WRONG CONVENTION]
│   ├── _quarto.yml                           # 93 lines - Main config (WORKING)
│   ├── index.qmd                             # 46 lines - Course homepage (WORKING)
│   ├── ACCESSIBILITY_SETUP.md                # 113 lines - Accessibility guide (TO MIGRATE)
│   └── requirements.txt                      # 16 lines - Python dependencies

### TARGET Directory Structure (AFTER REORGANIZATION)
```
class_template/
├── uumami/                                    # Main instructor content
│   ├── quarto_code/                          # NEW - Technical infrastructure
│   │   ├── scripts/                          # NEW - Automation scripts (TO CREATE)
│   │   ├── components/                       # MOVED FROM uumami/components/
│   │   ├── styles/                           # MOVED FROM uumami/styles/
│   │   ├── _extensions/                      # MOVED FROM uumami/_extensions/
│   │   └── templates/                        # NEW - File templates (TO CREATE)
│   ├── notas/                                # Enhanced course content structure
│   ├── quarto_development/                   # NEW - Framework documentation
│   ├── legacy/                               # NEW - Preserved reference content
│   │   ├── a_intro_appendix/                 # MOVED - Working reference
│   │   └── c_quarto_appendix/                # MOVED - Tutorial reference
│   │   ├── 00_intro/                         # Chapter 0: Introduction
│   │   │   ├── 00_index.qmd                  # Chapter landing (required)
│   │   │   ├── _nav.qmd                      # Chapter navigation (auto-generated)
│   │   │   ├── 00_prompt_engineering_basics/ # Section 0.0 (with subsections)
│   │   │   │   ├── 00_what_is_prompting.qmd  # 0.0.0 content
│   │   │   │   ├── 01_prompt_structure.qmd   # 0.0.1 content
│   │   │   │   ├── 02_advanced_techniques/   # 0.0.2 nested section
│   │   │   │   │   ├── 00_chain_of_thought.qmd
│   │   │   │   │   └── 01_few_shot_learning.qmd
│   │   │   │   └── examples/                 # Supporting files (not rendered)
│   │   │   │       ├── prompt_examples.py
│   │   │   │       ├── test_prompts.sh
│   │   │   │       └── sample_data.json
│   │   │   ├── 01_sistema_operativo.qmd      # 0.1 single file section
│   │   │   ├── 02_terminal_commands/         # 0.2 multi-file section
│   │   │   │   ├── 00_basic_commands.qmd
│   │   │   │   ├── 01_file_operations.qmd
│   │   │   │   └── scripts/                  # Supporting code
│   │   │   │       ├── practice_commands.sh
│   │   │   │       └── file_manager.py
│   │   │   └── resources/                    # Chapter-level resources
│   │   │       ├── setup_scripts.sh
│   │   │       └── common_utilities.py
│   │   ├── 01_python_fundamentals/           # Chapter 1
│   │   ├── 02_data_structures/               # Chapter 2
│   │   └── a_appendices/                     # Appendices
│   │       ├── a_index.qmd
│   │       ├── _nav.qmd
│   │       ├── a_installation_guides/
│   │       └── b_troubleshooting/
│   ├── quarto_development/                   # Framework tutorials (NOT course content)
│   │   ├── 00_index.qmd                      # Development hub
│   │   ├── _nav.qmd                          # Development navigation
│   │   ├── 00_theme_system/                  # Theme creation guides
│   │   │   ├── 00_theme_architecture.qmd     # Based on THEME_SYSTEM.md
│   │   │   ├── 01_creating_new_themes.qmd
│   │   │   └── 02_theme_troubleshooting.qmd
│   │   ├── 01_callout_usage/                 # Educational callout system
│   │   │   ├── 00_callout_overview.qmd       # Based on CALLOUT_GUIDE.md
│   │   │   ├── 01_callout_types.qmd
│   │   │   └── 02_callout_best_practices.qmd
│   │   ├── 02_accessibility_features/        # Accessibility system
│   │   │   ├── 00_accessibility_setup.qmd    # Based on ACCESSIBILITY_SETUP.md
│   │   │   └── 01_accessibility_testing.qmd
│   │   ├── 03_content_creation_workflow/     # Content authoring
│   │   ├── 04_script_automation/             # Using automation scripts
│   │   └── 05_troubleshooting/               # Common issues
│   ├── legacy/                               # Preserved old content (unused)
│   │   ├── a_intro_appendix/                 # Old intro content (WORKING reference)
│   │   └── c_quarto_appendix/                # General Quarto tutorials
│   ├── _extensions/                          # Quarto extensions (CRITICAL)
│   │   └── coatless-quarto/                  # Custom callout system
│   │       └── custom-callout/               # Extension files
│   │           ├── _extension.yml            # Extension configuration
│   │           ├── customcallout.lua         # Lua filter for callouts
│   │           └── fa.lua                    # Font Awesome icons
│   ├── _quarto.yml                           # Main Quarto config (AUTO-GENERATED)
│   ├── index.qmd                             # Course homepage
│   ├── requirements.txt                      # Python dependencies
│   └── ACCESSIBILITY_SETUP.md                # Accessibility guide
├── students/                                 # Student workspace system
│   └── _template/                            # Template for new students
│       ├── styles/                           # Student style system
│       ├── sync_with_instructor.sh           # Update script (WORKING)
│       ├── requirements.txt                  # Student dependencies
│       └── .gitignore                        # Student Git config
├── .github/workflows/                        # GitHub Actions
│   └── publish.yml                           # Smart student/instructor detection (WORKING)
├── .quarto/                                  # Quarto build cache
├── _site/                                    # Generated website
├── requirements.txt                          # Root dependencies
├── .gitignore                                # Global Git ignore
└── README.md                                 # Project overview
```

## Existing Code Infrastructure and Quirks

### Quarto Configuration System (`_quarto.yml`)
**Current Working Configuration Pattern:**
```yaml
project:
  type: website
  output-dir: _site

website:
  title: "Class Template"
  description: "Programming Class Notes"
  navbar:
    left:
      - text: "Home"
        file: index.qmd
      - text: "Notes" 
        menu:
          - text: "Introduction"
            file: a_intro_appendix/_nav.qmd
    right:
      - icon: github
        href: https://github.com/username/repo
    tools:
      - icon: globe
        menu:
          - text: "Accessibility"
            file: components/accessibility-test.qmd

format:
  html:
    theme: 
      - styles/main.css
      - styles/themes/evangelion.css
    css: styles/main.css
    include-after-body: components/accessibility-auto.html
    toc: true
    toc-location: right
    toc-depth: 3

filters:
  - _extensions/coatless-quarto/custom-callout/customcallout.lua

# QUIRK: Must exclude Python/shell files from rendering
project:
  render:
    - "*.qmd"
    - "*.md"
    - "!**/*.py"
    - "!**/*.sh" 
    - "!**/*.json"
    - "!**/scripts/**"
    - "!**/examples/**"
    - "!**/resources/**"
```

### Current Navigation System (EXISTING SOPHISTICATED PATTERN)

**Existing `_nav.qmd` Pattern (FROM `uumami/a_intro_appendix/_nav.qmd` - 107 LINES):**

The current navigation has THREE integrated components that should be enhanced:

#### 1. Section Overview Callout (EXISTING - TO ENHANCE)
```markdown
::: {.callout-note .fw-light}
#### Setup Guides
- [**A.1** AI Assistants](./01_creating_llm_accounts.qmd)
- [**A.2** How to Get Help](./02_how_to_get_help.qmd)
- [**A.3** Install Python](./03_installing_python.qmd)
[... continues for all sections ...]
:::
```
**ENHANCEMENT NEEDED**: Make this collapsible/expandable for larger chapters

#### 2. Sophisticated Dropdown Breadcrumb (EXISTING - EXCELLENT PATTERN)
```html
<div class="breadcrumb-container">
  <details class="breadcrumb-dropdown">
    <summary>
      <span class="breadcrumb-prefix">Setup Guide:</span>
      <span class="breadcrumb-current">Current Page</span>
      <span class="breadcrumb-caret">▼</span>
    </summary>
    <ul class="breadcrumb-list">
      <li><a href="./00_index.qmd">Welcome</a></li>
      <li><a href="./01_creating_llm_accounts.qmd">A.1 AI Assistants</a></li>
      [... all sections listed ...]
    </ul>
  </details>
</div>
```
**PATTERN TO MAINTAIN**: This dropdown pattern is excellent and should be auto-generated

#### 3. JavaScript-Powered Prev/Next Navigation (EXISTING - SOPHISTICATED)
```javascript
// EXISTING PATTERN: Both file and title arrays
const pages = [
  { file: '00_index.qmd', title: 'Welcome' },
  { file: '01_creating_llm_accounts.qmd', title: 'A.1 AI Assistants' },
  { file: '02_how_to_get_help.qmd', title: 'A.2 How to Get Help' },
  // ... continues with file + title objects
];

// EXISTING LOGIC: Smart current page detection
const currentFile = currentPath.split('/').pop().replace('.html', '.qmd');
const currentIndex = pages.findIndex(page => page.file === currentFile);

// EXISTING FEATURE: Dynamic button creation with titles
document.getElementById('nav-prev').innerHTML = 
  `<a href="./${prevHtml}" class="nav-button prev">← ${prevPage.title}</a>`;

// EXISTING FEATURE: Auto-update breadcrumb current page
document.querySelector('.breadcrumb-current').textContent = pages[currentIndex].title;
```

### YAML Header Structure Patterns (EXISTING CONVENTIONS)

**Current Header Pattern (FROM WORKING FILES):**
```yaml
---
title: "A.B Section Title"
format:
  html:
    css:
      - ../styles/main.css                      # CURRENT PATH - TO UPDATE
      - ../styles/themes/evangelion.css         # CURRENT PATH - TO UPDATE
---
```

**Enhanced Header Pattern (TARGET AFTER REORGANIZATION):**
```yaml
---
title: "Section.Number Descriptive Title"
format:
  html:
    css:
      - ../../quarto_code/styles/main.css      # NEW PATH (depth-dependent)
      - ../../quarto_code/styles/themes/evangelion.css
---
```

### Chapter/Section Ordering Logic (CURRENT vs TARGET)

**CURRENT NAMING (in `uumami/a_intro_appendix/`):**
- Chapters: Letter prefix (A, B, C...)
- Sections: `01_`, `02_`, `03_`...  
- Appendices: `a_`, `b_`, `c_`...

**TARGET NAMING CONVENTION:**
- Chapters: `00_intro/`, `01_python_basics/`, `02_data_structures/`
- Sections: `00_first_section.qmd`, `01_second_section.qmd`
- Subsections: `00_subsection_name/` (can nest 2-3 levels)
- Appendices: `a_installation_guides/`, `b_troubleshooting/`
- Index files: `00_index.qmd`, `01_index.qmd`, `a_index.qmd`

**ORDERING ALGORITHM:**
```python
def sort_content_items(items):
    """Sort by prefix: numbers first (00-99), then letters (a-z)"""
    def get_sort_key(item_name):
        if re.match(r'^\d{2}_', item_name):
            return (0, int(item_name[:2]))  # Numeric chapters first
        elif re.match(r'^[a-z]_', item_name):
            return (1, ord(item_name[0]) - ord('a'))  # Letter appendices after
        else:
            return (2, item_name)  # Other items last
    
    return sorted(items, key=lambda x: get_sort_key(x.name))
```

### CSS Variable Theme System (EXISTING ARCHITECTURE)
**Core Theme Pattern (`styles/themes/evangelion.css`):**
```css
/* QUIRK: Google Fonts must be imported first */
@import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;500&family=Inter:wght@300;400;500;600;700&display=swap');

/* CRITICAL: CSS variables override main.css defaults */
:root {
  /* Core color palette - all themes must define these */
  --primary-color: #4A90E2;
  --accent-color: #7B68EE;
  --text-color: #E0E6ED;
  --text-color-light: #8B949E;
  --bg-color: #0D1117;
  --bg-color-offset: #161B22;
  --link-color: #58A6FF;
  --link-color-hover: #79C0FF;
  --border-color: #30363D;

  /* QUIRK: Font families with fallbacks required */
  --font-family-body: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-heading: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-family-monospace: 'Fira Code', 'Monaco', 'Consolas', monospace;

  /* Component-specific overrides */
  --code-bg-color: #161B22;
  --code-text-color: #E6EDF3;
  --table-header-bg: #21262D;
  --table-row-even-bg: #0D1117;

  /* QUIRK: Callout color system (optional overrides) */
  --callout-note-bg: rgba(84, 174, 255, 0.1);
  --callout-note-border: #54AEFF;
  --callout-tip-bg: rgba(56, 211, 159, 0.1);
  --callout-tip-border: #38D39F;
}

/* QUIRK: Specific hover effects for theme personality */
h1:hover, h2:hover, h3:hover {
  text-shadow: 0 0 10px var(--accent-color);
  transition: text-shadow 0.3s ease;
}
```

### Custom Callout Extension System (CRITICAL DEPENDENCY)
**Extension Configuration (`_extensions/coatless-quarto/custom-callout/_extension.yml`):**
```yaml
title: "Custom Educational Callouts"
author: "Coatless Professor"
version: "1.0.0"
quarto-required: ">=1.3.0"

contributes:
  filters:
    - customcallout.lua

# QUIRK: Custom callout types must be defined here
callouts:
  prompt:
    icon: robot
    color: teal
    title: "AI Prompt"
  exercise:
    icon: pencil
    color: amber  
    title: "Exercise"
  homework:
    icon: clipboard-list
    color: coral
    title: "Homework"
  objective:
    icon: target
    color: blue
    title: "Learning Objective"
  definition:
    icon: book-open
    color: purple
    title: "Definition"
```

**Callout Usage Pattern (EXISTING SYNTAX):**
```markdown
<!-- Built-in callouts (work without extension) -->
::: {.callout-note}
Standard note content
:::

::: {.callout-tip title="Custom Title"}
Tip with custom title
:::

<!-- Custom callouts (require extension) -->
::: {.prompt}
AI prompting guidance content
:::

::: {.exercise title="Practice Time"}
In-class exercise instructions
:::

::: {.objective}
Learning objectives for this section
:::
```

### Relative Path Resolution System (MAJOR QUIRK)
**Path Pattern from Content Files:**
```yaml
# QUIRK: All paths relative to current file location
---
title: "Section Title"
format:
  html:
    css:
      - ../quarto_code/styles/main.css              # From section to styles
      - ../quarto_code/styles/themes/evangelion.css # Theme path
---

# QUIRK: Include paths also relative
{{< include _nav.qmd >}}                           # Same directory
{{< include ../components/accessibility-auto.html >}} # Parent directory
```

### Accessibility Integration System (WORKING CODE)
**Auto-Injection Pattern (`components/accessibility-auto.html`):**
```html
<!-- QUIRK: Inlined CSS and JavaScript for reliability -->
<style>
/* OpenDyslexic font loading */
@import url('https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@4.5.0/index.css');

/* QUIRK: Dyslexic mode overrides ALL fonts when activated */
.dyslexic-mode * {
  font-family: 'OpenDyslexic', 'Comic Sans MS', 'Trebuchet MS', sans-serif !important;
}

/* Navbar accessibility toggle styling */
.accessibility-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

/* QUIRK: Responsive text hiding on mobile */
@media (max-width: 768px) {
  .accessibility-toggle .toggle-text {
    display: none;
  }
}
</style>

<script>
// QUIRK: Automatic navbar injection on page load
document.addEventListener('DOMContentLoaded', function() {
    // Try to find navbar (multiple possible locations)
    const navbarRight = document.querySelector('.navbar-nav.ms-auto') || 
                       document.querySelector('.navbar-nav') ||
                       document.querySelector('nav ul');
    
    if (navbarRight) {
        // Create accessibility toggle
        const toggleHTML = `
            <li class="nav-item">
                <label class="nav-link accessibility-toggle">
                    <input type="checkbox" id="dyslexic-toggle" style="margin-right: 0.5rem;">
                    <span class="toggle-text">🔤 Dyslexic</span>
                    <span class="toggle-icon" style="display: none;">🔤</span>
                </label>
            </li>
        `;
        navbarRight.insertAdjacentHTML('beforeend', toggleHTML);
        
        // QUIRK: Persistent localStorage preference
        const toggle = document.getElementById('dyslexic-toggle');
        const isDyslexic = localStorage.getItem('dyslexic-mode') === 'true';
        
        if (isDyslexic) {
            toggle.checked = true;
            document.body.classList.add('dyslexic-mode');
        }
        
        toggle.addEventListener('change', function() {
            if (this.checked) {
                document.body.classList.add('dyslexic-mode');
                localStorage.setItem('dyslexic-mode', 'true');
            } else {
                document.body.classList.remove('dyslexic-mode');
                localStorage.setItem('dyslexic-mode', 'false');
            }
        });
    }
});
</script>
```

### Student Distribution System (WORKING CODE)
**GitHub Actions Configuration (`publish.yml`):**
```yaml
# QUIRK: Smart directory detection for student vs instructor
- name: Identify Render Target
  id: identify_target
  run: |
    if [[ -d "students/${{ github.actor }}" ]]; then
      echo "TARGET_DIR=students/${{ github.actor }}" >> $GITHUB_ENV
      echo "Student directory found. Rendering student version."
    else
      echo "TARGET_DIR=uumami" >> $GITHUB_ENV
      echo "No student directory found. Rendering instructor version."
    fi

- name: Install Python dependencies
  run: pip install -r ${{ env.TARGET_DIR }}/requirements.txt

- name: Render Quarto Website
  uses: quarto-dev/quarto-actions/render@v2
  with:
    path: ${{ env.TARGET_DIR }}
```

**Sync Script Pattern (`students/_template/sync_with_instructor.sh`):**
```bash
#!/bin/bash
# QUIRK: Path-independent script execution
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$( cd -- "${SCRIPT_DIR}/../.." &> /dev/null && pwd )

# QUIRK: rsync exclusion patterns prevent overwriting student work
EXCLUDE_PATTERNS=(
    -path '*/_site/*'
    -path '*/.quarto/*' 
    -path '*/__pycache__/*'
    -path '*/styles/*'  # Styles handled separately
    -name '*.pyc'
)

# QUIRK: --ignore-existing prevents overwriting student modifications
rsync -av --ignore-existing "${INSTRUCTOR_CONTENT_DIR}/" "${DEST_DIR}/"
```

### Content Organization System

### Naming Convention Requirements (STRICT)
- **Chapters**: `{00-99}_{descriptive_name}/` (e.g., `00_intro/`, `01_python_basics/`)
- **Appendices**: `{a-z}_{descriptive_name}/` (e.g., `a_installation_guides/`, `b_troubleshooting/`)
- **Sections**: `{00-99}_{descriptive_name}.qmd` or `{00-99}_{descriptive_name}/`
- **Subsections**: Can nest 2-3 levels deep following same pattern
- **Index Files**: `{prefix}_index.qmd` (e.g., `00_index.qmd`, `a_index.qmd`)
- **Navigation Files**: `_nav.qmd` in each directory that needs navigation

### File Type Processing Rules (CRITICAL)
```python
# File discovery pattern for automation scripts
RENDERABLE_EXTENSIONS = {'.qmd', '.md'}
IGNORE_PATTERNS = {
    '**/*.py', '**/*.sh', '**/*.json', '**/*.csv', '**/*.txt',
    '**/scripts/**', '**/examples/**', '**/resources/**',
    '**/_site/**', '**/.quarto/**', '**/__pycache__/**',
    '**/.*'  # Hidden files
}

SUPPORTING_DIRECTORIES = {'scripts', 'examples', 'resources', 'assets', 'data'}
```

## Educational Content Template System (EXISTING PATTERNS)

### Standard Content File Template (WORKING PATTERN)
**Every `.qmd` file follows this exact structure:**
```yaml
---
title: "A.B Section Title"
format:
  html:
    css:
      - ../quarto_code/styles/main.css
      - ../quarto_code/styles/themes/evangelion.css
---

::: {.objective}
## 🎯 Learning Objectives

By the end of this section, you will be able to:
- [Specific measurable objective 1]
- [Specific measurable objective 2]
- [Specific measurable objective 3]
:::

## 📋 Overview

```{mermaid}
graph TD
    A["Current Topic"] --> B["Key Concept 1"]
    A --> C["Key Concept 2"]
    A --> D["Key Concept 3"]
    
    B --> E["Practical Application"]
    C --> E
    D --> E
    
    style A fill:#2E3440
    style E fill:#5E81AC
```

## Content Sections

[Main educational content with callouts]

::: {.definition}
**Key Term**: Formal definition here
:::

::: {.exercise}
**Practice Time**
1. Step-by-step instructions
2. Expected outcomes
3. Verification steps
:::

::: {.prompt}
Try this AI prompt: "Your specific prompt here"
:::

## Summary

[Key takeaways and next steps]

---

{{< include _nav.qmd >}}
```

### Educational Callout System (8 TYPES - CRITICAL SPECS)

**Built-in Callouts (No Extension Required):**
```markdown
::: {.callout-note}
📖 **Purpose**: General information and context
**Usage**: Background info, explanations, additional details
:::

::: {.callout-tip title="Pro Tip"}
⭐ **Purpose**: Helpful advice and shortcuts
**Usage**: Efficiency tips, best practices, shortcuts
:::

::: {.callout-warning}
⚠️ **Purpose**: Important cautions and alerts
**Usage**: Common mistakes, dangerous operations, critical info
:::

::: {.callout-important}
❗ **Purpose**: Critical information that must not be missed
**Usage**: Requirements, prerequisites, must-know facts
:::
```

**Custom Callouts (Require Extension):**
```markdown
::: {.definition}
📚 **Purpose**: Formal definitions and terminology
**Font Size**: 1.3rem (presentation optimized)
**Contrast**: 6:1 minimum ratio
:::

::: {.exercise title="Practice Exercise"}
✏️ **Purpose**: In-class practice activities
**Structure**: Step-by-step instructions with outcomes
:::

::: {.homework}
📝 **Purpose**: Take-home assignments and projects
**Structure**: Clear deliverables and deadlines
:::

::: {.objective}
🎯 **Purpose**: Learning goals and expected outcomes
**Placement**: Always at beginning of sections
:::

::: {.prompt}
🤖 **Purpose**: AI/LLM prompting guidance
**Structure**: Specific prompts to try with AI tools
:::
```

### Typography and Accessibility Standards (LOCKED REQUIREMENTS)
```css
/* CRITICAL: These standards NEVER change across themes */
:root {
  /* Educational presentation requirements */
  --base-font-size: 1.4rem;           /* Classroom visibility */
  --line-height-base: 1.65;           /* Reading comfort */
  --callout-font-size: 1.3rem;        /* Callout text size */
  --callout-title-size: 1.3rem;       /* Callout title size */
  --callout-padding: 1.5rem;          /* Internal spacing */
  
  /* Contrast requirements (WCAG AA+) */
  --min-contrast-ratio: 6:1;          /* Accessibility compliance */
  
  /* Responsive breakpoints */
  --mobile-breakpoint: 768px;
  --tablet-breakpoint: 1024px;
  --desktop-breakpoint: 1200px;
}
```

## Automation Script System Requirements

### Core Automation Scripts (TO BE CREATED)

#### 1. `generate_site.py` - Master Orchestrator
```python
"""
Master script that orchestrates entire site generation.
MUST be runnable from any directory in project.
"""

def main():
    # Auto-detect uumami directory from current location
    uumami_dir = find_uumami_directory()
    
    # Phase 1: Scan content structure
    structure = scan_content_structure(uumami_dir)
    
    # Phase 2: Validate naming conventions
    validate_structure(structure)
    
    # Phase 3: Generate main navigation (_quarto.yml)
    generate_main_navigation(structure, uumami_dir)
    
    # Phase 4: Update all _nav.qmd files
    update_navigation_components(structure, uumami_dir)
    
    print("✅ Site generation complete!")

# QUIRK: Must handle relative vs absolute paths
def find_uumami_directory():
    current = Path.cwd()
    while current != current.parent:
        if (current / 'uumami').exists():
            return current / 'uumami'
        current = current.parent
    raise FileNotFoundError("Cannot find uumami directory")
```

#### 2. `scan_structure.py` - Content Discovery
```python
"""
Discovers and analyzes content structure.
Handles complex nesting and file type filtering.
"""

class ContentScanner:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        
    def scan_all_content(self):
        """Discover all content following naming conventions."""
        structure = {
            'chapters': [],
            'appendices': [],
            'development': []
        }
        
        # Scan notas/ directory
        if (self.base_dir / 'notas').exists():
            structure['chapters'] = self._scan_chapters()
            
        # Scan quarto_development/ directory  
        if (self.base_dir / 'quarto_development').exists():
            structure['development'] = self._scan_development()
            
        return structure
        
    def _scan_chapters(self):
        """Handle numbered chapters and lettered appendices."""
        chapters = []
        notas_dir = self.base_dir / 'notas'
        
        for item in sorted(notas_dir.iterdir()):
            if item.is_dir():
                if re.match(r'^\d{2}_', item.name):
                    # Numbered chapter
                    chapters.append(self._analyze_chapter(item))
                elif re.match(r'^[a-z]_', item.name):
                    # Lettered appendix
                    chapters.append(self._analyze_appendix(item))
                    
        return chapters
        
    def _analyze_chapter(self, chapter_dir):
        """Deep analysis of chapter structure."""
        chapter = {
            'name': chapter_dir.name,
            'path': chapter_dir,
            'has_index': (chapter_dir / f"{chapter_dir.name[:2]}_index.qmd").exists(),
            'sections': [],
            'navigation_file': chapter_dir / '_nav.qmd'
        }
        
        # Scan for sections
        for item in sorted(chapter_dir.iterdir()):
            if item.is_file() and item.suffix == '.qmd':
                if not item.name.endswith('_index.qmd') and item.name != '_nav.qmd':
                    chapter['sections'].append(self._analyze_section(item))
            elif item.is_dir() and not item.name in SUPPORTING_DIRECTORIES:
                chapter['sections'].append(self._analyze_section_directory(item))
                
        return chapter
```

#### 3. `generate_navigation.py` - Main Navigation Creation
```python
"""
Generates _quarto.yml navbar from discovered structure.
Creates collapsible multi-level menus.
"""

class NavigationGenerator:
    def create_navbar_config(self, structure):
        """Generate complete navbar configuration."""
        navbar = {
            'left': [
                {'text': 'Home', 'file': 'index.qmd'},
                self._create_notes_menu(structure['chapters']),
                self._create_development_menu(structure['development'])
            ],
            'right': [
                {'icon': 'github', 'href': 'https://github.com/username/repo'}
            ],
            'tools': [
                {
                    'icon': 'globe',
                    'menu': [
                        {'text': 'Accessibility', 'file': 'components/accessibility-test.qmd'}
                    ]
                }
            ]
        }
        return navbar
        
    def _create_notes_menu(self, chapters):
        """Create hierarchical notes menu."""
        menu_items = []
        
        for chapter in chapters:
            if chapter['sections']:
                # Chapter with subsections
                chapter_menu = {
                    'text': f"{chapter['display_number']}. {chapter['title']}",
                    'file': chapter['index_path'],
                    'contents': []
                }
                
                for section in chapter['sections']:
                    if section['type'] == 'file':
                        chapter_menu['contents'].append({
                            'text': f"{section['number']} {section['title']}",
                            'file': section['path']
                        })
                    elif section['type'] == 'directory':
                        # Nested subsections
                        chapter_menu['contents'].append(
                            self._create_section_submenu(section)
                        )
                        
                menu_items.append(chapter_menu)
            else:
                # Simple chapter link
                menu_items.append({
                    'text': f"{chapter['display_number']}. {chapter['title']}",
                    'file': chapter['index_path']
                })
                
        return {'text': '📚 Notes', 'menu': menu_items}
```

#### 4. `update_nav_components.py` - Navigation Component Generation
```python
"""
Generates _nav.qmd files for each chapter/section.
Creates breadcrumbs and prev/next navigation.
"""

class NavComponentUpdater:
    def update_all_nav_files(self, structure):
        """Update navigation components throughout site."""
        for chapter in structure['chapters']:
            self._update_chapter_nav(chapter)
            
    def _update_chapter_nav(self, chapter):
        """Generate _nav.qmd for a chapter."""
        nav_content = self._generate_nav_template(chapter)
        
        nav_file = chapter['path'] / '_nav.qmd'
        with open(nav_file, 'w', encoding='utf-8') as f:
            f.write(nav_content)
            
    def _generate_nav_template(self, chapter):
        """Create navigation component content."""
        # JavaScript pages array
        pages_array = [section['filename'] for section in chapter['sections'] 
                      if section['type'] == 'file']
        
        template = f'''<!-- Auto-generated navigation for {chapter['name']} -->
<script>
const pages = {json.dumps(pages_array, indent=4)};

// Navigation logic (same as existing pattern)
function getCurrentPageIndex() {{
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split('/').pop();
    return pages.findIndex(page => currentPath.includes(page.replace('.qmd', '')));
}}

function updateNavigation() {{
    const currentIndex = getCurrentPageIndex();
    const prevBtn = document.querySelector('.nav-prev');
    const nextBtn = document.querySelector('.nav-next');
    
    if (prevBtn && currentIndex > 0) {{
        prevBtn.onclick = () => navigateTo(pages[currentIndex - 1]);
        prevBtn.style.display = 'block';
    }}
    
    if (nextBtn && currentIndex < pages.length - 1) {{
        nextBtn.onclick = () => navigateTo(pages[currentIndex + 1]);
        nextBtn.style.display = 'block';
    }}
}}

function navigateTo(page) {{
    window.location.href = page;
}}

document.addEventListener('DOMContentLoaded', updateNavigation);
</script>

<!-- Breadcrumb navigation -->
{self._generate_breadcrumb(chapter)}

<!-- Section navigation -->
{self._generate_section_list(chapter)}

<!-- Previous/Next controls -->
<div class="navigation-controls">
    <button class="nav-prev" style="display: none;">⬅️ Previous</button>
    <button class="nav-next" style="display: none;">Next ➡️</button>
</div>
'''
        return template
```

### Navigation System Requirements (DETAILED SPECS)

#### Main Navbar Generation Rules
- **Auto-Detection**: Scan `notas/` and `quarto_development/` for content
- **Hierarchy**: Support 3-4 levels of nesting with collapsible menus
- **Order**: Sort by numeric prefixes (00-99) then alphabetic (a-z)
- **Index Detection**: Link to chapter index if exists, first section if not
- **Menu Structure**: Numbered chapters + lettered appendices + development section

#### Navigation Component (`_nav.qmd`) Requirements
- **JavaScript Arrays**: Hardcoded pages arrays for each chapter (existing pattern)
- **Breadcrumb Generation**: Automatic path construction from file location
- **Prev/Next Logic**: Sequential navigation through content files only (.qmd/.md)
- **Section Lists**: Collapsible chapter overview with current section highlighting
- **Path Resolution**: All links relative to current file location

#### Index Page Strategy (IMPLEMENTATION DECISION NEEDED)
- **Chapters**: MUST have index pages (`00_index.qmd`, `a_index.qmd`)
- **Sections**: MAY have index pages based on complexity
- **Detection Logic**: Auto-create if multiple files OR subdirectories exist
- **Override Options**: 
  - Marker file approach: `.force_index` or `.skip_index`
  - YAML frontmatter: `has_index: true/false`
  - Naming pattern: `_index.qmd` forces index creation

## Theme and Styling System (SOPHISTICATED EXISTING ARCHITECTURE)

### Style System Architecture (EXISTING WORKING LOGIC)

**Core CSS Logic (`uumami/styles/main.css` - EXISTING FILE):**
The main.css file establishes universal educational standards that NEVER change:

```css
/* EXISTING PATTERN: Educational presentation standards */
:root {
  /* Classroom-optimized typography (EXISTING) */
  --font-size-base: 1.4rem;                    /* Large enough for projection */
  --line-height-base: 1.65;                    /* Reading comfort */
  --callout-font-size: 1.3rem;                 /* Callout visibility */
  
  /* Layout standards (EXISTING) */
  --content-max-width: 95vw;                   /* Maximize screen usage */
  --toc-width: 300px;                          /* Sidebar table of contents */
  
  /* Universal accessibility (EXISTING) */
  --min-contrast-ratio: 6:1;                   /* WCAG AA+ compliance */
}

/* EXISTING PATTERN: Component structure (NEVER modify structure) */
.callout {
  font-size: var(--callout-font-size);         /* Theme can override size */
  padding: var(--callout-padding, 1.5rem);     /* Theme can override padding */
  border-left: 4px solid var(--callout-border-color); /* Theme sets colors */
}

/* EXISTING PATTERN: Navigation styling */
.breadcrumb-dropdown summary {
  cursor: pointer;
  padding: 0.5rem 1rem;
  background: var(--bg-color-offset, #f8f9fa);
  border: 1px solid var(--border-color, #dee2e6);
}
```

**Theme Override System (EXISTING LOGIC FROM `uumami/styles/themes/`):**

Each theme file follows this exact pattern:

```css
/* STEP 1: Font imports (REQUIRED FIRST) */
@import url('https://fonts.googleapis.com/css2?family=...');

/* STEP 2: Core variable definitions (REQUIRED) */
:root {
  /* Core palette (MUST define all) */
  --primary-color: #value;                     /* Headings, major elements */
  --accent-color: #value;                      /* Links, highlights */
  --bg-color: #value;                          /* Page background */
  --text-color: #value;                        /* Body text */
  
  /* Typography (MUST define with fallbacks) */
  --font-family-body: 'FontName', fallback;
  --font-family-heading: 'FontName', fallback;
  
  /* Optional component overrides */
  --callout-note-bg: rgba(color, 0.1);         /* Theme-specific callout colors */
  --breadcrumb-bg: var(--bg-color-offset);     /* Navigation colors */
}

/* STEP 3: Theme personality (OPTIONAL) */
h1:hover, h2:hover {
  text-shadow: 0 0 10px var(--accent-color);   /* Theme-specific effects */
}
```

**EXISTING THEMES (WORKING EXAMPLES):**
- `evangelion.css` - Dark sci-fi theme (DEFAULT)
- `cyberpunk.css` - Neon colors theme
- `_template.css` - Base template for new themes

### Accessibility System Integration (EXISTING WORKING CODE)

**Current Location: `uumami/ACCESSIBILITY_SETUP.md` (113 LINES)**
- Complete OpenDyslexic integration guide
- Auto-injection JavaScript code
- Navbar toggle implementation
- Persistent localStorage preferences
- **TARGET MIGRATION**: Move to `uumami/quarto_development/02_accessibility_features/00_setup_guide.qmd`

**Working Implementation (`uumami/components/accessibility-auto.html`):**
```html
<!-- EXISTING PATTERN: Inlined for reliability -->
<style>
/* CRITICAL: CDN font loading */
@import url('https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@4.5.0/index.css');

/* EXISTING LOGIC: Universal font override */
.dyslexic-mode * {
  font-family: 'OpenDyslexic', 'Comic Sans MS', 'Trebuchet MS', sans-serif !important;
}

/* EXISTING STYLING: Navbar integration */
.accessibility-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* EXISTING RESPONSIVE: Mobile optimization */
@media (max-width: 768px) {
  .accessibility-toggle .toggle-text { display: none; }
}
</style>

<script>
// EXISTING LOGIC: Smart navbar detection
const navbarLocations = [
  '.navbar-nav.ms-auto',    // Bootstrap 5
  '.navbar-nav',            // Bootstrap 4
  'nav ul'                  // Generic fallback
];

// EXISTING FEATURE: Persistent preferences
localStorage.getItem('dyslexic-mode') === 'true'
</script>
```

**INTEGRATION POINTS:**
- Auto-included via `_quarto.yml`: `include-after-body: components/accessibility-auto.html`
- Works with all themes (font override is universal)
- No conflicts with existing navigation

### Comprehensive Documentation System (EXISTING CONTENT)
**`styles/THEME_SYSTEM.md` (1000+ lines):**
- Complete theme creation tutorial with step-by-step examples
- CSS variable reference with all available overrides
- Multiple theme examples (Ocean, Academic, Minimalist, Cyberpunk)
- Troubleshooting guide with common issues
- Performance optimization guidelines
- Accessibility compliance requirements

**`styles/CALLOUT_GUIDE.md` (350+ lines):**
- Educational callout usage patterns
- 8 callout types with specific pedagogical purposes
- Extension setup and configuration
- Syntax examples and best practices
- Theme compatibility information

**Integration Requirements:**
- Move documentation content to `quarto_development/00_theme_system/`
- Update all relative paths for new directory structure
- Add to main navigation as development resource
- Maintain existing content quality and examples

### Accessibility System (WORKING IMPLEMENTATION)
**OpenDyslexic Integration (`components/accessibility-auto.html`):**
```html
<!-- QUIRK: Must be inlined for reliability -->
<style>
@import url('https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@4.5.0/index.css');

.dyslexic-mode * {
  font-family: 'OpenDyslexic', 'Comic Sans MS', sans-serif !important;
}
</style>

<script>
// QUIRK: Auto-injection into navbar
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar-nav.ms-auto');
    if (navbar) {
        const toggleHTML = `
            <li class="nav-item">
                <label class="accessibility-toggle">
                    <input type="checkbox" id="dyslexic-toggle">
                    <span>🔤 Dyslexic</span>
                </label>
            </li>`;
        navbar.insertAdjacentHTML('beforeend', toggleHTML);
        
        // Persistent localStorage preference
        const toggle = document.getElementById('dyslexic-toggle');
        if (localStorage.getItem('dyslexic-mode') === 'true') {
            toggle.checked = true;
            document.body.classList.add('dyslexic-mode');
        }
        
        toggle.addEventListener('change', function() {
            document.body.classList.toggle('dyslexic-mode', this.checked);
            localStorage.setItem('dyslexic-mode', this.checked.toString());
        });
    }
});
</script>
```

**Accessibility Requirements:**
- 6:1 contrast ratio minimum (WCAG AA+)
- Font sizes optimized for classroom projection
- Responsive design for all screen sizes
- Persistent cross-page preferences
- Universal font override capability

## Student Workflow and Distribution (WORKING SYSTEM)

### GitHub Actions Smart Detection (EXISTING CODE)
**`.github/workflows/publish.yml` Pattern:**
```yaml
# QUIRK: Automatic student vs instructor detection
- name: Identify Render Target
  id: identify_target
  run: |
    if [[ -d "students/${{ github.actor }}" ]]; then
      echo "TARGET_DIR=students/${{ github.actor }}" >> $GITHUB_ENV
      echo "Student directory found. Rendering student workspace."
    else
      echo "TARGET_DIR=uumami" >> $GITHUB_ENV  
      echo "No student directory. Rendering instructor version."
    fi

- name: Install Python dependencies
  run: pip install -r ${{ env.TARGET_DIR }}/requirements.txt

- name: Render Quarto Website
  uses: quarto-dev/quarto-actions/render@v2
  with:
    path: ${{ env.TARGET_DIR }}

- name: Upload artifact
  uses: actions/upload-pages-artifact@v3
  with:
    path: ${{ env.TARGET_DIR }}/_site
```

### Sophisticated Sync System (WORKING CODE)
**`students/_template/sync_with_instructor.sh` (125 lines):**
```bash
#!/bin/bash
# QUIRK: Path-independent execution
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DEST_DIR="${SCRIPT_DIR}"
ROOT_DIR=$( cd -- "${SCRIPT_DIR}/../.." &> /dev/null && pwd )
INSTRUCTOR_CONTENT_DIR="${ROOT_DIR}/uumami"

# QUIRK: Comprehensive exclusion patterns
EXCLUDE_PATTERNS=(
    -path '*/_site/*'
    -path '*/.quarto/*'
    -path '*/__pycache__/*'
    -path '*/styles/*'  # Styles handled separately by rsync
    -name '*.pyc'
)

# CRITICAL: Safe update mechanism
echo "Updating styles (won't overwrite your changes)..."
rsync -av --ignore-existing "${ROOT_DIR}/styles/" "${DEST_DIR}/styles/"

echo "Finding new content files..."
SOURCE_FILES=()
while IFS= read -r -d $'\0' file; do
    SOURCE_FILES+=("$file")
done < <(find "$INSTRUCTOR_CONTENT_DIR" -type f \( "${EXCLUDE_PATTERNS[@]}" \) -prune -o -type f -print0)

# QUIRK: Only copy files that don't exist (non-destructive)
FILES_TO_COPY=()
for src_file in "${SOURCE_FILES[@]}"; do
    relative_path="${src_file#"$INSTRUCTOR_CONTENT_DIR"/}"
    dest_file="${DEST_DIR}/${relative_path}"
    
    if [ ! -f "$dest_file" ]; then
        FILES_TO_COPY+=("$relative_path")
    fi
done

# Execute safe copy
for rel_path in "${FILES_TO_COPY[@]}"; do
    src_file="${INSTRUCTOR_CONTENT_DIR}/${rel_path}"
    dest_file="${DEST_DIR}/${rel_path}"
    mkdir -p "$(dirname "$dest_file")"
    cp "$src_file" "$dest_file"
    echo "  Copied: ${rel_path}"
done
```

### Student Directory Structure (SELF-CONTAINED)
```
students/[username]/
├── quarto_code/                    # Complete technical infrastructure
│   ├── scripts/                    # All automation tools
│   ├── components/                 # Accessibility and navigation
│   ├── styles/                     # Full theme system
│   └── templates/                  # Content templates
├── notas/                          # Student's personal notes
├── quarto_development/             # Framework documentation
├── _quarto.yml                     # Student-specific configuration
├── index.qmd                       # Student homepage
├── requirements.txt                # Student dependencies
└── sync_with_instructor.sh         # Update mechanism

# QUIRK: Students get COMPLETE copy of instructor infrastructure
# BENEFIT: Self-contained workspace, no external dependencies
```

### Sync Process Requirements
- **Non-Destructive**: NEVER overwrite existing student files
- **Additive Only**: Add new files, update unchanged files
- **Style Handling**: Separate rsync process for style updates
- **Path Independence**: Script works from any execution location
- **Confirmation Required**: User must approve all changes
- **Granular Reporting**: Show exactly what will be copied
- **Error Handling**: Graceful failures with helpful messages

## Legacy Content Handling (PRESERVATION STRATEGY)

### Current Content Locations (WORKING REFERENCES)
**`uumami/a_intro_appendix/` (FUNCTIONAL OLD STRUCTURE):**
- 9 complete sections with working navigation
- Established YAML headers and content patterns
- Working `_nav.qmd` with JavaScript navigation
- Complete callout usage examples
- All content should be preserved for reference during migration

**`uumami/c_quarto_appendix/` (GENERAL TUTORIALS):**
- Quarto language fundamentals
- Executable document concepts  
- Project workflow guidance
- Style and layout tutorials
- NOT course-specific content, more general framework documentation

### Migration Decisions Required

#### Legacy Directory Structure
```
uumami/legacy/                      # Preserved reference content
├── a_intro_appendix/               # Complete old intro (WORKING EXAMPLE)
│   ├── _nav.qmd                    # Reference for navigation patterns
│   ├── 01_creating_llm_accounts.qmd
│   ├── 02_how_to_get_help.qmd
│   ├── [... all existing content ...]
│   └── 09_alternative_gitpod_setup.qmd
└── c_quarto_appendix/              # General Quarto tutorials
    ├── 00_index.qmd
    ├── 01_the_language_of_quarto.qmd
    ├── 02_executable_documents.qmd
    ├── 03_the_project_workflow.qmd
    └── 04_style_and_layout.qmd
```

#### Content Categorization Strategy
**Course Content → `notas/00_intro/`:**
- All `a_intro_appendix/` content (class-specific setup)
- Reorganized with new naming conventions
- Updated paths for new directory structure

**Framework Documentation → `quarto_development/`:**
- `c_quarto_appendix/` content (general Quarto usage)
- `styles/THEME_SYSTEM.md` and `styles/CALLOUT_GUIDE.md`
- `ACCESSIBILITY_SETUP.md`
- New content creation workflows
- Script usage documentation

### Exclusion from Navigation/Building
**Update `_quarto.yml` to exclude legacy:**
```yaml
project:
  render:
    - "*.qmd"
    - "*.md"
    - "!legacy/**"        # Exclude legacy directory from building
    - "!**/*.py"
    - "!**/*.sh"
```

**Automation Script Exclusions:**
```python
# In content scanning scripts
LEGACY_DIRECTORIES = {'legacy', 'a_intro_appendix', 'c_quarto_appendix'}

def should_include_directory(dir_path):
    """Skip legacy directories in navigation generation."""
    return dir_path.name not in LEGACY_DIRECTORIES
```

## Technical Development Framework (`quarto_development/`)

### Purpose and Integration Strategy
**Separate Framework Documentation from Course Content:**
- Complete development tutorials for the Quarto educational system
- Distinct from `notas/` (course content) and `legacy/` (preserved content)
- Added to main navbar as separate "Development" section
- Follows same organizational patterns as course content but focused on framework usage

### Comprehensive Content Structure
```
uumami/quarto_development/
├── 00_index.qmd                     # Development hub and overview
├── _nav.qmd                         # Development navigation component
├── 00_theme_system/                 # Complete theme creation system
│   ├── 00_index.qmd                 # Theme system overview
│   ├── 00_theme_architecture.qmd    # Based on THEME_SYSTEM.md
│   ├── 01_creating_new_themes.qmd   # Step-by-step creation
│   ├── 02_css_variables.qmd         # Variable reference
│   ├── 03_theme_examples.qmd        # Working examples
│   └── 04_troubleshooting.qmd       # Common theme issues
├── 01_callout_system/               # Educational callout framework
│   ├── 00_index.qmd                 # Callout system overview  
│   ├── 00_callout_overview.qmd      # Based on CALLOUT_GUIDE.md
│   ├── 01_extension_setup.qmd       # Extension installation
│   ├── 02_callout_types.qmd         # 8 callout types detailed
│   └── 03_best_practices.qmd        # Usage patterns
├── 02_accessibility_features/       # Accessibility system
│   ├── 00_index.qmd                 # Accessibility overview
│   ├── 00_setup_guide.qmd           # Based on ACCESSIBILITY_SETUP.md
│   ├── 01_dyslexic_integration.qmd  # OpenDyslexic implementation
│   └── 02_testing_compliance.qmd    # Accessibility testing
├── 03_content_creation/             # Content authoring workflows
│   ├── 00_index.qmd                 # Content creation overview
│   ├── 00_file_templates.qmd        # Using content templates
│   ├── 01_naming_conventions.qmd    # Directory and file naming
│   ├── 02_yaml_headers.qmd          # Header configuration
│   └── 03_navigation_setup.qmd      # Setting up navigation
├── 04_automation_scripts/           # Script usage and development
│   ├── 00_index.qmd                 # Automation overview
│   ├── 00_generate_site.qmd         # Master script usage
│   ├── 01_content_scanning.qmd      # Structure discovery
│   ├── 02_navigation_generation.qmd # Navbar creation
│   └── 03_script_development.qmd    # Creating new scripts
├── 05_student_distribution/         # Student workflow system
│   ├── 00_index.qmd                 # Distribution overview
│   ├── 00_sync_mechanism.qmd        # How sync works
│   ├── 01_github_actions.qmd        # CI/CD setup
│   └── 02_student_setup.qmd         # Student onboarding
└── 06_troubleshooting/              # Common issues and solutions
    ├── 00_index.qmd                 # Troubleshooting overview
    ├── 00_build_issues.qmd          # Quarto build problems
    ├── 01_navigation_problems.qmd   # Navigation debugging
    ├── 02_theme_issues.qmd          # Theme troubleshooting
    └── 03_sync_problems.qmd         # Student sync issues
```

### Content Migration Requirements
**From Existing Documentation:**
- `styles/THEME_SYSTEM.md` → `00_theme_system/` (organized into multiple files)
- `styles/CALLOUT_GUIDE.md` → `01_callout_system/` (structured content)
- `ACCESSIBILITY_SETUP.md` → `02_accessibility_features/` (detailed guide)
- `c_quarto_appendix/` → Integrate into appropriate sections

**New Content Creation:**
- Script usage tutorials and development guides
- Content creation workflows and best practices
- Student distribution system documentation
- Comprehensive troubleshooting guides

### Navigation Integration Pattern
**Main Navbar Addition:**
```yaml
website:
  navbar:
    left:
      - text: "Home"
        file: index.qmd
      - text: "📚 Notes"
        menu: [... course content ...]
      - text: "🔧 Development"          # NEW SECTION
        menu:
          - text: "🎨 Theme System"
            file: quarto_development/00_theme_system/00_index.qmd
          - text: "📋 Callout System"  
            file: quarto_development/01_callout_system/00_index.qmd
          - text: "♿ Accessibility"
            file: quarto_development/02_accessibility_features/00_index.qmd
          - text: "✏️ Content Creation"
            file: quarto_development/03_content_creation/00_index.qmd
          - text: "⚙️ Automation"
            file: quarto_development/04_automation_scripts/00_index.qmd
          - text: "🎓 Student System"
            file: quarto_development/05_student_distribution/00_index.qmd
          - text: "🔧 Troubleshooting"
            file: quarto_development/06_troubleshooting/00_index.qmd
```

## Automation Scripts System

### Location: `uumami/quarto_code/scripts/`
**Rationale**: Scripts belong in student-copied content for self-contained workspaces

### Core Scripts Required
1. **`generate_site.py`**: Master orchestrator for full site generation
2. **`scan_structure.py`**: Analyzes directory structure and discovers content
3. **`generate_navigation.py`**: Creates/updates `_quarto.yml` navbar automatically
4. **`update_nav_components.py`**: Generates all `_nav.qmd` files
5. **`create_chapter.py`**: Interactive chapter/section creation wizard
6. **`validate_structure.py`**: Ensures naming conventions and structure integrity

### Script Design Principles
- **Semi-Automated**: Generate structure, allow manual content creation
- **Path-Independent**: Work from any directory in project
- **Non-Destructive**: Never overwrite existing content without confirmation
- **Template-Based**: Use configurable templates for generated content
- **Error-Handling**: Graceful failures with helpful error messages

### Automation Scope
- **Auto-Generate**: Navigation structure, `_quarto.yml`, `_nav.qmd` files
- **Manual Creation**: All educational content, custom styling, specific configurations
- **Template Application**: Chapter indices, section templates, YAML headers
- **Validation**: Naming conventions, file structure, required components

## Implementation Requirements (DETAILED PHASES)

### Phase 1: Infrastructure Reorganization (CRITICAL FOUNDATION)
**Directory Structure Setup:**
```bash
# 1. Create new directory structure
mkdir -p uumami/quarto_code/{scripts,components,styles/themes,templates}
mkdir -p uumami/quarto_development
mkdir -p uumami/legacy

# 2. Move existing components (PRESERVE ALL WORKING CODE)
mv uumami/components/* uumami/quarto_code/components/
mv uumami/styles/* uumami/quarto_code/styles/
mv uumami/_extensions uumami/quarto_code/_extensions/

# 3. Preserve legacy content
mv uumami/a_intro_appendix uumami/legacy/
mv uumami/c_quarto_appendix uumami/legacy/

# 4. Update all relative paths in content files
# CRITICAL: Update CSS imports and include paths
```

**Path Updates Required (SYSTEMATIC APPROACH):**
```python
# Script to update all relative paths
import re
from pathlib import Path

def update_yaml_headers(file_path):
    """Update CSS paths in YAML headers."""
    old_patterns = [
        r'- styles/main\.css',
        r'- styles/themes/(\w+)\.css'
    ]
    new_patterns = [
        r'- quarto_code/styles/main.css',
        r'- quarto_code/styles/themes/\1.css'
    ]
    # Apply regex replacements...

def update_include_paths(file_path):
    """Update {{< include >}} paths.""" 
    old_patterns = [
        r'{{< include components/(.+) >}}',
        r'{{< include _nav\.qmd >}}'
    ]
    new_patterns = [
        r'{{< include quarto_code/components/\1 >}}',
        r'{{< include _nav.qmd >}}'  # _nav.qmd stays in same directory
    ]
    # Apply replacements...
```

### Phase 2: Automation Script Development (CORE FUNCTIONALITY)
**Script Creation Priority:**
1. **`scan_structure.py`**: Content discovery foundation
2. **`validate_structure.py`**: Naming convention enforcement  
3. **`generate_navigation.py`**: Navbar generation
4. **`update_nav_components.py`**: _nav.qmd creation
5. **`generate_site.py`**: Master orchestrator
6. **`create_chapter.py`**: Interactive content creation

**Critical Implementation Details:**
```python
# Extension and dependency requirements
REQUIRED_EXTENSIONS = {
    'coatless-quarto/custom-callout': '>= 1.0.0'
}

PYTHON_DEPENDENCIES = {
    'pathlib': 'built-in',
    'pyyaml': '>= 6.0', 
    'click': '>= 8.0',  # For CLI interfaces
    'rich': '>= 12.0'   # For pretty console output
}

# File processing patterns
CONTENT_PATTERNS = {
    'chapter': r'^\d{2}_[\w_]+/?$',
    'appendix': r'^[a-z]_[\w_]+/?$', 
    'section': r'^\d{2}_[\w_]+\.(qmd|md)$',
    'index': r'^\d{2}_index\.qmd$'
}
```

### Phase 3: Content Migration and Development Framework (CONTENT STRATEGY)
**Development Tutorial Creation:**
```python
# Content migration mapping
MIGRATION_MAP = {
    'styles/THEME_SYSTEM.md': 'quarto_development/00_theme_system/',
    'styles/CALLOUT_GUIDE.md': 'quarto_development/01_callout_system/',
    'ACCESSIBILITY_SETUP.md': 'quarto_development/02_accessibility_features/',
    'legacy/c_quarto_appendix/': 'quarto_development/03_content_creation/'
}

# Content splitting strategy for large files
def split_large_documentation(source_file, target_directory):
    """Split comprehensive guides into structured sections."""
    # Parse markdown sections by headers
    # Create individual files for each major section
    # Maintain internal cross-references
    # Update navigation structure
```

**Legacy Content Handling:**
- **Preserve**: All `a_intro_appendix/` content in `legacy/` for reference
- **Exclude**: Update `_quarto.yml` to skip legacy directories in builds
- **Reference**: Keep as working examples for content creation patterns

### Phase 4: Navigation and Template System (AUTOMATION CORE)
**Template System Implementation:**
```python
# Template variable system
TEMPLATE_VARIABLES = {
    'chapter': {
        'CHAPTER_NUMBER': lambda ctx: ctx['prefix'],
        'CHAPTER_TITLE': lambda ctx: ctx['title'],
        'SECTION_LINKS': lambda ctx: generate_section_links(ctx['sections']),
        'RELATIVE_ROOT': lambda ctx: calculate_relative_path(ctx['depth'])
    },
    'navigation': {
        'BREADCRUMB_PATH': lambda ctx: build_breadcrumb(ctx['path']),
        'SECTION_LIST': lambda ctx: generate_section_list(ctx['chapter']),
        'PREV_NEXT': lambda ctx: generate_nav_controls(ctx['position'])
    }
}
```

**Navigation Generation Logic:**
```python
def generate_navbar_structure(content_structure):
    """Create hierarchical navbar from content discovery."""
    navbar = {
        'left': [
            {'text': 'Home', 'file': 'index.qmd'},
            create_notes_menu(content_structure['chapters']),
            create_development_menu(content_structure['development'])
        ],
        'right': [
            {'icon': 'github', 'href': 'REPO_URL'}
        ]
    }
    return navbar

def create_notes_menu(chapters):
    """Build nested menu structure for course content."""
    menu_items = []
    for chapter in sorted(chapters, key=lambda x: x['sort_key']):
        if chapter['sections']:
            # Multi-section chapter with submenu
            chapter_item = {
                'text': f"{chapter['number']}. {chapter['title']}",
                'file': chapter['index_path'],
                'contents': build_section_menu(chapter['sections'])
            }
        else:
            # Simple chapter link
            chapter_item = {
                'text': f"{chapter['number']}. {chapter['title']}",
                'file': chapter['index_path']
            }
        menu_items.append(chapter_item)
    return {'text': '📚 Notes', 'menu': menu_items}
```

### Phase 5: Student Distribution and Testing (VALIDATION)
**Student Sync Updates:**
```bash
# Update sync script for new structure
sed -i 's|uumami/styles|uumami/quarto_code/styles|g' students/_template/sync_with_instructor.sh
sed -i 's|uumami/components|uumami/quarto_code/components|g' students/_template/sync_with_instructor.sh

# Add new exclusion patterns
EXCLUDE_PATTERNS+=(
    -path '*/legacy/*'
    -path '*/quarto_code/_extensions/*'  # Extensions sync differently
)
```

**Testing Strategy:**
1. **Unit Testing**: Each automation script with test content
2. **Integration Testing**: Full site generation with sample structure
3. **Student Testing**: Sync mechanism with sample student directory
4. **Accessibility Testing**: All themes meet WCAG AA+ standards
5. **Performance Testing**: Large content structures (100+ files)

## Critical Technical Specifications

### File Processing and Build Requirements
**Quarto Project Configuration:**
```yaml
# CRITICAL: Exact _quarto.yml structure required
project:
  type: website
  output-dir: _site
  render:
    - "*.qmd"
    - "*.md"
    - "!**/*.py"                # Exclude Python scripts
    - "!**/*.sh"                # Exclude shell scripts  
    - "!**/*.json"              # Exclude data files
    - "!**/scripts/**"          # Exclude script directories
    - "!**/examples/**"         # Exclude example code
    - "!**/resources/**"        # Exclude resource directories
    - "!**/legacy/**"           # Exclude legacy content
    - "!**/_site/**"            # Exclude build output
    - "!**/.quarto/**"          # Exclude Quarto cache

website:
  navbar:
    # AUTO-GENERATED by scripts - DO NOT EDIT MANUALLY
    
format:
  html:
    theme: 
      - quarto_code/styles/main.css
      - quarto_code/styles/themes/evangelion.css
    include-after-body: quarto_code/components/accessibility-auto.html
    toc: true
    toc-location: right
    toc-depth: 3

filters:
  - quarto_code/_extensions/coatless-quarto/custom-callout/customcallout.lua
```

**Extension Dependencies (CRITICAL):**
```bash
# REQUIRED: Custom callout extension installation
cd uumami/
quarto add coatless-quarto/custom-callout

# Verify extension structure exists:
# uumami/quarto_code/_extensions/coatless-quarto/custom-callout/
# ├── _extension.yml
# ├── customcallout.lua  
# └── fa.lua
```

### Path Resolution System (MAJOR QUIRK)
**All paths must be relative to current file location:**
```yaml
# From root level (index.qmd)
css:
  - quarto_code/styles/main.css
  - quarto_code/styles/themes/evangelion.css

# From chapter level (notas/00_intro/00_index.qmd)  
css:
  - ../../quarto_code/styles/main.css
  - ../../quarto_code/styles/themes/evangelion.css

# From section level (notas/00_intro/00_prompt_engineering/00_what_is_prompting.qmd)
css:
  - ../../../quarto_code/styles/main.css
  - ../../../quarto_code/styles/themes/evangelion.css
```

### Navigation Component Requirements (EXACT SPECS)
**JavaScript Navigation Pattern (MUST MAINTAIN):**
```html
<!-- CRITICAL: Hardcoded pages array for each chapter -->
<script>
const pages = [
    "00_what_is_prompting.qmd",
    "01_prompt_structure.qmd", 
    "02_advanced_techniques.qmd"
];

// QUIRK: URL-based page detection
function getCurrentPageIndex() {
    const currentPath = window.location.pathname;
    return pages.findIndex(page => currentPath.includes(page.replace('.qmd', '')));
}

// QUIRK: Must handle both development and production URLs
function navigateTo(page) {
    window.location.href = page;
}

// CRITICAL: Auto-initialize on every page
document.addEventListener('DOMContentLoaded', updateNavigation);
</script>
```

### Theme System Requirements (EXACT VARIABLE NAMES)
**Required CSS Variables (NEVER CHANGE NAMES):**
```css
:root {
  /* CORE PALETTE - Required by all themes */
  --primary-color: #value;
  --accent-color: #value;
  --text-color: #value;
  --text-color-light: #value;
  --bg-color: #value;
  --bg-color-offset: #value;
  --link-color: #value;
  --link-color-hover: #value;
  --border-color: #value;

  /* TYPOGRAPHY - Required with fallbacks */
  --font-family-body: 'FontName', fallback;
  --font-family-heading: 'FontName', fallback;
  --font-family-monospace: 'FontName', fallback;

  /* COMPONENTS - Optional overrides */
  --code-bg-color: #value;
  --code-text-color: #value;
  --table-header-bg: #value;
  --table-row-even-bg: #value;

  /* CALLOUT OVERRIDES - Optional theme-specific colors */
  --callout-note-bg: #value;
  --callout-note-border: #value;
  --callout-tip-bg: #value;
  --callout-tip-border: #value;
  /* ... etc for all 8 callout types */
}
```

### Accessibility System Requirements (EXACT IMPLEMENTATION)
**Font Loading and Override System:**
```html
<!-- CRITICAL: Must be inlined in components/accessibility-auto.html -->
<style>
@import url('https://cdn.jsdelivr.net/npm/@fontsource/opendyslexic@4.5.0/index.css');

.dyslexic-mode * {
  font-family: 'OpenDyslexic', 'Comic Sans MS', 'Trebuchet MS', sans-serif !important;
}
</style>
```

**Navbar Integration (AUTO-INJECTION REQUIRED):**
```javascript
// QUIRK: Must find navbar dynamically (different Quarto versions)
const navbarRight = document.querySelector('.navbar-nav.ms-auto') || 
                   document.querySelector('.navbar-nav') ||
                   document.querySelector('nav ul');
```

### Content Validation Patterns (REGEX REQUIREMENTS)
```python
# CRITICAL: Exact regex patterns for validation
NAMING_PATTERNS = {
    'chapter_dir': r'^\d{2}_[a-zA-Z0-9_]+$',
    'appendix_dir': r'^[a-z]_[a-zA-Z0-9_]+$',
    'section_file': r'^\d{2}_[a-zA-Z0-9_]+\.(qmd|md)$',
    'index_file': r'^\d{2}_index\.qmd$',
    'nav_file': r'^_nav\.qmd$'
}

# File type exclusions
EXCLUDE_FROM_NAVIGATION = {
    'directories': {'scripts', 'examples', 'resources', 'assets', 'data', 'legacy'},
    'extensions': {'.py', '.sh', '.json', '.csv', '.txt', '.yml', '.yaml'},
    'patterns': ['.*', '_*', '__*']  # Hidden and temp files
}
```

## Quality Assurance Standards

### Educational Standards
- **Content Accessibility**: All materials meet WCAG AA+ standards
- **Presentation Optimized**: Font sizes and contrast for classroom projection
- **Learning Structure**: Clear hierarchy with appropriate callout usage
- **Sequential Flow**: Logical progression with proper navigation

### Technical Standards
- **Cross-Platform**: Works on macOS, Windows, Linux
- **Browser Compatibility**: Modern browsers with graceful degradation
- **Performance**: Fast loading with minimal resource usage
- **Responsive Design**: Works on mobile, tablet, desktop, large screens

### Maintenance Standards
- **Documentation**: Every script and component documented
- **Error Handling**: Graceful failures with helpful messages
- **Validation**: Automated checking of conventions and structure
- **Testing**: Comprehensive testing of all automation

## Constraints and Limitations

### Technical Constraints
- **Quarto Dependencies**: Requires Quarto 1.3+ with extension support
- **Python Requirements**: Scripts require Python 3.8+
- **Git Integration**: Assumes Git repository for version control
- **Extension Dependencies**: Requires `quarto-custom-callout` extension

### Design Constraints
- **Naming Conventions**: Must follow strict prefix ordering system
- **File Types**: Only `.qmd` and `.md` for rendered content
- **Depth Limits**: Maximum 3-4 nesting levels for usability
- **Template Structure**: Must maintain educational content pattern

### Content Constraints
- **Callout Standards**: Must use 8 defined callout types appropriately
- **Theme Compatibility**: All content must work across all themes
- **Accessibility Requirements**: 6:1 contrast ratio minimum maintained
- **Student Distribution**: All content must be safe for student copying

## Success Criteria

### Functional Success
- **Automated Navigation**: Complete navbar generation from directory structure
- **Content Creation**: Streamlined workflow for new chapters/sections
- **Student Distribution**: Seamless updates without overwriting student work
- **Theme System**: Easy creation of new themes with documentation

### Educational Success
- **Clear Organization**: Intuitive content discovery and navigation
- **Accessibility**: Full compliance with accessibility standards
- **Presentation Quality**: Optimized for classroom teaching
- **Student Experience**: Self-contained, easy-to-use student workspaces

### Technical Success
- **Maintainability**: Clear, documented, extensible codebase
- **Reliability**: Robust error handling and validation
- **Performance**: Fast builds and responsive user experience
- **Scalability**: Supports large amounts of content without degradation

## Open Questions for Implementation

### Index Page Strategy
- **Question**: How to determine when subsections need index pages?
- **Options**: File count threshold, subdirectory detection, manual markers
- **Decision Needed**: Specific logic for auto-detection

### Legacy Content Integration  
- **Question**: Should `c_quarto_appendix/` content go in `notas/` or `quarto_development/`?
- **Consideration**: General Quarto tutorials vs. specific course content
- **Decision Needed**: Content categorization and placement

### Navigation Scope Configuration
- **Question**: Should `_nav.qmd` show all chapters or just current chapter sections?
- **Options**: Configurable scope, automatic detection, user preference
- **Decision Needed**: Default behavior and customization options

### Force/Skip Index Mechanism
- **Question**: How should users override automatic index page detection?
- **Options**: Marker files (`.force_index`), YAML frontmatter, naming patterns
- **Decision Needed**: Most intuitive and maintainable approach

## Summary for Coding Agents

This specification provides the **complete technical foundation** for implementing a sophisticated Quarto educational content management system. The document includes:

### What's Included ✅
- **Complete Directory Structure**: Every important directory with detailed examples
- **Existing Working Code**: All current implementations with technical quirks
- **Infrastructure Details**: JavaScript navigation, CSS theming, callout systems, accessibility
- **Automation Requirements**: Detailed script specifications with code examples
- **Student Distribution**: Working sync system and GitHub Actions configuration
- **Theme Architecture**: CSS variable system with unlimited theme support
- **Legacy Content Strategy**: Preservation and migration plans
- **Implementation Roadmap**: 5 detailed phases with specific technical requirements

### Critical Technical Dependencies 🔧
- **Quarto 1.3+** with extension support
- **`coatless-quarto/custom-callout` extension** (REQUIRED for educational callouts)
- **Python 3.8+** for automation scripts
- **Git repository** with GitHub Actions for student distribution
- **Relative path architecture** (all paths relative to file location)
- **CSS variable theme system** (unlimited themes with universal readability)

### Key Technical Quirks ⚠️
- **Hardcoded JavaScript navigation** with pages arrays in each `_nav.qmd`
- **Relative path resolution** from each file's location (major path complexity)
- **Extension-based callouts** requiring specific Lua filter configuration
- **Auto-injection accessibility** system with navbar integration
- **Smart student detection** in GitHub Actions based on directory existence
- **Non-destructive sync** system preserving student modifications

### Success Criteria 🎯
A coding agent should be able to use this specification to:
1. **Understand the complete existing system** without additional context
2. **Implement all automation scripts** following established patterns
3. **Maintain compatibility** with current working components
4. **Preserve educational standards** (accessibility, presentation optimization)
5. **Support the student workflow** without breaking self-contained workspaces
6. **Extend the system** with new themes, content, and features

### What's NOT Included (Intentionally) ❌
- **Specific content creation** (handled manually by instructors)
- **Exact implementation code** (coding agents should create tailored solutions)
- **Hardcoded solutions** (specification provides flexibility for appropriate technical decisions)
- **Theme-specific designs** (system supports unlimited theme creation)

This specification enables **autonomous implementation** of the complete educational content management system while maintaining the sophisticated existing infrastructure and educational quality standards. 