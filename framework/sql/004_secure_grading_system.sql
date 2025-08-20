-- Migration 004: Secure Grading System
-- This migration enhances the grading system with proper security for public deployment
-- Fixes RLS policies, adds class isolation, and implements security audit trail

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- CLASS CONTEXT AND SECURITY TABLES
-- ============================================================================

-- Classes table for proper class isolation
CREATE TABLE IF NOT EXISTS classes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    repo_name TEXT UNIQUE NOT NULL,
    class_name TEXT NOT NULL,
    professor_github_id TEXT NOT NULL,
    professor_github_username TEXT NOT NULL, -- For easier lookup
    supabase_project_ref TEXT, -- If using separate projects
    start_date TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    end_date TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ensure professor can only own one class per repo
    UNIQUE(repo_name, professor_github_id)
);

-- Add indexes for performance
CREATE INDEX IF NOT EXISTS idx_classes_repo_name ON classes(repo_name);
CREATE INDEX IF NOT EXISTS idx_classes_professor ON classes(professor_github_id);
CREATE INDEX IF NOT EXISTS idx_classes_active ON classes(is_active) WHERE is_active = true;

-- Security audit log table
CREATE TABLE IF NOT EXISTS security_audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id),
    class_id UUID REFERENCES classes(id),
    event_type TEXT NOT NULL,
    event_details JSONB,
    ip_address INET,
    user_agent TEXT,
    endpoint TEXT,
    request_data JSONB,
    response_status INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for security log
CREATE INDEX IF NOT EXISTS idx_security_audit_user ON security_audit_log(user_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_class ON security_audit_log(class_id);
CREATE INDEX IF NOT EXISTS idx_security_audit_event ON security_audit_log(event_type);
CREATE INDEX IF NOT EXISTS idx_security_audit_time ON security_audit_log(created_at);

-- API rate limiting table
CREATE TABLE IF NOT EXISTS api_rate_limits (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES profiles(id),
    endpoint TEXT NOT NULL,
    class_id UUID REFERENCES classes(id),
    calls_count INTEGER DEFAULT 1,
    window_start TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Composite key for rate limiting windows
    UNIQUE(user_id, endpoint, class_id, window_start)
);

-- Add indexes for rate limiting
CREATE INDEX IF NOT EXISTS idx_rate_limits_window ON api_rate_limits(user_id, endpoint, window_start);
CREATE INDEX IF NOT EXISTS idx_rate_limits_cleanup ON api_rate_limits(created_at) WHERE created_at < NOW() - interval '1 day';

-- ============================================================================
-- ENHANCE EXISTING TABLES FOR SECURITY
-- ============================================================================

-- COMPATIBILITY NOTE: Add class_id columns but make them nullable for backward compatibility
-- Existing data will have NULL class_id, which means "global" or "legacy" 

-- Add class_id to homework_items if not exists (nullable for backward compatibility)
ALTER TABLE homework_items 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id);

-- Add security tracking columns to existing tables
ALTER TABLE modules 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS sync_version INTEGER DEFAULT 1;

ALTER TABLE constituents 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id),
ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT true,
ADD COLUMN IF NOT EXISTS sync_version INTEGER DEFAULT 1;

ALTER TABLE homework_items 
ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS item_type TEXT DEFAULT 'markdown',
ADD COLUMN IF NOT EXISTS sync_version INTEGER DEFAULT 1;

-- COMPATIBILITY: Update existing data to set defaults
-- Set all existing records to active and version 1 if not already set
UPDATE modules SET is_active = true WHERE is_active IS NULL;
UPDATE modules SET sync_version = 1 WHERE sync_version IS NULL;

UPDATE constituents SET is_active = true WHERE is_active IS NULL;
UPDATE constituents SET sync_version = 1 WHERE sync_version IS NULL;

UPDATE homework_items SET is_archived = false WHERE is_archived IS NULL;
UPDATE homework_items SET item_type = 'markdown' WHERE item_type IS NULL;
UPDATE homework_items SET sync_version = 1 WHERE sync_version IS NULL;

-- Add security columns to submissions
ALTER TABLE student_submissions
ADD COLUMN IF NOT EXISTS security_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS submission_hash TEXT, -- For integrity verification
ADD COLUMN IF NOT EXISTS client_ip INET,
ADD COLUMN IF NOT EXISTS user_agent TEXT;

ALTER TABLE student_grades_cache
ADD COLUMN IF NOT EXISTS calculation_verified BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS last_security_check TIMESTAMP WITH TIME ZONE;

-- Add indexes for new security columns
CREATE INDEX IF NOT EXISTS idx_homework_items_class ON homework_items(class_id) WHERE class_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_modules_class ON modules(class_id) WHERE class_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_constituents_class ON constituents(class_id) WHERE class_id IS NOT NULL;

