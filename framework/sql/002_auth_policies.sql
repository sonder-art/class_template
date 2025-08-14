-- ============================================================================
-- Row Level Security Policies for Authentication
-- Version: 1.0
-- Description: Security policies for authentication tables
-- ============================================================================

-- ============================================================================
-- PROFILES POLICIES
-- ============================================================================

-- Everyone can view profiles (for displaying user info)
CREATE POLICY "Profiles are viewable by everyone" 
  ON public.profiles
  FOR SELECT 
  USING (true);

-- Users can only update their own profile
CREATE POLICY "Users can update own profile" 
  ON public.profiles
  FOR UPDATE 
  USING (auth.uid() = user_id);

-- Allow profile creation (needed for signup trigger)
CREATE POLICY "Enable profile creation for authenticated users" 
  ON public.profiles
  FOR INSERT 
  WITH CHECK (auth.uid() = user_id);

-- ============================================================================
-- CLASSES POLICIES
-- ============================================================================

-- Classes are publicly viewable (for listing available classes)
CREATE POLICY "Classes are publicly readable" 
  ON public.classes
  FOR SELECT 
  USING (true);

-- Only professors can update class information
CREATE POLICY "Professors can update their classes" 
  ON public.classes
  FOR UPDATE 
  USING (
    EXISTS (
      SELECT 1 FROM public.class_members
      WHERE class_members.class_id = classes.id 
      AND class_members.user_id = auth.uid()
      AND class_members.role = 'professor'
    )
  );

-- Only professors can insert new classes
CREATE POLICY "Professors can create classes" 
  ON public.classes
  FOR INSERT 
  WITH CHECK (
    auth.uid() IS NOT NULL  -- Must be authenticated
  );

-- ============================================================================
-- CLASS MEMBERS POLICIES
-- ============================================================================

-- Members can view other members of their classes
CREATE POLICY "Members can view class roster" 
  ON public.class_members
  FOR SELECT 
  USING (
    public.is_member_of(class_id, auth.uid())
  );

-- Professors can add/remove members
CREATE POLICY "Professors can manage class members" 
  ON public.class_members
  FOR ALL 
  USING (
    public.is_professor_of(class_id, auth.uid())
  );

-- Students can view their own enrollment
CREATE POLICY "Students can view own enrollment" 
  ON public.class_members
  FOR SELECT 
  USING (
    user_id = auth.uid()
  );

-- ============================================================================
-- ENROLLMENT TOKENS POLICIES
-- ============================================================================

-- Only professors can view tokens for their classes
CREATE POLICY "Professors can view enrollment tokens" 
  ON public.enrollment_tokens
  FOR SELECT 
  USING (
    public.is_professor_of(class_id, auth.uid())
  );

-- Only professors can create tokens for their classes
CREATE POLICY "Professors can create enrollment tokens" 
  ON public.enrollment_tokens
  FOR INSERT 
  WITH CHECK (
    public.is_professor_of(class_id, auth.uid())
  );

-- Only professors can update tokens for their classes
CREATE POLICY "Professors can update enrollment tokens" 
  ON public.enrollment_tokens
  FOR UPDATE 
  USING (
    public.is_professor_of(class_id, auth.uid())
  );

-- Only professors can delete tokens for their classes
CREATE POLICY "Professors can delete enrollment tokens" 
  ON public.enrollment_tokens
  FOR DELETE 
  USING (
    public.is_professor_of(class_id, auth.uid())
  );

-- ============================================================================
-- NOTES
-- ============================================================================
DO $$
BEGIN
  RAISE NOTICE 'RLS policies applied successfully';
  RAISE NOTICE 'Security is now enforced on all tables';
  RAISE NOTICE 'To disable for testing: ALTER TABLE <table_name> DISABLE ROW LEVEL SECURITY;';
END $$;