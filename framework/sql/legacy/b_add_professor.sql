-- ============================================================================
-- Professor Enrollment Script
-- Run this in Supabase SQL Editor to enroll a professor in a class
-- ============================================================================

-- INSTRUCTIONS:
-- 1. First, run a_add_class.sql to create the class and get the UUID
-- 2. Replace the values below with actual class_id and professor info
-- 3. Run this script to enroll the professor
-- 4. Verify the enrollment with the query at the bottom

-- ============================================================================
-- STEP 1: Find the professor by GitHub username
-- ============================================================================

SELECT 
    user_id, 
    github_username, 
    email, 
    full_name,
    created_at
FROM profiles 
WHERE github_username = 'uumami';  -- CHANGE: Professor's GitHub username

-- Copy the user_id from the result above for step 2

-- ============================================================================
-- STEP 2: Enroll the professor in the class
-- ============================================================================

INSERT INTO class_members (class_id, user_id, role, enrolled_at)
VALUES (
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid,  -- CHANGE: Class UUID from a_add_class.sql
    '385dd2ab-a193-483d-9df9-d5a2cca2cea3'::uuid,  -- CHANGE: User UUID from step 1 above
    'professor',
    NOW()
) 
ON CONFLICT (class_id, user_id) 
DO UPDATE SET 
    role = 'professor',
    enrolled_at = NOW();

-- ============================================================================
-- STEP 3: Verify the enrollment was successful
-- ============================================================================

SELECT 
    cm.role,
    cm.enrolled_at,
    c.slug as class_slug,
    c.title as class_title,
    p.github_username,
    p.email
FROM class_members cm
JOIN classes c ON c.id = cm.class_id
JOIN profiles p ON p.user_id = cm.user_id
WHERE cm.class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid  -- CHANGE: Your class UUID
AND cm.role = 'professor';

-- ============================================================================
-- SECURITY VERIFICATION
-- Test that professor isolation is working correctly
-- ============================================================================

-- This should return TRUE only for professors of this specific class
SELECT public.is_professor_of(
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid,  -- CHANGE: Your class UUID
    '385dd2ab-a193-483d-9df9-d5a2cca2cea3'::uuid   -- CHANGE: Professor's user UUID
);

-- SECURITY NOTES:
-- 1. Professors can only access classes they are enrolled in
-- 2. is_professor_of() function prevents cross-class access
-- 3. RLS policies enforce database-level security
-- 4. Manual enrollment ensures controlled access

-- NEXT STEPS AFTER ENROLLMENT:
-- 1. Add class_id to course.yml in your repository
-- 2. Run: ./manage.sh --validate to update framework config
-- 3. Test professor access at: /grading/ page
-- 4. Generate enrollment tokens for students if needed