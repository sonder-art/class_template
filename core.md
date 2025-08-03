# Foundational Document: GitHub Class Template Repository

> **Purpose:** This repository is a *template* for classes. It provides basic information and general/basic modules, but its core function is to act as a **template** from which each class instance (professor and students) can derive a self‑contained project. The document below captures the full philosophy, intent, structure, and operating ideas. It intentionally avoids prescribing final code solutions; instead it emphasizes concepts, automation principles, and future directions.

The repository must serve **technical and non‑technical people** *and* be easy for **coding agents** to consume. Therefore: keep everything ordered, contained, simple, minimal at the root, and as automatic as possible.

---

## 1. Directory Model & Philosophy

Assume the GitHub repository is the root of the project; paths are relative to root.

### 1.1 Core Directories

* **`/professor`** – Acts as the *source/base* project. It contains everything necessary for the website to render via GitHub Pages. Keep *all complex assets* here (themes, framework code, etc.). Later, this directory name will be changed to the professor's GitHub username (we use `professor` now as a placeholder—this is part of the "lore" for fun).
* **`/students`** – Contains *student work*. Each student creates a subdirectory named **exactly** their GitHub username: e.g., `/students/uumami`. Students **only** work inside their own directory; no modifications outside are allowed.

### 1.2 Forking & Rendering

Students **fork** the template and work inside `/students/<username>`. CI/CD will later control pushes and pull requests back into the professor repository (not priority now). Immediate priority: **automatic GitHub Pages rendering**.

If a folder exists at `students/<username>` matching the student's GitHub username, GitHub Pages renders that folder as the student's site. The professor may also create a directory in `/students` under their own username for testing. We avoid confusion using a management file.

### 1.3 Configuration File Hierarchy & Separation

**CRITICAL PRINCIPLE**: Configuration files have distinct purposes and different scopes.

#### **1.3.1 `dna.yml` - Framework Meta-Process Control (Repository Root)**
Place a `dna.yml` file at the repository root. It stores **framework and operational metadata** used by automation scripts and CI/CD. **NEVER contains rendering preferences** - only meta-process controls.

**Required field:**
```yaml
professor_profile: uumami
```

**Purpose**: Meta-process control only
- Framework behavior switches  
- CI/CD automation settings
- Sync operation modes
- Repository-wide operational flags

**Examples of appropriate dna.yml content:**
```yaml
professor_profile: uumami      # Required for directory handling
sync_mode: additive           # How sync operations behave
authoring_tools: ["agent"]    # Framework integrations
license: CC-BY-4.0           # Default license
hugo_auto_config: true       # Enable config generation
accessibility_enabled: true  # Framework accessibility features
index_generation: true       # Auto-generate indices
strict_validation: false     # Validation behavior
auto_deploy: true            # CI/CD deployment
```

#### **1.3.2 `config.yml` - Rendering Preferences (Per Directory)**
Each directory (`professor/`, `students/<username>/`) contains its own `config.yml` with **all rendering and visual preferences**. This file makes each directory **self-contained** for rendering purposes.

**Purpose**: Complete rendering configuration
- Theme selection and paths
- Visual appearance settings
- Hugo content sources
- Accessibility preferences
- Build options

**Critical Rule**: **NO dependency on root files for rendering** - each directory must be able to generate its site independently using only its local `config.yml`, `course.yml`, and `framework_code/`.

#### **1.3.3 `course.yml` - Class Offering Metadata (Per Directory)**
Contains class-specific information that changes per semester but follows a consistent schema.

**Purpose**: Class metadata for content generation
- Course information (name, code, semester)
- Professor contact details
- Resource links
- Branding colors

### 1.4 Self-Contained Principle

**Each directory is a complete, independent Hugo project:**
- `professor/` can render its site using only local files
- `students/alice/` can render her site using only local files  
- **No shared dependencies** for rendering operations
- Framework tools (`framework_code/`) are synced to maintain this independence

### 1.5 Synchronization Philosophy

Professors actively update `/professor`. Students **fetch** those updates selectively into `/students/<username>`. This differs from Git pull/merge: it is *framework‑level synchronization*.

