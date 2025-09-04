-- ============================================================================
-- Migration 005: Grade Persistence Across Submission Versions
-- Dependencies: 003_grading_system.sql, 004_grading_edge_function_support.sql
-- Description: Implements grade persistence - grades remain constant across submission versions
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
        RAISE EXCEPTION 'Grading system not found. Please run 003_grading_system.sql first';
    END IF;
    
    RAISE NOTICE '✅ Dependencies verified, proceeding with grade persistence schema';
END $$;

-- ============================================================================
-- ADD GRADE PERSISTENCE COLUMNS
-- ============================================================================

-- Add columns to track which attempt was graded and version status
ALTER TABLE public.student_submissions 
ADD COLUMN IF NOT EXISTS graded_attempt_number INTEGER,
ADD COLUMN IF NOT EXISTS has_newer_version BOOLEAN DEFAULT FALSE;

-- ============================================================================
-- CREATE GRADE INHERITANCE FUNCTION
-- ============================================================================

-- Function to get the effective grade for a student's item (from any version)
CREATE OR REPLACE FUNCTION public.get_effective_grade(
    p_student_id UUID,
    p_item_id TEXT,
    p_class_id UUID
)
RETURNS TABLE (
    effective_raw_score NUMERIC,
    effective_adjusted_score NUMERIC,
    effective_feedback TEXT,
    effective_graded_at TIMESTAMPTZ,
    effective_grader_id UUID,
    graded_attempt_number INTEGER,
    latest_attempt_number INTEGER,
    has_newer_version BOOLEAN
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $$
DECLARE
    v_graded_submission RECORD;
    v_latest_attempt INTEGER;
BEGIN
    -- Get the latest attempt number for this item
    SELECT COALESCE(MAX(attempt_number), 1)
    INTO v_latest_attempt
    FROM public.student_submissions
    WHERE student_id = p_student_id
    AND item_id = p_item_id
    AND class_id = p_class_id;
    
    -- Find the most recent graded submission for this student/item
    SELECT raw_score, adjusted_score, feedback, graded_at, grader_id, attempt_number
    INTO v_graded_submission
    FROM public.student_submissions
    WHERE student_id = p_student_id
    AND item_id = p_item_id
    AND class_id = p_class_id
    AND graded_at IS NOT NULL
    ORDER BY graded_at DESC, attempt_number DESC
    LIMIT 1;
    
    -- Return the effective grade information
    RETURN QUERY SELECT 
        v_graded_submission.raw_score,
        v_graded_submission.adjusted_score,
        v_graded_submission.feedback,
        v_graded_submission.graded_at,
        v_graded_submission.grader_id,
        v_graded_submission.attempt_number,
        v_latest_attempt,
        (v_latest_attempt > COALESCE(v_graded_submission.attempt_number, 0));
END;
$$;

-- ============================================================================
-- CREATE GRADE PERSISTENCE TRIGGER
-- ============================================================================

-- Function to maintain grade persistence when new submissions are added
CREATE OR REPLACE FUNCTION public.maintain_grade_persistence()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_effective_grade RECORD;
BEGIN
    -- Only process INSERT operations for new submissions
    IF TG_OP = 'INSERT' THEN
        -- Check if this is a new attempt (not the first one)
        IF NEW.attempt_number > 1 THEN
            -- Get the effective grade from previous attempts
            SELECT * INTO v_effective_grade
            FROM public.get_effective_grade(NEW.student_id, NEW.item_id, NEW.class_id);
            
            -- If there's an existing grade, inherit it
            IF v_effective_grade.effective_graded_at IS NOT NULL THEN
                NEW.raw_score := v_effective_grade.effective_raw_score;
                NEW.adjusted_score := v_effective_grade.effective_adjusted_score;
                NEW.feedback := v_effective_grade.effective_feedback;
                NEW.graded_at := v_effective_grade.effective_graded_at;
                NEW.grader_id := v_effective_grade.effective_grader_id;
                NEW.graded_attempt_number := v_effective_grade.graded_attempt_number;
                NEW.has_newer_version := FALSE; -- This IS the newer version
            END IF;
        END IF;
        
        -- Mark all previous attempts as having newer versions
        UPDATE public.student_submissions
        SET has_newer_version = TRUE
        WHERE student_id = NEW.student_id
        AND item_id = NEW.item_id
        AND class_id = NEW.class_id
        AND attempt_number < NEW.attempt_number;
        
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$;

-- Create the trigger
DROP TRIGGER IF EXISTS trigger_grade_persistence ON public.student_submissions;
CREATE TRIGGER trigger_grade_persistence
    BEFORE INSERT ON public.student_submissions
    FOR EACH ROW
    EXECUTE FUNCTION public.maintain_grade_persistence();

-- ============================================================================
-- UPDATE EXISTING DATA
-- ============================================================================

-- Populate graded_attempt_number for existing graded submissions
UPDATE public.student_submissions
SET graded_attempt_number = attempt_number
WHERE graded_at IS NOT NULL
AND graded_attempt_number IS NULL;

-- Update has_newer_version flags for existing data
DO $$
DECLARE
    submission_record RECORD;
    max_attempt INTEGER;
BEGIN
    -- For each unique student/item combination
    FOR submission_record IN 
        SELECT DISTINCT student_id, item_id, class_id
        FROM public.student_submissions
    LOOP
        -- Find the maximum attempt number
        SELECT MAX(attempt_number) INTO max_attempt
        FROM public.student_submissions
        WHERE student_id = submission_record.student_id
        AND item_id = submission_record.item_id
        AND class_id = submission_record.class_id;
        
        -- Mark all non-latest attempts as having newer versions
        IF max_attempt > 1 THEN
            UPDATE public.student_submissions
            SET has_newer_version = TRUE
            WHERE student_id = submission_record.student_id
            AND item_id = submission_record.item_id
            AND class_id = submission_record.class_id
            AND attempt_number < max_attempt;
        END IF;
    END LOOP;
END $$;

-- ============================================================================
-- CREATE VIEW FOR EFFECTIVE GRADES
-- ============================================================================

-- Create a view that shows the "effective" state of all submissions
CREATE OR REPLACE VIEW public.effective_submissions AS
SELECT 
    s.*,
    eg.effective_raw_score,
    eg.effective_adjusted_score,
    eg.effective_feedback,
    eg.effective_graded_at,
    eg.effective_grader_id,
    eg.graded_attempt_number as effective_graded_attempt,
    eg.has_newer_version as effective_has_newer_version,
    -- Determine if this is the latest attempt
    (s.attempt_number = eg.latest_attempt_number) as is_latest_attempt,
    -- Determine the effective graded status
    (eg.effective_graded_at IS NOT NULL) as is_effectively_graded
FROM public.student_submissions s
CROSS JOIN LATERAL public.get_effective_grade(s.student_id, s.item_id, s.class_id) eg;

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for graded_attempt_number lookups
CREATE INDEX IF NOT EXISTS idx_submissions_graded_attempt 
ON public.student_submissions(student_id, item_id, graded_attempt_number);

-- Index for has_newer_version flag
CREATE INDEX IF NOT EXISTS idx_submissions_newer_version 
ON public.student_submissions(has_newer_version) WHERE has_newer_version = TRUE;

-- ============================================================================
-- HELPER FUNCTIONS FOR FRONTEND
-- ============================================================================

-- Function to get latest submissions with effective grades
CREATE OR REPLACE FUNCTION public.get_latest_submissions_with_grades(p_class_id UUID)
RETURNS TABLE (
    id UUID,
    student_id UUID,
    item_id TEXT,
    class_id UUID,
    attempt_number INTEGER,
    submission_data JSONB,
    submitted_at TIMESTAMPTZ,
    -- Effective grade fields
    raw_score NUMERIC,
    adjusted_score NUMERIC,
    feedback TEXT,
    graded_at TIMESTAMPTZ,
    grader_id UUID,
    -- Version tracking fields
    graded_attempt_number INTEGER,
    has_newer_version BOOLEAN,
    is_latest_attempt BOOLEAN
)
LANGUAGE plpgsql
STABLE
SECURITY DEFINER
AS $$
BEGIN
    RETURN QUERY
    WITH latest_attempts AS (
        -- Get only the latest attempt for each student/item
        SELECT DISTINCT ON (student_id, item_id) *
        FROM public.student_submissions
        WHERE class_id = p_class_id
        ORDER BY student_id, item_id, attempt_number DESC
    )
    SELECT 
        la.id,
        la.student_id,
        la.item_id,
        la.class_id,
        la.attempt_number,
        la.submission_data,
        la.submitted_at,
        -- Use effective grades
        eg.effective_raw_score,
        eg.effective_adjusted_score,
        eg.effective_feedback,
        eg.effective_graded_at,
        eg.effective_grader_id,
        eg.graded_attempt_number,
        eg.has_newer_version,
        TRUE as is_latest_attempt
    FROM latest_attempts la
    CROSS JOIN LATERAL public.get_effective_grade(la.student_id, la.item_id, la.class_id) eg;
END;
$$;

-- ============================================================================
-- MIGRATION COMPLETION MESSAGE
-- ============================================================================

DO $$
DECLARE
    v_submissions_count INTEGER;
    v_graded_count INTEGER;
    v_newer_versions_count INTEGER;
    v_functions_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_submissions_count FROM public.student_submissions;
    SELECT COUNT(*) INTO v_graded_count FROM public.student_submissions WHERE graded_at IS NOT NULL;
    SELECT COUNT(*) INTO v_newer_versions_count FROM public.student_submissions WHERE has_newer_version = TRUE;
    
    -- Count new functions and views
    SELECT COUNT(*) INTO v_functions_count 
    FROM information_schema.routines 
    WHERE routine_schema = 'public' 
    AND routine_name IN ('get_effective_grade', 'maintain_grade_persistence', 'get_latest_submissions_with_grades');
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '✅ GRADE PERSISTENCE MIGRATION 005 COMPLETED!';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database Schema Updated:';
    RAISE NOTICE '   • Total submissions: %', v_submissions_count;
    RAISE NOTICE '   • Graded submissions: %', v_graded_count;
    RAISE NOTICE '   • Submissions with newer versions: %', v_newer_versions_count;
    RAISE NOTICE '';
    RAISE NOTICE '⚙️  New Database Functions: %', v_functions_count;
    RAISE NOTICE '   • get_effective_grade() - Gets inherited grades';
    RAISE NOTICE '   • maintain_grade_persistence() - Auto-inherits grades';
    RAISE NOTICE '   • get_latest_submissions_with_grades() - Frontend helper';
    RAISE NOTICE '';
    RAISE NOTICE '🔄 New Features:';
    RAISE NOTICE '   • Grades persist across submission versions';
    RAISE NOTICE '   • Automatic grade inheritance for new attempts';
    RAISE NOTICE '   • Version tracking with has_newer_version flag';
    RAISE NOTICE '   • Effective grades view for simplified queries';
    RAISE NOTICE '';
    RAISE NOTICE '🎯 Frontend Integration:';
    RAISE NOTICE '   • Use get_latest_submissions_with_grades() function';
    RAISE NOTICE '   • Check has_newer_version flag for UI indicators';
    RAISE NOTICE '   • Display effective grades regardless of version';
    RAISE NOTICE '';
    RAISE NOTICE '✨ Grade persistence is now active across all submission versions!';
    RAISE NOTICE '';
END $$;