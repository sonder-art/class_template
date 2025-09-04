-- ============================================================================
-- Migration 003: Complete Grading System
-- Dependencies: 001_basic_auth.sql, 002_auth_policies.sql
-- Description: Creates the complete grading system with correct terminology
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- SAFETY CHECK: Ensure dependencies are met
-- ============================================================================

DO $$
BEGIN
    -- Check if we have the basic auth tables
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'profiles') THEN
        RAISE EXCEPTION 'Basic auth schema not found. Please run 001_basic_auth.sql first';
    END IF;
    
    IF NOT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'classes') THEN
        RAISE EXCEPTION 'Classes table not found. Please run 001_basic_auth.sql first';
    END IF;
    
    RAISE NOTICE '✅ Dependencies verified, proceeding with grading system';
END $$;

-- ============================================================================
-- MODULES AND CONSTITUENTS TABLES 
-- Grading hierarchy: modules > constituents > items > submissions
-- ============================================================================

-- Modules: High-level course components (e.g., "Authentication", "Databases")
CREATE TABLE IF NOT EXISTS modules (
    id TEXT PRIMARY KEY,  -- e.g., "auth-module"
    name TEXT NOT NULL,   -- e.g., "Authentication Module" 
    description TEXT,
    weight NUMERIC(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    order_index INTEGER NOT NULL,
    color TEXT,
    icon TEXT,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    is_current BOOLEAN DEFAULT true,  -- File-based activation: true if defined in current YAML files
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance  
CREATE INDEX IF NOT EXISTS idx_modules_current ON modules(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_modules_class_current ON modules(class_id, is_current);

-- Constituents: Grading components within modules (e.g., "Homework", "Projects")  
CREATE TABLE IF NOT EXISTS constituents (
    id TEXT PRIMARY KEY,          -- e.g., "auth-homework"
    slug TEXT NOT NULL UNIQUE,    -- e.g., "auth-setup" (matches markdown shortcodes)
    name TEXT NOT NULL,           -- e.g., "Authentication Setup"
    description TEXT,
    module_id TEXT NOT NULL REFERENCES modules(id) ON DELETE CASCADE,
    weight NUMERIC(5,2) NOT NULL CHECK (weight >= 0 AND weight <= 100),
    type TEXT NOT NULL,           -- e.g., "homework", "project", "exam"
    max_attempts INTEGER DEFAULT 3,
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    is_current BOOLEAN DEFAULT true,  -- File-based activation: true if defined in current YAML files
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_constituents_slug ON constituents(slug);
CREATE INDEX IF NOT EXISTS idx_constituents_module ON constituents(module_id);
CREATE INDEX IF NOT EXISTS idx_constituents_current ON constituents(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_constituents_class_current ON constituents(class_id, is_current);

-- ============================================================================
-- ITEMS TABLE (Individual graded items)
-- These correspond to {{< item-inline constituent_slug="auth-setup" item_id="github_oauth" >}}
-- ============================================================================

-- Items: Individual graded components defined in markdown files
CREATE TABLE IF NOT EXISTS items (
    id TEXT PRIMARY KEY,                    -- e.g., "github_oauth_setup" (from markdown)
    constituent_slug TEXT NOT NULL REFERENCES constituents(slug),  -- Links to constituent
    title TEXT NOT NULL,                    -- Human-readable title
    file_path TEXT,                         -- Path to markdown file (optional)
    points NUMERIC(6,2) NOT NULL CHECK (points > 0),
    due_date TIMESTAMPTZ,
    delivery_type TEXT NOT NULL CHECK (delivery_type IN ('text', 'url', 'file', 'upload', 'code')),
    instructions TEXT,
    grading_criteria JSONB,
    is_active BOOLEAN DEFAULT true,         -- General active/inactive flag
    is_current BOOLEAN DEFAULT true,        -- File-based activation: true if defined in current markdown files
    class_id UUID REFERENCES classes(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Ensure uniqueness: one item_id per constituent
    UNIQUE(constituent_slug, id)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_items_constituent ON items(constituent_slug);
CREATE INDEX IF NOT EXISTS idx_items_due_date ON items(due_date);
CREATE INDEX IF NOT EXISTS idx_items_active ON items(is_active);
CREATE INDEX IF NOT EXISTS idx_items_current ON items(is_current) WHERE is_current = true;
CREATE INDEX IF NOT EXISTS idx_items_class_current ON items(class_id, is_current);

-- ============================================================================
-- STUDENT SUBMISSIONS TABLE
-- Stores actual student submissions - designed for JavaScript compatibility
-- ============================================================================

-- Student submissions: What students actually submit
CREATE TABLE IF NOT EXISTS student_submissions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- WHO submitted
    student_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- WHAT they submitted for  
    item_id TEXT NOT NULL,  -- String reference to items.id (matches JavaScript expectations!)
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    
    -- SUBMISSION details
    attempt_number INTEGER NOT NULL DEFAULT 1,
    submission_data JSONB NOT NULL, -- {type: "url", url: "...", description: "..."}
    
    -- TIMING
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- GRADING (initially null, filled by professor)
    graded_at TIMESTAMPTZ,
    raw_score NUMERIC(6,2),        -- Points earned before adjustments
    adjusted_score NUMERIC(6,2),   -- Final points after bonuses/penalties  
    feedback TEXT,
    grader_id UUID REFERENCES auth.users(id),
    
    -- CONSTRAINTS
    UNIQUE(student_id, item_id, attempt_number),  -- One attempt per student per item
    CHECK (raw_score >= 0),
    CHECK (adjusted_score >= 0),
    CHECK (attempt_number > 0)
);

-- Indexes for performance (optimized for JavaScript queries)
CREATE INDEX IF NOT EXISTS idx_submissions_student ON student_submissions(student_id);
CREATE INDEX IF NOT EXISTS idx_submissions_item ON student_submissions(item_id);  -- JavaScript needs this!
CREATE INDEX IF NOT EXISTS idx_submissions_class ON student_submissions(class_id);
CREATE INDEX IF NOT EXISTS idx_submissions_submitted ON student_submissions(submitted_at);
CREATE INDEX IF NOT EXISTS idx_submissions_student_item ON student_submissions(student_id, item_id);  -- For loading existing submissions

-- ============================================================================
-- GRADING ADJUSTMENTS (Manual professor overrides)
-- ============================================================================

-- Manual adjustments by professors (bonuses, penalties, manual grades)
CREATE TABLE IF NOT EXISTS grading_adjustments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    item_id TEXT NOT NULL,  -- References items.id
    class_id UUID NOT NULL REFERENCES classes(id) ON DELETE CASCADE,
    professor_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    adjustment_type TEXT NOT NULL CHECK (adjustment_type IN ('manual_grade', 'bonus', 'penalty', 'extension')),
    points NUMERIC(6,2) NOT NULL,
    reason TEXT NOT NULL,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- One adjustment per type per student per item
    UNIQUE(student_id, item_id, adjustment_type)
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_adjustments_student ON grading_adjustments(student_id);
CREATE INDEX IF NOT EXISTS idx_adjustments_item ON grading_adjustments(item_id);
CREATE INDEX IF NOT EXISTS idx_adjustments_professor ON grading_adjustments(professor_id);

-- ============================================================================
-- ROW LEVEL SECURITY POLICIES
-- ============================================================================

-- Enable RLS on all new tables
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE constituents ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;
ALTER TABLE student_submissions ENABLE ROW LEVEL SECURITY;
ALTER TABLE grading_adjustments ENABLE ROW LEVEL SECURITY;

-- MODULES: Public read (for grade calculations)
CREATE POLICY "modules_public_read" ON modules
    FOR SELECT TO authenticated
    USING (true);

-- CONSTITUENTS: Public read (for grade calculations)  
CREATE POLICY "constituents_public_read" ON constituents
    FOR SELECT TO authenticated
    USING (true);

-- ITEMS: Public read (students need to see what they can submit)
CREATE POLICY "items_public_read" ON items
    FOR SELECT TO authenticated
    USING (is_active = true);

-- STUDENT SUBMISSIONS: Students see own, professors see all in their classes
CREATE POLICY "submissions_read_own_or_professor" ON student_submissions
    FOR SELECT TO authenticated
    USING (
        -- Students can see their own submissions
        student_id = auth.uid() 
        OR 
        -- Professors can see all submissions in their classes
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- STUDENT SUBMISSIONS: Students can insert their own (if they're enrolled)
CREATE POLICY "submissions_insert_student" ON student_submissions
    FOR INSERT TO authenticated
    WITH CHECK (
        student_id = auth.uid() 
        AND 
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'student'
        )
    );

-- STUDENT SUBMISSIONS: Professors can update (for grading)
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

-- GRADING ADJUSTMENTS: Only professors can manage
CREATE POLICY "adjustments_professor_only" ON grading_adjustments
    FOR ALL TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = grading_adjustments.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Function to get class_id from class slug (useful for JavaScript/Edge Functions)
CREATE OR REPLACE FUNCTION get_class_id_by_slug(p_slug TEXT)
RETURNS UUID
LANGUAGE SQL
STABLE
SECURITY DEFINER
AS $$
    SELECT id FROM classes WHERE slug = p_slug LIMIT 1;
$$;

-- Function to initialize a class with professor and sample data
CREATE OR REPLACE FUNCTION initialize_class(
    p_class_slug TEXT,
    p_class_title TEXT,
    p_professor_github TEXT
)
RETURNS JSON
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_class_id UUID;
    v_professor_id UUID;
    result JSON;
BEGIN
    -- Get or create class
    INSERT INTO classes (slug, title, description)
    VALUES (p_class_slug, p_class_title, 'Initialized by grading system')
    ON CONFLICT (slug) DO UPDATE SET 
        title = EXCLUDED.title,
        description = EXCLUDED.description,
        updated_at = NOW()
    RETURNING id INTO v_class_id;
    
    -- Find professor by GitHub username
    SELECT user_id INTO v_professor_id
    FROM profiles 
    WHERE github_username = p_professor_github
    LIMIT 1;
    
    IF v_professor_id IS NULL THEN
        RETURN json_build_object(
            'success', false,
            'error', format('Professor with GitHub username "%s" not found. Make sure they have logged in at least once.', p_professor_github)
        );
    END IF;
    
    -- Add professor to class (ignore if already exists)
    INSERT INTO class_members (class_id, user_id, role)
    VALUES (v_class_id, v_professor_id, 'professor')
    ON CONFLICT (class_id, user_id) DO NOTHING;
    
    -- Return success result
    result := json_build_object(
        'success', true,
        'class_id', v_class_id,
        'professor_id', v_professor_id,
        'class_slug', p_class_slug,
        'professor_github', p_professor_github,
        'message', format('Class "%s" initialized successfully with professor %s', p_class_title, p_professor_github)
    );
    
    RETURN result;
    
EXCEPTION WHEN OTHERS THEN
    RETURN json_build_object(
        'success', false,
        'error', SQLERRM,
        'message', 'Failed to initialize class due to database error'
    );
END;
$$;

-- ============================================================================
-- SAMPLE DATA FOR FRAMEWORK TESTING
-- These match the actual items in the class template framework
-- ============================================================================

-- Insert sample module (Authentication)
INSERT INTO modules (id, name, description, weight, order_index, color, icon)
VALUES ('auth-module', 'Authentication Module', 'Learning authentication systems and security', 25.0, 1, '#4f46e5', '🔐')
ON CONFLICT (id) DO NOTHING;

-- Insert sample constituents (homework assignments)
INSERT INTO constituents (id, slug, name, description, module_id, weight, type, max_attempts)
VALUES 
('auth-setup-homework', 'auth-setup', 'Authentication Setup', 'Setting up authentication systems', 'auth-module', 60.0, 'homework', 3),
('auth-integration-homework', 'auth-integration', 'Authentication Integration', 'Integrating auth with applications', 'auth-module', 40.0, 'homework', 3)
ON CONFLICT (id) DO NOTHING;

-- Insert sample items (these match the actual shortcodes in the framework markdown)
INSERT INTO items (id, constituent_slug, title, points, delivery_type, instructions)
VALUES 
('supabase_project_setup', 'auth-setup', 'Supabase Project Setup', 25.0, 'url', 'Create a Supabase project and provide the URL to your project dashboard'),
('github_oauth_setup', 'auth-setup', 'GitHub OAuth Setup', 25.0, 'upload', 'Configure GitHub OAuth in your Supabase project and upload configuration screenshots'),
('edge_functions_deployment', 'auth-integration', 'Edge Functions Deployment', 30.0, 'code', 'Deploy Edge Functions for authentication and provide your implementation code'),
('comprehensive_auth_testing', 'auth-integration', 'Comprehensive Auth Testing', 20.0, 'text', 'Test your complete authentication system and write a comprehensive testing report')
ON CONFLICT (constituent_slug, id) DO NOTHING;

-- ============================================================================
-- MIGRATION COMPLETION MESSAGE
-- ============================================================================

DO $$
DECLARE
    v_modules_count INTEGER;
    v_constituents_count INTEGER;
    v_items_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO v_modules_count FROM modules;
    SELECT COUNT(*) INTO v_constituents_count FROM constituents;
    SELECT COUNT(*) INTO v_items_count FROM items;
    
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '✅ GRADING SYSTEM MIGRATION 003 COMPLETED!';
    RAISE NOTICE '🎉 ============================================';
    RAISE NOTICE '';
    RAISE NOTICE '📊 Database Schema Created:';
    RAISE NOTICE '   • modules (% rows)', v_modules_count;
    RAISE NOTICE '   • constituents (% rows)', v_constituents_count; 
    RAISE NOTICE '   • items (% rows) - STRING item_id for JavaScript!', v_items_count;
    RAISE NOTICE '   • student_submissions - Ready for submissions!';
    RAISE NOTICE '   • grading_adjustments - Ready for professor grading!';
    RAISE NOTICE '';
    RAISE NOTICE '🔒 Security: RLS policies configured for public deployment';
    RAISE NOTICE '🎯 JavaScript: Compatible field names and data types';
    RAISE NOTICE '📝 Terminology: Uses "items" consistently (not homework_items)';
    RAISE NOTICE '🏗️  Framework: Matches Hugo shortcode structure perfectly';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next Steps:';
    RAISE NOTICE '   1. Run: SELECT initialize_class(''class_template'', ''Class Template Framework'', ''your_github_username'');';
    RAISE NOTICE '   2. Test submission interfaces at: /class_notes/.../01_homework_auth_setup/';
    RAISE NOTICE '   3. Deploy Edge Functions for backend grading API';
    RAISE NOTICE '';
    RAISE NOTICE '✨ Your grading system is ready for production!';
    RAISE NOTICE '';
END $$;