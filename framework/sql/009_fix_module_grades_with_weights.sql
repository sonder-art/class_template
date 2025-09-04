-- ============================================================================
-- Fix calculate_module_grades to include module weights
-- This ensures the JavaScript gets dynamic weights from the database
-- ============================================================================

-- Enhanced calculate_module_grades that includes module weights
CREATE OR REPLACE FUNCTION calculate_module_grades(
    p_student_id UUID,
    p_class_id UUID
) RETURNS TABLE(
    student_id UUID,
    class_id UUID,
    grade_level TEXT,
    module_id TEXT,
    final_score NUMERIC,
    max_points NUMERIC,
    computed_at TIMESTAMPTZ,
    modules JSONB
) AS $$
BEGIN
    RETURN QUERY
    WITH module_grades AS (
        -- Get all module calculations with weights
        SELECT 
            p_student_id as student_id,
            p_class_id as class_id,
            'module'::text as grade_level,
            m.id as module_id,
            
            -- Calculate module score using grading policy (0-10 scale)
            COALESCE(apply_grading_policy(m.id, p_class_id, 
                ARRAY(
                    SELECT COALESCE(
                        (COALESCE(ss.adjusted_score, ss.raw_score) / NULLIF(i.points, 0)) * 10, 
                        0
                    )
                    FROM student_submissions ss
                    JOIN items i ON i.id = ss.item_id
                    JOIN constituents c ON c.slug = i.constituent_slug
                    WHERE ss.student_id = p_student_id
                      AND c.module_id = m.id
                      AND i.is_current = true
                      AND ss.raw_score IS NOT NULL
                )
            ), 0) as final_score,
            
            -- Sum of item points in this module (for reference)
            COALESCE(SUM(i.points), 0) as max_points,
            
            NOW() as computed_at,
            
            -- Include module metadata WITH weight
            jsonb_build_object(
                'id', m.id,
                'name', m.name,
                'weight', m.weight,  -- ← This is the key addition!
                'color', m.color,
                'icon', m.icon,
                'order_index', m.order_index
            ) as modules
            
        FROM modules m
        LEFT JOIN constituents c ON c.module_id = m.id AND c.is_current = true
        LEFT JOIN items i ON i.constituent_slug = c.slug AND i.is_current = true
        LEFT JOIN student_submissions ss ON ss.item_id = i.id AND ss.student_id = p_student_id
        
        WHERE m.class_id = p_class_id
          AND m.is_current = true
        
        GROUP BY m.id, m.name, m.weight, m.color, m.icon, m.order_index
        ORDER BY m.order_index
    )
    
    SELECT 
        mg.student_id,
        mg.class_id,
        mg.grade_level,
        mg.module_id,
        mg.final_score,
        mg.max_points,
        mg.computed_at,
        mg.modules
    FROM module_grades mg;
END;
$$ LANGUAGE plpgsql;

-- Grant permissions
GRANT EXECUTE ON FUNCTION calculate_module_grades(UUID, UUID) TO authenticated;

-- ============================================================================
-- Test the fixed function
-- ============================================================================

-- Test query (uncomment to verify the weight is included)
/*
SELECT 
    module_id,
    final_score,
    max_points,
    modules->>'weight' as module_weight,
    modules->>'name' as module_name
FROM calculate_module_grades(
    (SELECT user_id FROM class_members WHERE role = 'student' LIMIT 1),
    'df6b6665-d793-445d-8514-f1680ff77369'::uuid
);
*/

-- Log success
DO $$
BEGIN
    RAISE NOTICE '✅ calculate_module_grades function updated with module weights';
    RAISE NOTICE '📊 JavaScript can now access dynamic weights via modules.weight';
    RAISE NOTICE '🔄 Grades will now adapt automatically to module configuration changes';
END $$;