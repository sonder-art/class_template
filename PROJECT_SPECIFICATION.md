# PROJECT SPECIFICATION: Quarto Educational Infrastructure Automation

> **⚠️ INFRASTRUCTURE AUTOMATION ONLY**  
> This specification is for coding agents to build automation backbone and framework infrastructure.  
> **AGENTS BUILD**: Scripts, navigation generation, templates, structure validation  
> **HUMANS CREATE**: All educational content, lessons, course materials, specific configurations

## TODO: Implementation Status

### Phase 1: Infrastructure Setup (Foundation) 🔧 ✅ **COMPLETED**
- [x] **Create new directory structure**: `quarto_code/`, `quarto_development/`, `legacy/`
- [x] **Move existing components**: Preserve working code during reorganization
  - [x] `uumami/components/` → `uumami/quarto_code/components/`
  - [x] `uumami/styles/` → `uumami/quarto_code/styles/`
  - [x] `uumami/_extensions/` → `uumami/quarto_code/_extensions/`
- [x] **Preserve legacy content**: Move `a_intro_appendix/` to `legacy/` and `c_quarto_appendix/` to `quarto_development/`
- [x] **Update critical paths**: Systematically update all relative paths (manual update completed)
  - [x] CSS imports in YAML headers: `styles/` → `quarto_code/styles/` (updated in `_quarto.yml` and `index.qmd`)
  - [x] Include statements: `components/` → `quarto_code/components/` (updated in `_quarto.yml`)
  - [x] Extension filters in `_quarto.yml`: Updated to full path `quarto_code/_extensions/coatless-quarto/custom-callout/customcallout.lua`
- [x] **Validation**: Ensure site builds and navigation works after moves (`quarto render index.qmd` ✅)

### Phase 2: Core Automation Scripts 🤖  
- [x] **`scan_structure.py`**: Content discovery with naming pattern validation ✅ **COMPLETED**
  - [x] Implement directory scanning with regex patterns for XX_name/ and Y_name/
  - [x] Detect .qmd files vs directories, identify index files
  - [x] Output structured JSON for other scripts to consume
  - [x] Professional CLI interface with click and rich console output
  - [x] YAML frontmatter title extraction from .qmd files
  - [x] Comprehensive error handling and validation modes
  - [x] Successfully tested against current notas/00_intro/ structure
- [ ] **`validate_structure.py`**: Structure enforcement and error checking
  - [ ] Validate naming conventions (XX_ for chapters, Y_ for appendices)
  - [ ] Check required files exist (XX_index.qmd, _nav.qmd)
  - [ ] Verify relative paths are correct for file locations
- [ ] **`generate_navigation.py`**: Auto-generate `_quarto.yml` navbar
  - [ ] Parse structure data and create hierarchical navbar
  - [ ] Sort chapters numerically (00-99), appendices alphabetically (a-z)
  - [ ] Preserve existing navbar elements (right side, tools)
- [ ] **`update_nav_components.py`**: Generate `_nav.qmd` files
  - [ ] Create JavaScript pages arrays from section discovery
  - [ ] Generate breadcrumb dropdowns and section overviews
  - [ ] Preserve existing navigation logic patterns
- [ ] **`create_chapter.py`**: Interactive content creation wizard
  - [ ] Prompt for chapter details with validation
  - [ ] Create directory structure with templates
  - [ ] Update global navigation automatically
- [ ] **`generate_site.py`**: Master orchestrator script
  - [ ] Coordinate all scripts in proper order
  - [ ] Provide dry-run mode and backup creation
  - [ ] Handle errors gracefully with rollback capability

### Phase 3: Template System 📋
- [ ] **Create generic templates**: Content scaffolding without course-specific material
  - [ ] `templates/chapter_index.qmd`: Chapter landing page template
  - [ ] `templates/section_single.qmd`: Single section file template  
  - [ ] `templates/navigation_component.qmd`: _nav.qmd template
- [ ] **Build variable substitution system**: Template processing engine
  - [ ] Implement variable replacement ({{CHAPTER_NUMBER}}, {{RELATIVE_CSS_PATHS}}, etc.)
  - [ ] Calculate relative paths based on file depth
  - [ ] Generate section links and navigation components
- [ ] **Test template application**: Verify generated content follows patterns
  - [ ] Validate YAML headers are correct
  - [ ] Ensure navigation integrates properly
  - [ ] Check relative paths resolve correctly

### Phase 4: Enhanced Navigation 🧭
- [ ] **Preserve JavaScript patterns**: Maintain existing navigation logic
  - [ ] Keep hardcoded pages arrays pattern (lines 60-75 in `a_intro_appendix/_nav.qmd`)
  - [ ] Preserve URL-based current page detection
  - [ ] Maintain breadcrumb update functionality
- [ ] **Add automation enhancements**: Auto-generate navigation components
  - [ ] Generate pages arrays from directory scanning
  - [ ] Create collapsible section overviews
  - [ ] Auto-update breadcrumb dropdowns
- [ ] **Integration testing**: Verify navigation works with new structure
  - [ ] Test prev/next buttons with generated arrays
  - [ ] Validate breadcrumb dropdown functionality
  - [ ] Ensure JavaScript runs correctly on all pages

### Phase 5: Student Distribution Updates 🎓
- [ ] **Update GitHub Actions**: Modify for new quarto_code/ structure
  - [ ] Verify smart detection still works (no changes needed to logic)
  - [ ] Test with sample student directories
  - [ ] Validate build process with new paths
- [ ] **Enhance sync script**: Update `students/_template/sync_with_instructor.sh`
  - [ ] Update source paths: `INSTRUCTOR_CONTENT_DIR` → new structure
  - [ ] Add exclusion patterns for `legacy/` and `quarto_code/_extensions/`
  - [ ] Preserve existing safety mechanisms (--ignore-existing)
- [ ] **Final integration testing**: Complete workflow validation
  - [ ] Test instructor creates content → student syncs → both build successfully
  - [ ] Verify non-destructive updates preserve student modifications
  - [ ] Performance testing with large content structures (100+ files)

