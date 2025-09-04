-- ============================================================================
-- Migration 004: Edge Function Support for Professor Grading
-- Dependencies: 001_basic_auth.sql, 002_auth_policies.sql, 003_grading_system.sql
-- Description: Adds missing database schema elements required by professor-grade-item Edge Function
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SAFETY CHECK: Ensure dependencies are met
-- ============================================================================

DO $$
BEGIN
    -- Check if we have the basic tables
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'classes') THEN
        RAISE EXCEPTION 'Classes table not found. Please run 001_basic_auth.sql first';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'student_submissions') THEN
        RAISE EXCEPTION 'Grading system not found. Please run 003_grading_system.sql first';
    END IF;
    
    RAISE NOTICE '✅ Dependencies verified, proceeding with Edge Function support schema';
END $$;

-- ============================================================================
-- ADD MISSING COLUMNS TO EXISTING TABLES
-- ============================================================================

-- Add missing columns to classes table
ALTER TABLE public.classes 
ADD COLUMN IF NOT EXISTS repo_name TEXT,
ADD COLUMN IF NOT EXISTS professor_github_username TEXT;

-- Add missing column to class_members table  
ALTER TABLE public.class_members
ADD COLUMN IF NOT EXISTS enrollment_status TEXT DEFAULT 'active' CHECK (enrollment_status IN ('active', 'inactive', 'pending'));

-- ============================================================================
-- POPULATE NEW COLUMNS WITH EXISTING DATA
-- ============================================================================

-- Populate repo_name with slug value (they serve the same purpose)
UPDATE public.classes 
SET repo_name = slug 
WHERE repo_name IS NULL;

-- Make repo_name NOT NULL after populating
ALTER TABLE public.classes 
ALTER COLUMN repo_name SET NOT NULL;

-- Set all existing class_members to active status
UPDATE public.class_members 
SET enrollment_status = 'active' 
WHERE enrollment_status IS NULL;

-- ============================================================================
-- CREATE MISSING DATABASE FUNCTIONS
-- ============================================================================

-- Function to verify professor ownership of a class
CREATE OR REPLACE FUNCTION public.verify_professor_ownership(
    p_user_id UUID,
    p_class_id UUID
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- Check if user is a professor of the specified class
    RETURN EXISTS (
        SELECT 1 
        FROM public.class_members cm
        JOIN public.classes c ON cm.class_id = c.id
        WHERE cm.user_id = p_user_id 
        AND cm.class_id = p_class_id
        AND cm.role = 'professor'
        AND cm.enrollment_status = 'active'
        AND c.is_active = true
    );
END;
$$;

-- Function to check rate limits (simplified version for production)
CREATE OR REPLACE FUNCTION public.check_rate_limit(
    p_user_id UUID,
    p_endpoint TEXT,
    p_class_id UUID,
    p_limit INTEGER,
    p_window_minutes INTEGER
)
RETURNS BOOLEAN
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_count INTEGER;
    v_window_start TIMESTAMPTZ;
BEGIN
    -- Calculate window start time
    v_window_start := NOW() - (p_window_minutes || ' minutes')::INTERVAL;
    
    -- For now, we'll implement a simple rate limit check
    -- In production, you might want to create a separate rate_limit_log table
    
    -- Count recent grading operations (simplified - counts all submissions graded)
    SELECT COUNT(*)
    INTO v_count
    FROM public.student_submissions
    WHERE grader_id = p_user_id
    AND class_id = p_class_id
    AND graded_at >= v_window_start;
    
    -- Return true if under limit
    RETURN v_count < p_limit;
END;
$$;

-- Function to log security events (simplified version)
CREATE OR REPLACE FUNCTION public.log_security_event(
    p_user_id UUID,
    p_class_id UUID,
    p_event_type TEXT,
    p_event_details JSONB
)
RETURNS VOID
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    -- For now, just log to PostgreSQL logs
    -- In production, you might want to create a security_events table
    RAISE NOTICE 'Security Event: % - User: % - Class: % - Details: %', 
        p_event_type, p_user_id, p_class_id, p_event_details;
END;
$$;

-- ============================================================================
-- ENSURE PROFESSOR IS PROPERLY ENROLLED
-- ============================================================================

-- Function to ensure a user is set up as a professor for a class
CREATE OR REPLACE FUNCTION public.ensure_professor_enrollment(
    p_github_username TEXT,
    p_class_slug TEXT
)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_user_id UUID;
    v_class_id UUID;
    v_result JSONB;
BEGIN
    -- Find user by GitHub username
    SELECT user_id INTO v_user_id
    FROM public.profiles
    WHERE github_username = p_github_username
    LIMIT 1;
    
    IF v_user_id IS NULL THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'User with GitHub username "' || p_github_username || '" not found'
        );
    END IF;
    
    -- Find class by slug
    SELECT id INTO v_class_id
    FROM public.classes
    WHERE slug = p_class_slug
    LIMIT 1;
    
    IF v_class_id IS NULL THEN
        RETURN jsonb_build_object(
            'success', false,
            'error', 'Class with slug "' || p_class_slug || '" not found'
        );
    END IF;
    
    -- Add professor to class (or update if exists)
    INSERT INTO public.class_members (class_id, user_id, role, enrollment_status)
    VALUES (v_class_id, v_user_id, 'professor', 'active')
    ON CONFLICT (class_id, user_id) DO UPDATE SET
        role = 'professor',
        enrollment_status = 'active',
        enrolled_at = NOW();
    
    -- Update class with professor GitHub username
    UPDATE public.classes
    SET professor_github_username = p_github_username
    WHERE id = v_class_id;
    
    RETURN jsonb_build_object(
        'success', true,
        'user_id', v_user_id,
        'class_id', v_class_id,
        'message', 'Professor enrollment ensured for ' || p_github_username || ' in class ' || p_class_slug
    );
