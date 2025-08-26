# Grading System Analysis & Implementation Plan

## System Overview

This document provides a comprehensive analysis of the GitHub Class Template Framework's grading system, what's implemented, what's missing, and the implementation plan to complete it.

## Architecture Description

### The Framework Design

The grading system is a **multi-stage pipeline** that handles:
1. **Item Definition** - Graded assignments defined in markdown files
2. **Structure Sync** - Syncing item definitions to database
3. **Submission Interface** - UI for students/professors to upload work  
4. **Submission Storage** - Storing uploaded work in database
5. **Grading Dashboard** - Interface for viewing and grading submissions

### Key Components

#### 1. Content Layer (Markdown Files)
- **Location**: `professor/class_notes/**/*.md`
- **Purpose**: Define graded items using Hugo shortcodes
- **Example**:
  ```markdown
  {{< item-inline constituent_slug="auth-setup" item_id="github_oauth_setup" points="20" due_date="2025-08-20T17:00:00-05:00" title="GitHub OAuth Configuration" delivery_type="upload" >}}
  ```

#### 2. Parsing Layer (Python Scripts)
- **Script**: `framework/scripts/parse_items.py`
- **Purpose**: Extract item definitions from markdown files
- **Output**: `hugo_generated/data/items.json`
- **Process**: 
  - Scans markdown files for `{{< item-inline >}}` shortcodes
  - Parses parameters into structured data
  - Generates JSON with all item definitions

#### 3. Hugo Rendering Layer
- **Template**: `framework/layouts/shortcodes/item-inline.html`
- **Purpose**: Render item metadata in HTML
- **Output**: Creates `.graded-item` divs with data attributes
- **Result**: Visual item cards on homework pages

#### 4. Sync Layer (JavaScript - Structure)
- **File**: `framework/assets/js/grading-sync.js`
- **Purpose**: Sync item DEFINITIONS to Supabase database
- **Target**: `items` table (structure/schema)
- **Process**:
  - Loads items from local JSON files
  - Compares with existing database items
  - Upserts new/changed item definitions
  - Professor-only operation

#### 5. Submission Layer (JavaScript - Content)
- **File**: `framework/assets/js/item-submission.js` 
- **Purpose**: Create submission forms and handle uploads
- **Target**: `student_submissions` table (actual work)
- **Process**:
  - Detects `.graded-item` elements on page
  - Creates submission forms based on delivery type
  - Handles upload/submit operations
  - Stores submissions in database

#### 6. Display Layer (JavaScript - Dashboard)
- **File**: `framework/assets/js/grading.js`
- **Purpose**: Grading dashboard for professors
- **Function**: 
  - Loads items from database
  - Loads submissions from database
  - Displays combined view for grading
  - Handles grade entry and updates

### Database Schema

#### Items Table (Structure)
- `id` (PRIMARY KEY) - Item identifier (e.g., "github_oauth_setup")
- `constituent_slug` - Links to constituent
- `title` - Human readable name
- `points` - Point value
- `delivery_type` - How to submit (upload, url, text, etc.)
- `due_date` - When it's due
- `is_active` - General active flag
- `is_current` - Current version flag (sync sets this)
- `class_id` - Which class this belongs to

#### Student Submissions Table (Content)
- `id` (PRIMARY KEY) - Submission identifier
- `student_id` - Who submitted (user_id)
- `item_id` - What item (references items.id)
- `class_id` - Which class
- `attempt_number` - Submission attempt
- `submission_data` - JSON with actual content
- `submitted_at` - When submitted
- `raw_score` - Points earned
- `feedback` - Instructor comments

## Complete Workflow (How It Should Work)

### Step 1: Item Definition
1. Professor writes markdown file with `{{< item-inline >}}` shortcodes
2. Each shortcode defines a graded item with metadata
3. Hugo builds the page, creating visual item cards

### Step 2: Structure Sync  
1. `parse_items.py` extracts items from markdown → `items.json`
2. Professor visits `/grading-sync/` page
3. `grading-sync.js` loads items from JSON
4. Compares with database, shows changes
5. Professor clicks "Sync" → items stored in database

### Step 3: Submission Interface Creation
1. Student/professor visits homework page
2. `item-submission.js` detects `.graded-item` elements
3. Creates submission forms based on delivery type
4. Forms allow file upload, URL submission, text entry, etc.

### Step 4: Work Submission
1. Student fills out submission form
2. JavaScript validates and submits to Supabase
3. Data stored in `student_submissions` table
4. References the item by `item_id`

