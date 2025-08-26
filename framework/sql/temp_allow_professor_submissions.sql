-- ============================================================================
-- TEMPORARY: Allow professors to submit items for testing
-- ============================================================================
-- 
-- This allows professors to test the submission functionality
-- In production, you may want to remove this or restrict it further
-- ============================================================================

-- Add policy to allow professors to insert submissions (for testing)
CREATE POLICY "submissions_insert_professor_testing" ON student_submissions
    FOR INSERT TO authenticated
    WITH CHECK (
        student_id = auth.uid() 
        AND 
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = student_submissions.class_id
            AND cm.user_id = auth.uid()
            AND cm.role = 'professor'
        )
    );

-- Verification query
SELECT policyname, cmd, qual, with_check 
FROM pg_policies 
WHERE tablename = 'student_submissions';