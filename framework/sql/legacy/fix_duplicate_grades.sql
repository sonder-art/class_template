-- ============================================================================
-- Fix Duplicate Grades Migration
-- Run this directly in Supabase SQL Editor to update grade calculation functions
-- This ensures only the most recent grade per item is shown to students
-- ============================================================================

-- Function: Get item-level grades for a student (LATEST SUBMISSION ONLY)
-- Returns individual submission grades with associated metadata
CREATE OR REPLACE FUNCTION get_item_grades(
  p_student_id UUID,
  p_class_id UUID
)
RETURNS TABLE (
  student_id UUID,
  class_id UUID,
  grade_level TEXT,
  item_id TEXT,
  final_score NUMERIC,
  max_points NUMERIC,
  computed_at TIMESTAMPTZ,
  items JSONB,
  constituents JSONB,
  modules JSONB
)
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
  -- Get only the most recent graded submission per item
  WITH latest_submissions AS (
    SELECT DISTINCT ON (ss.item_id)
      ss.student_id,
      ss.class_id,
      ss.item_id,
      ss.adjusted_score,
      ss.graded_at
    FROM student_submissions ss
    INNER JOIN items i ON i.id = ss.item_id
    WHERE ss.student_id = p_student_id
      AND ss.class_id = p_class_id
      AND ss.graded_at IS NOT NULL
      AND i.is_current = true
    ORDER BY ss.item_id, ss.graded_at DESC
  )
  SELECT 
    ls.student_id,
    ls.class_id,
    'item' as grade_level,
    ls.item_id,
    ls.adjusted_score as final_score,
    i.points as max_points,
    ls.graded_at as computed_at,
    jsonb_build_object('title', i.title, 'due_date', i.due_date) as items,
    jsonb_build_object('name', c.name, 'type', c.type) as constituents,
    jsonb_build_object('name', m.name, 'color', m.color, 'icon', m.icon) as modules
  FROM latest_submissions ls
  INNER JOIN items i ON i.id = ls.item_id
  INNER JOIN constituents c ON c.slug = i.constituent_slug
  INNER JOIN modules m ON m.id = c.module_id
  WHERE c.is_current = true
    AND m.is_current = true
  ORDER BY ls.graded_at DESC;
$$;

-- Function: Calculate constituent-level grades for a student (LATEST SUBMISSIONS ONLY)
-- Aggregates all item scores within each constituent
CREATE OR REPLACE FUNCTION calculate_constituent_grades(
  p_student_id UUID,
  p_class_id UUID
)
RETURNS TABLE (
  student_id UUID,
  class_id UUID,
  grade_level TEXT,
  constituent_id TEXT,
  final_score NUMERIC,
  max_points NUMERIC,
  computed_at TIMESTAMPTZ,
  constituents JSONB,
  modules JSONB
)
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
  -- Get only the most recent graded submission per item for accurate constituent scores
  WITH latest_submissions AS (
    SELECT DISTINCT ON (ss.item_id)
      ss.item_id,
      ss.adjusted_score,
      ss.graded_at
    FROM student_submissions ss
    INNER JOIN items i ON i.id = ss.item_id
    WHERE ss.student_id = p_student_id
      AND ss.class_id = p_class_id
      AND ss.graded_at IS NOT NULL
      AND i.is_current = true
    ORDER BY ss.item_id, ss.graded_at DESC
  )
  SELECT 
    p_student_id as student_id,
    p_class_id as class_id,
    'constituent' as grade_level,
    c.id as constituent_id,
    COALESCE(SUM(ls.adjusted_score), 0) as final_score,
    COALESCE(SUM(i.points), 0) as max_points,
    MAX(ls.graded_at) as computed_at,
    jsonb_build_object('name', c.name, 'type', c.type) as constituents,
    jsonb_build_object('name', m.name, 'color', m.color, 'icon', m.icon) as modules
  FROM constituents c
  INNER JOIN modules m ON m.id = c.module_id
  LEFT JOIN items i ON i.constituent_slug = c.slug AND i.class_id = p_class_id AND i.is_current = true
  LEFT JOIN latest_submissions ls ON ls.item_id = i.id
  WHERE c.class_id = p_class_id
    AND c.is_current = true
  GROUP BY c.id, c.name, c.type, m.name, m.color, m.icon
  HAVING COALESCE(SUM(i.points), 0) > 0; -- Only return constituents that have items
$$;

-- Function: Calculate module-level grades for a student (LATEST SUBMISSIONS ONLY)
-- Aggregates all item scores within each module
CREATE OR REPLACE FUNCTION calculate_module_grades(
  p_student_id UUID,
  p_class_id UUID
)
RETURNS TABLE (
  student_id UUID,
  class_id UUID,
  grade_level TEXT,
  module_id TEXT,
  final_score NUMERIC,
  max_points NUMERIC,
  computed_at TIMESTAMPTZ,
  modules JSONB
)
LANGUAGE sql
STABLE
SECURITY DEFINER
AS $$
  -- Get only the most recent graded submission per item for accurate module scores
  WITH latest_submissions AS (
    SELECT DISTINCT ON (ss.item_id)
      ss.item_id,
      ss.adjusted_score,
      ss.graded_at
    FROM student_submissions ss
    INNER JOIN items i ON i.id = ss.item_id
    WHERE ss.student_id = p_student_id
      AND ss.class_id = p_class_id
      AND ss.graded_at IS NOT NULL
      AND i.is_current = true
    ORDER BY ss.item_id, ss.graded_at DESC
  )
  SELECT 
    p_student_id as student_id,
    p_class_id as class_id,
    'module' as grade_level,
    m.id as module_id,
    COALESCE(SUM(ls.adjusted_score), 0) as final_score,
    COALESCE(SUM(i.points), 0) as max_points,
    MAX(ls.graded_at) as computed_at,
    jsonb_build_object('name', m.name, 'color', m.color, 'icon', m.icon) as modules
  FROM modules m
  LEFT JOIN constituents c ON c.module_id = m.id AND c.is_current = true
  LEFT JOIN items i ON i.constituent_slug = c.slug AND i.class_id = p_class_id AND i.is_current = true
  LEFT JOIN latest_submissions ls ON ls.item_id = i.id
  WHERE m.class_id = p_class_id
    AND m.is_current = true
  GROUP BY m.id, m.name, m.color, m.icon
  HAVING COALESCE(SUM(i.points), 0) > 0; -- Only return modules that have items
$$;

-- Grant permissions (if they don't already exist)
GRANT EXECUTE ON FUNCTION calculate_constituent_grades(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_module_grades(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_item_grades(UUID, UUID) TO authenticated;

-- Test query to verify the fix (optional - comment out after testing)
/*
SELECT 'Testing latest grade fix for your user:' as message;
SELECT 
  items->>'title' as item_title,
  final_score,
  max_points,
  computed_at
FROM get_item_grades(
  auth.uid(), -- Your user ID
  'df6b6665-d793-445d-8514-f1680ff77369'::uuid -- Class ID
)
ORDER BY computed_at DESC;
*/