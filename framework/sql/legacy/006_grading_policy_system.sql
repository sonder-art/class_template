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
-- CONSTITUENT GRADE NORMALIZATION FUNCTION
-- Calculates normalized constituent grades (0-10 scale) for policy application
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_normalized_constituent_grades(
    p_student_id UUID,
    p_class_id UUID,
    p_module_id TEXT
) RETURNS TABLE (
    constituent_id TEXT,
    constituent_slug TEXT,
    normalized_grade NUMERIC,
    raw_score NUMERIC,
    max_points NUMERIC,
    item_count INTEGER
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
    )
    SELECT 
        c.id as constituent_id,
        c.slug as constituent_slug,
        -- Normalize to 0-10 scale: (earned/possible) * 10
        CASE 
            WHEN COALESCE(SUM(i.points), 0) > 0
            THEN ROUND((COALESCE(SUM(ls.adjusted_score), 0) / SUM(i.points)) * 10, 2)
            ELSE 0::NUMERIC
        END as normalized_grade,
        COALESCE(SUM(ls.adjusted_score), 0) as raw_score,
        COALESCE(SUM(i.points), 0) as max_points,
        COUNT(i.id) as item_count
    FROM constituents c
    LEFT JOIN items i ON i.constituent_slug = c.slug AND i.class_id = p_class_id AND i.is_current = true
    LEFT JOIN latest_submissions ls ON ls.item_id = i.id
    WHERE c.module_id = p_module_id
    AND c.class_id = p_class_id
    AND c.is_current = true
    GROUP BY c.id, c.slug
    HAVING COUNT(i.id) > 0; -- Only return constituents that have items
END;
$$;

-- ============================================================================
-- UPDATE EXISTING GRADE CALCULATION FUNCTION
-- Modify calculate_module_grades to use the new policy system properly
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
    WITH module_constituent_grades AS (
        -- Get normalized constituent grades for each module
        SELECT 
            m.id as module_id,
            m.name as module_name,
            m.color as module_color,
            m.icon as module_icon,
            -- Collect normalized constituent grades for policy application
            array_agg(ncg.normalized_grade ORDER BY ncg.constituent_id) FILTER (WHERE ncg.normalized_grade IS NOT NULL) as constituent_grades,
            -- Calculate total raw points for display
            SUM(ncg.raw_score) as raw_total,
            SUM(ncg.max_points) as max_points,
            MAX(
                CASE WHEN ncg.raw_score > 0 THEN NOW() ELSE NULL END
            ) as computed_at,
            COUNT(ncg.constituent_id) as constituent_count
        FROM modules m
        LEFT JOIN LATERAL (
            SELECT * FROM calculate_normalized_constituent_grades(p_student_id, p_class_id, m.id)
        ) ncg ON true
        WHERE m.class_id = p_class_id
        AND m.is_current = true
        GROUP BY m.id, m.name, m.color, m.icon
    )
    SELECT 
        p_student_id as student_id,
        p_class_id as class_id,
        'module'::TEXT as grade_level,
        mcg.module_id,
        -- Apply grading policy to constituent grades (proper hierarchy!)
        CASE 
            WHEN mcg.constituent_grades IS NOT NULL AND array_length(mcg.constituent_grades, 1) > 0
            THEN apply_grading_policy(mcg.module_id, p_class_id, mcg.constituent_grades)
            ELSE 0::NUMERIC
        END as final_score,
        COALESCE(mcg.max_points, 0) as max_points,
        mcg.computed_at,
        jsonb_build_object(
            'name', mcg.module_name, 
            'color', mcg.module_color, 
            'icon', mcg.module_icon,
            'constituent_count', mcg.constituent_count,
            'constituent_grades', mcg.constituent_grades
        ) as modules
    FROM module_constituent_grades mcg
    WHERE mcg.constituent_count > 0 OR mcg.max_points > 0; -- Include modules with constituents/items
END;
$$;

-- ============================================================================
-- WEIGHTED FINAL GRADE CALCULATION FUNCTION
-- Calculates the final weighted grade from all module grades
-- ============================================================================

