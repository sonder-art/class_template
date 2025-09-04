-- DIAGNOSTIC QUERIES FOR MY GRADES PAGE DEBUGGING
-- Run these in Supabase SQL Editor to check the data

-- 1. Check if we have any students and their basic info
SELECT 
    cm.user_id,
    p.full_name,
    p.github_username,
    cm.role,
    cm.enrollment_status
FROM class_members cm
LEFT JOIN profiles p ON p.user_id = cm.user_id
WHERE cm.class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND cm.role = 'student'
ORDER BY p.full_name;

-- 2. Check if we have any student submissions
SELECT 
    COUNT(*) as total_submissions,
    COUNT(DISTINCT student_id) as students_with_submissions,
    COUNT(*) FILTER (WHERE raw_score IS NOT NULL) as graded_submissions
FROM student_submissions 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid;

-- 3. Check if calculate_module_grades function exists and works
SELECT 
    proname as function_name,
    pg_get_function_arguments(oid) as arguments
FROM pg_proc 
WHERE proname = 'calculate_module_grades';

-- 4. Test calculate_module_grades with a student (if students exist)
-- Replace the student_id with actual student from query #1
SELECT * FROM calculate_module_grades(
    (SELECT user_id FROM class_members WHERE role = 'student' AND class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid LIMIT 1),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid
);

-- 5. Check what items exist and are current
SELECT 
    id,
    title,
    points,
    constituent_slug,
    is_current,
    is_active
FROM items 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND is_current = true
ORDER BY title;

-- 6. Check what modules and constituents are configured
SELECT 
    'modules' as type,
    id,
    name,
    weight::text as weight_text,
    order_index,
    is_current
FROM modules 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND is_current = true
UNION ALL
SELECT 
    'constituents' as type,
    id,
    name,
    weight::text as weight_text,
    NULL as order_index,
    is_current
FROM constituents 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND is_current = true
ORDER BY type, id;

-- 7. Check if calculate_grade_summary function was created
SELECT 
    proname as function_name,
    pg_get_function_arguments(oid) as arguments
FROM pg_proc 
WHERE proname = 'calculate_grade_summary';

-- 8. Test the student-grades endpoint data structure
-- This simulates what the Edge Function should return
SELECT 
    'Module grades test' as test_type,
    COUNT(*) as grade_count
FROM calculate_module_grades(
    (SELECT user_id FROM class_members WHERE role = 'student' AND class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid LIMIT 1),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid
);

-- 9. Check submissions with item details for debugging
SELECT 
    ss.student_id,
    ss.item_id,
    i.title as item_title,
    i.points as item_points,
    ss.raw_score,
    ss.adjusted_score,
    ss.graded_at,
    c.slug as constituent,
    c.module_id
FROM student_submissions ss
JOIN items i ON i.id = ss.item_id
JOIN constituents c ON c.slug = i.constituent_slug
WHERE ss.class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND i.is_current = true
ORDER BY ss.student_id, c.module_id, i.title;