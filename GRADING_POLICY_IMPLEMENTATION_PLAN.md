# Grading Policy Implementation Plan

## Executive Summary

This document outlines the implementation plan for an automatic, flexible grading policy system that eliminates manual SQL queries and allows policy changes through YAML configuration files that automatically sync to the database.

## Current State Analysis

### Existing Infrastructure

#### Files to Read for Context
1. **Database Schema**: `/framework/sql/003_grading_system.sql`
   - Contains modules, constituents, items, submissions tables
   - Missing: grading_policies table

2. **Grade Calculation**: `/framework/sql/004_grading_edge_function_support.sql`
   - Contains `calculate_module_grades()` function
   - Currently uses simple SUM, no policy application

3. **Parsing Scripts**: 
   - `/framework/scripts/parse_grading_data.py` - Parses YAML to JSON
   - `/framework/scripts/sync_grading_data.py` - Syncs to database
   - Both expect grading_policies but table doesn't exist

4. **Configuration Files**:
   - `/class_template/modules.yml` - Module definitions (has unused settings lines 56-95)
   - `/class_template/constituents.yml` - Constituent definitions (has unused settings lines 115-130)
   - `/class_template/grading_policies/auth_implementation_policy.yml` - Complex unused policy

### Problems Identified
1. **No grading_policies table** in database despite sync scripts expecting it
2. **No policy application** in grade calculations (just simple sum)
3. **Unused configuration** sections in YAML files
4. **Complex unused policy** file that doesn't match requirements

## Proposed Solution Architecture

### 1. Database Structure

#### New Table: grading_policies
```sql
CREATE TABLE IF NOT EXISTS grading_policies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    module_id TEXT NOT NULL REFERENCES modules(id),
    class_id UUID NOT NULL REFERENCES classes(id),
    policy_name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    
    -- JSON policy definition
    policy_rules JSONB NOT NULL,
    
    -- Metadata
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Unique constraint per module/class/version
    UNIQUE(module_id, class_id, version)
);
```

### 2. Policy YAML Structure

#### Location: `/class_template/grading_policies/`

Create one file per module or a single `module_grading_policy.yml`:

```yaml
# Universal Module Grading Policy
# Applied to all modules using the 5-rule system

policy_metadata:
  name: "Universal 5-Rule Grading Policy"
  version: "1.0"
  description: "Applies 5-rule grading algorithm to all modules"
  applies_to: "all_modules"  # or specific module_id

# The 5-rule algorithm as JSON-serializable rules
grading_rules:
  - rule_id: "exceptional_performance"
    description: "All grades > 9.0 → Final = 10.0"
    condition:
      type: "all_grades_above"
      threshold: 9.0
    action:
      type: "set_final_score"
      value: 10.0
    priority: 1

  - rule_id: "good_performance"
    description: "All grades > 8.0 → Average + bonus (0.15 to 0.5)"
    condition:
      type: "all_grades_above"
      threshold: 8.0
    action:
      type: "add_bonus"
      calculation: "linear_interpolation"
      min_bonus: 0.15
      max_bonus: 0.5
      min_avg: 8.0
      max_avg: 9.0
    priority: 2

  - rule_id: "acceptable_performance"
    description: "All grades > 7.5 → Exact average"
    condition:
      type: "all_grades_above"
      threshold: 7.5
    action:
      type: "use_average"
    priority: 3

  - rule_id: "warning_zone"
    description: "Any grade 6.0-7.5 → Average - 0.3 (min 6.0)"
    condition:
      type: "any_grade_between"
      min: 6.0
      max: 7.5
    action:
      type: "subtract_penalty"
      penalty: 0.3
      minimum_score: 6.0
    priority: 4

  - rule_id: "problematic_performance"
    description: "Any grade < 6.0 → Remove highest, average rest"
    condition:
      type: "any_grade_below"
      threshold: 6.0
    action:
      type: "remove_highest_and_average"
      protection:
        min_items_required: 2
        fallback: "use_average"
    priority: 5

# Additional settings
settings:
  apply_to_modules:
    - "auth_implementation"
    - "framework_basics"
    - "content_management"
    - "advanced_features"
    - "deployment"
  decimal_places: 2
  cache_duration_minutes: 30
```

### 3. SQL Implementation

#### Universal Policy Interpreter Function

Create `/framework/sql/006_grading_policy_system.sql`:

```sql
-- Create grading_policies table
CREATE TABLE IF NOT EXISTS grading_policies (
    id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    module_id TEXT,
    class_id UUID NOT NULL REFERENCES classes(id),
    policy_name TEXT NOT NULL,
    version TEXT NOT NULL DEFAULT '1.0',
    policy_rules JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(module_id, class_id, version)
);

-- Function to apply grading policy
CREATE OR REPLACE FUNCTION apply_grading_policy(
    p_module_id TEXT,
    p_class_id UUID,
    p_grades NUMERIC[]
) RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_policy JSONB;
    v_rules JSONB;
    v_final_score NUMERIC;
    v_avg_score NUMERIC;
    v_min_grade NUMERIC;
    v_max_grade NUMERIC;
    v_all_above_9 BOOLEAN;
    v_all_above_8 BOOLEAN;
    v_all_above_75 BOOLEAN;
    v_any_between_6_75 BOOLEAN;
    v_any_below_6 BOOLEAN;
BEGIN
    -- Get active policy for this module
    SELECT policy_rules INTO v_policy
    FROM grading_policies
    WHERE (module_id = p_module_id OR module_id IS NULL)
    AND class_id = p_class_id
    AND is_active = true
    ORDER BY module_id NULLS LAST, created_at DESC
    LIMIT 1;
    
    -- If no policy, return simple average
    IF v_policy IS NULL THEN
        RETURN COALESCE(AVG(grade), 0) FROM UNNEST(p_grades) AS grade;
    END IF;
    
    -- Calculate statistics
    v_avg_score := AVG(grade) FROM UNNEST(p_grades) AS grade;
    v_min_grade := MIN(grade) FROM UNNEST(p_grades) AS grade;
    v_max_grade := MAX(grade) FROM UNNEST(p_grades) AS grade;
    
    -- Check conditions for 5-rule policy
    v_all_above_9 := v_min_grade > 9.0;
    v_all_above_8 := v_min_grade > 8.0;
    v_all_above_75 := v_min_grade > 7.5;
    v_any_between_6_75 := EXISTS (SELECT 1 FROM UNNEST(p_grades) AS g WHERE g >= 6.0 AND g <= 7.5);
    v_any_below_6 := v_min_grade < 6.0;
    
    -- Apply rules in priority order
    IF v_all_above_9 THEN
        -- Rule 1: Exceptional performance
        v_final_score := 10.0;
    ELSIF v_all_above_8 THEN
        -- Rule 2: Good performance with bonus
        -- Linear interpolation: 8.0→+0.15, 9.0→+0.5
        v_final_score := v_avg_score + (0.15 + (v_avg_score - 8.0) * 0.35);
    ELSIF v_all_above_75 THEN
        -- Rule 3: Acceptable performance
        v_final_score := v_avg_score;
    ELSIF v_any_between_6_75 THEN
        -- Rule 4: Warning zone
        v_final_score := GREATEST(6.0, v_avg_score - 0.3);
    ELSIF v_any_below_6 THEN
        -- Rule 5: Problematic performance
        IF array_length(p_grades, 1) > 1 THEN
            -- Remove highest and average the rest
            v_final_score := (
                SELECT AVG(grade) 
                FROM UNNEST(p_grades) AS grade 
                WHERE grade < v_max_grade OR grade = v_max_grade 
                LIMIT array_length(p_grades, 1) - 1
            );
        ELSE
            v_final_score := v_avg_score;
        END IF;
    ELSE
        -- Default fallback
        v_final_score := v_avg_score;
    END IF;
    
    RETURN ROUND(v_final_score, 2);
END;
$$;

-- Update calculate_module_grades to use policy
CREATE OR REPLACE FUNCTION calculate_module_grades(
    p_student_id UUID,
    p_class_id UUID
) RETURNS TABLE (
    module_id TEXT,
    module_name TEXT,
    raw_score NUMERIC,
    final_score NUMERIC,
    grade_count INTEGER
) 
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    WITH module_grades AS (
        SELECT 
            m.id,
            m.name,
            array_agg(
                COALESCE(ls.adjusted_score, ls.raw_score, 0)
            ) AS grades_array
        FROM modules m
        LEFT JOIN constituents c ON c.module_id = m.id
        LEFT JOIN homework_items hi ON hi.constituent_slug = c.slug
        LEFT JOIN LATERAL (
            SELECT DISTINCT ON (ss.item_id)
                ss.raw_score,
                ss.adjusted_score
            FROM student_submissions ss
            WHERE ss.student_id = p_student_id
            AND ss.class_id = p_class_id
            AND ss.item_id = hi.id
            ORDER BY ss.item_id, ss.attempt_number DESC
        ) ls ON true
        WHERE m.class_id = p_class_id
        AND m.is_current = true
        GROUP BY m.id, m.name
    )
    SELECT 
        mg.id,
        mg.name,
        COALESCE(AVG(g), 0) as raw_score,
        apply_grading_policy(mg.id, p_class_id, mg.grades_array) as final_score,
        array_length(mg.grades_array, 1) as grade_count
    FROM module_grades mg
    LEFT JOIN LATERAL UNNEST(mg.grades_array) AS g ON true
    GROUP BY mg.id, mg.name, mg.grades_array;
END;
$$;
```