### Validation Checkpoints ✅
- [ ] **Phase 1 Complete**: Site builds without errors, all navigation functional
- [ ] **Phase 2 Complete**: All automation scripts work independently and together
- [ ] **Phase 3 Complete**: Template system creates valid content with correct paths
- [ ] **Phase 4 Complete**: Enhanced navigation preserves existing patterns
- [ ] **Phase 5 Complete**: Student distribution system updated and tested
- [ ] **Final Validation**: Complete infrastructure supports content creation workflow

---

## Getting Started for Coding Agents

### Prerequisites Checklist ✅
Before starting implementation, verify these exist:
- [ ] `uumami/` directory with working Quarto site
- [ ] Git repository with clean working directory (backup current state)
- [ ] Python 3.8+ installed with pip
- [ ] Quarto 1.3+ installed and functional
- [ ] Working `quarto render uumami/` command (test current site builds)

### First Steps - Phase 1 Implementation
**Working Directory**: All commands should be run from project root (`/path/to/class_template/`)

**Step 1: Create Backup**
```bash
# Create backup of current working state
cp -r uumami uumami_backup_$(date +%Y%m%d_%H%M%S)
git add -A && git commit -m "Backup before infrastructure reorganization"
```

**Step 2: Verify Current State**
```bash
# Test that site currently builds
cd uumami && quarto render
# Should generate _site/ without errors
# Test accessibility: open _site/index.html and verify navigation works
```

**Step 3: Begin Infrastructure Setup**
```bash
# Create new directory structure
mkdir -p uumami/quarto_code/{scripts,components,styles,_extensions,templates}
mkdir -p uumami/{quarto_development,legacy}
```

### Validation Commands for Each Phase

**Phase 1 Validation**:
```bash
# After moves, test site still builds
cd uumami && quarto render
# Test navigation: check that JavaScript navigation still works
# Test themes: verify accessibility toggle appears in navbar
# Test extensions: ensure callouts render (look for custom callout icons)
```

**Phase 2 Validation**:
```bash
# Test each script individually
python uumami/quarto_code/scripts/scan_structure.py uumami/
python uumami/quarto_code/scripts/validate_structure.py uumami/
python uumami/quarto_code/scripts/generate_navigation.py uumami/
```

**Phase 3 Validation**:
```bash
# Test template system
python uumami/quarto_code/scripts/create_chapter.py
# Follow prompts to create test chapter, verify files are created correctly
```

**Rollback Procedures**:
```bash
# If Phase 1 fails, restore from backup
rm -rf uumami
cp -r uumami_backup_* uumami
git reset --hard HEAD~1  # If committed
```

### Path Update Implementation Details

**Find Files Needing Updates**:
```bash
# Find all .qmd files with CSS imports
find uumami -name "*.qmd" -exec grep -l "styles/" {} \;

# Find files with component includes  
find uumami -name "*.qmd" -exec grep -l "components/" {} \;
```

**Systematic Path Update Algorithm**:
```python
# Implementation for path update script
import re
from pathlib import Path

def update_css_paths_in_file(file_path):
    """Update CSS paths in YAML header of a .qmd file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Calculate relative depth to determine ../ prefix needed
    depth = len(file_path.relative_to('uumami').parts) - 1
    relative_prefix = '../' * depth
    
    # Update CSS paths in YAML header
    patterns = [
        (r'- styles/main\.css', f'- {relative_prefix}quarto_code/styles/main.css'),
        (r'- styles/themes/(\w+)\.css', f'- {relative_prefix}quarto_code/styles/themes/\\1.css')
    ]
    
    for old_pattern, new_pattern in patterns:
        content = re.sub(old_pattern, new_pattern, content)
    
    with open(file_path, 'w') as f:
        f.write(content)
```

### Extension Verification Commands

**Test `coatless-quarto/custom-callout` Extension**:
```bash
# After moving _extensions, verify extension loads
cd uumami && quarto render --log-level debug 2>&1 | grep -i callout

# Test custom callouts in content
echo '::: {.prompt}
Test prompt callout
:::' > test_callout.qmd

quarto render test_callout.qmd
# Check output for custom callout styling
```

**Critical Verification Points**:
- [ ] Extension path in `_quarto.yml` updated correctly
- [ ] All 8 custom callout types render with icons
- [ ] No Lua filter errors in render log
- [ ] Custom callout CSS loads properly

## Executive Summary

This project implements automation infrastructure for a Quarto-based educational content management system. The system features **JavaScript-powered navigation**, **CSS variable theming**, **custom callout extensions**, **accessibility integration**, and **automated student distribution**.

### Core Infrastructure Components
- **Directory Scanning & Validation**: Automated content discovery with naming convention enforcement
- **Navigation Generation**: Auto-generate `_quarto.yml` navbar and `_nav.qmd` components from directory structure
- **Template System**: Generic content scaffolding with variable substitution
- **Student Distribution**: Non-destructive sync system with GitHub Actions integration
- **Path Resolution**: Handle complex relative path management across reorganized structure

### Agent vs Human Responsibilities

**🤖 CODING AGENTS BUILD:**
- Automation scripts (`scan_structure.py`, `generate_navigation.py`, etc.)
- Template system with variable substitution
- Directory reorganization utilities
- Navigation component generation
- Path update automation
- Structure validation tools

**👩‍🏫 HUMANS CREATE:**
- All educational content (.qmd files with actual lessons)
- Course-specific configurations and themes
- Learning objectives and exercise materials
- Custom styling beyond base system

### Success Criteria
- **Automated Structure**: Complete navbar generation from directory scanning
- **Template Workflow**: Streamlined chapter/section creation with consistent structure  
- **Path Independence**: All relative paths automatically calculated and updated
- **Student Safety**: Non-destructive updates preserving student modifications
- **Scalability**: System handles large content structures (100+ files) efficiently

---

## Current System Analysis

### Existing Directory Structure (CURRENT STATE)

