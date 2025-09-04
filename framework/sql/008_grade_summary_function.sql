-- ============================================================================
-- Grade Summary Function
-- Creates the missing calculate_grade_summary function for dashboard display
-- ============================================================================

-- Function to calculate grade summaries at different levels
CREATE OR REPLACE FUNCTION calculate_grade_summary(
    p_student_id UUID,
    p_class_id UUID,
    p_grade_level TEXT DEFAULT 'module'
) RETURNS JSONB AS $$
DECLARE
    v_summary JSONB;
    v_total_grades INTEGER;
    v_average_score NUMERIC;
    v_graded_count INTEGER;
BEGIN
    IF p_grade_level = 'module' THEN
        -- Calculate module-level summary
        SELECT 
            COUNT(*) FILTER (WHERE final_score IS NOT NULL),
            AVG(final_score * 10) -- Convert 0-10 to percentage for display
        INTO v_graded_count, v_average_score
        FROM calculate_module_grades(p_student_id, p_class_id);
        
    ELSIF p_grade_level = 'constituent' THEN
        -- Calculate constituent-level summary  
        SELECT 
            COUNT(*) FILTER (WHERE final_score IS NOT NULL),
            AVG((final_score / NULLIF(max_points, 0)) * 100)
        INTO v_graded_count, v_average_score
        FROM calculate_constituent_grades(p_student_id, p_class_id);
        
    ELSE -- item level
        -- Calculate item-level summary
        SELECT 
            COUNT(*) FILTER (WHERE raw_score IS NOT NULL),
            AVG((COALESCE(adjusted_score, raw_score) / NULLIF(points, 0)) * 100)
        INTO v_graded_count, v_average_score
        FROM student_submissions ss
        JOIN items i ON i.id = ss.item_id
        WHERE ss.student_id = p_student_id 
          AND ss.class_id = p_class_id
          AND i.is_current = true;
    END IF;
    
    -- Build summary JSON
    v_summary := jsonb_build_object(
        'total_grades', COALESCE(v_graded_count, 0),
        'average_score', COALESCE(ROUND(v_average_score, 1), 0),
        'grade_level', p_grade_level,
        'grade_distribution', jsonb_build_object(),
        'last_updated', NOW()
    );
    
    RETURN v_summary;
    
EXCEPTION WHEN OTHERS THEN
    -- Return default summary on error
    RAISE WARNING 'Error in calculate_grade_summary: %', SQLERRM;
    RETURN jsonb_build_object(
        'total_grades', 0,
        'average_score', 0,
        'grade_level', p_grade_level,
        'grade_distribution', jsonb_build_object(),
        'last_updated', NOW(),
        'error', SQLERRM
    );
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT EXECUTE ON FUNCTION calculate_grade_summary(UUID, UUID, TEXT) TO authenticated;

-- ============================================================================
-- TESTING QUERIES (for manual verification)
-- ============================================================================

-- Test with a sample student (uncomment to test)
/*
SELECT calculate_grade_summary(
    (SELECT user_id FROM class_members WHERE role = 'student' LIMIT 1),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid,
    'module'
);
*/

-- Check function installation
DO $$
BEGIN
    RAISE NOTICE '✅ calculate_grade_summary function created successfully';
    RAISE NOTICE '📊 This function converts 0-10 module grades to percentages for dashboard display';
    RAISE NOTICE '🔧 Deploy this to Supabase SQL Editor to fix dashboard grade display';
END $$;