### Step 5: Grading Dashboard
1. Professor visits `/grading/` page  
2. `grading.js` loads items and submissions from database
3. Displays items with associated submissions
4. Professor can enter grades and feedback

## Current State Analysis

### What's IMPLEMENTED ✅

#### Definition System ✅
- **Modules/Constituents**: Defined in YAML files (`class_template/modules.yml`, `constituents.yml`)
- **Items**: Defined via `{{< item-inline >}}` shortcodes in professor markdown files
- **Build Process**: Generates JSON files with all definitions (`items.json`, `modules.json`, etc.)
- **Manual Sync**: Professor visits `/grading-sync/` page to push definitions to Supabase database

#### Submission System ✅
- **Inline Forms**: `item-submission.js` creates submission forms directly in markdown content
- **Dynamic UI**: Forms adapt to delivery_type (url, text, code, upload, file)
- **Backend**: `submit-item` Edge Function processes submissions to database
- **History**: Shows previous submissions for each item

#### Grade Display ✅
- **Student Dashboard**: Real-time grade loading with module breakdowns
- **My Grades**: Detailed grade view with submissions history
- **SQL Functions**: On-the-fly grade calculations (`calculate_module_grades`, etc.)
- **Data Flow**: Edge Functions → Database → Client display

### What's MISSING - Implementation Gaps

#### 1. Smart Upload/Submission Hub (`/upload/` page) ❌
**Current**: Demo file upload placeholder  
**Needed**: Central submission interface for students
- List all active items grouped by module/constituent
- Show submission status (not submitted/pending/graded)  
- Quick access to submit each item
- Filters by due date, status, module
- Smart UX for bulk workflows

#### 2. Professor Grading Interface (`/grading/` page) ❌  
**Current**: Empty div, `grading.js` loads data but no UI  
**Needed**: Complete grading workflow
- Table of pending submissions by student/item
- Inline score input with validation
- Feedback textarea for each submission
- Batch grading capabilities
- Integration with `professor-grade-item` Edge Function

#### 3. Grade Policy Engine (Enhancement) ⚠️
**Current**: `grading_policies` table exists but unused  
**Needed**: Automated policy application
- Late penalty calculations based on due_date vs submission_date
- Grade adjustments and bonus systems
- Policy-based modifications to SQL grade functions

## Technical Constraints

### Static Site Architecture
- **GitHub Pages deployment** = No server-side execution
- **Manual sync by design** = Professor must trigger definition sync
- **Client-side runtime** = All interactions via JavaScript + Edge Functions
- **JSON files** = Source of truth during build process

### Current Data Flow
1. **Build Time**: Markdown → JSON files → Hugo static site
2. **Manual Sync**: Professor visits grading-sync → Definitions pushed to Supabase  
3. **Runtime**: Students submit → Edge Functions → Database → Grade display

## Implementation Plan

### Phase 1: Smart Upload Page (Student Experience)
Transform `/upload/index.md` into comprehensive submission hub:
- Load items from generated JSON data
- Group by academic hierarchy (module → constituent → item)
- Display submission status and due dates
- Reuse existing `item-submission.js` components
- Add filtering and search capabilities

### Phase 2: Complete Grading Interface (Professor Experience)  
Finish `/grading/index.md` with functional UI:
- Render submissions table with student/item organization
- Add inline grading forms (score + feedback)
- Connect to `professor-grade-item` Edge Function
- Implement real-time updates and batch operations

### Phase 3: Grade Policies (Advanced Feature)
Enhance grade calculation system:
- Extend SQL functions with policy application
- Read from `grading_policies` table
- Apply late penalties and adjustments automatically
- Support custom grading curves and bonus systems

## Success Criteria
- **Students**: Can easily find and submit all required work
- **Professors**: Can efficiently grade submissions with feedback  
- **System**: Maintains static site deployment while providing dynamic functionality
- **Data**: Consistent flow from definition → submission → grading → display

## Implementation Priorities

### Priority 1: Smart Upload Page (Student Critical)
Students need a central place to see all their assignments:
- List all items from JSON data grouped by module
- Show submission status and due dates
- Quick submit interface for each item type
- Filter/search functionality

### Priority 2: Complete Grading Interface (Professor Critical)  
Professors need to actually grade submissions:
- Display pending submissions in organized table
- Add inline grading forms for score + feedback
- Integration with existing `professor-grade-item` Edge Function
- Real-time updates and efficient workflow

### Priority 3: Grade Policies (Enhancement)
Automated grading improvements:
- Late penalty calculations
- Grade adjustments and curves
- Policy-based SQL function enhancements

---

*Ready to implement these missing components to complete the grading system workflow.*