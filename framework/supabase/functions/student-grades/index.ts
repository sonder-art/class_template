// Edge Function: Student Grades API
// This function provides grade retrieval for students (own grades) and professors (all grades)
// Uses the grading system database schema and RLS policies

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

serve(async (req) => {
  // CORS headers
  const corsHeaders = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
    'Access-Control-Allow-Methods': 'GET, OPTIONS'
  }

  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Get Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Verify authentication
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ error: 'Missing authorization header' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const { data: { user }, error: authError } = await supabaseClient.auth.getUser(
      authHeader.replace('Bearer ', '')
    )

    if (authError || !user) {
      return new Response(
        JSON.stringify({ error: 'Invalid authentication' }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get user's class membership and role
    const { data: membershipData, error: membershipError } = await supabaseClient
      .from('class_members')
      .select('role, class_id')
      .eq('user_id', user.id)
      .single()

    if (membershipError || !membershipData) {
      return new Response(
        JSON.stringify({ error: 'Not enrolled in any class' }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const { role, class_id } = membershipData

    if (req.method === 'GET') {
      const url = new URL(req.url)
      const gradeLevel = url.searchParams.get('level') || 'module' // module, constituent, item
      const targetStudentId = url.searchParams.get('student_id')

      // Students can only access their own grades
      if (role === 'student' && targetStudentId && targetStudentId !== user.id) {
        return new Response(
          JSON.stringify({ error: 'Students can only access their own grades' }),
          { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
        )
      }

      // Set target student (professors can specify, students default to self)
      const studentId = targetStudentId || user.id

      // Calculate grades on-the-fly using SQL functions
      let grades = []
      let gradesError = null

      try {
        if (gradeLevel === 'item') {
          const { data, error } = await supabaseClient
            .rpc('get_item_grades', {
              p_student_id: studentId,
              p_class_id: class_id
            })
          grades = data || []
          gradesError = error
        } else if (gradeLevel === 'constituent') {
          const { data, error } = await supabaseClient
            .rpc('calculate_constituent_grades', {
              p_student_id: studentId,
              p_class_id: class_id
            })
          grades = data || []
          gradesError = error
        } else { // module level
          const { data, error } = await supabaseClient
            .rpc('calculate_module_grades', {
              p_student_id: studentId,
              p_class_id: class_id
            })
          grades = data || []
          gradesError = error
        }

        if (gradesError) {
          throw gradesError
        }
      } catch (error) {
        console.error('Error calculating grades:', error)
        throw new Error(`Failed to calculate ${gradeLevel} grades: ${error.message}`)
      }

      // Get summary statistics using SQL function
      let summary = {
        total_grades: 0,
        average_score: 0,
        grade_distribution: {},
        last_updated: null
      }

      try {
        const { data: summaryData, error: summaryError } = await supabaseClient
          .rpc('calculate_grade_summary', {
            p_student_id: studentId,
            p_class_id: class_id,
            p_grade_level: gradeLevel
          })

        if (!summaryError && summaryData) {
          summary = {
            total_grades: summaryData.total_grades || 0,
            average_score: summaryData.average_score || 0,
            grade_distribution: summaryData.grade_distribution || {},
            last_updated: summaryData.last_updated || null
          }
        }
      } catch (error) {
        console.error('Error calculating summary:', error)
        // Continue with empty summary rather than failing
      }

      // Add cache headers for performance
      const cacheHeaders = {
        ...corsHeaders,
        'Content-Type': 'application/json',
        'Cache-Control': 'private, max-age=300', // 5 minutes
        'ETag': `"${studentId}-${gradeLevel}-${summary.last_updated || 'empty'}"`
      }

      return new Response(
        JSON.stringify({
          success: true,
          grades,
          summary,
          student_info: {
            student_id: studentId,
            class_id,
            role,
            grade_level: gradeLevel
          }
        }),
        { headers: cacheHeaders }
      )
    }

    return new Response(
      JSON.stringify({ error: 'Method not allowed' }),
      { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('Error in student-grades function:', error)
    return new Response(
      JSON.stringify({ error: error.message }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})