END;
$$;

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Index for repo_name lookups
CREATE INDEX IF NOT EXISTS idx_classes_repo_name ON public.classes(repo_name);

-- Index for enrollment_status
CREATE INDEX IF NOT EXISTS idx_class_members_enrollment_status ON public.class_members(enrollment_status);

-- Index for professor_github_username
CREATE INDEX IF NOT EXISTS idx_classes_professor_github ON public.classes(professor_github_username);

-- ============================================================================
-- SET UP CURRENT CLASS WITH PROFESSOR
-- ============================================================================

DO $$
DECLARE
    v_result JSONB;
BEGIN
    -- Try to set up the current class template with a professor
    -- This will work if there's already a user with a GitHub profile
    SELECT public.ensure_professor_enrollment('uumami', 'class_template') INTO v_result;
    
    -- Log the result
    RAISE NOTICE 'Professor setup result: %', v_result;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not auto-setup professor (this is normal if user hasn''t logged in yet): %', SQLERRM;
END $$;

-- ============================================================================
-- MIGRATION COMPLETION MESSAGE
-- ============================================================================

DO $$
DECLARE
    v_classes_count INTEGER;
    v_members_count INTEGER;
    v_functions_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_classes_count FROM public.classes WHERE repo_name IS NOT NULL;
    SELECT COUNT(*) INTO v_members_count FROM public.class_members WHERE enrollment_status IS NOT NULL;
    
    -- Count new functions
    SELECT COUNT(*) INTO v_functions_count 
    FROM information_schema.routines 
    WHERE routine_schema = 'public' 
    AND routine_name IN ('verify_professor_ownership', 'check_rate_limit', 'log_security_event', 'ensure_professor_enrollment');
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '✅ EDGE FUNCTION SUPPORT MIGRATION 004 COMPLETED!';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database Schema Updated:';
    RAISE NOTICE '   • classes.repo_name added (% rows)', v_classes_count;
    RAISE NOTICE '   • classes.professor_github_username added';
    RAISE NOTICE '   • class_members.enrollment_status added (% rows)', v_members_count;
    RAISE NOTICE '';
    RAISE NOTICE '⚙️  Database Functions Created: %', v_functions_count;
    RAISE NOTICE '   • verify_professor_ownership()';
    RAISE NOTICE '   • check_rate_limit()';
    RAISE NOTICE '   • log_security_event()';
    RAISE NOTICE '   • ensure_professor_enrollment()';
    RAISE NOTICE '';
    RAISE NOTICE '🔒 Security: All functions use SECURITY DEFINER for proper access';
    RAISE NOTICE '📈 Performance: Indexes added for new columns';
    RAISE NOTICE '🎯 Compatibility: Edge Function professor-grade-item should now work';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next Steps:';
    RAISE NOTICE '   1. If auto-setup failed, manually run:';
    RAISE NOTICE '      SELECT ensure_professor_enrollment(''your_github_username'', ''class_template'');';
    RAISE NOTICE '   2. Test grading functionality in the professor interface';
    RAISE NOTICE '';
    RAISE NOTICE '✨ Your grading system is now compatible with the Edge Function!';
    RAISE NOTICE '';
END $$;