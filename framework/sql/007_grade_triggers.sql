-- ============================================================================
-- Grade Calculation Triggers
-- Automatically recalculate grades when submissions or grading data changes
-- ============================================================================

-- Create a table to queue grade calculations (for optimization)
CREATE TABLE IF NOT EXISTS grade_calculation_queue (
    student_id UUID NOT NULL,
    class_id UUID NOT NULL,
    requested_at TIMESTAMPTZ DEFAULT NOW(),
    processed_at TIMESTAMPTZ,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'error')),
    PRIMARY KEY (student_id, class_id)
);

-- Index for performance
CREATE INDEX IF NOT EXISTS idx_grade_queue_pending ON grade_calculation_queue(status, requested_at) 
WHERE status = 'pending';

-- ============================================================================
-- TRIGGER FUNCTIONS
-- ============================================================================

-- Main trigger function for automatic grade recalculation
CREATE OR REPLACE FUNCTION trigger_grade_recalculation()
RETURNS TRIGGER AS $$
BEGIN
    -- Log the calculation request
    INSERT INTO grade_calculation_queue (student_id, class_id, requested_at)
    VALUES (NEW.student_id, NEW.class_id, NOW())
    ON CONFLICT (student_id, class_id) 
    DO UPDATE SET 
        requested_at = NOW(),
        status = 'pending';
    
    -- For immediate UI responsiveness, we could trigger calculations here
    -- But for production, it's better to process these in a background job
    
    -- Optional: Immediate calculation (can be resource intensive)
    BEGIN
        -- Mark as processing
        UPDATE grade_calculation_queue 
        SET status = 'processing', processed_at = NOW()
        WHERE student_id = NEW.student_id AND class_id = NEW.class_id;
        
        -- Perform calculations (these functions are optimized and fast)
        PERFORM calculate_module_grades(NEW.student_id, NEW.class_id);
        PERFORM calculate_grade_summary(NEW.student_id, NEW.class_id);
        
        -- Mark as completed
        UPDATE grade_calculation_queue 
        SET status = 'completed', processed_at = NOW()
        WHERE student_id = NEW.student_id AND class_id = NEW.class_id;
        
        RAISE NOTICE 'Grades recalculated for student % in class %', NEW.student_id, NEW.class_id;
        
    EXCEPTION WHEN OTHERS THEN
        -- Mark as error but don't fail the original operation
        UPDATE grade_calculation_queue 
        SET status = 'error', processed_at = NOW()
        WHERE student_id = NEW.student_id AND class_id = NEW.class_id;
        
        RAISE WARNING 'Grade calculation failed for student % in class %: %', 
            NEW.student_id, NEW.class_id, SQLERRM;
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger function specifically for grading adjustments
CREATE OR REPLACE FUNCTION trigger_grade_adjustment_recalculation()
RETURNS TRIGGER AS $$
BEGIN
    -- Similar to above but handles grading_adjustments table
    INSERT INTO grade_calculation_queue (student_id, class_id, requested_at)
    VALUES (NEW.student_id, NEW.class_id, NOW())
    ON CONFLICT (student_id, class_id) 
    DO UPDATE SET 
        requested_at = NOW(),
        status = 'pending';
        
    -- Immediate calculation for adjustments (these are typically manual and infrequent)
    BEGIN
        PERFORM calculate_module_grades(NEW.student_id, NEW.class_id);
        PERFORM calculate_grade_summary(NEW.student_id, NEW.class_id);
        
        UPDATE grade_calculation_queue 
        SET status = 'completed', processed_at = NOW()
        WHERE student_id = NEW.student_id AND class_id = NEW.class_id;
        
    EXCEPTION WHEN OTHERS THEN
        UPDATE grade_calculation_queue 
        SET status = 'error', processed_at = NOW()
        WHERE student_id = NEW.student_id AND class_id = NEW.class_id;
        
        RAISE WARNING 'Grade calculation failed for adjustment % in class %: %', 
            NEW.student_id, NEW.class_id, SQLERRM;
    END;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CREATE TRIGGERS
-- ============================================================================

-- Drop existing triggers if they exist
DROP TRIGGER IF EXISTS recalculate_grades_on_submission ON student_submissions;
DROP TRIGGER IF EXISTS recalculate_grades_on_grading ON student_submissions;
DROP TRIGGER IF EXISTS recalculate_grades_on_adjustment ON grading_adjustments;

-- Trigger on new submission
CREATE TRIGGER recalculate_grades_on_submission
    AFTER INSERT ON student_submissions
    FOR EACH ROW
    EXECUTE FUNCTION trigger_grade_recalculation();

-- Trigger on grade update (when professor grades)
CREATE TRIGGER recalculate_grades_on_grading  
    AFTER UPDATE ON student_submissions
    FOR EACH ROW
    WHEN (
        -- Only trigger when scores actually change
        OLD.adjusted_score IS DISTINCT FROM NEW.adjusted_score OR
        OLD.raw_score IS DISTINCT FROM NEW.raw_score
    )
    EXECUTE FUNCTION trigger_grade_recalculation();

-- Trigger on grading adjustments (manual professor adjustments)
CREATE TRIGGER recalculate_grades_on_adjustment
    AFTER INSERT OR UPDATE ON grading_adjustments
    FOR EACH ROW
    EXECUTE FUNCTION trigger_grade_adjustment_recalculation();

-- ============================================================================
-- BACKGROUND PROCESSING FUNCTION (Optional - for batch processing)
-- ============================================================================

