-- ============================================================================
-- TEMPORARY MIGRATION: Fix Grading System to be Class-Specific
-- ============================================================================
-- 
-- PURPOSE: This is a TEMPORARY file to fix the current database schema
-- to match what the JavaScript expects. Once tested and working, we will:
-- 1. Update the original SQL files (003_grading_system.sql) to reflect the correct schema
-- 2. Delete this temporary file
-- 
-- The original SQL files should represent the intended schema from the beginning,
-- not a series of patches.
-- ============================================================================

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- STEP 1: Add class_id columns to make grading system class-specific
-- ============================================================================

-- Add class_id to modules table (each class has its own modules)
ALTER TABLE modules 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id) ON DELETE CASCADE;

-- Add class_id to constituents table (each class has its own constituents)
ALTER TABLE constituents 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id) ON DELETE CASCADE;

-- Add class_id to items table (each class has its own items)
ALTER TABLE items 
ADD COLUMN IF NOT EXISTS class_id UUID REFERENCES classes(id) ON DELETE CASCADE;

-- ============================================================================
-- STEP 2: Update existing data with class_id
-- Use your current class UUID: df6b6665-d793-445d-8514-f1680ff77369
-- ============================================================================

-- Update all existing modules to belong to your class
UPDATE modules 
SET class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid 
WHERE class_id IS NULL;

-- Update all existing constituents to belong to your class
UPDATE constituents 
SET class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid 
WHERE class_id IS NULL;

-- Update all existing items to belong to your class
UPDATE items 
SET class_id = 'df6b6665-d793-445d-8514-f1680ff77369'::uuid 
WHERE class_id IS NULL;

-- ============================================================================
-- STEP 3: Fix foreign key relationships for JavaScript compatibility
-- ============================================================================

-- Add proper foreign key constraint for item_id in submissions
-- This allows JavaScript to use: items!student_submissions_item_id_fkey
ALTER TABLE student_submissions
DROP CONSTRAINT IF EXISTS student_submissions_item_id_check;

-- First ensure all item_ids in submissions exist in items table
-- (This prevents FK constraint creation from failing)
DELETE FROM student_submissions 
WHERE item_id NOT IN (SELECT id FROM items);

-- Now add the foreign key constraint
-- Note: PostgreSQL doesn't support IF NOT EXISTS for constraints, so check first
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'student_submissions_item_id_fkey'
    ) THEN
        ALTER TABLE student_submissions
        ADD CONSTRAINT student_submissions_item_id_fkey 
        FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE;
    END IF;
END $$;

-- ============================================================================
-- STEP 4: Create performance indexes for class-specific queries
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_modules_class ON modules(class_id);
CREATE INDEX IF NOT EXISTS idx_constituents_class ON constituents(class_id);
CREATE INDEX IF NOT EXISTS idx_items_class ON items(class_id);

-- Composite indexes for common queries
CREATE INDEX IF NOT EXISTS idx_constituents_class_module ON constituents(class_id, module_id);
CREATE INDEX IF NOT EXISTS idx_items_class_constituent ON items(class_id, constituent_slug);

-- ============================================================================
-- STEP 5: Update RLS policies for class-specific access
-- ============================================================================

-- Modules: Only members of the class can see modules
DROP POLICY IF EXISTS "modules_public_read" ON modules;
CREATE POLICY "modules_class_members_read" ON modules
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = modules.class_id
            AND cm.user_id = auth.uid()
        )
    );

-- Constituents: Only members of the class can see constituents
DROP POLICY IF EXISTS "constituents_public_read" ON constituents;
CREATE POLICY "constituents_class_members_read" ON constituents
    FOR SELECT TO authenticated
    USING (
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = constituents.class_id
            AND cm.user_id = auth.uid()
        )
    );

-- Items: Only members of the class can see items
DROP POLICY IF EXISTS "items_public_read" ON items;
CREATE POLICY "items_class_members_read" ON items
    FOR SELECT TO authenticated
    USING (
        is_active = true
        AND
        EXISTS (
            SELECT 1 FROM class_members cm
            WHERE cm.class_id = items.class_id
            AND cm.user_id = auth.uid()
        )
    );

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Check that all tables now have class_id
SELECT 
    'modules' as table_name,
    COUNT(*) as total_rows,
    COUNT(class_id) as rows_with_class_id
FROM modules
UNION ALL
SELECT 
    'constituents' as table_name,
    COUNT(*) as total_rows,
    COUNT(class_id) as rows_with_class_id
FROM constituents
UNION ALL
SELECT 
    'items' as table_name,
    COUNT(*) as total_rows,
    COUNT(class_id) as rows_with_class_id
FROM items;

-- Verify foreign key constraint was added
SELECT conname, contype 
FROM pg_constraint 
WHERE conrelid = 'student_submissions'::regclass 
AND conname LIKE '%item_id%';

-- ============================================================================
-- NOTES
-- ============================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔧 ============================================';
    RAISE NOTICE '✅ TEMPORARY MIGRATION APPLIED!';
    RAISE NOTICE '🔧 ============================================';
    RAISE NOTICE '';
    RAISE NOTICE '📋 Changes Applied:';
    RAISE NOTICE '   • Added class_id to modules, constituents, items';
    RAISE NOTICE '   • Updated existing data with your class UUID';
    RAISE NOTICE '   • Added proper foreign key: item_id → items(id)';
    RAISE NOTICE '   • Updated RLS policies for class isolation';
    RAISE NOTICE '   • Added performance indexes';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 Next Steps:';
    RAISE NOTICE '   1. Test the grading interface';
    RAISE NOTICE '   2. If working, update 003_grading_system.sql permanently';
    RAISE NOTICE '   3. Delete this temporary file';
    RAISE NOTICE '';
    RAISE NOTICE '⚠️  This is a TEMPORARY file - do not keep long-term!';
    RAISE NOTICE '';
END $$;