import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

interface RosterMember {
  user_id: string
  email: string
  github_username: string | null
  full_name: string | null
  role: 'professor' | 'student'
  enrolled_at: string
  avatar_url: string | null
}

interface RosterResponse {
  success: boolean
  class_info?: {
    id: string
    title: string
    slug: string
    member_count: number
  }
  members?: RosterMember[]
  stats?: {
    professors: number
    students: number
    total: number
  }
  error?: string
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('👥 /class-roster endpoint called')
    
    // Only allow GET method
    if (req.method !== 'GET') {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Method not allowed' 
        }),
        { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get class_slug from query parameters
    const url = new URL(req.url)
    const classSlug = url.searchParams.get('class_slug')
    
    if (!classSlug) {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Missing required parameter: class_slug' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('📋 Roster request for class:', classSlug)

    // Initialize Supabase clients
    const supabaseUrl = Deno.env.get('SUPABASE_URL')
    const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
    
    if (!supabaseUrl || !supabaseServiceKey) {
      console.error('❌ Missing Supabase configuration')
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Server configuration error' 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Create service role client for database operations
    const supabaseService = createClient(supabaseUrl, supabaseServiceKey)
    
    // Create client with user JWT for authentication
    const supabaseUser = createClient(
      supabaseUrl,
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    // Verify user authentication
    const { data: { user }, error: authError } = await supabaseUser.auth.getUser()
    if (authError || !user) {
      console.error('❌ Authentication failed:', authError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Authentication required' 
        }),
        { status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ User authenticated:', user.email)

    // Get class information
    const { data: classData, error: classError } = await supabaseService
      .from('classes')
      .select('id, title, slug')
      .eq('slug', classSlug)
      .single()

    if (classError || !classData) {
      console.error('❌ Class not found:', classError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Class not found' 
        }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ Class found:', classData.title)

    // Verify user is a professor of this class (only professors can view roster)
    console.log('🔍 Checking membership for user:', user.id, 'in class:', classData.id)
    
    const { data: membership, error: membershipError } = await supabaseService
      .from('class_members')
      .select('role')
      .eq('class_id', classData.id)
      .eq('user_id', user.id)
      .eq('role', 'professor')
      .single()

    console.log('🔍 Membership query result:', { membership, membershipError })

    if (membershipError || !membership) {
      console.error('❌ User is not a professor of this class:', membershipError)
      
      // Let's also check if the user exists in class_members at all
      const { data: anyMembership, error: anyMembershipError } = await supabaseService
        .from('class_members')
        .select('role')
        .eq('class_id', classData.id)
        .eq('user_id', user.id)
        
      console.log('🔍 Any membership check:', { anyMembership, anyMembershipError })
      
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Only professors can view class roster',
          debug: {
            user_id: user.id,
            class_id: classData.id,
            membership_error: membershipError,
            any_membership: anyMembership
          }
        }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ User authorized as professor')

    // Fetch class roster - get basic membership data first
    const { data: rosterData, error: rosterError } = await supabaseService
      .from('class_members')
      .select('user_id, role, enrolled_at')
      .eq('class_id', classData.id)
      .order('enrolled_at', { ascending: false })

    if (rosterError) {
      console.error('❌ Failed to fetch roster:', rosterError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Failed to fetch class roster' 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get user details from both auth.users and profiles table
    const userIds = rosterData?.map(member => member.user_id) || []
    const emailMap = new Map()
    const profileMap = new Map()
    
    console.log('👥 Found', userIds.length, 'users to fetch details for')
    
    // If we have users, fetch their details
    if (userIds.length > 0) {
      // Fetch emails from auth.users
      try {
        const userPromises = userIds.map(async (userId) => {
          try {
            const { data: userData, error: userError } = await supabaseService.auth.admin.getUserById(userId)
            if (!userError && userData.user) {
              emailMap.set(userId, userData.user.email)
            } else {
              emailMap.set(userId, 'Email not available')
            }
          } catch (error) {
            emailMap.set(userId, 'Email error')
          }
        })
        
        await Promise.all(userPromises)
        console.log('📧 Email lookup completed for', emailMap.size, 'users')
        
      } catch (error) {
        console.error('❌ Failed to fetch user emails:', error)
        userIds.forEach(userId => emailMap.set(userId, 'Email unavailable'))
      }
      
      // Try to fetch profiles separately (this may fail if table doesn't exist)
      try {
        const { data: profilesData, error: profilesError } = await supabaseService
          .from('profiles')
          .select('user_id, github_username, full_name, avatar_url')
          .in('user_id', userIds)
        
        if (!profilesError && profilesData) {
          profilesData.forEach(profile => {
            profileMap.set(profile.user_id, profile)
          })
          console.log('👤 Profile lookup completed for', profileMap.size, 'users')
        } else {
          console.warn('⚠️ Profiles table not available or empty:', profilesError)
        }
      } catch (error) {
        console.warn('⚠️ Could not fetch profiles (table may not exist):', error)
      }
    }

    // Process roster data - handle empty roster gracefully
    const members: RosterMember[] = (rosterData || []).map(member => {
      const profile = profileMap.get(member.user_id)
      return {
        user_id: member.user_id,
        email: emailMap.get(member.user_id) || 'Unknown',
        github_username: profile?.github_username || null,
        full_name: profile?.full_name || null,
        role: member.role as 'professor' | 'student',
        enrolled_at: member.enrolled_at,
        avatar_url: profile?.avatar_url || null
      }
    })

    // Calculate stats
    const stats = {
      professors: members.filter(m => m.role === 'professor').length,
      students: members.filter(m => m.role === 'student').length,
      total: members.length
    }

    if (members.length === 0) {
      console.log('📊 Empty roster - no members found for class')
    } else {
      console.log('📊 Roster loaded:', stats)
    }

    const response: RosterResponse = {
      success: true,
      class_info: {
        id: classData.id,
        title: classData.title,
        slug: classData.slug,
        member_count: stats.total
      },
      members,
      stats
    }

    return new Response(
      JSON.stringify(response),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('❌ Unexpected error in /class-roster:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: `Internal server error: ${error.message}` 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})