```
uumami/                                    # Main instructor content
├── components/                           # ➡️ MOVE TO: quarto_code/components/
│   ├── accessibility-auto.html            # Working accessibility system
│   ├── accessibility-bar.html             # Legacy template
│   └── accessibility-test.qmd             # Test page
├── styles/                               # ➡️ MOVE TO: quarto_code/styles/
│   ├── main.css                          # Core structure (NEVER EDIT)
│   ├── THEME_SYSTEM.md                   # ➡️ MIGRATE TO: quarto_development/
│   ├── CALLOUT_GUIDE.md                  # ➡️ MIGRATE TO: quarto_development/
│   └── themes/                           # Complete theme collection
├── _extensions/                          # ➡️ MOVE TO: quarto_code/_extensions/
│   └── coatless-quarto/custom-callout/   # CRITICAL: Required for callouts
├── a_intro_appendix/                     # ➡️ PRESERVE IN: legacy/
│   └── _nav.qmd                          # REFERENCE PATTERN for automation
├── c_quarto_appendix/                    # ➡️ MIGRATE TO: quarto_development/
├── notas/                                # Current course content (ENHANCE)
│   └── 00_intro/                         # Chapter structure example
├── _quarto.yml                           # Main config (UPDATE paths)
├── index.qmd                             # Homepage (UPDATE paths)
└── ACCESSIBILITY_SETUP.md                # ➡️ MIGRATE TO: quarto_development/
```

### Working Code Patterns (CRITICAL REFERENCES)

#### JavaScript Navigation System 
**Pattern Location**: `uumami/a_intro_appendix/_nav.qmd` (lines 59-107)

**Existing Working Code** (lines 62-72):
```javascript
const pages = [
  { file: '00_index.qmd', title: 'Welcome' },
  { file: '01_creating_llm_accounts.qmd', title: 'A.1 AI Assistants' },
  { file: '02_how_to_get_help.qmd', title: 'A.2 How to Get Help' },
  { file: '03_installing_python.qmd', title: 'A.3 Install Python' },
  { file: '04_first_python_interaction.qmd', title: 'A.4 First Python Steps' },
  // ... continues with file + title objects (11 total items)
];
```

**AUTOMATION TARGET**: Generate these pages arrays from `scan_structure.py` output

**Critical Navigation Logic** (lines 75-77):
```javascript
const currentPath = window.location.pathname;
const currentFile = currentPath.split('/').pop().replace('.html', '.qmd');
const currentIndex = pages.findIndex(page => page.file === currentFile);
```

**QUIRK**: URL detection handles `.html` → `.qmd` conversion for build vs source

**Dynamic Button Generation** (lines 83-85):
```javascript
const prevHtml = prevPage.file.replace('.qmd', '.html');
document.getElementById('nav-prev').innerHTML = 
  `<a href="./${prevHtml}" class="nav-button prev">← ${prevPage.title}</a>`;
```

**QUIRK**: Buttons show page titles from hardcoded array, not filenames

**Breadcrumb Integration** (line 102): 
```javascript
document.querySelector('.breadcrumb-current').textContent = pages[currentIndex].title;
```

**AUTOMATION REQUIREMENT**: Scripts must generate identical pages array structure

#### CSS Theme System
**Pattern Location**: `uumami/styles/themes/evangelion.css` (lines 22-35)

**Required Font Import Pattern** (line 22):
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Fira+Code:wght@300;400;500;600&family=Source+Sans+Pro:wght@400;700&family=Share+Tech+Mono&display=swap');
```

**QUIRK**: Google Fonts `@import` must be first line in theme files

**CSS Variable Override Architecture** (line 31+):
```css
:root {
  /* Core palette variables that override main.css defaults */
  --primary-color: #value;
  --text-color: #value;
  --bg-color: #value;
  /* ... continues with all required variables */
}
```

**AUTOMATION REQUIREMENT**: After move to `quarto_code/styles/`, update all YAML headers:
- From: `- styles/themes/evangelion.css`  
- To: `- quarto_code/styles/themes/evangelion.css`

**Path Update Complexity**: Each content file has different relative depth to styles directory

#### Accessibility Auto-Injection
**Pattern Location**: `uumami/components/accessibility-auto.html` (lines 21-28)

**Smart Navbar Detection Logic** (lines 21-25):
```javascript
const navbar = document.querySelector('.navbar-nav.navbar-nav-scroll.ms-auto') || 
               document.querySelector('.navbar-nav[class*="right"]') ||
               document.querySelector('.navbar .navbar-nav:last-child') ||
               document.querySelector('.navbar-nav');
