-- ============================================================================
-- Manual Class Creation Script
-- Run this in Supabase SQL Editor to create a new class
-- ============================================================================

-- INSTRUCTIONS:
-- 1. Replace 'your_class_slug' with your repository name
-- 2. Replace 'Your Class Title' with the actual class name
-- 3. Run this script and copy the returned UUID
-- 4. Add the UUID to course.yml as class_id: "uuid-here"
-- 5. Use b_add_professor.sql to enroll professors

-- ============================================================================
-- CREATE CLASS
-- ============================================================================

INSERT INTO classes (slug, title, description, is_active)
VALUES (
    'your_class_slug',              -- CHANGE: Repository name (e.g., 'cs101_fall2024')
    'Your Class Title',             -- CHANGE: Human-readable title (e.g., 'Computer Science 101 - Fall 2024')
    'Class created via template',   -- Optional: Description
    true                            -- Class is active
) 
RETURNING id, slug, title, created_at;

-- ============================================================================
-- COPY THE UUID FROM THE RESULT ABOVE
-- Add it to your course.yml file as:
--   class_id: "the-uuid-from-above"
-- ============================================================================

-- SECURITY NOTES:
-- 1. Only enrolled professors can manage this class (RLS enforced)
-- 2. Students cannot access professor functions even with the UUID
-- 3. Cross-class access is prevented by is_professor_of() checks
-- 4. Use b_add_professor.sql to enroll professors manually

-- NEXT STEPS:
-- 1. Copy the UUID from the result above
-- 2. Add to course.yml: class_id: "uuid-here"
-- 3. Run: ./manage.sh --validate to regenerate framework config
-- 4. Use b_add_professor.sql to enroll professors