**Initial Setup**: Students use `students/start.sh` for one-time directory creation
**Ongoing Updates**: Students use sync script for framework and content updates

A master script (sync_student.py) will:

1. Read operational settings from `dna.yml` (if needed for sync behavior)
2. Bring relevant code/data from `/professor` into each student directory
3. **Never overwrite** existing student‑modified files. Only add new files
4. **Smart exclusions**: Never sync auto-generated content, build artifacts, or development files

Forced updates: the professor may force replacement of a file. During a forced replace the script preserves any regions wrapped with the syntax:

```html
<!-- KEEP:START -->
...content...
<!-- KEEP:END -->
```

All preserved regions are appended to the end of the new file under a clear heading (ensuring nothing is lost). Complex merging/diff is deferred to the future.

### 1.6 Simplicity for Non‑Technical Users

Because many students are non‑technical, the root repository exposes only minimal files/directories and simple abstractions. Internally, directories can hold complex logic; the root remains clean and discoverable.

---

## 2. Stack Overview

The stack includes **Hugo** and **JupyterLite**. Content formats: Markdown, Jupyter notebooks (`.ipynb`), JupyterLite embedded content, and Python (`.py`). The goal is a framework for professors and students: Python, Hugo, JavaScript, LaTeX, JupyterLite, etc. The template itself **is** the framework. LaTeX support and browser‑based execution (JupyterLite) are required. Future packaging can emerge later.

### 2.1 Automated Hugo Configuration
Hugo's configuration file (`hugo.toml`) is **generated** from a template. The generator merges values from **course.yml** and **config.yml** only - **NO dependency on root dna.yml** for rendering. Each directory generates its own `hugo.toml` using local configuration files only.

---

## 3. Framework Concept

The framework automates: website rendering, sync of professor ↔ student directories, notebook synchronization, Python code sync, Markdown sync, LaTeX sync, JupyterLite assets sync, and other file transfers.

It also **enforces structure** enabling automation: consistent indexing, nesting, designated content locations, file headers, callouts, special strings/decorators/macros, etc.

Automation examples:

* Automatic component creation based on directory/file naming conventions.
* Pre‑Hugo processing that generates components/content: tables of contents, file lists, directory lists, links, images, videos, audio, etc.

This begins as a GitHub template repository but evolves into a full framework.

---

## 4. Content Philosophy

Content combines Markdown, Jupyter notebooks, JupyterLite, and Python. Complex `.py` code may or may not appear in the final website. It might be referenced or fully exposed. Notebooks are not always ideal; plain Python files aid organization. Both coexist.

---

## 5. Internal Structure (Professor Focus)

```
professor/
    class_notes/              # Main instructional content: Markdown, notebooks, Python, etc.
    framework_code/           # Framework internals: Python, Hugo, JS, etc. Students consume but don't edit.
    framework_documentation/  # Technical documentation for framework_code (how to contribute, use, etc.).
    framework_tutorials/      # Practical tutorials for framework_code; student‑facing usage examples.
    framework_code/components/        # Functional components (logic, data generation).
    framework_code/themes/<theme>/    # Theme folders: visual overrides (colors, fonts, minor styling).
    framework_code/hugo_generated/    # Auto-generated Hugo output and auxiliary build artifacts (never edited manually)
    framework_code/hugo_config/       # Hugo configuration template files (e.g., hugo.toml.j2)
    framework_code/scripts/           # Automation scripts (config generation, sync, etc.)
    framework_code/assets/            # Shared global assets (fonts, images)
    framework_code/css/               # Baseline shared CSS (main.css)
    course.yml                        # Class offering metadata
    config.yml                        # Rendering preferences (self-contained)
    home.md                           # Homepage content
    hugo.toml                         # Generated Hugo configuration (auto-generated)
    ...other relevant files...
```

**Components & Themes:** Functional components live in `framework_code/components/`. Visual customization is separated into `framework_code/themes/<theme_name>/`. The active theme (declared in `config.yml`, not dna.yml) plus core components are synchronized into student directories. Students can clone a theme folder to create a new theme with color/style changes only.

