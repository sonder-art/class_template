-- Migration 003: Advanced Grading System
-- This creates the database schema for the markdown-driven homework system
-- with complex algorithmic grading support

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- MODULES AND CONSTITUENTS TABLES
-- ============================================================================

-- Modules: High-level course components
CREATE TABLE IF NOT EXISTS modules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    order_index INTEGER NOT NULL,
    color TEXT,
    icon TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Constituents: Grading components within modules  
CREATE TABLE IF NOT EXISTS constituents (
    id TEXT PRIMARY KEY,
    slug TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    description TEXT,
    module_id TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    weight NUMERIC(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    type TEXT NOT NULL,
    max_attempts INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index for fast lookups by slug
CREATE INDEX IF NOT EXISTS idx_constituents_slug ON constituents(slug);
CREATE INDEX IF NOT EXISTS idx_constituents_module ON constituents(module_id);

-- ============================================================================
-- HOMEWORK ITEMS AND SUBMISSIONS
-- ============================================================================

-- Homework items: Individual graded items defined in markdown files
CREATE TABLE IF NOT EXISTS homework_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    item_id TEXT NOT NULL, -- From markdown: item_id field
    constituent_slug TEXT NOT NULL REFERENCES constituents(slug),
    title TEXT NOT NULL,
    file_path TEXT NOT NULL, -- Path to the markdown file
    points NUMERIC(6,2) NOT NULL CHECK (points > 0),
    due_date TIMESTAMP WITH TIME ZONE,
    submission_type TEXT NOT NULL, -- url, file, code_and_demo, etc.
    instructions TEXT,
    grading_criteria JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure uniqueness per constituent
    UNIQUE(constituent_slug, item_id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_homework_items_constituent ON homework_items(constituent_slug);
CREATE INDEX IF NOT EXISTS idx_homework_items_due_date ON homework_items(due_date);
CREATE INDEX IF NOT EXISTS idx_homework_items_file_path ON homework_items(file_path);

-- Student submissions
CREATE TABLE IF NOT EXISTS student_submissions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES profiles(id),
    item_id UUID NOT NULL REFERENCES homework_items(id),
    class_id UUID NOT NULL, -- From class_members table
    attempt_number INTEGER NOT NULL DEFAULT 1,
    submission_data JSONB NOT NULL, -- URLs, file paths, etc.
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    graded_at TIMESTAMP WITH TIME ZONE,
    raw_score NUMERIC(6,2), -- Before any adjustments
    adjusted_score NUMERIC(6,2), -- After penalties/bonuses
    feedback TEXT,
    grader_id UUID REFERENCES profiles(id),
    
    UNIQUE(student_id, item_id, attempt_number),
    CHECK (raw_score >= 0),
    CHECK (adjusted_score >= 0)
);

-- Indexes for student submissions
CREATE INDEX IF NOT EXISTS idx_submissions_student ON student_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_item ON student_submissions(item_id);
CREATE INDEX IF NOT EXISTS idx_submissions_class ON student_submissions(class_id);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted_at ON student_submissions(submitted_at);

-- ============================================================================
-- GRADE COMPUTATION AND CACHING
-- ============================================================================

-- Materialized view for student submission statistics (performance optimization)
CREATE MATERIALIZED VIEW IF NOT EXISTS student_submission_stats AS
SELECT 
    s.student_id,
    s.class_id,
    hi.constituent_slug,
    c.module_id,
    COUNT(*) as attempt_count,
    MAX(s.submitted_at) as last_submission,
    MAX(s.adjusted_score) as best_score,
    AVG(s.adjusted_score) as avg_score,
    SUM(CASE WHEN s.submitted_at <= hi.due_date THEN 1 ELSE 0 END) as on_time_count,
    COUNT(DISTINCT hi.id) as total_items
FROM student_submissions s
JOIN homework_items hi ON s.item_id = hi.id  
JOIN constituents c ON hi.constituent_slug = c.slug
GROUP BY s.student_id, s.class_id, hi.constituent_slug, c.module_id;

-- Index for the materialized view
CREATE UNIQUE INDEX IF NOT EXISTS idx_submission_stats_pk 
ON student_submission_stats(student_id, class_id, constituent_slug);

-- Computed grades cache table
CREATE TABLE IF NOT EXISTS student_grades_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID NOT NULL REFERENCES profiles(id),
    class_id UUID NOT NULL,
    module_id TEXT REFERENCES modules(id),
    constituent_slug TEXT REFERENCES constituents(slug),
    item_id UUID REFERENCES homework_items(id),
    
    -- Grade level (module, constituent, or item)
    grade_level TEXT NOT NULL CHECK (grade_level IN ('module', 'constituent', 'item')),
    
    -- Computed grade data
    final_score NUMERIC(6,2),
    base_score NUMERIC(6,2),
    adjustments JSONB, -- Bonuses, penalties, multipliers
    letter_grade TEXT,
    
    -- Metadata
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    policy_version TEXT,
    dependencies_hash TEXT, -- For cache invalidation
    
    -- Ensure one record per student per graded entity
    UNIQUE(student_id, class_id, grade_level, COALESCE(module_id, ''), COALESCE(constituent_slug, ''), COALESCE(item_id::text, ''))
);

-- Indexes for grades cache
CREATE INDEX IF NOT EXISTS idx_grades_cache_student ON student_grades_cache(student_id);
CREATE INDEX IF NOT EXISTS idx_grades_cache_class ON student_grades_cache(class_id);
CREATE INDEX IF NOT EXISTS idx_grades_cache_level ON student_grades_cache(grade_level);
CREATE INDEX IF NOT EXISTS idx_grades_cache_computed_at ON student_grades_cache(computed_at);

-- ============================================================================
-- GRADING POLICIES METADATA
-- ============================================================================

-- Store grading policy metadata and version info
CREATE TABLE IF NOT EXISTS grading_policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    module_id TEXT NOT NULL REFERENCES modules(id),
    policy_name TEXT NOT NULL,
    version TEXT NOT NULL,
    policy_data JSONB NOT NULL, -- Full YAML policy as JSON
    sql_function_name TEXT, -- Generated SQL function name
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    UNIQUE(module_id, version)
);

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE constituents ENABLE ROW LEVEL SECURITY;
ALTER TABLE homework_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_grades_cache ENABLE ROW LEVEL SECURITY;
ALTER TABLE grading_policies ENABLE ROW LEVEL SECURITY;