```

**QUIRK**: Multiple fallback selectors handle different Quarto/Bootstrap versions

**Auto-Injection Pattern** (lines 30-35): Creates accessibility toggle and injects into navbar
**Persistent Storage** (throughout): Uses `localStorage.getItem('dyslexic-mode')` for cross-page memory

**Current Integration** (`uumami/_quarto.yml` line 90):
```yaml
include-after-body: components/accessibility-auto.html
```

**AUTOMATION REQUIREMENT**: Update to `include-after-body: quarto_code/components/accessibility-auto.html`

#### Student Sync Safety
**Pattern Location**: `students/_template/sync_with_instructor.sh` (lines 20-50)

**Path Independence Pattern** (lines 25-29):
```bash
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DEST_DIR="${SCRIPT_DIR}"
ROOT_DIR=$( cd -- "${SCRIPT_DIR}/../.." &> /dev/null && pwd )
INSTRUCTOR_CONTENT_DIR="${ROOT_DIR}/uumami"
```

**QUIRK**: Complex path resolution works regardless of execution location

**Non-Destructive Safety** (line 45):
```bash
rsync -av --ignore-existing "${INSTRUCTOR_CONTENT_DIR}/" "${DEST_DIR}/"
```

**CRITICAL**: `--ignore-existing` flag prevents overwriting student modifications

**AUTOMATION REQUIREMENT**: Update for multiple source paths in new structure:
- Current: Single source `INSTRUCTOR_CONTENT_DIR="${ROOT_DIR}/uumami"`  
- New: Multiple sources needed:
  - Infrastructure: `"${ROOT_DIR}/uumami/quarto_code/"` (components, styles, scripts)
  - Content: `"${ROOT_DIR}/uumami/notas/"` (course content)
  - Development: `"${ROOT_DIR}/uumami/quarto_development/"` (framework docs)
- Add exclusions: `legacy/`, `quarto_code/_extensions/` (extensions sync separately)
- Preserve safety: `--ignore-existing` for all sync operations

### Critical Dependencies

**Quarto Requirements**:
- Quarto 1.3+ (extension support required)
- `coatless-quarto/custom-callout` extension (CRITICAL for educational callouts)

**Python Dependencies** (for automation scripts) ✅ **UPDATED**:
```python
REQUIRED_PACKAGES = {
    'pathlib': 'built-in',      # Path manipulation
    'pyyaml': '>= 6.0',         # YAML processing (already in requirements.txt)
    'click': '>= 8.0',          # CLI interfaces (✅ added to uumami/requirements.txt)
    'rich': '>= 12.0',          # Console output (✅ added to uumami/requirements.txt)
    're': 'built-in'            # Regex validation
}
```

**Git Integration**:
- GitHub repository with Actions for student distribution
- Working `.github/workflows/publish.yml` with smart directory detection

---

## Infrastructure Requirements

### Directory Reorganization Specifications

#### Target Structure (POST-AUTOMATION)
```
uumami/
├── quarto_code/                          # 🆕 Technical infrastructure
│   ├── scripts/                          # 🆕 All automation tools
│   │   ├── generate_site.py              # Master orchestrator
│   │   ├── scan_structure.py             # Content discovery
│   │   ├── generate_navigation.py        # Navbar creation
│   │   ├── update_nav_components.py      # _nav.qmd generation
│   │   ├── create_chapter.py             # Interactive content creation
│   │   └── validate_structure.py         # Structure enforcement
│   ├── components/                       # ⬅️ FROM: uumami/components/
│   ├── styles/                           # ⬅️ FROM: uumami/styles/
│   ├── _extensions/                      # ⬅️ FROM: uumami/_extensions/
│   └── templates/                        # 🆕 Content templates
│       ├── chapter_index.qmd             # Chapter landing template
│       ├── section_single.qmd            # Single section template
│       └── navigation_component.qmd      # _nav.qmd template
├── notas/                                # Course content structure
│   ├── XX_chapter_name/                  # Numbered chapters (00-99)
│   │   ├── XX_index.qmd                  # Chapter landing page
│   │   ├── _nav.qmd                      # 🤖 AUTO-GENERATED navigation
│   │   ├── XX_section_name.qmd           # Single file sections
│   │   └── XX_section_dir/               # Multi-file sections
│   └── Y_appendix_name/                  # Lettered appendices (a-z)
├── quarto_development/                   # 🆕 Framework documentation
├── legacy/                               # 🆕 Preserved reference content
│   ├── a_intro_appendix/                 # Working navigation example
│   └── c_quarto_appendix/                # General Quarto tutorials
├── _quarto.yml                           # 🤖 AUTO-GENERATED main config
└── index.qmd                             # Homepage (path updates needed)
```

#### Critical Move Operations
1. **Preserve Working Code**: Move `components/`, `styles/`, `_extensions/` intact
2. **Update All Paths**: CSS imports, includes, filter references
3. **Create New Directories**: `scripts/`, `templates/`, `quarto_development/`, `legacy/`
4. **Validate Extensions**: Ensure `coatless-quarto/custom-callout` remains functional

### Automation Script Specifications

#### 1. `scan_structure.py` - Content Discovery Engine
**Purpose**: Discover and analyze directory structure for navigation generation

**Input**: Path to `uumami/` directory  
**Output**: Structured JSON with chapters, sections, appendices

**Key Logic**:
```python
NAMING_PATTERNS = {
    'chapter': r'^\d{2}_[\w_]+$',           # 00_intro, 01_python_basics
    'appendix': r'^[a-z]_[\w_]+$',          # a_installation, b_troubleshooting  
    'section_file': r'^\d{2}_[\w_]+\.qmd$', # 00_overview.qmd, 01_setup.qmd
    'index_file': r'^\d{2}_index\.qmd$'     # 00_index.qmd, 01_index.qmd
}

EXCLUDE_PATTERNS = {
    'directories': {'scripts', 'examples', 'resources', 'legacy', 'quarto_code'},
    'files': {'.py', '.sh', '.json', '_nav.qmd', '.*'}
}
```

**Integration**: Feeds data to all other generation scripts

**Output Data Structure**:
```python
{
    "chapters": [
        {
            "name": "00_intro",
            "prefix": "00", 
            "title": "Introduction",
            "path": "uumami/notas/00_intro",
            "has_index": True,
            "index_file": "00_index.qmd",
            "sections": [
                {
                    "file": "00_overview.qmd",
                    "title": "Course Overview", 
                    "display_title": "0.0 Course Overview",
                    "type": "file"
                },
                {
                    "name": "01_getting_started",
                    "title": "Getting Started",
                    "display_title": "0.1 Getting Started", 
                    "type": "directory",
                    "subsections": [...]
                }
            ]
        }
    ],
    "appendices": [
        {
            "name": "a_installation",
            "prefix": "a",
            "title": "Installation Guides",
            "path": "uumami/notas/a_installation",
            "sections": [...]
        }
    ]
}
```

#### 2. `generate_navigation.py` - Main Navbar Creation
**Purpose**: Create/update `_quarto.yml` navbar from discovered structure

**Input**: Structure data from `scan_structure.py`  
**Output**: Updated `_quarto.yml` with complete navbar

**Navigation Hierarchy**:
```yaml
navbar:
  left:
    - text: "Home"
      file: index.qmd
    - text: "📚 Course"                    # 🤖 AUTO-GENERATED
      menu:
        - text: "XX. Chapter Name"         # Numbered chapters
          file: notas/XX_chapter/XX_index.qmd
          contents:                        # Subsections if exist
            - text: "XX.Y Section Name"
              file: notas/XX_chapter/XX_section.qmd
        - section: "Appendices"
        - text: "Y. Appendix Name"         # Lettered appendices  
          file: notas/Y_appendix/Y_index.qmd
    - text: "🔧 Development"               # Framework docs
      menu: [... quarto_development structure ...]
```

**Current Navbar Structure** (`uumami/_quarto.yml` lines 52-75):
```yaml
website:
  navbar:
    left:
      - href: index.qmd
        text: Class Notes
      - href: syllabus.qmd
        text: Syllabus
      - text: "Appendices"        # MANUAL navigation structure
        menu:
          - text: "A: Getting Started"
            href: a_intro_appendix/00_index.qmd
          - text: "C: Quarto Crash Course"
            href: c_quarto_appendix/00_index.qmd
    right:
      - icon: github
        href: https://github.com/your-organization/your-repo-template