**Use Case:** A professor forks the template and starts a class. They need straightforward access to master files that adapt easily to the class context. Organization favors clarity, modularity, and ease of modification.

### 1.7 Directory Decision Matrix
To keep the root minimal and automation predictable, use this quick reference when deciding *where* a new artefact belongs:

| Need | Location | Rationale |
|------|----------|-----------|
| Repo-wide automation switch | `dna.yml` | Read early by CI & scripts |
| Per-class visual/UX preference | `professor/config.yml` | Editable by instructor without touching root |
| Shared asset (fonts, images) | `framework_code/assets/` | Accessible to all themes without duplication |
| Theme-specific styling | `framework_code/themes/<theme>/css/` | Encapsulates look & feel |
| Reusable component logic | `framework_code/components/` | Centralized, theme-agnostic |
| Build/utility script | `framework_code/scripts/` | Clear tooling home |
| Auto-generated output | `framework_code/hugo_generated/` | Never committed, always recreated |
| Course content | `professor/class_notes/`, `framework_tutorials/` | Structured, student-facing |

These rules ensure future additions stay coherent with the framework philosophy outlined above.

### 1.8 Naming & Ordering Conventions {#naming-ordering}
Predictable file names let scripts infer hierarchy while keeping things clear for humans.

| Item | Convention | Rationale |
|------|------------|-----------|
| Chapter directory | `01_intro/` (zero-padded) | Lexical & numeric sort align |
| Section markdown  | `01_first_topic.md` | Matches nav order |
| Companion code    | `01_a_first_topic.py` | Letter suffix avoids collision with next section |
| Homework          | `hw_01.md` | Easy auto-detection |
| Appendix          | `A_advanced/` | Capital pushes after numbers |

### 1.9 Metadata Schema {#metadata-schema}
A minimal required set with forward-compatibility.

| Field | Required? | Purpose |
|-------|-----------|---------|
| `title` | ✔︎ | Human nav & `<title>` tag |
| `type`  | ✔︎ | Styling / icon mapping |
| `date`  | ✔︎ | Chronological sort & RSS |
| `author`| ✔︎ | Attribution & syllabus gen |
| `summary` | ✔︎ | Search snippet & cards |
| `difficulty` | optional | Badge & filtering |
| …future keys… | optional | Ignored if unknown |

Example front-matter in practice:
```yaml
---
title: "First Topic"
type: note
date: 2025-08-01
author: "Dr. Jane Doe"
summary: "Introduce core concepts"
---
```

### 1.10 Automation & Build Triggers {#automation-triggers}
Never edit generated artefacts. Regenerate on every build.

| Artefact | Script | Trigger | Stored In | Status |
|----------|--------|---------|-----------|--------|
| `hugo.toml` | `generate_hugo_config.py` | course.yml / config.yml change | directory root | working |
| `00_index.md` | `generate_navigation.py` | New/renamed chapter file | chapter folder | pending |
| `00_master_index.md` | same | Structure change | `class_notes/` root | pending |
| Search index JSON | `generate_search.py` | Front-matter change | `hugo_generated/` | future |

### 1.11 Configuration Hierarchy {#configuration-hierarchy}
Who edits what, and how often. **UPDATED: Clear separation of concerns**

| File | Audience | Lifespan | Keys | Purpose |
|------|----------|----------|------|---------|
| `dna.yml` | Framework maintainers | Rare | sync_mode, CI toggles, operational flags | Meta-process only |
| `professor/config.yml` | Instructor | Per semester | theme, content_sources, visual preferences | Complete rendering config |
| `course.yml` | Components | Each offering | course_name, prof contact, branding | Class metadata |

**CRITICAL**: `dna.yml` NEVER contains rendering preferences. Each directory is self-contained for rendering.

### 1.12 Theme Layering Model {#theme-layering}
No duplication of structural CSS.

