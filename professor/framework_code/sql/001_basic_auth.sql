-- ============================================================================
-- Basic Authentication Schema for Class Template Framework
-- Version: 1.0
-- Description: Minimal authentication tables without grading complexity
-- ============================================================================

-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- 1. USER PROFILES
-- Links to Supabase auth.users table, stores GitHub profile information
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  github_username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_profiles_github_username ON public.profiles(github_username);

-- ============================================================================
-- 2. CLASSES
-- Each repository/course is a class
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.classes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,  -- e.g., "class_template"
  title TEXT NOT NULL,
  description TEXT,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for slug lookups
CREATE INDEX IF NOT EXISTS idx_classes_slug ON public.classes(slug);

-- ============================================================================
-- 3. CLASS MEMBERS
-- Unified table for both professors and students with role distinction
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.class_members (
  class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  role TEXT NOT NULL CHECK (role IN ('professor', 'student')),
  enrolled_at TIMESTAMPTZ DEFAULT NOW(),
  enrollment_token_id BIGINT,  -- Reference to token used (for students)
  PRIMARY KEY (class_id, user_id)
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_class_members_user ON public.class_members(user_id);
CREATE INDEX IF NOT EXISTS idx_class_members_class ON public.class_members(class_id);
CREATE INDEX IF NOT EXISTS idx_class_members_role ON public.class_members(role);

-- ============================================================================
-- 4. ENROLLMENT TOKENS
-- Tokens for student enrollment
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.enrollment_tokens (
  id BIGSERIAL PRIMARY KEY,
  class_id UUID REFERENCES public.classes(id) ON DELETE CASCADE,
  token_hash TEXT NOT NULL,  -- Store bcrypt hash for security
  expires_at TIMESTAMPTZ NOT NULL,
  max_uses INT DEFAULT 0,  -- 0 = unlimited
  uses INT DEFAULT 0,
  created_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true
);

-- Create index for class lookups
CREATE INDEX IF NOT EXISTS idx_enrollment_tokens_class ON public.enrollment_tokens(class_id);
CREATE INDEX IF NOT EXISTS idx_enrollment_tokens_active ON public.enrollment_tokens(is_active);

-- ============================================================================
-- 5. HELPER FUNCTIONS
-- Utility functions for checking roles
-- ============================================================================

-- Check if user is a professor of a class
CREATE OR REPLACE FUNCTION public.is_professor_of(p_class_id UUID, p_user_id UUID) 
RETURNS BOOLEAN 
LANGUAGE SQL 
STABLE 
SECURITY DEFINER
AS $$
  SELECT EXISTS(
    SELECT 1 FROM public.class_members 
    WHERE class_id = p_class_id 
    AND user_id = p_user_id 
    AND role = 'professor'
  );
$$;

-- Check if user is a student of a class
CREATE OR REPLACE FUNCTION public.is_student_of(p_class_id UUID, p_user_id UUID) 
RETURNS BOOLEAN 
LANGUAGE SQL 
STABLE 
SECURITY DEFINER
AS $$
  SELECT EXISTS(
    SELECT 1 FROM public.class_members 
    WHERE class_id = p_class_id 
    AND user_id = p_user_id 
    AND role = 'student'
  );
$$;

-- Check if user is any member of a class
CREATE OR REPLACE FUNCTION public.is_member_of(p_class_id UUID, p_user_id UUID) 
RETURNS BOOLEAN 
LANGUAGE SQL 
STABLE 
SECURITY DEFINER
AS $$
  SELECT EXISTS(
    SELECT 1 FROM public.class_members 
    WHERE class_id = p_class_id 
    AND user_id = p_user_id
  );
$$;

-- ============================================================================
-- 6. TRIGGERS
-- Automatic profile creation and timestamp updates
-- ============================================================================

-- Function to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user() 
RETURNS TRIGGER 
LANGUAGE PLPGSQL 
SECURITY DEFINER
AS $$
BEGIN
  INSERT INTO public.profiles (user_id, github_username, full_name, avatar_url)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'user_name', NEW.raw_user_meta_data->>'preferred_username'),
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  )
  ON CONFLICT (user_id) DO UPDATE
  SET 
    github_username = EXCLUDED.github_username,
    full_name = EXCLUDED.full_name,
    avatar_url = EXCLUDED.avatar_url,
    updated_at = NOW();
  RETURN NEW;
END;
$$;

-- Create trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- Function to update timestamps
CREATE OR REPLACE FUNCTION public.update_updated_at()
RETURNS TRIGGER
LANGUAGE PLPGSQL
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- Add update triggers
CREATE TRIGGER update_profiles_updated_at 
  BEFORE UPDATE ON public.profiles
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

CREATE TRIGGER update_classes_updated_at 
  BEFORE UPDATE ON public.classes
  FOR EACH ROW EXECUTE FUNCTION public.update_updated_at();

-- ============================================================================
-- 7. ROW LEVEL SECURITY (RLS)
-- Enable RLS but don't create policies yet (for easier testing)
-- ============================================================================

-- Enable RLS on all tables (policies will be added in 002_auth_policies.sql)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.class_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.enrollment_tokens ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- 8. INITIAL TEST DATA
-- Creates the class_template class for development
-- Comment this section out for production
-- ============================================================================

-- Insert test class if it doesn't exist
INSERT INTO public.classes (slug, title, description)
VALUES (
  'class_template', 
  'Class Template Framework', 
  'A framework for creating self-contained class websites with authentication'
)
ON CONFLICT (slug) DO NOTHING;

-- Output confirmation
DO $$
BEGIN
  RAISE NOTICE 'Basic authentication schema created successfully';
  RAISE NOTICE 'Test class "class_template" has been created';
  RAISE NOTICE 'RLS is enabled but no policies are set (for testing)';
  RAISE NOTICE 'Run 002_auth_policies.sql to add security policies';
END $$;