-- ============================================================================
-- SECURITY FUNCTIONS
-- ============================================================================

-- Function to verify professor ownership of a class
CREATE OR REPLACE FUNCTION verify_professor_ownership(
    p_user_id UUID,
    p_class_id UUID
) RETURNS BOOLEAN AS $$
DECLARE
    user_github_username TEXT;
    class_professor_username TEXT;
BEGIN
    -- Get user's GitHub username from auth.users metadata
    SELECT raw_user_meta_data->>'user_name' INTO user_github_username
    FROM auth.users 
    WHERE id = p_user_id;
    
    -- Get class professor's GitHub username
    SELECT professor_github_username INTO class_professor_username
    FROM classes 
    WHERE id = p_class_id AND is_active = true;
    
    -- Return true if they match
    RETURN user_github_username = class_professor_username;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log security events
CREATE OR REPLACE FUNCTION log_security_event(
    p_user_id UUID,
    p_class_id UUID DEFAULT NULL,
    p_event_type TEXT DEFAULT 'unknown',
    p_event_details JSONB DEFAULT '{}',
    p_ip_address INET DEFAULT NULL,
    p_user_agent TEXT DEFAULT NULL,
    p_endpoint TEXT DEFAULT NULL,
    p_request_data JSONB DEFAULT '{}',
    p_response_status INTEGER DEFAULT NULL
) RETURNS VOID AS $$
BEGIN
    INSERT INTO security_audit_log (
        user_id, class_id, event_type, event_details,
        ip_address, user_agent, endpoint, request_data, response_status
    ) VALUES (
        p_user_id, p_class_id, p_event_type, p_event_details,
        p_ip_address, p_user_agent, p_endpoint, p_request_data, p_response_status
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check rate limits
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_user_id UUID,
    p_endpoint TEXT,
    p_class_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 100,
    p_window_minutes INTEGER DEFAULT 60
) RETURNS BOOLEAN AS $$
DECLARE
    current_count INTEGER;
    window_start TIMESTAMP WITH TIME ZONE;
BEGIN
    -- Calculate window start time
    window_start := date_trunc('hour', NOW()) + 
                   (EXTRACT(minute FROM NOW())::integer / p_window_minutes) * 
                   (p_window_minutes || ' minutes')::interval;
    
    -- Get or create rate limit entry
    INSERT INTO api_rate_limits (user_id, endpoint, class_id, window_start)
    VALUES (p_user_id, p_endpoint, p_class_id, window_start)
    ON CONFLICT (user_id, endpoint, class_id, window_start)
    DO UPDATE SET 
        calls_count = api_rate_limits.calls_count + 1,
        created_at = NOW()
    RETURNING calls_count INTO current_count;
    
    -- Return true if under limit
    RETURN current_count <= p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to clean up old rate limit and audit data
CREATE OR REPLACE FUNCTION cleanup_security_tables()
RETURNS VOID AS $$
BEGIN
    -- Clean up rate limits older than 24 hours
    DELETE FROM api_rate_limits 
    WHERE created_at < NOW() - interval '24 hours';
    
    -- Clean up audit logs older than 90 days (adjust as needed)
    DELETE FROM security_audit_log 
    WHERE created_at < NOW() - interval '90 days';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- ENHANCED ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Drop existing policies that are insecure
DROP POLICY IF EXISTS "modules_select_authenticated" ON modules;
DROP POLICY IF EXISTS "constituents_select_authenticated" ON constituents;
DROP POLICY IF EXISTS "homework_items_select_class_members" ON homework_items;
DROP POLICY IF EXISTS "submissions_select_own_or_professor" ON student_submissions;
DROP POLICY IF EXISTS "submissions_insert_own" ON student_submissions;
DROP POLICY IF EXISTS "submissions_update_professor" ON student_submissions;
DROP POLICY IF EXISTS "grades_cache_select_own_or_professor" ON student_grades_cache;
DROP POLICY IF EXISTS "grading_policies_professor_only" ON grading_policies;

-- Classes table policies
CREATE POLICY "classes_select_members" ON classes
    FOR SELECT TO authenticated
    USING (
        -- Only class members can see class info
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = classes.id
            AND cm.user_id = auth.uid()
            AND cm.enrollment_status = 'active'
        )
    );

-- Modules: Only visible to class members OR legacy data (NULL class_id)
CREATE POLICY "modules_select_class_members" ON modules
    FOR SELECT TO authenticated
    USING (
        -- Legacy data (NULL class_id) is visible to all authenticated users
        class_id IS NULL OR 
        -- New data requires class membership
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = modules.class_id
            AND cm.user_id = auth.uid()
            AND cm.enrollment_status = 'active'
        )
    );