| Layer | Location | Scope |
|-------|----------|-------|
| Base utilities | `framework_code/css/main.css` | All themes |
| Theme tokens | `framework_code/themes/<theme>/css/theme.css` | Colours, fonts |
| Per-site tweaks | inline from config.yml | Single course |

**NO duplicate theme directories** - themes live only in `framework_code/themes/` and are mounted directly by Hugo.

### 1.13 Accessibility Commitments {#accessibility}
Built-in, user-controlled.

| Feature | Default | Toggle Component | Config Flag |
|---------|---------|-----------------|-------------|
| OpenDyslexic font | off | `font-toggle.html` | `accessibility.default_font` |
| Reduced motion | auto | n/a | n/a |
| High-contrast (future) | off | `contrast-toggle.html` | `accessibility.theme` |

### 1.14 Sync & Conflict Strategy {#sync-strategy}
Student work is never lost. Smart exclusions prevent syncing inappropriate content.

| Scenario | Script Behaviour | Student Impact |
|----------|-----------------|----------------|
| New file from professor | Copy | Gains file |
| Modified by prof, untouched by student | Replace | Gets update |
| Modified by both | Skip (default) | Student resolves manually |
| Forced replace + KEEP | Replace & append preserved blocks | No data loss |
| Auto-generated content | Skip (excluded) | Never synced |
| Build artifacts | Skip (excluded) | Never synced |

**Smart Exclusions**: Framework automatically excludes auto-generated content, build artifacts, and development files from sync operations.

### 1.15 Student Initialization {#student-initialization}
**NEW**: Proper initialization process following framework principles.

| Operation | Method | Frequency |
|-----------|--------|-----------|
| Initial setup | `students/start.sh` | Once |
| Framework updates | `sync_student.py` | Regular |
| Content updates | `sync_student.py` | Regular |
| Manual operations | **Never** | Framework handles all |

### 1.16 Future / Experimental Features {#future-experimental}
Mark postponed ideas with a clear *WHY* comment in TODO so intent isn't lost.

---

## 6. Content Structure & Naming Conventions

Each *major category* (`framework_tutorials`, `framework_documentation`, `class_notes`, `homework`, etc.) has its own nested structure. Example for `class_notes/` (one level, expandable to more):

```
class_notes/  # category
    01_introduction/   # chapter
        00_index.md                     # auto-generated chapter index
        01_introduction.md              # section
        01_a_code_for_introduction.py
        01_b_code_for_introduction.py
        01_c_code_for_introduction.ipynb
        02_testing.md
        03_new_concept.md
        03_a_code_for_new_concept.py
        hw_01.md
        hw_01_a_code_for_hw_01.py
    02_testing/
    ...
    A_advanced_topics/
        1_advanced_topics.md
        1_a_code_for_1_advanced_topics.py
    00_master_index.md  # auto-generated master index
```

**Key Rules:**

* **Numbering & Letters:** Numbers for primary content files; letters (`a`, `b`, `c`, …) for associated code files. Strict order enables parsing and automation.
* **Capital Letters:** Appendices (e.g., `A_advanced_topics/`) behave like chapters but appear at the end.
* **Homework Files:** Prefixed with `hw` (Markdown and code). Homework inside `class_notes` is parsed automatically and surfaced in a Homework navigation category. The navigation bar shows homework automatically. Student solutions may follow a naming pattern (e.g., `solved_hw_01.md`) and are read similarly without duplication.
* **Indices:** Each chapter has a `00_index.md` (auto‑generated). A global `00_master_index.md` aggregates all chapters/sections. Both appear at their respective levels.
* **Metadata Headers:** Each Markdown file (and potentially other types) may include YAML or similar front matter specifying `title`, `type`, `date`, `author`, and a short `summary` sentence used in indices. This metadata powers component generation and automation.

These structural constraints (hierarchy + naming) make generation, presentation, reading, and specialized behaviors deterministic. Specialized strings/decorators/macros may further differentiate usage.

---

## 7. Templates / Styles

Templates and styles are **configurable and organized** so professors (and optionally students) can extend them. Students can create their own templates by copying a theme folder. Only minor visual aspects (colors, fonts) are changed; functional logic remains in components.