### 4. Update Sync Pipeline

#### Modify `/framework/scripts/sync_grading_data.py`

Key changes needed:
1. Ensure grading_policies table exists (check migration)
2. Parse policy YAML files correctly
3. Store policy_rules as JSONB
4. Handle "all_modules" vs specific module policies

#### Modify `/framework/scripts/parse_grading_data.py`

Key changes needed:
1. Parse new simplified policy format
2. Convert rules to JSON-serializable format
3. Handle universal vs module-specific policies

### 5. Clean Up Unused Settings

#### Files to modify:

1. `/class_template/modules.yml`
   - Remove lines 56-95 (unused settings section)
   - Keep only module definitions

2. `/class_template/constituents.yml`
   - Remove lines 115-130 (unused settings section)
   - Keep constituent_types (used for UI)

3. `/class_template/grading_policies/auth_implementation_policy.yml`
   - Delete entirely (complex unused policy)
   - Replace with new universal policy file

## Implementation Steps

### Phase 1: Database Setup
1. Create SQL migration file `006_grading_policy_system.sql`
2. Run migration to create grading_policies table
3. Create policy interpreter function
4. Update calculate_module_grades function

### Phase 2: Policy Configuration
1. Create new universal policy YAML file
2. Delete old complex policy file
3. Clean up unused settings in modules.yml and constituents.yml

### Phase 3: Sync Pipeline
1. Update parse_grading_data.py to handle new format
2. Update sync_grading_data.py to properly sync policies
3. Test with `./manage.sh --build`

### Phase 4: Testing
1. Run `./manage.sh --build` to parse policies
2. Click "Sync to Database" button on grading sync page
3. Verify policies are in database
4. Check that grades are calculated with policy

## Benefits of This Approach

1. **No Manual SQL**: Change YAML → Sync → Done
2. **Flexible**: Easy to modify rules without touching SQL
3. **Maintainable**: All logic in one place (YAML files)
4. **Versioned**: Policy history maintained
5. **Universal**: One policy can apply to all modules
6. **Simple**: JSON-based rules, not complex SQL
7. **Automatic**: Grades always use latest active policy

## Testing Checklist

- [ ] grading_policies table created successfully
- [ ] Policy YAML files parse without errors
- [ ] Sync button uploads policies to database
- [ ] calculate_module_grades uses policy
- [ ] Grades reflect 5-rule algorithm
- [ ] Changes to YAML automatically apply after sync
- [ ] Old unused settings removed from files

## Important Notes

1. **Backwards Compatibility**: System falls back to simple average if no policy exists
2. **Priority Order**: Module-specific policies override universal policies
3. **Caching**: Consider caching policy lookups for performance
4. **Validation**: Add validation to ensure policy rules are valid JSON
5. **Logging**: Add logging to track which policy was applied

## Files Summary

### To Create:
- `/framework/sql/006_grading_policy_system.sql` - Database migration
- `/class_template/grading_policies/module_grading_policy.yml` - Universal policy

### To Modify:
- `/framework/scripts/parse_grading_data.py` - Handle new policy format
- `/framework/scripts/sync_grading_data.py` - Sync policies correctly
- `/class_template/modules.yml` - Remove unused settings
- `/class_template/constituents.yml` - Remove unused settings

### To Delete:
- `/class_template/grading_policies/auth_implementation_policy.yml` - Complex unused policy

## Next Steps

1. Review this plan
2. Create database migration
3. Create policy YAML file
4. Update sync scripts
5. Test end-to-end
6. Deploy to production