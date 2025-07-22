# Foundational Document: GitHub Class Template Repository

> **Purpose:** This repository is a *template* for classes. It provides basic information and general/basic modules, but its core function is to act as a **template** from which each class instance (professor and students) can derive a self‑contained project. The document below captures the full philosophy, intent, structure, and operating ideas. It intentionally avoids prescribing final code solutions; instead it emphasizes concepts, automation principles, and future directions.

The repository must serve **technical and non‑technical people** *and* be easy for **coding agents** to consume. Therefore: keep everything ordered, contained, simple, minimal at the root, and as automatic as possible.

---

## 1. Directory Model & Philosophy

Assume the GitHub repository is the root of the project; paths are relative to root.

### 1.1 Core Directories

* **`/professor`** – Acts as the *source/base* project. It contains everything necessary for the website to render via GitHub Pages. Keep *all complex assets* here (themes, framework code, etc.). Later, this directory name will be changed to the professor’s GitHub username (we use `professor` now as a placeholder—this is part of the “lore” for fun).
* **`/students`** – Contains *student work*. Each student creates a subdirectory named **exactly** their GitHub username: e.g., `/students/uumami`. Students **only** work inside their own directory; no modifications outside are allowed.

### 1.2 Forking & Rendering

Students **fork** the template and work inside `/students/<username>`. CI/CD will later control pushes and pull requests back into the professor repository (not priority now). Immediate priority: **automatic GitHub Pages rendering**.

If a folder exists at `students/<username>` matching the student’s GitHub username, GitHub Pages renders that folder as the student’s site. The professor may also create a directory in `/students` under their own username for testing. We avoid confusion using a management file.

### 1.3 `dna.yml` Management File

Place a `dna.yml` file at the repository root. It stores **framework and operational metadata** used by automation scripts and CI/CD. One mandatory field:

```yaml
professor_profile: uumami
```

When `professor_profile` is set, CI/CD **ignores** `/students/uumami` during rendering and instead renders the root‑level `/uumami` directory (mirrors the professor’s profile). Each student directory remains a self‑contained complete project.

`dna.yml` is intentionally extensible. Additional keys can be added over time and interpreted by scripts/components without changing structure. Examples of future keys include:

```yaml
theme: default             # Active visual theme from framework_code/themes/
search_mode: simple        # Switch to alternate search implementations later
index_generation: true     # Enable/disable automatic index regeneration
sync_mode: additive        # Future: control strategy (additive, force)
authoring_tools: ["agent"] # Declare enabled agent/tool integrations
license: CC-BY-4.0         # Default license for content display
```

Automation reads unknown keys generically so new behavior can be layered gradually. This file becomes the **declarative DNA** of the repository—scripts derive actions from it.

### 1.4 `course.yml` (Class Offering Metadata)

In addition to `dna.yml`, each class instance maintains a **course metadata file** stored under `/professor` (and synchronized to students) named `course.yml` (name can vary, YAML/JSON acceptable). This file contains information specific to the current offering—data that changes per semester but follows a consistent schema. Example:

```yaml
course_name: "Introduction to Data Science"
course_code: "DS101"
semester: "Fall 2025"
professor:
  name: "Dr. Jane Doe"
  email: "jane.doe@example.edu"
  office_hours: "Tue 14:00-16:00, Room 123"
  office_location: "Building A, Room 123"
resources:
  repository: "github.com/university/ds101"
  shared_drive: "https://drive.example.com/ds101"
  syllabus: "syllabus.pdf" # will be in the professors (and students) root/main directory
  announcements_feed: "announcements.md" # will be in the professors (and students) root/main directory
contact_policy: "Email within 24h."
```

**Purpose and Future Uses:**

* Components (e.g., syllabus page, contact card, footer) read `course.yml` to render consistent information automatically.
* Scripts can validate presence of required fields and generate printable summaries.
* Future automation (e.g., calendar integration, announcement feeds, agent prompts) can extend the schema without structural changes.
* Student forks inherit a baseline file they customize for their personal copy if needed (e.g., local notes fields).

Both `dna.yml` (framework DNA) and `course.yml` (offering metadata) establish a clear separation between **operational logic** and **class‑specific content**, allowing future unknown values to be safely added under the same principles.

### 1.5 Synchronization Philosophy

Professors actively update `/professor`. Students **fetch** those updates selectively into `/students/<username>`. This differs from Git pull/merge: it is *framework‑level synchronization*.

A master script (one of several automation scripts) will:

1. Read `professor_profile` and other values from `dna.yml`.
2. Bring relevant code/data from `/professor` into each student directory.
3. **Never overwrite** existing student‑modified files. Only add new files.

Forced updates: the professor may force replacement of a file. During a forced replace the script preserves any regions wrapped with the syntax:

<!-- KEEP:START -->
...content...
<!-- KEEP:END -->


All preserved regions are appended to the end of the new file under a clear heading (ensuring nothing is lost). Complex merging/diff is deferred to the future.

### 1.6 Simplicity for Non‑Technical Users

Because many students are non‑technical, the root repository exposes only minimal files/directories and simple abstractions. Internally, directories can hold complex logic; the root remains clean and discoverable.

---

## 2. Stack Overview

The stack includes **Hugo** and **JupyterLite**. Content formats: Markdown, Jupyter notebooks (`.ipynb`), JupyterLite embedded content, and Python (`.py`). The goal is a framework for professors and students: Python, Hugo, JavaScript, LaTeX, JupyterLite, etc. The template itself **is** the framework. LaTeX support and browser‑based execution (JupyterLite) are required. Future packaging can emerge later.

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
    ...other relevant files...# Master Hugo files, global variables, editor aids, etc.
```

**Components & Themes:** Functional components live in `framework_code/components/`. Visual customization is separated into `framework_code/themes/<theme_name>/`. The active theme (declared in `dna.yml`, e.g., `theme: default`) plus core components are synchronized into student directories. Students can clone a theme folder to create a new theme with color/style changes only.

**Use Case:** A professor forks the template and starts a class. They need straightforward access to master files that adapt easily to the class context. Organization favors clarity, modularity, and ease of modification.

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
* Optional collapsible flap/panel (canvas) showing the current chapter’s full index.

### 8.3 Metadata & Index Integration

Metadata headers enable indices and navigation. Additional optional fields (see Section 9) enhance filtering and display.

---

## 9. Framework-Level Behaviors & Macros

Introduce special strings/decorators/macros inside files to control automation.

**Preservation Syntax:**

```html
<!-- KEEP -->
...student custom content...
<!-- KEEP -->
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
* **Git Separation:** Scripts never manage Git operations. Users perform `git pull`/commits manually. CI/CD runs build/generation only.

---

## 12. Index & Component Generation

Indices (`00_index.md`, `00_master_index.md`) and any dependent components are **regenerated automatically before each build** based on the enforced framework structure. Generated Markdown files may also create machine‑readable JSON for search/navigation. Scripts verify freshness (e.g., checksum) and update as required.

---

## 13. Summary

This template repository aspires to become a comprehensive framework for class content delivery. Core tenets: **automation**, **strict structure**, **non‑destructive syncing**, **simplicity for students**, **extensibility for professors**, and **agent readiness**. All structural rules, naming conventions, metadata, macros, and generation scripts ensure fully automated component creation without losing the human philosophy and playful lore that make the system engaging.

*End of foundational document.*