Design criteria:

* Maintain a clean, simple structure.
* Make adapting to a particular class easy.
* Provide widgets/components that are easy to adapt across templates/styles.
* Simplify templates to be minimal, comprehensible, and straightforward to clone or extend.

---

## 8. Components & Navigation

### 8.1 Layout Decisions

Primary platform: **desktop** (sidebar tree). Mobile: secondary support.

* **Desktop:** Left sidebar tree for chapters/sections (auto‑generated), main content center, optional right mini‑TOC (page headings). Previous/next arrows at top/bottom.
* **Mobile:** Collapsible hamburger revealing the tree; previous/next arrows below content.

### 8.2 Navigation Elements

Automatically generated elements include:

* Previous/next page arrows based on file order.
* Sidebar tree derived from structure.
* Per‑page mini‑TOC (current page headings).
* Chapter index display using `00_index.md` and master index via `00_master_index.md`.
* Optional collapsible flap/panel (canvas) showing the current chapter's full index.

### 8.3 Metadata & Index Integration

Metadata headers enable indices and navigation. Additional optional fields (see Section 9) enhance filtering and display.

---

## 9. Framework-Level Behaviors & Macros

Introduce special strings/decorators/macros inside files to control automation.

**Preservation Syntax:**

```html
<!-- KEEP:START -->
...student custom content...
<!-- KEEP:END -->
```

During a forced update, preserved regions are appended unchanged to the end of the replaced file. Default synchronization never overwrites existing files.

Additional framework features:

* Automatic search with a simple client‑side index (front matter + first content characters). Tags come from front matter or optional extraction.
* Attractive display of Python code (`.py` & `.ipynb`) in the rendered site.
* Use of libraries like `rich` for console output in scripts to improve usability.

---

## 10. Metadata Fields

**Required Now:** `title`, `type` (e.g., note, homework), `date`, `author`, `summary`.

**Optional Future Fields:**

* `difficulty` (easy | medium | hard) – badge display/filtering.
* `prerequisites` (array of slugs) – dependency graph for guidance.
* `estimated_time` (minutes) – display next to homework/sections.
* `tags` (list) – search filtering.
* `agent` (bool) – mark agent‑specific docs (also integrated within normal docs).

A validation script checks required fields and enumerations. Missing/invalid metadata triggers warnings or build failure in CI.

---

## 11. General Operational Principles

* **Single Master Script:** One primary script automates generation (calling specialized sub‑scripts). Scripts remain separated, clean, and user friendly (Python/shell). Output is clear (errors, overwrites, successes).
* **Student Usability:** Provide simple actionable messages. Warn early about overwrites or errors.
* **Agent Compatibility:** Documentation and tutorials explicitly include agent guidance; agent‑specific docs are visible (no hiding). Agents can parse structure easily.
* **Agent Content Creation Protocol:** Agents must prompt the human before creating new Markdown or content files. For quick debugging, they may create up to two scratch files inside `framework_code/test/`; no instructional directories should be modified without approval.
* **Git Separation:** Scripts never manage Git operations. Users perform `git pull`/commits manually. CI/CD runs build/generation only.
* **Self-Contained Operation:** Each directory can render independently using only local configuration files.
* **Framework-Only Operations:** All file operations go through framework scripts - no manual copying/symlinking.

---

## 12. Index & Component Generation

Indices (`00_index.md`, `00_master_index.md`) and any dependent components are **regenerated automatically before each build** based on the enforced framework structure. Generated Markdown files may also create machine‑readable JSON for search/navigation. Scripts verify freshness (e.g., checksum) and update as required.

---

## 13. Summary

This template repository aspires to become a comprehensive framework for class content delivery. Core tenets: **automation**, **strict structure**, **non‑destructive syncing**, **simplicity for students**, **extensibility for professors**, **agent readiness**, and **self-contained operation**. All structural rules, naming conventions, metadata, macros, and generation scripts ensure fully automated component creation without losing the human philosophy and playful lore that make the system engaging.

*End of foundational document.*
