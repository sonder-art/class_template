# TODO: GitHub Class Template Repository Implementation

> **Source:** Tasks derived from `core.md` foundational document  
> **Status:** Complete implementation roadmap with 60+ granular tasks  
> **Last Updated:** Created from initial requirements analysis

## 🏗️ Foundation & Setup

- [x] Create the core directory structure with /professor and /students directories
- [x] Define the dna.yml file schema with required and optional fields for framework configuration
- [x] Define the course.yml file schema for class offering metadata
- [x] Create a parser to read and validate dna.yml configuration values
- [x] Create a parser to read and validate course.yml metadata
- [x] Create the detailed internal structure for /professor directory with all subdirectories (class_notes, framework_code, etc.)
- [x] Create the framework_code/components/ directory structure for functional components
- [x] Create the framework_code/themes/ directory structure with theme organization system
- [x] Implement a default theme with basic styling and layout
- [x] Implement the file naming convention rules (numbers for primary content, letters for code files)
- [ ] Create validation logic for chapter directory structure and naming conventions
- [ ] Configure Hugo as the static site generator with basic settings
- [ ] Integrate JupyterLite for browser-based notebook execution
- [ ] Setup LaTeX rendering support in Hugo for mathematical content

## 📋 Content & Metadata System

- [ ] Define the required metadata fields (title, type, date, author, summary) for content files
- [ ] Create parser to extract and validate YAML front matter from content files
- [ ] Define optional metadata fields (difficulty, prerequisites, estimated_time, tags, agent)

## 🔄 Synchronization System

- [ ] Implement the main synchronization script that reads dna.yml and syncs professor to student directories
- [ ] Create logic to sync files without overwriting existing student-modified files
- [ ] Add support for <!-- KEEP:START --> and <!-- KEEP:END --> syntax to preserve content during forced updates
- [ ] Create functionality for professor to force replacement of specific files with content preservation
- [ ] Implement logic to handle professor_profile from dna.yml and ignore matching student directory

## 🧭 Navigation & Layout

- [ ] Create desktop layout with left sidebar tree, main content center, optional right mini-TOC
- [ ] Create mobile layout with collapsible hamburger menu and responsive navigation
- [ ] Create automatic sidebar tree generation based on directory structure
- [ ] Create previous/next page arrows based on file order
- [ ] Create per-page mini table of contents from page headings
- [ ] Implement automatic generation of 00_index.md for each chapter
- [ ] Implement automatic generation of 00_master_index.md for the entire site
- [ ] Create logic to detect homework files (hw_ prefix) and surface them in navigation
- [ ] Add support for appendix chapters with capital letter prefixes (A_, B_, etc.)

## 🎨 Content Processing & Display

- [ ] Implement attractive display of Python code (.py and .ipynb) in the rendered site
- [ ] Create Jupyter notebook rendering capability within Hugo pages
- [ ] Implement system to detect and handle student solution files (solved_hw_ prefix)

## 🔍 Search & Filtering

- [ ] Implement simple client-side search with index generation from front matter and content
- [ ] Build search index from metadata and first content characters of files
- [ ] Add tag-based search and filtering functionality

## 🎭 Theme & Component Systems

- [ ] Implement ability to switch between themes based on dna.yml configuration
- [ ] Create functionality for students to copy and customize themes
- [ ] Implement the component system for reusable functional elements

## ✅ Validation & Quality

- [ ] Create script to validate required metadata fields and enumerations
- [ ] Implement validation of directory structure and naming conventions
- [ ] Add checksum verification for generated files to detect when updates are needed
- [ ] Implement rich console output for scripts using the rich library
- [ ] Create clear error reporting with actionable messages for students

## 🚀 Deployment & Automation

- [ ] Setup automatic GitHub Pages rendering for student directories
- [ ] Create CI/CD workflow for automatic builds without Git management
- [ ] Create automatic generation of directory listings for navigation
- [ ] Create automatic generation of file listings within directories
- [ ] Create pre-Hugo processing pipeline for content generation
- [ ] Generate machine-readable JSON files for search and navigation data

## 🔧 Advanced Features

- [ ] Create optional collapsible flap/panel showing current chapter's full index
- [ ] Ensure all documentation and structure is easily parseable by coding agents
- [ ] Create system to handle unknown configuration keys gracefully for future extensions
- [ ] Implement system to migrate from /professor to actual professor username directory
- [ ] Create system to detect when content files have changed and need regeneration
- [ ] Design template structure for new student directories with minimal required files
- [ ] Create components that read course.yml to render syllabus, contact info, and footer
- [ ] Implement announcement feed reading from course.yml configuration

## 🏷️ Enhanced Features

- [ ] Implement difficulty badges for content based on metadata
- [ ] Implement prerequisite dependency visualization and validation
- [ ] Add estimated time display next to homework and sections

## 🧪 Testing & Documentation

- [ ] Develop testing suite to validate all framework functionality
- [ ] Write comprehensive documentation for the framework in framework_documentation/
- [ ] Create practical tutorials for framework usage in framework_tutorials/

## 🎯 Final Setup

- [ ] Ensure root directory remains minimal and clean for non-technical users
- [ ] Configure repository as GitHub template with proper settings

---

## Task Categories Summary

| Category | Count | Description |
|----------|-------|-------------|
| 🏗️ Foundation & Setup | 14 | Core infrastructure and basic integrations |
| 📋 Content & Metadata | 3 | Content structure and metadata systems |
| 🔄 Synchronization | 5 | Professor-student sync mechanisms |
| 🧭 Navigation & Layout | 9 | UI/UX and navigation systems |
| 🎨 Content Processing | 3 | Content rendering and display |
| 🔍 Search & Filtering | 3 | Search and discovery features |
| 🎭 Theme & Components | 3 | Customization and modularity |
| ✅ Validation & Quality | 5 | Error handling and validation |
| 🚀 Deployment & Automation | 6 | Build and deployment systems |
| 🔧 Advanced Features | 8 | Future-proofing and extensions |
| 🏷️ Enhanced Features | 3 | Quality-of-life improvements |
| 🧪 Testing & Documentation | 3 | Quality assurance and docs |
| 🎯 Final Setup | 2 | Repository preparation |

**Total Tasks:** 67

---

## Notes

- Tasks are ordered logically with dependencies considered
- Each task is granular and actionable
- Solutions are not prescribed - focus is on requirements
- Tasks can be checked off as completed
- New tasks can be added as requirements evolve 