-- Constituents: Only visible to class members OR legacy data (NULL class_id)
CREATE POLICY "constituents_select_class_members" ON constituents
    FOR SELECT TO authenticated
    USING (
        -- Legacy data (NULL class_id) is visible to all authenticated users
        class_id IS NULL OR 
        -- New data requires class membership
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = constituents.class_id
            AND cm.user_id = auth.uid()
            AND cm.enrollment_status = 'active'
        )
    );

-- Homework items: Only visible to class members OR legacy data (NULL class_id)
CREATE POLICY "homework_items_select_class_members" ON homework_items
    FOR SELECT TO authenticated
    USING (
        -- Legacy data (NULL class_id) is visible to all authenticated users
        class_id IS NULL OR
        -- New data requires class membership
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = homework_items.class_id
            AND cm.user_id = auth.uid()
            AND cm.enrollment_status = 'active'
        )
    );

-- Student submissions: Students see only their own, professors see all in their classes
CREATE POLICY "submissions_select_secure" ON student_submissions
    FOR SELECT TO authenticated
    USING (
        -- Students can see their own submissions
        (student_id = auth.uid() AND
         EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'student'
            AND cm.enrollment_status = 'active'
         )) 
        OR
        -- Professors can see all submissions in classes they own
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
            AND cm.enrollment_status = 'active'
            AND verify_professor_ownership(auth.uid(), cm.class_id)
        )
    );

-- Student submissions: Students can insert their own submissions only
CREATE POLICY "submissions_insert_secure" ON student_submissions
    FOR INSERT TO authenticated
    WITH CHECK (
        student_id = auth.uid() AND
        -- Must be enrolled as active student in this class
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'student'
            AND cm.enrollment_status = 'active'
        ) AND
        -- Class must be active
        EXISTS (
            SELECT 1 FROM classes c
            WHERE c.id = student_submissions.class_id
            AND c.is_active = true
            AND (c.end_date IS NULL OR c.end_date > NOW())
        ) AND
        -- Homework item must exist and belong to this class
        EXISTS (
            SELECT 1 FROM homework_items hi
            WHERE hi.id = student_submissions.item_id
            AND hi.class_id = student_submissions.class_id
            AND hi.is_archived = false
        )
    );

-- Student submissions: Only professors who own the class can update grades
CREATE POLICY "submissions_update_professor_owner" ON student_submissions
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
            AND cm.enrollment_status = 'active'
            AND verify_professor_ownership(auth.uid(), cm.class_id)
        )
    )
    WITH CHECK (
        -- Prevent students from being changed to different classes
        student_id = (SELECT student_id FROM student_submissions WHERE id = student_submissions.id) AND
        class_id = (SELECT class_id FROM student_submissions WHERE id = student_submissions.id)
    );

-- Grades cache: Students see their own, professors see all in owned classes
CREATE POLICY "grades_cache_select_secure" ON student_grades_cache
    FOR SELECT TO authenticated
    USING (
        -- Students see their own grades
        (student_id = auth.uid() AND
         EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_grades_cache.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'student'
            AND cm.enrollment_status = 'active'
         ))
        OR
        -- Professors see all grades in classes they own
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_grades_cache.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
            AND cm.enrollment_status = 'active'
            AND verify_professor_ownership(auth.uid(), cm.class_id)
        )
    );

-- Grading policies: Only professors who own the class
CREATE POLICY "grading_policies_professor_owner" ON grading_policies
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM modules m
            JOIN class_members cm ON cm.class_id = m.class_id
            WHERE m.id = grading_policies.module_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
            AND cm.enrollment_status = 'active'
            AND verify_professor_ownership(auth.uid(), cm.class_id)
        )
    );

-- Security audit log: Only accessible to the user themselves and system
CREATE POLICY "audit_log_own_records" ON security_audit_log
    FOR SELECT TO authenticated
    USING (user_id = auth.uid());

-- Rate limits: Only accessible to the user themselves
CREATE POLICY "rate_limits_own_records" ON api_rate_limits
    FOR SELECT TO authenticated
    USING (user_id = auth.uid());

-- ============================================================================
-- SECURITY TRIGGERS
-- ============================================================================