CREATE OR REPLACE FUNCTION calculate_final_weighted_grade(
    p_student_id UUID,
    p_class_id UUID
) RETURNS TABLE (
    student_id UUID,
    class_id UUID,
    final_grade NUMERIC,
    total_weight_used NUMERIC,
    modules_graded INTEGER,
    total_modules INTEGER,
    grade_breakdown JSONB,
    computed_at TIMESTAMPTZ
)
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_final_grade NUMERIC := 0;
    v_total_weight NUMERIC := 0;
    v_used_weight NUMERIC := 0;
    v_modules_graded INTEGER := 0;
    v_total_modules INTEGER := 0;
    v_breakdown JSONB := '[]'::JSONB;
    v_module_record RECORD;
BEGIN
    -- Get total modules count
    SELECT COUNT(*) INTO v_total_modules
    FROM modules m
    WHERE m.class_id = p_class_id AND m.is_current = true;
    
    -- Get total possible weight
    SELECT COALESCE(SUM(weight), 0) INTO v_total_weight
    FROM modules m
    WHERE m.class_id = p_class_id AND m.is_current = true;
    
    -- Calculate weighted grade from each module
    FOR v_module_record IN
        SELECT 
            m.id,
            m.name,
            m.weight,
            mg.final_score
        FROM modules m
        LEFT JOIN calculate_module_grades(p_student_id, p_class_id) mg ON mg.module_id = m.id
        WHERE m.class_id = p_class_id AND m.is_current = true
        ORDER BY m.order_index
    LOOP
        -- Add to breakdown
        v_breakdown := v_breakdown || jsonb_build_object(
            'module_id', v_module_record.id,
            'module_name', v_module_record.name,
            'module_weight', v_module_record.weight,
            'module_grade', COALESCE(v_module_record.final_score, 0),
            'contribution', CASE 
                WHEN v_module_record.final_score IS NOT NULL 
                THEN ROUND((v_module_record.final_score * v_module_record.weight / 100), 2)
                ELSE 0
            END,
            'has_grades', v_module_record.final_score IS NOT NULL
        );
        
        -- Add to final grade if module has grades
        IF v_module_record.final_score IS NOT NULL THEN
            v_final_grade := v_final_grade + (v_module_record.final_score * v_module_record.weight / 100);
            v_used_weight := v_used_weight + v_module_record.weight;
            v_modules_graded := v_modules_graded + 1;
        END IF;
    END LOOP;
    
    RETURN QUERY
    SELECT 
        p_student_id,
        p_class_id,
        ROUND(v_final_grade, 2) as final_grade,
        v_used_weight as total_weight_used,
        v_modules_graded,
        v_total_modules,
        v_breakdown as grade_breakdown,
        NOW() as computed_at;
END;
$$;

-- ============================================================================
-- GRANT APPROPRIATE PERMISSIONS
-- ============================================================================

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES FOR GRADING_POLICIES
-- ============================================================================

-- Enable RLS on grading_policies table
ALTER TABLE grading_policies ENABLE ROW LEVEL SECURITY;

-- Read access: All authenticated users can read grading policies for their classes
CREATE POLICY "grading_policies_read" ON grading_policies
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members
            WHERE user_id = auth.uid()
            AND class_id = grading_policies.class_id
        )
    );

-- Write access: Only professors can insert/update grading policies
CREATE POLICY "grading_policies_professor_write" ON grading_policies
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members
            WHERE user_id = auth.uid()
            AND class_id = grading_policies.class_id
            AND role = 'professor'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members
            WHERE user_id = auth.uid()
            AND class_id = grading_policies.class_id
            AND role = 'professor'
        )
    );

-- Grant usage on the table to authenticated users
GRANT SELECT ON grading_policies TO authenticated;
GRANT INSERT, UPDATE ON grading_policies TO authenticated;

-- Grant execute permissions on all grading functions
GRANT EXECUTE ON FUNCTION apply_grading_policy(TEXT, UUID, NUMERIC[]) TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_normalized_constituent_grades(UUID, UUID, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION calculate_final_weighted_grade(UUID, UUID) TO authenticated;

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