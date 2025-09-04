-- Debug query to test if the duplicate grades fix is working
-- Run this in Supabase SQL Editor to see what the function returns

-- First, let's see all submissions for your items (to understand the data)
SELECT 
    'All submissions for your items:' as debug_section,
    ss.item_id,
    i.title as item_title,
    ss.adjusted_score,
    ss.graded_at,
    ss.attempt_number
FROM student_submissions ss
INNER JOIN items i ON i.id = ss.item_id
WHERE ss.student_id = auth.uid()
  AND ss.class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid
  AND ss.graded_at IS NOT NULL
ORDER BY ss.item_id, ss.graded_at DESC;

-- Now let's test the get_item_grades function
SELECT 
    'Results from get_item_grades function:' as debug_section,
    item_id,
    items->>'title' as item_title,
    final_score,
    max_points,
    computed_at
FROM get_item_grades(
    auth.uid(),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid
)
ORDER BY computed_at DESC;

-- Let's also check if there are any duplicate item_ids in the function results
SELECT 
    'Duplicate check - should show 0 rows if fix works:' as debug_section,
    item_id,
    COUNT(*) as occurrence_count
FROM get_item_grades(
    auth.uid(),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid
)
GROUP BY item_id
HAVING COUNT(*) > 1;