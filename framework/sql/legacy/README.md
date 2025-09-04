# Framework SQL Migrations

This directory contains the complete, ordered database migrations for the Class Template Framework. These are the **definitive** SQL files that represent the correct database schema.

## 📋 Migration Order

**IMPORTANT**: Run these migrations in exact order:

### 1. `001_basic_auth.sql` - Foundation
- ✅ Core authentication tables (`profiles`, `classes`, `class_members`) 
- ✅ Enrollment token system (`enrollment_tokens`)
- ✅ Helper functions (`is_professor_of`, `is_student_of`, `is_member_of`)
- ✅ User signup triggers
- ✅ RLS enabled (policies added in 002)

### 2. `002_auth_policies.sql` - Security
- ✅ Row Level Security (RLS) policies for auth tables
- ✅ Professor/student access control
- ✅ Class isolation security
- ✅ Token management policies

### 3. `003_grading_system.sql` - Complete Grading System  
- ✅ Grading hierarchy: `modules` → `constituents` → `items` → `submissions`
- ✅ **Correct terminology**: Uses "items" (not "homework_items")
- ✅ **JavaScript compatibility**: String `item_id` fields
- ✅ Student submissions with attempt tracking
- ✅ Professor grading adjustments
- ✅ Sample data matching framework shortcodes
- ✅ Complete RLS security policies
- ✅ Helper functions (`get_class_id_by_slug`, `initialize_class`)

## 🎯 Key Design Principles

### Correct Terminology
- ✅ **`items`** table (not `homework_items`) - represents any graded component
- ✅ **`delivery_type`** field - matches HTML `data-delivery-type="url"`
- ✅ **String `item_id`** - matches JavaScript expectations: `item_id="supabase_project_setup"`

### JavaScript Compatibility
- ✅ All field names match what the frontend JavaScript expects
- ✅ Optimized indexes for common JavaScript queries
- ✅ JSONB `submission_data` for flexible submission types

### Framework Integration
- ✅ Sample data matches actual Hugo shortcodes in markdown
- ✅ `constituent_slug` matches shortcode parameters
- ✅ `delivery_type` matches shortcode `delivery_type` attributes

### Security (Multi-Class Deployment)
- ✅ Row Level Security (RLS) on all tables
- ✅ Class isolation (professors only see their classes)
- ✅ Student data privacy (students only see their own submissions)
- ✅ Professor grading permissions (can only grade their classes)

## 🚀 Quick Setup

### For New Database:
```sql
-- Run in order:
\i 001_basic_auth.sql
\i 002_auth_policies.sql  
\i 003_grading_system.sql

-- Initialize your class:
SELECT initialize_class('class_template', 'Class Template Framework', 'your_github_username');
```

### For Supabase Dashboard:
1. Copy and paste each file contents into SQL Editor
2. Run `001_basic_auth.sql`
3. Run `002_auth_policies.sql`
4. Run `003_grading_system.sql`
5. Run: `SELECT initialize_class('class_template', 'Class Template Framework', 'uumami');`

## 📊 Database Schema Overview

```
Classes (Multi-tenant)
└── Class Members (Professors, Students)
    └── Enrollment Tokens (For student enrollment)

Grading Hierarchy:
Modules (e.g., "Authentication")
└── Constituents (e.g., "auth-setup" homework)
    └── Items (e.g., "supabase_project_setup")
        └── Student Submissions
            └── Grading Adjustments
```

## 🔧 Framework Integration

### Hugo Shortcodes → Database
```markdown
{{< item-inline constituent_slug="auth-setup" item_id="github_oauth_setup" delivery_type="upload" points="25" >}}
```
↓
```sql
items table:
- id: "github_oauth_setup" (STRING)
- constituent_slug: "auth-setup" 
- delivery_type: "upload"
- points: 25.0
```

### JavaScript → Database
```javascript
// JavaScript queries by string item_id
const submissions = await supabase
  .from('student_submissions')
  .select('*')
  .eq('item_id', 'github_oauth_setup')  // STRING field!
```

## ✅ Validation Checklist

After running migrations, verify:

- [ ] All tables exist: `\dt` in psql
- [ ] Sample data loaded: `SELECT COUNT(*) FROM items;` should return 4
- [ ] RLS enabled: `SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public';`
- [ ] Class initialized: `SELECT * FROM classes WHERE slug = 'class_template';`
- [ ] Professor enrolled: `SELECT * FROM class_members WHERE role = 'professor';`

## 🚨 Common Issues

### "relation does not exist" 
- **Cause**: Migrations run out of order
- **Fix**: Run migrations in exact order: 001 → 002 → 003

### "item_id does not match"
- **Cause**: Old schema had UUID item_id  
- **Fix**: Use these migrations - they use STRING item_id

### RLS prevents access
- **Cause**: User not enrolled in class
- **Fix**: Run `initialize_class()` after professor logs in

## 🎉 Success Indicators

When working correctly:
- ✅ Submission interfaces appear on homework pages
- ✅ No "relation does not exist" errors in browser console
- ✅ Students can submit assignments
- ✅ Professors can grade submissions
- ✅ Multi-class security works (professors only see their classes)

---

**These migrations are the authoritative database schema for the Class Template Framework.**