```

**AUTOMATION TARGET**: Replace manual "Setup Guides" with auto-generated course structure

**Critical Requirements**:
- Preserve existing navbar structure (right side, tools, metadata)
- Sort chapters numerically (00-99), appendices alphabetically (a-z)
- Auto-detect index files vs first section files
- Handle nested subsections with appropriate hierarchy

#### 3. `update_nav_components.py` - Navigation Component Generator
**Purpose**: Generate `_nav.qmd` files for each chapter with JavaScript navigation

**Section Overview Pattern** (`uumami/a_intro_appendix/_nav.qmd` lines 1-15):
```markdown
::: {.callout-note .fw-light}
#### Setup Guides
- [**A.1** AI Assistants](./01_creating_llm_accounts.qmd)
- [**A.2** How to Get Help](./02_how_to_get_help.qmd)
- [**A.3** Install Python](./03_installing_python.qmd)
// ... continues with manual section links
:::
```

**AUTOMATION TARGET**: Generate section links automatically from `scan_structure.py` discovery

**Template Pattern** (based on working navigation):
```html
<!-- 🤖 AUTO-GENERATED Navigation Component -->
<script>
const pages = {{PAGES_ARRAY}};              // Generated from section discovery

// Preserve existing navigation logic pattern
function getCurrentPageIndex() {
    const currentPath = window.location.pathname;
    const currentFile = currentPath.split('/').pop().replace('.html', '.qmd');
    return pages.findIndex(page => page.file === currentFile);
}

// [... rest of existing JavaScript logic preserved ...]
</script>

<!-- Breadcrumb dropdown (preserve existing <details> pattern) -->
{{BREADCRUMB_COMPONENT}}

<!-- Section overview (enhance with collapsible) -->
{{SECTION_OVERVIEW}}

<!-- Navigation controls -->
{{PREV_NEXT_CONTROLS}}
```

**Variable Substitution**:
- `{{PAGES_ARRAY}}`: JSON array of `{file: 'XX.qmd', title: 'YY'}` objects
- `{{BREADCRUMB_COMPONENT}}`: Chapter-specific breadcrumb dropdown
- `{{SECTION_OVERVIEW}}`: Collapsible section list with current highlighting
- `{{PREV_NEXT_CONTROLS}}`: Previous/next buttons (preserve existing logic)

#### 4. `create_chapter.py` - Interactive Content Creation
**Purpose**: Wizard for creating new chapters/sections with proper structure

**Workflow**:
1. **Prompt for Details**: Chapter number, name, type (chapter vs appendix)
2. **Validate Naming**: Ensure follows convention and doesn't conflict
3. **Create Structure**: Directory, index file, navigation component
4. **Update Global Navigation**: Regenerate `_quarto.yml` and affected `_nav.qmd` files

**Template Application**:
- Use `templates/chapter_index.qmd` with variable substitution
- Create `_nav.qmd` with empty sections list
- Update relative paths based on directory depth

#### 5. `validate_structure.py` - Structure Enforcement
**Purpose**: Ensure naming conventions and required components exist

**Validation Rules**:
- All directories follow naming patterns
- Required files exist (`XX_index.qmd`, `_nav.qmd`)
- No conflicting numbering or naming
- Relative paths are correct for file locations
- Extensions and dependencies are intact

#### 6. `generate_site.py` - Master Orchestrator
**Purpose**: One-command full site generation and validation

**Execution Flow**:
```python
def main():
    uumami_dir = find_uumami_directory()
    
    # Phase 1: Discover structure
    structure = scan_content_structure(uumami_dir)
    
    # Phase 2: Validate conventions
    validate_structure(structure)
    
    # Phase 3: Generate navigation
    generate_main_navigation(structure, uumami_dir)
    
    # Phase 4: Update components
    update_navigation_components(structure, uumami_dir)
    
    print("✅ Site generation complete!")
```

### Template System Architecture

#### Generic Content Templates

**Chapter Index Template** (`templates/chapter_index.qmd`):
```yaml
---
title: "{{CHAPTER_NUMBER}}. {{CHAPTER_TITLE}}"
format:
  html:
    css: {{RELATIVE_CSS_PATHS}}
---

{{CHAPTER_OVERVIEW_CALLOUT}}

## Sections

{{SECTION_LINKS_LIST}}

---

{{< include _nav.qmd >}}
```

**Section Template** (`templates/section_single.qmd`):
```yaml
---
title: "{{SECTION_NUMBER}} {{SECTION_TITLE}}" 
format:
  html:
    css: {{RELATIVE_CSS_PATHS}}
---

## Overview

[Content goes here - created by humans]

---

{{< include _nav.qmd >}}
```

**Navigation Template** (`templates/navigation_component.qmd`):
```html
<!-- Auto-generated for {{CHAPTER_NAME}} -->
<script>
const pages = {{PAGES_ARRAY}};
// [JavaScript navigation logic preserved from working example]
</script>

{{BREADCRUMB_DROPDOWN}}
{{SECTION_OVERVIEW}}
{{NAVIGATION_CONTROLS}}
```

#### Variable System Implementation
```python
TEMPLATE_VARIABLES = {
    'CHAPTER_NUMBER': lambda ctx: ctx['prefix'],
    'CHAPTER_TITLE': lambda ctx: ctx['title'], 
    'RELATIVE_CSS_PATHS': lambda ctx: calculate_css_paths(ctx['depth']),
    'PAGES_ARRAY': lambda ctx: json.dumps(ctx['sections']),
    'BREADCRUMB_DROPDOWN': lambda ctx: generate_breadcrumb(ctx),
    'SECTION_OVERVIEW': lambda ctx: generate_overview(ctx['sections']),
    'CHAPTER_OVERVIEW_CALLOUT': lambda ctx: generate_chapter_overview(ctx['sections'])
}

def calculate_css_paths(depth):
    """Generate CSS paths based on file depth"""
    relative_prefix = '../' * depth
    return [
        f"- {relative_prefix}quarto_code/styles/main.css",
        f"- {relative_prefix}quarto_code/styles/themes/evangelion.css"
    ]