-- Trigger to log submission activities
CREATE OR REPLACE FUNCTION trigger_log_submission_activity()
RETURNS TRIGGER AS $$
BEGIN
    -- Log insertion
    IF TG_OP = 'INSERT' THEN
        PERFORM log_security_event(
            NEW.student_id,
            NEW.class_id,
            'submission_created',
            jsonb_build_object(
                'item_id', NEW.item_id,
                'attempt_number', NEW.attempt_number,
                'submission_type', (SELECT submission_type FROM homework_items WHERE id = NEW.item_id)
            )
        );
        RETURN NEW;
    END IF;
    
    -- Log updates (grading)
    IF TG_OP = 'UPDATE' THEN
        -- If score changed, log who graded
        IF (OLD.raw_score IS DISTINCT FROM NEW.raw_score) OR 
           (OLD.adjusted_score IS DISTINCT FROM NEW.adjusted_score) THEN
            PERFORM log_security_event(
                NEW.grader_id,
                NEW.class_id,
                'submission_graded',
                jsonb_build_object(
                    'student_id', NEW.student_id,
                    'item_id', NEW.item_id,
                    'old_score', OLD.raw_score,
                    'new_score', NEW.raw_score,
                    'feedback_provided', NEW.feedback IS NOT NULL
                )
            );
        END IF;
        RETURN NEW;
    END IF;
    
    RETURN NULL;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for submission logging
DROP TRIGGER IF EXISTS trigger_submission_audit ON student_submissions;
CREATE TRIGGER trigger_submission_audit
    AFTER INSERT OR UPDATE ON student_submissions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_log_submission_activity();

-- Trigger to verify submission integrity
CREATE OR REPLACE FUNCTION trigger_verify_submission_integrity()
RETURNS TRIGGER AS $$
BEGIN
    -- Generate hash for submission data
    NEW.submission_hash := encode(digest(NEW.submission_data::text, 'sha256'), 'hex');
    
    -- Mark as security verified (will be updated by edge function)
    NEW.security_verified := false;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for submission integrity
DROP TRIGGER IF EXISTS trigger_submission_integrity ON student_submissions;
CREATE TRIGGER trigger_submission_integrity
    BEFORE INSERT OR UPDATE ON student_submissions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_verify_submission_integrity();

-- ============================================================================
-- PERFORMANCE AND MAINTENANCE
-- ============================================================================

-- Create scheduled job to clean up security tables (requires pg_cron extension)
-- This would typically be set up as a cron job or scheduled function

-- For Supabase, you would create a scheduled edge function to call this
CREATE OR REPLACE FUNCTION scheduled_security_cleanup()
RETURNS VOID AS $$
BEGIN
    PERFORM cleanup_security_tables();
    
    -- Log cleanup activity
    INSERT INTO security_audit_log (
        user_id, event_type, event_details
    ) VALUES (
        NULL, 'system_cleanup', 
        jsonb_build_object('cleaned_at', NOW())
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- INITIAL DATA SETUP HELPER
-- ============================================================================

-- Function to initialize a class (called during framework setup)
CREATE OR REPLACE FUNCTION initialize_class(
    p_repo_name TEXT,
    p_class_name TEXT,
    p_professor_github_id TEXT,
    p_professor_github_username TEXT
) RETURNS UUID AS $$
DECLARE
    class_id UUID;
    professor_user_id UUID;
BEGIN
    -- Insert or update class
    INSERT INTO classes (repo_name, class_name, professor_github_id, professor_github_username)
    VALUES (p_repo_name, p_class_name, p_professor_github_id, p_professor_github_username)
    ON CONFLICT (repo_name, professor_github_id)
    DO UPDATE SET 
        class_name = EXCLUDED.class_name,
        professor_github_username = EXCLUDED.professor_github_username,
        updated_at = NOW()
    RETURNING id INTO class_id;
    
    -- Find professor's user ID
    SELECT id INTO professor_user_id
    FROM auth.users
    WHERE raw_user_meta_data->>'user_name' = p_professor_github_username;
    
    -- If professor exists, ensure they have class membership
    IF professor_user_id IS NOT NULL THEN
        INSERT INTO class_members (user_id, class_id, role, enrollment_status)
        VALUES (professor_user_id, class_id, 'professor', 'active')
        ON CONFLICT (user_id, class_id)
        DO UPDATE SET 
            role = 'professor',
            enrollment_status = 'active',
            updated_at = NOW();
    END IF;
    
    -- Log class initialization
    PERFORM log_security_event(
        professor_user_id,
        class_id,
        'class_initialized',
        jsonb_build_object(
            'repo_name', p_repo_name,
            'class_name', p_class_name
        )
    );
    
    RETURN class_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant necessary permissions to authenticated users
GRANT SELECT ON classes TO authenticated;
GRANT SELECT ON security_audit_log TO authenticated;
GRANT SELECT ON api_rate_limits TO authenticated;

-- Grant execution permissions on security functions
GRANT EXECUTE ON FUNCTION verify_professor_ownership TO authenticated;
GRANT EXECUTE ON FUNCTION log_security_event TO service_role;
GRANT EXECUTE ON FUNCTION check_rate_limit TO service_role;
GRANT EXECUTE ON FUNCTION initialize_class TO service_role;