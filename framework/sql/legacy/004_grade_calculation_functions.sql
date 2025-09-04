-- ============================================================================
-- Migration 004: Grade Calculation Functions for On-the-Fly Computation
-- Dependencies: 003_grading_system.sql
-- Description: SQL functions to calculate grades dynamically, replacing cache tables
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SAFETY CHECK: Ensure dependencies are met
-- ============================================================================

DO $$
BEGIN
    -- Check if we have the grading system tables
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'student_submissions') THEN
        RAISE EXCEPTION 'Grading system schema not found. Please run 003_grading_system.sql first';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'modules') THEN
        RAISE EXCEPTION 'Modules table not found. Please run 003_grading_system.sql first';
    END IF;
    
    RAISE NOTICE '✅ Dependencies verified, proceeding with grade calculation functions';
END $$;

-- ============================================================================
-- GRADE CALCULATION FUNCTIONS
-- These replace the need for student_grades_cache table by computing grades on-the-fly
-- ============================================================================

-- Function: Calculate constituent-level grades for a student
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

-- Function: Calculate module-level grades for a student
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

-- Function: Get item-level grades for a student (with full metadata)
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

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES FOR FUNCTIONS
-- ============================================================================

-- Grant execute permissions to authenticated users
GRANT EXECUTE ON FUNCTION calculate_constituent_grades(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_module_grades(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION get_item_grades(UUID, UUID) TO authenticated;

-- ============================================================================
-- HELPER FUNCTIONS FOR GRADE SUMMARIES
-- ============================================================================

-- Function: Calculate grade summary statistics
CREATE OR REPLACE FUNCTION calculate_grade_summary(
  p_student_id UUID,
  p_class_id UUID,
  p_grade_level TEXT DEFAULT 'module'
)
RETURNS JSONB
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $$
DECLARE
  v_total_grades INTEGER := 0;
  v_total_score NUMERIC := 0;
  v_total_max_points NUMERIC := 0;
  v_average_score NUMERIC := 0;
  v_last_updated TIMESTAMPTZ;
  v_result JSONB;
BEGIN
  -- Get grade data based on level
  IF p_grade_level = 'item' THEN
    SELECT 
      COUNT(*),
      COALESCE(SUM(final_score), 0),
      COALESCE(SUM(max_points), 0),
      MAX(computed_at)
    INTO v_total_grades, v_total_score, v_total_max_points, v_last_updated
    FROM get_item_grades(p_student_id, p_class_id);
    
  ELSIF p_grade_level = 'constituent' THEN
    SELECT 
      COUNT(*),
      COALESCE(SUM(final_score), 0),
      COALESCE(SUM(max_points), 0),
      MAX(computed_at)
    INTO v_total_grades, v_total_score, v_total_max_points, v_last_updated
    FROM calculate_constituent_grades(p_student_id, p_class_id);
    
  ELSE -- module level
    SELECT 
      COUNT(*),
      COALESCE(SUM(final_score), 0),
      COALESCE(SUM(max_points), 0),
      MAX(computed_at)
    INTO v_total_grades, v_total_score, v_total_max_points, v_last_updated
    FROM calculate_module_grades(p_student_id, p_class_id);
  END IF;

  -- Calculate average percentage
  IF v_total_max_points > 0 THEN
    v_average_score := (v_total_score / v_total_max_points) * 100;
  ELSE
    v_average_score := 0;
  END IF;

  -- Build result JSON
  v_result := jsonb_build_object(
    'total_grades', v_total_grades,
    'average_score', ROUND(v_average_score, 1),
    'total_score', v_total_score,
    'max_points', v_total_max_points,
    'last_updated', v_last_updated,
    'grade_distribution', '{}'::jsonb -- Can be enhanced later if needed
  );

  RETURN v_result;
END;
$$;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION calculate_grade_summary(UUID, UUID, TEXT) TO authenticated;

-- ============================================================================
-- MIGRATION COMPLETION MESSAGE
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '✅ GRADE CALCULATION FUNCTIONS 004 COMPLETED!';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Functions Created:';
    RAISE NOTICE '   • calculate_constituent_grades(UUID, UUID)';
    RAISE NOTICE '   • calculate_module_grades(UUID, UUID)';
    RAISE NOTICE '   • get_item_grades(UUID, UUID)';
    RAISE NOTICE '   • calculate_grade_summary(UUID, UUID, TEXT)';
    RAISE NOTICE '';
    RAISE NOTICE '⚡ Performance: On-the-fly calculation with proper indexing';
    RAISE NOTICE '🔒 Security: SECURITY DEFINER with authenticated user grants';
    RAISE NOTICE '📝 Architecture: Eliminates need for grades cache table';
    RAISE NOTICE '🏗️  Integration: Compatible with existing Edge Functions';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next Steps:';
    RAISE NOTICE '   1. Update student-grades Edge Function to use these functions';
    RAISE NOTICE '   2. Test with: SELECT * FROM calculate_module_grades($user_id, $class_id);';
    RAISE NOTICE '   3. Verify performance with realistic data volumes';
    RAISE NOTICE '';
    RAISE NOTICE '✨ Grade calculations are now real-time and cache-free!';
    RAISE NOTICE '';
END $$;