def generate_breadcrumb(ctx):
    """Generate breadcrumb dropdown HTML"""
    chapter_name = f"{ctx['prefix']}. {ctx['title']}"
    items = []
    for section in ctx['sections']:
        items.append(f'<li><a href="./{section["file"]}">{section["display_title"]}</a></li>')
    
    return f'''
<details class="breadcrumb-dropdown">
    <summary>
        <span class="breadcrumb-prefix">{chapter_name}:</span>
        <span class="breadcrumb-current">Current Page</span>
        <span class="breadcrumb-caret">▼</span>
    </summary>
    <ul class="breadcrumb-list">
        {''.join(items)}
    </ul>
</details>'''

def generate_overview(sections):
    """Generate section overview callout"""
    links = []
    for i, section in enumerate(sections):
        links.append(f'- [**{ctx["prefix"]}.{i}** {section["title"]}](./{section["file"]})')
    
    return f'''
::: {{.callout-note .fw-light}}
#### {ctx["title"]} Sections
{chr(10).join(links)}
:::'''

def generate_chapter_overview(sections):
    """Generate chapter overview callout for index pages"""
    if not sections:
        return '::: {.callout-note}\nThis chapter is empty. Add sections to see them listed here.\n:::'
    
    section_count = len(sections)
    return f'''
::: {{.callout-tip}}
## Chapter Overview
This chapter contains {section_count} section{'s' if section_count != 1 else ''}. 
Use the navigation below to explore the content.
:::'''
```

### Naming Convention Enforcement

#### Strict Validation Patterns
```python
REQUIRED_PATTERNS = {
    'chapter_directory': r'^\d{2}_[a-zA-Z0-9_]+$',      # 00_intro, 01_python
    'appendix_directory': r'^[a-z]_[a-zA-Z0-9_]+$',     # a_install, b_troubleshoot
    'section_file': r'^\d{2}_[a-zA-Z0-9_]+\.qmd$',      # 00_overview.qmd
    'index_file': r'^\d{2}_index\.qmd$',                 # 00_index.qmd
    'navigation_file': r'^_nav\.qmd$'                    # _nav.qmd
}

