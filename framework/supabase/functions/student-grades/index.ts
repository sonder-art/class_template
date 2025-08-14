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

      // Build query based on grade level
      let query = supabaseClient
        .from('student_grades_cache')
        .select(`
          *,
          modules (name, color, icon),
          constituents (name, type),
          homework_items (title, due_date)
        `)
        .eq('student_id', studentId)
        .eq('class_id', class_id)
        .eq('grade_level', gradeLevel)
        .order('computed_at', { ascending: false })

      const { data: grades, error: gradesError } = await query

      if (gradesError) {
        throw gradesError
      }

      // Calculate summary statistics
      const summary = {
        total_grades: grades.length,
        average_score: grades.length > 0 ? 
          grades.reduce((sum, g) => sum + (g.final_score || 0), 0) / grades.length : 0,
        grade_distribution: {},
        last_updated: grades.length > 0 ? grades[0].computed_at : null
      }

      // Count letter grades
      grades.forEach(grade => {
        const letter = grade.letter_grade || 'N/A'
        summary.grade_distribution[letter] = (summary.grade_distribution[letter] || 0) + 1
      })

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
        { headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
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