-- ============================================================================
-- Migration 006: Professor INSERT Policies for Grading Data
-- Description: Adds INSERT and UPDATE policies for professors to manage grading data
-- ============================================================================

-- Enable RLS (should already be enabled)
ALTER TABLE modules ENABLE ROW LEVEL SECURITY;
ALTER TABLE constituents ENABLE ROW LEVEL SECURITY;
ALTER TABLE items ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- MODULES: Professor INSERT/UPDATE policies
-- ============================================================================

-- Allow professors to insert modules for their classes
CREATE POLICY "modules_professor_insert" ON modules
    FOR INSERT TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = modules.class_id
            AND role = 'professor'
        )
    );

-- Allow professors to update modules for their classes  
CREATE POLICY "modules_professor_update" ON modules
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = modules.class_id 
            AND role = 'professor'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = modules.class_id
            AND role = 'professor'
        )
    );

-- ============================================================================
-- CONSTITUENTS: Professor INSERT/UPDATE policies  
-- ============================================================================

-- Allow professors to insert constituents for their classes
CREATE POLICY "constituents_professor_insert" ON constituents
    FOR INSERT TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = constituents.class_id
            AND role = 'professor'
        )
    );

-- Allow professors to update constituents for their classes
CREATE POLICY "constituents_professor_update" ON constituents
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = constituents.class_id
            AND role = 'professor'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = constituents.class_id
            AND role = 'professor'
        )
    );

-- ============================================================================
-- ITEMS: Professor INSERT/UPDATE policies
-- ============================================================================

-- Allow professors to insert items for their classes
CREATE POLICY "items_professor_insert" ON items
    FOR INSERT TO authenticated
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = items.class_id
            AND role = 'professor'
        )
    );

-- Allow professors to update items for their classes
CREATE POLICY "items_professor_update" ON items
    FOR UPDATE TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = items.class_id
            AND role = 'professor'
        )
    )
    WITH CHECK (
        EXISTS (
            SELECT 1 FROM class_members 
            WHERE user_id = auth.uid() 
            AND class_id = items.class_id
            AND role = 'professor'
        )
    );

-- ============================================================================
-- VERIFICATION: Check that policies were created successfully
-- ============================================================================

DO $$
BEGIN
    -- Verify module policies
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'modules' 
        AND policyname = 'modules_professor_insert'
    ) THEN
        RAISE EXCEPTION 'Failed to create modules_professor_insert policy';
    END IF;
    
    -- Verify constituent policies
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'constituents' 
        AND policyname = 'constituents_professor_insert'
    ) THEN
        RAISE EXCEPTION 'Failed to create constituents_professor_insert policy';
    END IF;
    
    -- Verify item policies
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies 
        WHERE tablename = 'items' 
        AND policyname = 'items_professor_insert'
    ) THEN
        RAISE EXCEPTION 'Failed to create items_professor_insert policy';
    END IF;
    
    RAISE NOTICE '✅ All professor INSERT/UPDATE policies created successfully';
END $$;