SORT_ORDER = {
    'chapters': lambda x: int(x[:2]),                    # Numeric sort 00-99
    'appendices': lambda x: ord(x[0]) - ord('a'),        # Alphabetic sort a-z
    'sections': lambda x: int(x[:2])                     # Numeric sort within chapter
}
```

#### File Type Processing
```python
RENDERABLE_EXTENSIONS = {'.qmd', '.md'}
IGNORE_PATTERNS = {
    'directories': {'scripts', 'examples', 'resources', 'assets', 'data', 'legacy'},
    'extensions': {'.py', '.sh', '.json', '.csv', '.txt', '.yml'},
    'patterns': ['.*', '_*', '__*']  # Hidden and temporary files
}
```

---

## Implementation Plan

### Phase 1: Infrastructure Setup (Foundation)

**Objectives**: Move existing components safely, update paths, preserve functionality

**Tasks**:
1. **Create Directory Structure**:
   ```bash
   mkdir -p uumami/quarto_code/{scripts,components,styles,_extensions,templates}
   mkdir -p uumami/{quarto_development,legacy}
   ```

2. **Move Components** (preserve all working code):
   ```bash
   mv uumami/components/* uumami/quarto_code/components/
   mv uumami/styles/* uumami/quarto_code/styles/
   mv uumami/_extensions uumami/quarto_code/_extensions/
   ```

3. **Preserve Legacy Content**:
   ```bash
   mv uumami/a_intro_appendix uumami/legacy/
   mv uumami/c_quarto_appendix uumami/legacy/
   ```

4. **Update Relative Paths**: Create `update_paths.py` script to systematically update:
   - CSS imports in YAML headers: `../styles/` → `../quarto_code/styles/`
   - Include statements: `components/` → `quarto_code/components/`
   - Filter paths in `_quarto.yml`: `_extensions/` → `quarto_code/_extensions/`

**Success Criteria**: 
- Site builds without errors after moves
- Navigation still works on existing content
- Themes and accessibility function normally
- Extensions remain functional

**Rollback Plan**: Keep backup of original structure until validation complete

### Phase 2: Automation Script Development (Core Functionality)

**Development Order** (dependencies):
1. `scan_structure.py` → Foundation for all other scripts
2. `validate_structure.py` → Ensure data quality
3. `generate_navigation.py` → Navbar creation
4. `update_nav_components.py` → Navigation components
5. `create_chapter.py` → Content creation workflow
6. `generate_site.py` → Master orchestrator

**Testing Strategy**:
- **Unit Testing**: Each script with sample directory structures
- **Integration Testing**: Full workflow with test content
- **Edge Case Testing**: Invalid naming, missing files, deep nesting

**Key Development Requirements**:
- **Path Independence**: Scripts work from any directory location
- **Error Handling**: Graceful failures with helpful messages
- **Dry Run Mode**: Preview changes before applying
- **Backup Creation**: Automatic backups before modifications

### Phase 3: Template System Implementation (Content Scaffolding)

**Template Creation**:
1. **Extract Patterns**: Analyze existing content for common structures
2. **Create Generic Templates**: Remove course-specific content, add variables
3. **Build Variable System**: Template substitution engine
4. **Test Template Application**: Verify output matches expected structure

**Template Validation**:
- Generated content follows naming conventions
- Relative paths are correct for file locations
- Navigation components integrate properly
- YAML headers are valid and complete

### Phase 4: Navigation Enhancement (Automation Integration)

**JavaScript Preservation**: 
- Maintain existing navigation logic patterns
- Enhance with auto-generation capabilities
- Add collapsible section overviews
- Preserve breadcrumb dropdown functionality

**Integration Points**:
- `update_nav_components.py` generates pages arrays
- Template system creates consistent navigation structure
- Master script regenerates navigation when structure changes

**Enhancement Features**:
- **Collapsible Sections**: Expandable overview with current section highlighting
- **Auto-Breadcrumbs**: Generate breadcrumb paths from file location
- **Navigation Scope**: Configurable showing all chapters vs current chapter only

### Phase 5: Student Distribution Updates (System Integration)

**GitHub Actions Updates**:
- Update source paths for new `quarto_code/` structure
- Verify smart detection still works
- Test with sample student directories

**Sync Script Modifications**:
```bash
# Update sync_with_instructor.sh for multiple source directories
INSTRUCTOR_ROOT="${ROOT_DIR}/uumami"
INSTRUCTOR_INFRASTRUCTURE="${INSTRUCTOR_ROOT}/quarto_code"
INSTRUCTOR_CONTENT="${INSTRUCTOR_ROOT}/notas" 
INSTRUCTOR_DEVELOPMENT="${INSTRUCTOR_ROOT}/quarto_development"

# Sync infrastructure (styles, components, scripts)
rsync -av --ignore-existing "${INSTRUCTOR_INFRASTRUCTURE}/" "${DEST_DIR}/quarto_code/"

# Sync course content  
rsync -av --ignore-existing "${INSTRUCTOR_CONTENT}/" "${DEST_DIR}/notas/"

# Sync development documentation
rsync -av --ignore-existing "${INSTRUCTOR_DEVELOPMENT}/" "${DEST_DIR}/quarto_development/"

# Sync root files (_quarto.yml, index.qmd, requirements.txt)
rsync -av --ignore-existing --exclude="legacy" --exclude="notas" --exclude="quarto_code" --exclude="quarto_development" "${INSTRUCTOR_ROOT}/" "${DEST_DIR}/"

# Add new exclusion patterns
EXCLUDE_PATTERNS+=(
    -path '*/legacy/*'                    # Don't sync preserved content
    -path '*/quarto_code/_extensions/*'   # Extensions managed separately
    -path '*/_site/*'                     # Build artifacts
    -path '*/.quarto/*'                   # Quarto cache
)
```

**Student Workspace Testing**:
- Create test student directory
- Verify sync preserves student modifications
- Test automation scripts work in student environment
- Validate self-contained workspace functionality

**Final Integration Testing**:
- Full workflow: instructor creates content → student syncs → both can build
- Performance testing with large content structures
- Accessibility compliance across all themes
- Cross-platform compatibility (macOS, Windows, Linux)

---

## Integration Specifications

### Critical Technical Requirements

#### Path Resolution System (Complex Automation)
**Challenge**: All paths must be relative to file location

**Current Pattern** (from `uumami/a_intro_appendix/01_creating_llm_accounts.qmd`):
```yaml
css:
  - ../styles/main.css                      # One level up from section
  - ../styles/themes/evangelion.css
```

**Target Pattern** (after reorganization):
```yaml
css:
  - ../../quarto_code/styles/main.css       # Two levels up from section  
  - ../../quarto_code/styles/themes/evangelion.css
```

**Automation Requirement**: 
```python
def calculate_relative_path(from_file, to_directory):
    """Calculate relative path from content file to resource directory."""
    from_depth = len(Path(from_file).parts) - 1  # Subtract filename
    relative_prefix = '../' * from_depth
    return f"{relative_prefix}{to_directory}"

# Examples:
# notas/00_intro/00_index.qmd → ../../quarto_code/styles/
# notas/00_intro/00_section/00_subsection.qmd → ../../../../quarto_code/styles/
```

#### Extension Dependency Management
**Critical**: `coatless-quarto/custom-callout` extension must remain functional

**Current Config** (`_quarto.yml`):
```yaml
filters:
  - _extensions/coatless-quarto/custom-callout/customcallout.lua
```

**Target Config** (after move):
```yaml
filters:
  - quarto_code/_extensions/coatless-quarto/custom-callout/customcallout.lua
```

**Validation Required**: 
- Extension loads correctly from new location
- All 8 custom callout types render properly
- No conflicts with theme system

#### Theme System Integration Points
**Architecture Preservation** (see `uumami/styles/themes/evangelion.css`):

**Load Order Requirements**:
1. Google Fonts imports (must be first)
2. `main.css` (establishes base structure)
3. Theme files (override via CSS variables)

**CSS Variable Compatibility**:
- All themes must define core palette variables
- Component-specific overrides are optional
- Universal readability standards maintained

**Integration with Navigation**:
- Navigation components styled via CSS variables
- Breadcrumb dropdowns respect theme colors
- Accessibility toggle integrates with all themes

#### Accessibility Auto-Injection Maintenance
**Current Implementation** (`uumami/components/accessibility-auto.html`):

**Integration Method**: 
```yaml
# _quarto.yml configuration
format:
  html:
    include-after-body: quarto_code/components/accessibility-auto.html
```

**Critical Behaviors to Preserve**:
- Smart navbar detection across Bootstrap versions
- Persistent localStorage preferences
- Universal font override when dyslexic mode activated
- Responsive text hiding on mobile devices

**Path Update Requirements**: Update include path in `_quarto.yml` after move

### Student Distribution System Updates

#### GitHub Actions Modifications
**Current Smart Detection** (`.github/workflows/publish.yml`):
```yaml
- name: Identify Render Target
  run: |
    if [[ -d "students/${{ github.actor }}" ]]; then
      echo "TARGET_DIR=students/${{ github.actor }}" >> $GITHUB_ENV
    else
      echo "TARGET_DIR=uumami" >> $GITHUB_ENV
    fi
```

**Update Requirements**: No changes needed - detection logic remains valid

**Dependency Installation**: 
```yaml
- name: Install Python dependencies
  run: pip install -r ${{ env.TARGET_DIR }}/requirements.txt
```

**Path Validation**: Ensure student workspaces include updated `requirements.txt`

#### Sync Script Updates
**Current Safety Mechanisms** (`students/_template/sync_with_instructor.sh`):

**Path Updates Required**:
```bash
# Update source paths for new structure
INSTRUCTOR_STYLES="${ROOT_DIR}/uumami/quarto_code/styles/"
INSTRUCTOR_COMPONENTS="${ROOT_DIR}/uumami/quarto_code/components/"

# Add new exclusion patterns
EXCLUDE_PATTERNS+=(
    -path '*/quarto_code/_extensions/*'    # Extensions sync separately  
    -path '*/legacy/*'                     # Don't sync preserved content
)
```

**Safety Validation**: 
- `rsync --ignore-existing` still prevents overwriting student files
- All paths resolve correctly from student workspace
- Script remains path-independent

### Performance and Scalability

#### Build Performance  
**Quarto Rendering Exclusions** (updated `_quarto.yml`):
```yaml
project:
  render:
    - "*.qmd"
    - "*.md"
    - "!**/*.py"                # Exclude automation scripts
    - "!**/*.sh"                # Exclude shell scripts
    - "!**/scripts/**"          # Exclude script directories
    - "!**/legacy/**"           # Exclude preserved content
    - "!**/examples/**"         # Exclude supporting code
