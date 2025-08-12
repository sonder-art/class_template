import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🔐 /me endpoint called')
    
    // Get class_slug from query parameters
    const url = new URL(req.url)
    const classSlug = url.searchParams.get('class_slug')
    
    console.log('📋 Class slug requested:', classSlug)
    
    if (!classSlug) {
      return new Response(
        JSON.stringify({ 
          error: { 
            code: 'invalid_input', 
            message: 'class_slug parameter is required' 
          } 
        }),
        { 
          status: 400, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    // Create Supabase client with user's JWT token
    const authHeader = req.headers.get('Authorization')
    if (!authHeader) {
      return new Response(
        JSON.stringify({ 
          error: { 
            code: 'unauthorized', 
            message: 'Missing authorization header' 
          } 
        }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    const supabaseUrl = Deno.env.get('SUPABASE_URL') ?? ''
    const supabaseAnonKey = Deno.env.get('SUPABASE_ANON_KEY') ?? ''
    
    console.log('🔗 Creating Supabase client...')
    
    const supabase = createClient(supabaseUrl, supabaseAnonKey, {
      global: {
        headers: { Authorization: authHeader }
      }
    })

    // Get authenticated user
    console.log('👤 Getting user from token...')
    const { data: { user }, error: authError } = await supabase.auth.getUser()
    
    if (authError || !user) {
      console.log('❌ Auth error:', authError?.message)
      return new Response(
        JSON.stringify({ 
          error: { 
            code: 'unauthorized', 
            message: 'Invalid or expired token' 
          } 
        }),
        { 
          status: 401, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    console.log('✅ User authenticated:', user.email)

    // Get class by slug
    console.log('🏫 Looking up class:', classSlug)
    const { data: classData, error: classError } = await supabase
      .from('classes')
      .select('id, slug, title')
      .eq('slug', classSlug)
      .single()

    if (classError || !classData) {
      console.log('❌ Class lookup error:', classError?.message)
      return new Response(
        JSON.stringify({ 
          error: { 
            code: 'not_found', 
            message: `Class '${classSlug}' not found` 
          } 
        }),
        { 
          status: 404, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    console.log('🏫 Class found:', classData.title)

    // Check membership
    console.log('👥 Checking membership for user:', user.id)
    const { data: membership, error: membershipError } = await supabase
      .from('class_members')
      .select('role, enrolled_at')
      .eq('class_id', classData.id)
      .eq('user_id', user.id)
      .single()

    if (membershipError && membershipError.code !== 'PGRST116') {
      // PGRST116 is "no rows returned" which is OK (user not a member)
      console.log('❌ Membership lookup error:', membershipError.message)
      return new Response(
        JSON.stringify({ 
          error: { 
            code: 'internal', 
            message: 'Error checking membership' 
          } 
        }),
        { 
          status: 500, 
          headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
        }
      )
    }

    console.log('👥 Membership status:', membership ? `${membership.role}` : 'not a member')

    // Get user profile
    const { data: profile } = await supabase
      .from('profiles')
      .select('github_username, full_name, avatar_url')
      .eq('user_id', user.id)
      .single()

    // Build response
    const response = {
      user_id: user.id,
      email: user.email,
      github_username: profile?.github_username || null,
      full_name: profile?.full_name || null,
      avatar_url: profile?.avatar_url || null,
      class_id: classData.id,
      class_slug: classData.slug,
      class_title: classData.title,
      role: membership?.role || null,
      is_professor: membership?.role === 'professor',
      is_student: membership?.role === 'student',
      is_member: !!membership,
      enrolled_at: membership?.enrolled_at || null
    }

    console.log('✅ Response prepared:', { 
      user: user.email, 
      class: classData.slug, 
      role: response.role || 'none',
      is_member: response.is_member 
    })

    return new Response(
      JSON.stringify(response),
      { 
        status: 200, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )

  } catch (error) {
    console.error('❌ Unexpected error in /me endpoint:', error)
    return new Response(
      JSON.stringify({ 
        error: { 
          code: 'internal', 
          message: 'An unexpected error occurred' 
        } 
      }),
      { 
        status: 500, 
        headers: { ...corsHeaders, 'Content-Type': 'application/json' } 
      }
    )
  }
})