-- Modules: Readable by all authenticated users
CREATE POLICY "modules_select_authenticated" ON modules
    FOR SELECT TO authenticated
    USING (true);

-- Constituents: Readable by all authenticated users  
CREATE POLICY "constituents_select_authenticated" ON constituents
    FOR SELECT TO authenticated
    USING (true);

-- Homework items: Readable by class members
CREATE POLICY "homework_items_select_class_members" ON homework_items
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.user_id = auth.uid()
        )
    );

-- Student submissions: Students can only see their own, professors can see all in their classes
CREATE POLICY "submissions_select_own_or_professor" ON student_submissions
    FOR SELECT TO authenticated
    USING (
        student_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- Student submissions: Students can insert their own submissions
CREATE POLICY "submissions_insert_own" ON student_submissions
    FOR INSERT TO authenticated
    WITH CHECK (
        student_id = auth.uid() AND
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'student'
        )
    );

-- Student submissions: Professors can update grades and feedback
CREATE POLICY "submissions_update_professor" ON student_submissions
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- Grades cache: Students can see their own grades, professors can see all
CREATE POLICY "grades_cache_select_own_or_professor" ON student_grades_cache
    FOR SELECT TO authenticated
    USING (
        student_id = auth.uid() OR
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_grades_cache.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- Grading policies: Only professors can read/write
CREATE POLICY "grading_policies_professor_only" ON grading_policies
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to refresh submission stats materialized view
CREATE OR REPLACE FUNCTION refresh_submission_stats()
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY student_submission_stats;
END;
$$;

-- Function to invalidate grades cache for a student
CREATE OR REPLACE FUNCTION invalidate_student_grades_cache(target_student_id UUID, target_class_id UUID)
RETURNS void
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    DELETE FROM student_grades_cache 
    WHERE student_id = target_student_id 
    AND class_id = target_class_id;
END;
$$;

-- Trigger to refresh stats when submissions change
CREATE OR REPLACE FUNCTION trigger_refresh_submission_stats()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    -- Refresh stats asynchronously (in production, consider pg_cron)
    PERFORM refresh_submission_stats();
    
    -- Invalidate affected student's grade cache
    PERFORM invalidate_student_grades_cache(
        COALESCE(NEW.student_id, OLD.student_id),
        COALESCE(NEW.class_id, OLD.class_id)
    );
    
    RETURN COALESCE(NEW, OLD);
END;
$$;

-- Create trigger on student_submissions
DROP TRIGGER IF EXISTS trigger_submission_stats_refresh ON student_submissions;
CREATE TRIGGER trigger_submission_stats_refresh
    AFTER INSERT OR UPDATE OR DELETE ON student_submissions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_refresh_submission_stats();

-- ============================================================================
-- EXAMPLE GRADE COMPUTATION FUNCTION (Template)
-- ============================================================================

-- This is a template function that would be generated from grading policies
-- Real functions will be generated from the YAML policy files
CREATE OR REPLACE FUNCTION calculate_sample_module_grade(
    target_student_id UUID,
    target_module_id TEXT,
    calculation_date TIMESTAMP DEFAULT NOW()
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    result JSONB;
    base_score NUMERIC(6,2);
    final_score NUMERIC(6,2);
BEGIN
    -- Example calculation (would be generated from policy YAML)
    SELECT AVG(sgc.final_score) INTO base_score
    FROM student_grades_cache sgc
    WHERE sgc.student_id = target_student_id
    AND sgc.module_id = target_module_id
    AND sgc.grade_level = 'constituent';
    
    final_score := COALESCE(base_score, 0);
    
    -- Build result JSON
    result := jsonb_build_object(
        'final_score', final_score,
        'base_score', base_score,
        'grade_letter', CASE 
            WHEN final_score >= 95 THEN 'A'
            WHEN final_score >= 90 THEN 'A-'
            WHEN final_score >= 87 THEN 'B+'
            WHEN final_score >= 83 THEN 'B'
            WHEN final_score >= 80 THEN 'B-'
            WHEN final_score >= 77 THEN 'C+'
            WHEN final_score >= 73 THEN 'C'
            WHEN final_score >= 70 THEN 'C-'
            WHEN final_score >= 67 THEN 'D+'
            WHEN final_score >= 63 THEN 'D'
            WHEN final_score >= 60 THEN 'D-'
            ELSE 'F'
        END,
        'calculated_at', calculation_date,
        'breakdown', jsonb_build_object(
            'constituent_count', (
                SELECT COUNT(*)
                FROM constituents c
                WHERE c.module_id = target_module_id
            )
        )
    );
    
    RETURN result;
END;
$$;