```

**CRITICAL**: Update filters section after moving extensions:
```yaml
filters:
  - quarto_code/_extensions/coatless-quarto/custom-callout/customcallout.lua
```

**CRITICAL**: Update include-after-body path:
```yaml
format:
  html:
    include-after-body: quarto_code/components/accessibility-auto.html
```

**Large Structure Handling**:
- Navigation generation scales to 100+ content files
- JavaScript pages arrays remain manageable per chapter
- CSS performance maintained across all themes

#### Memory and Storage
**Script Efficiency**: 
- Content scanning uses iterative processing
- Navigation generation batches updates
- Template application minimizes file I/O

**Student Workspace Size**:
- Complete infrastructure copy maintains self-containment
- Sync exclusions prevent unnecessary file duplication
- Build artifacts excluded from distribution

### Quality Assurance Integration

#### Automated Validation
**Structure Validation** (`validate_structure.py`):
- Naming convention enforcement
- Required file existence checking
- Relative path validation
- Extension dependency verification

**Build Testing**:
- Automated site generation after structure changes
- Theme compatibility across all content
- Accessibility compliance validation
- Cross-platform build verification

#### Error Recovery
**Backup Strategy**:
- Automatic backups before major reorganization
- Rollback procedures for failed migrations
- Progressive validation with early failure detection

**Graceful Degradation**:
- Site functions with partial automation
- Manual navigation fallbacks
- Clear error messages for troubleshooting

---

## Success Criteria and Validation

### Infrastructure Completion Indicators

**✅ Automated Structure Management**:
- Directory scanning discovers all content automatically
- Navigation generation creates complete navbar from structure
- Template system creates consistent chapter/section scaffolding
- Validation ensures naming conventions and completeness

**✅ Preserved Functionality**:
- All existing navigation patterns work after reorganization
- Theme system maintains compatibility and performance
- Accessibility features function across all content
- Student distribution preserves safety mechanisms

**✅ Development Workflow**:
- `create_chapter.py` streamlines new content creation
- `generate_site.py` provides one-command full site generation
- Path updates handle complex relative path calculations
- Error handling provides clear troubleshooting guidance

**✅ Scalability and Maintenance**:
- System handles large content structures efficiently
- Scripts work independently of execution location
- Documentation supports future development and customization
- Student workflows remain self-contained and reliable

### Validation Test Suite

**Functional Testing**:
1. **Fresh Installation**: Complete setup from empty directory
2. **Content Creation**: Create sample chapters/sections with templates
3. **Navigation Generation**: Verify complete navbar creation from structure
4. **Student Distribution**: Test sync with sample student workspace
5. **Cross-Platform**: Verify functionality on macOS, Windows, Linux

**Integration Testing**:
1. **Theme Compatibility**: All themes work with new structure
2. **Accessibility Compliance**: Dyslexic mode functions across all content  
3. **Extension Dependencies**: Custom callouts render correctly
4. **Performance**: Large structures (100+ files) generate efficiently

**Edge Case Testing**:
1. **Invalid Structure**: Graceful handling of naming violations
2. **Missing Dependencies**: Clear error messages for missing extensions
3. **Partial Migration**: System functions during incomplete reorganization
4. **Student Modifications**: Sync preserves student customizations

### Common Issues and Troubleshooting

#### Extension Not Loading
**Symptoms**: Custom callouts render as regular markdown blocks
**Solution**:
```bash
# Check extension path in _quarto.yml
grep -A5 "filters:" uumami/_quarto.yml
# Should show: quarto_code/_extensions/coatless-quarto/custom-callout/customcallout.lua

# Verify extension files exist
ls -la uumami/quarto_code/_extensions/coatless-quarto/custom-callout/
# Should contain: _extension.yml, customcallout.lua, fa.lua
```

#### Navigation JavaScript Errors
**Symptoms**: Prev/next buttons don't appear, breadcrumb doesn't update
**Solution**:
```bash
# Check for JavaScript errors in browser console
# Verify pages array syntax in _nav.qmd
grep -A10 "const pages = " uumami/notas/*/\_nav.qmd

# Common issue: Missing comma in pages array
# Correct format: { file: 'name.qmd', title: 'Title' },
```

#### CSS Paths Not Found  
**Symptoms**: Site renders without styling
**Solution**:
```bash
# Check CSS paths in YAML headers
find uumami -name "*.qmd" -exec grep -H "styles/" {} \;
# Should show relative paths to quarto_code/styles/

# Verify CSS files exist at expected locations
ls -la uumami/quarto_code/styles/
ls -la uumami/quarto_code/styles/themes/
```

#### Student Sync Overwrites Files
**Symptoms**: Student work gets replaced during sync
**Solution**:
```bash
# Verify --ignore-existing flag in sync script
grep "ignore-existing" students/_template/sync_with_instructor.sh

# Test sync in dry-run mode first
rsync -av --ignore-existing --dry-run SOURCE/ DEST/
```

This infrastructure specification provides coding agents with clear, actionable requirements for building a sophisticated educational content management system while preserving all existing functionality and maintaining educational quality standards.

---

## Reference Documents

- **`PROJECT_SPECIFICATION_COMPREHENSIVE.md`**: Complete system documentation with detailed examples and full technical analysis
- **`uumami/a_intro_appendix/_nav.qmd`**: Working navigation pattern reference (107 lines)
- **`uumami/styles/THEME_SYSTEM.md`**: Complete theme system documentation (1000+ lines)
- **`students/_template/sync_with_instructor.sh`**: Student distribution safety patterns (125 lines) 