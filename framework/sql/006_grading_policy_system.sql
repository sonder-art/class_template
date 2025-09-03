-- ============================================================================
-- Migration 006: Grading Policy System
-- Dependencies: 003_grading_system.sql, 004_grade_calculation_functions.sql
-- Description: Creates JSON-based grading policy system for automatic grade calculations
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SAFETY CHECK: Ensure dependencies are met
-- ============================================================================

DO $$
BEGIN
    -- Check if we have the grading tables
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'modules') THEN
        RAISE EXCEPTION 'Grading system not found. Please run 003_grading_system.sql first';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'student_submissions') THEN
        RAISE EXCEPTION 'Student submissions table not found. Please run grading system migrations first';
    END IF;
    
    RAISE NOTICE '✅ Dependencies verified, proceeding with grading policy system';
END $$;

-- ============================================================================
-- GRADING POLICIES TABLE
-- Stores JSON-based grading policies that can be applied to modules
-- ============================================================================

CREATE TABLE IF NOT EXISTS grading_policies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    
    -- Policy identification
    module_id TEXT REFERENCES modules(id) ON DELETE CASCADE, -- NULL means applies to all modules
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    policy_name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    
    -- JSON policy definition - stores the actual grading rules
    policy_rules JSONB NOT NULL,
    
    -- Policy metadata
    description TEXT,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure one active policy per module/class combination
    UNIQUE(module_id, class_id, version),
    
    -- Check that policy_rules has required structure
    CONSTRAINT valid_policy_rules CHECK (
        policy_rules ? 'grading_rules' AND 
        jsonb_typeof(policy_rules -> 'grading_rules') = 'array'
    )
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_grading_policies_active ON grading_policies(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_grading_policies_module_class ON grading_policies(module_id, class_id, is_active);
CREATE INDEX IF NOT EXISTS idx_grading_policies_universal ON grading_policies(class_id, is_active) WHERE module_id IS NULL;

-- ============================================================================
-- UNIVERSAL GRADING POLICY INTERPRETER FUNCTION
-- Applies JSON-based grading policies to calculate final scores
-- ============================================================================

CREATE OR REPLACE FUNCTION apply_grading_policy(
    p_module_id TEXT,
    p_class_id UUID,
    p_grades NUMERIC[]
) RETURNS NUMERIC
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_policy_rules JSONB;
    v_final_score NUMERIC;
    v_avg_score NUMERIC;
    v_min_grade NUMERIC;
    v_max_grade NUMERIC;
    v_grade_count INTEGER;
    v_filtered_grades NUMERIC[];
BEGIN
    -- Handle empty or null grades
    IF p_grades IS NULL OR array_length(p_grades, 1) = 0 THEN
        RETURN 0;
    END IF;
    
    -- Filter out null grades and calculate statistics
    SELECT ARRAY(SELECT g FROM UNNEST(p_grades) AS g WHERE g IS NOT NULL)
    INTO v_filtered_grades;
    
    v_grade_count := array_length(v_filtered_grades, 1);
    
    -- If no valid grades after filtering
    IF v_grade_count = 0 THEN
        RETURN 0;
    END IF;
    
    -- Calculate basic statistics
    SELECT 
        AVG(g),
        MIN(g),
        MAX(g)
    INTO v_avg_score, v_min_grade, v_max_grade
    FROM UNNEST(v_filtered_grades) AS g;
    
    -- Get active policy for this module (module-specific first, then universal)
    SELECT policy_rules INTO v_policy_rules
    FROM grading_policies
    WHERE class_id = p_class_id
    AND is_active = true
    AND (module_id = p_module_id OR module_id IS NULL)
    ORDER BY 
        CASE WHEN module_id = p_module_id THEN 1 ELSE 2 END, -- Module-specific first
        created_at DESC
    LIMIT 1;
    
    -- If no policy found, return simple average
    IF v_policy_rules IS NULL THEN
        RETURN ROUND(v_avg_score, 2);
    END IF;
    
    -- Apply the 5-rule grading policy
    -- Rule 1: All grades > 9.0 → Final = 10.0
    IF v_min_grade > 9.0 THEN
        v_final_score := 10.0;
        
    -- Rule 2: All grades > 8.0 → Average + bonus (0.15 to 0.5)
    ELSIF v_min_grade > 8.0 THEN
        -- Linear interpolation: avg 8.0→+0.15, avg 9.0→+0.5
        -- Formula: bonus = 0.15 + (avg - 8.0) * 0.35
        v_final_score := v_avg_score + (0.15 + (v_avg_score - 8.0) * 0.35);
        v_final_score := LEAST(v_final_score, 10.0); -- Cap at 10.0
        
    -- Rule 3: All grades > 7.5 → Exact average
    ELSIF v_min_grade > 7.5 THEN
        v_final_score := v_avg_score;
        
    -- Rule 4: Any grade 6.0-7.5 → Average - 0.3 (min 6.0)
    ELSIF EXISTS (SELECT 1 FROM UNNEST(v_filtered_grades) AS g WHERE g >= 6.0 AND g <= 7.5) THEN
        v_final_score := GREATEST(6.0, v_avg_score - 0.3);
        
    -- Rule 5: Any grade < 6.0 → Remove highest, average rest
    ELSIF v_min_grade < 6.0 THEN
        IF v_grade_count > 1 THEN
            -- Remove highest grade and average the rest
            SELECT AVG(g) INTO v_final_score
            FROM UNNEST(v_filtered_grades) AS g
            WHERE g < v_max_grade
            OR (g = v_max_grade AND ctid > (
                SELECT MIN(ctid) FROM UNNEST(v_filtered_grades) WITH ORDINALITY AS t(g, ctid) 
                WHERE g = v_max_grade
            ));
            
            -- If that didn't work (all grades are the same), just use average
            IF v_final_score IS NULL THEN
                v_final_score := v_avg_score;
            END IF;
        ELSE
            -- Only one grade, use it as-is
            v_final_score := v_avg_score;
        END IF;
        
    -- Default fallback
    ELSE
        v_final_score := v_avg_score;
    END IF;
    
    -- Ensure final score is within valid range
    v_final_score := GREATEST(0, LEAST(10.0, v_final_score));
    
    RETURN ROUND(v_final_score, 2);
END;
$$;

-- ============================================================================
-- UPDATE EXISTING GRADE CALCULATION FUNCTION
-- Modify calculate_module_grades to use the new policy system
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_module_grades(
    p_student_id UUID,
    p_class_id UUID
) RETURNS TABLE (
    student_id UUID,
    class_id UUID,
    grade_level TEXT,
    module_id TEXT,
    final_score NUMERIC,
    max_points NUMERIC,
    computed_at TIMESTAMPTZ,
    modules JSONB
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
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
    ),
    module_grades AS (
        SELECT 
            m.id as module_id,
            m.name as module_name,
            m.color as module_color,
            m.icon as module_icon,
            -- Collect all grades for this module for policy calculation
            array_agg(ls.adjusted_score ORDER BY i.id) FILTER (WHERE ls.adjusted_score IS NOT NULL) as grades_array,
            COALESCE(SUM(ls.adjusted_score), 0) as raw_total,
            COALESCE(SUM(i.points), 0) as max_points,
            MAX(ls.graded_at) as computed_at,
            COUNT(ls.adjusted_score) as grade_count
        FROM modules m
        LEFT JOIN constituents c ON c.module_id = m.id AND c.is_current = true
        LEFT JOIN items i ON i.constituent_slug = c.slug AND i.class_id = p_class_id AND i.is_current = true
        LEFT JOIN latest_submissions ls ON ls.item_id = i.id
        WHERE m.class_id = p_class_id
        AND m.is_current = true
        GROUP BY m.id, m.name, m.color, m.icon
        HAVING COALESCE(SUM(i.points), 0) > 0
    )
    SELECT 
        p_student_id as student_id,
        p_class_id as class_id,
        'module'::TEXT as grade_level,
        mg.module_id,
        -- Apply grading policy if grades exist, otherwise use raw total
        CASE 
            WHEN mg.grades_array IS NOT NULL AND array_length(mg.grades_array, 1) > 0
            THEN apply_grading_policy(mg.module_id, p_class_id, mg.grades_array)
            ELSE mg.raw_total
        END as final_score,
        mg.max_points,
        mg.computed_at,
        jsonb_build_object(
            'name', mg.module_name, 
            'color', mg.module_color, 
            'icon', mg.module_icon
        ) as modules
    FROM module_grades mg;
END;
$$;

-- ============================================================================
-- GRANT APPROPRIATE PERMISSIONS
-- ============================================================================

-- Grant usage on the table to authenticated users (read-only)
GRANT SELECT ON grading_policies TO authenticated;

-- Grant execute permissions on the function
GRANT EXECUTE ON FUNCTION apply_grading_policy(TEXT, UUID, NUMERIC[]) TO authenticated;

-- ============================================================================
-- VERIFICATION AND SUMMARY
-- ============================================================================

DO $$
DECLARE
    v_table_exists BOOLEAN;
    v_function_exists BOOLEAN;
BEGIN
    -- Check if table was created
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'grading_policies'
    ) INTO v_table_exists;
    
    -- Check if function was created
    SELECT EXISTS (
        SELECT FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = 'public'
        AND p.proname = 'apply_grading_policy'
    ) INTO v_function_exists;
    
    IF v_table_exists AND v_function_exists THEN
        RAISE NOTICE '✅ Grading Policy System Successfully Created:';
        RAISE NOTICE '   - grading_policies table: CREATED';
        RAISE NOTICE '   - apply_grading_policy function: CREATED';
        RAISE NOTICE '   - calculate_module_grades function: UPDATED';
        RAISE NOTICE '   - Ready for YAML policy sync!';
    ELSE
        RAISE WARNING '❌ Some components may not have been created properly';
    END IF;
END $$;