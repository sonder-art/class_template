# Grading System Analysis & Fix Plan

## System Overview

This document provides a comprehensive analysis of the GitHub Class Template Framework's grading system, current issues, and solution plan.

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

## Current Issues Analysis

### Issue 1: Supabase Client API Inconsistency ❌ CRITICAL
**Problem**: JavaScript files use inconsistent Supabase API calls
- CDN script exposes `supabase` globally
- `supabase-auth.js` correctly uses `supabase.createClient()` ✅
- All other files incorrectly use `window.supabase.createClient()` ❌

**Impact**: 
- `item-submission.js` fails initialization
- No submission forms are created
- Students can't upload work

**Files Affected**:
- `grading.js` (line 49)
- `grading-sync.js` (lines 46, 59)  
- `item-submission.js` (lines 85-86)
- `student-grades.js` (line 98)

### Issue 2: Sync Change Detection Bug ❌ HIGH
**Problem**: `hasChanged()` function compares wrong fields
- Compares: `['id', 'name', 'description', 'weight', 'points', 'title']`
- Items don't have `name`, `description`, `weight` fields
- Always returns "changed" because fields don't exist

**Impact**:
- Sync always shows "4 changes" even when nothing changed
- Items may not sync properly due to faulty logic

**Location**: `grading-sync.js` lines 242-249

### Issue 3: Database Query Issues ❌ MEDIUM
**Problem**: Class ID filtering was inconsistent
- Fixed: Items query now includes `class_id` filter
- But may still have remnant issues from previous bugs

### Issue 4: Professor Test Submissions Not Visible ❌ MEDIUM  
**Problem**: Grading dashboard doesn't separate professor vs student submissions
- All members queried but only students shown in UI
- Professor submissions exist but aren't displayed

## Solution Plan

### Fix 1: Standardize Supabase Client Usage
**Priority**: CRITICAL - Fixes submission forms

**Files to Update**:
```javascript
// Change FROM:
if (typeof window.supabase !== 'undefined') {
    this.supabaseClient = window.supabase.createClient(url, key);
}

// Change TO:
if (typeof supabase !== 'undefined') {
    this.supabaseClient = supabase.createClient(url, key);
}
```

**Affected Files**:
- `framework/assets/js/grading.js` (line 49)
- `framework/assets/js/grading-sync.js` (lines 46, 59)
- `framework/assets/js/item-submission.js` (lines 85-86)
- `framework/assets/js/student-grades.js` (line 98)

### Fix 2: Fix Item Comparison Logic
**Priority**: HIGH - Fixes sync behavior

**File**: `framework/assets/js/grading-sync.js` (lines 242-249)
```javascript
hasChanged(fileItem, dbItem) {
    // Compare actual item fields that exist
    const itemFields = ['points', 'title', 'delivery_type', 'due_date', 'constituent_slug'];
    return itemFields.some(key => {
        const fileVal = fileItem[key];
        const dbVal = dbItem[key];
        
        // Handle numeric comparison for points
        if (key === 'points') {
            return parseFloat(fileVal || 0) !== parseFloat(dbVal || 0);
        }
        
        // Handle date comparison  
        if (key === 'due_date') {
            // Normalize date strings or handle nulls
            const fDate = fileVal ? new Date(fileVal).toISOString() : null;
            const dDate = dbVal ? new Date(dbVal).toISOString() : null;
            return fDate !== dDate;
        }
        
        return fileVal !== dbVal;
    });
}
```

### Fix 3: Enhanced Debug Logging
**Priority**: MEDIUM - Helps troubleshooting

Add comprehensive logging to understand what's happening:
```javascript
// In syncItems() function
console.log('🔍 Items comparison debug:', this.gradingData.items.map(item => ({
    local_id: item.item_id,
    local_points: item.points,
    local_title: item.title,
    has_db_match: !!currentDbItems.find(db => db.id === item.item_id)
})));
```

### Fix 4: Professor Submission Display
**Priority**: MEDIUM - Shows test submissions

**File**: `framework/assets/js/grading.js`
- Already implemented in previous work
- Shows professor submissions in separate section
- Clearly labeled as "test submissions"

## Implementation Order

### Phase 1: Critical Fixes
1. **Fix Supabase API calls** (Fix 1)
   - Update all 4 JavaScript files  
   - Test: Submission forms should appear on homework pages

2. **Fix sync comparison logic** (Fix 2)
   - Update `hasChanged()` function
   - Test: Sync should show correct change count

### Phase 2: Verification
3. **Test complete workflow**:
   - Run grading sync → should sync items to database
   - Visit homework page → should see submission forms
   - Submit work as professor → should succeed
   - Visit grading dashboard → should show items and submissions

### Phase 3: Enhancement  
4. **Add enhanced debugging** (Fix 3)
   - Better error messages and logging
   - Easier troubleshooting for future issues

## Testing Strategy

### Test 1: Submission Forms Appear
**URL**: `http://localhost:1313/class_template/class_notes/01_authentication_basics/01_homework_auth_setup/`
**Expected**: Submission forms visible below each item
**Console**: Should show "Found X graded items on page"

### Test 2: Sync Works Correctly  
**URL**: `http://localhost:1313/class_template/grading-sync/`
**Expected**: 
- First run: Shows 4 items to sync
- After sync: Shows 0 changes (unless items actually changed)
**Console**: Should show successful sync messages

### Test 3: Submissions Work
**Process**: 
1. Go to homework page
2. Fill out and submit a form
3. Check console for success message
4. Verify in grading dashboard

### Test 4: Grading Dashboard Shows Data
**URL**: `http://localhost:1313/class_template/grading/`
**Expected**:
- Items load from database (not empty)
- Professor submissions visible in test section
- Can navigate and see submission data

## Recovery Information

### Quick Status Check
If system isn't working, check these in order:

1. **Are items parsed?** → Check `hugo_generated/data/items.json` has 4 items
2. **Are items synced?** → Check grading-sync page, should show "0 changes" after first sync
3. **Do forms appear?** → Check homework page for submission interfaces  
4. **Do submissions work?** → Check console for errors during submit
5. **Does dashboard work?** → Check grading page loads items and submissions

### Key Log Messages
- `item-submission.js`: "Found X graded items on page"
- `grading-sync.js`: "✅ Synced X items to database"  
- `grading.js`: "📊 Grading data loaded: {items: X, submissions: Y}"

### Common Error Patterns
- "Supabase client library not loaded" → Fix 1 needed
- "4 changes every time" → Fix 2 needed
- No submission forms → Fix 1 needed
- No items in grading dashboard → Check sync completed

This document serves as the master reference for understanding and fixing the grading system. Keep it updated as issues are resolved.