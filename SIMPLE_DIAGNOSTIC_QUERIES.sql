-- SIMPLE DIAGNOSTIC QUERIES - Run one by one

-- Query 1: Check students
SELECT 
    cm.user_id,
    p.full_name,
    p.github_username,
    cm.role
FROM class_members cm
LEFT JOIN profiles p ON p.user_id = cm.user_id
WHERE cm.class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND cm.role = 'student';

-- Query 2: Check submissions count  
SELECT COUNT(*) as total_submissions
FROM student_submissions 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid;

-- Query 3: Check if calculate_module_grades exists
SELECT proname FROM pg_proc WHERE proname = 'calculate_module_grades';

-- Query 4: Check modules table
SELECT id, name, weight FROM modules 
WHERE class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid;

-- Query 5: Test module grades function (replace student_id with actual ID from Query 1)
-- SELECT * FROM calculate_module_grades('REPLACE_WITH_ACTUAL_STUDENT_ID'::uuid, 'df6b6665-d793-445d-8514-f1680ff77369'::uuid);