-- Function to process grade calculation queue in batches
CREATE OR REPLACE FUNCTION process_grade_calculation_queue(batch_size INTEGER DEFAULT 10)
RETURNS INTEGER AS $$
DECLARE
    processed_count INTEGER := 0;
    queue_record RECORD;
BEGIN
    -- Process pending calculations in batches
    FOR queue_record IN 
        SELECT student_id, class_id 
        FROM grade_calculation_queue 
        WHERE status = 'pending'
        ORDER BY requested_at 
        LIMIT batch_size
    LOOP
        BEGIN
            -- Mark as processing
            UPDATE grade_calculation_queue 
            SET status = 'processing', processed_at = NOW()
            WHERE student_id = queue_record.student_id AND class_id = queue_record.class_id;
            
            -- Perform calculations
            PERFORM calculate_module_grades(queue_record.student_id, queue_record.class_id);
            PERFORM calculate_grade_summary(queue_record.student_id, queue_record.class_id);
            
            -- Mark as completed
            UPDATE grade_calculation_queue 
            SET status = 'completed'
            WHERE student_id = queue_record.student_id AND class_id = queue_record.class_id;
            
            processed_count := processed_count + 1;
            
        EXCEPTION WHEN OTHERS THEN
            -- Mark as error
            UPDATE grade_calculation_queue 
            SET status = 'error'
            WHERE student_id = queue_record.student_id AND class_id = queue_record.class_id;
            
            RAISE WARNING 'Batch grade calculation failed for student % in class %: %', 
                queue_record.student_id, queue_record.class_id, SQLERRM;
        END;
    END LOOP;
    
    RETURN processed_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- UTILITY FUNCTIONS
-- ============================================================================

-- Function to manually trigger grade recalculation for a specific student
CREATE OR REPLACE FUNCTION recalculate_student_grades(
    p_student_id UUID,
    p_class_id UUID
) RETURNS BOOLEAN AS $$
BEGIN
    -- Add to queue
    INSERT INTO grade_calculation_queue (student_id, class_id, requested_at)
    VALUES (p_student_id, p_class_id, NOW())
    ON CONFLICT (student_id, class_id) 
    DO UPDATE SET 
        requested_at = NOW(),
        status = 'pending';
    
    -- Immediate calculation
    BEGIN
        UPDATE grade_calculation_queue 
        SET status = 'processing', processed_at = NOW()
        WHERE student_id = p_student_id AND class_id = p_class_id;
        
        PERFORM calculate_module_grades(p_student_id, p_class_id);
        PERFORM calculate_grade_summary(p_student_id, p_class_id);
        
        UPDATE grade_calculation_queue 
        SET status = 'completed'
        WHERE student_id = p_student_id AND class_id = p_class_id;
        
        RETURN TRUE;
        
    EXCEPTION WHEN OTHERS THEN
        UPDATE grade_calculation_queue 
        SET status = 'error'
        WHERE student_id = p_student_id AND class_id = p_class_id;
        
        RAISE WARNING 'Manual grade calculation failed: %', SQLERRM;
        RETURN FALSE;
    END;
END;
$$ LANGUAGE plpgsql;

-- Function to recalculate grades for entire class
CREATE OR REPLACE FUNCTION recalculate_class_grades(p_class_id UUID)
RETURNS INTEGER AS $$
DECLARE
    student_record RECORD;
    success_count INTEGER := 0;
BEGIN
    -- Get all students in the class
    FOR student_record IN 
        SELECT DISTINCT user_id 
        FROM class_members 
        WHERE class_id = p_class_id 
          AND role = 'student' 
          AND enrollment_status = 'active'
    LOOP
        IF recalculate_student_grades(student_record.user_id, p_class_id) THEN
            success_count := success_count + 1;
        END IF;
    END LOOP;
    
    RETURN success_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- CLEANUP FUNCTION
-- ============================================================================

-- Function to clean up old queue entries (run periodically)
CREATE OR REPLACE FUNCTION cleanup_grade_calculation_queue(retention_days INTEGER DEFAULT 7)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM grade_calculation_queue 
    WHERE processed_at < NOW() - INTERVAL '1 day' * retention_days
      AND status IN ('completed', 'error');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- PERMISSIONS
-- ============================================================================

-- Grant necessary permissions for Edge Functions
GRANT SELECT, INSERT, UPDATE ON grade_calculation_queue TO anon, authenticated;
GRANT EXECUTE ON FUNCTION trigger_grade_recalculation() TO anon, authenticated;
GRANT EXECUTE ON FUNCTION trigger_grade_adjustment_recalculation() TO anon, authenticated;
GRANT EXECUTE ON FUNCTION recalculate_student_grades(UUID, UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION recalculate_class_grades(UUID) TO authenticated;
GRANT EXECUTE ON FUNCTION process_grade_calculation_queue(INTEGER) TO authenticated;
GRANT EXECUTE ON FUNCTION cleanup_grade_calculation_queue(INTEGER) TO authenticated;

-- ============================================================================
-- INITIAL SETUP COMPLETE
-- ============================================================================

-- Log successful installation
DO $$
BEGIN
    RAISE NOTICE '✅ Grade calculation triggers installed successfully';
    RAISE NOTICE '📊 Triggers will fire on: student_submissions (INSERT/UPDATE), grading_adjustments (INSERT/UPDATE)';
    RAISE NOTICE '🔧 Use recalculate_student_grades(student_id, class_id) for manual calculations';
    RAISE NOTICE '🧹 Use cleanup_grade_calculation_queue() periodically to clean old entries';
END $$;