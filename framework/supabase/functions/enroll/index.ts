import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

/**
 * Hash function using crypto.subtle (compatible with Deno Edge Functions)
 */
async function hashToken(text: string): Promise<string> {
  const encoder = new TextEncoder()
  const data = encoder.encode(text)
  const hashBuffer = await crypto.subtle.digest('SHA-256', data)
  const hashArray = Array.from(new Uint8Array(hashBuffer))
  const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('')
  return hashHex
}

interface EnrollmentRequest {
  class_slug: string
  token: string
}

interface EnrollmentResponse {
  success: boolean
  message: string
  role?: string
  class_id?: string
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🎓 /enroll endpoint called')
    
    // Only allow POST method
    if (req.method !== 'POST') {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Method not allowed' 
        }),
        { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Parse request body
    let requestBody: EnrollmentRequest
    try {
      requestBody = await req.json()
    } catch (error) {
      console.error('❌ Invalid request body:', error)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Invalid request body' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    const { class_slug, token } = requestBody
    
    console.log('📋 Enrollment request:', { class_slug, token: token ? '***' : 'missing' })
    
    // Validate input
    if (!class_slug || !token) {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Missing required fields: class_slug and token' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Initialize Supabase client
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
      .select('id, title')
      .eq('slug', class_slug)
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

    // Check if user is already enrolled
    const { data: existingMembership, error: membershipError } = await supabaseService
      .from('class_members')
      .select('role')
      .eq('class_id', classData.id)
      .eq('user_id', user.id)
      .single()

    if (existingMembership) {
      console.log('ℹ️ User already enrolled as:', existingMembership.role)
      return new Response(
        JSON.stringify({ 
          success: true,
          message: `You are already enrolled as a ${existingMembership.role}`,
          role: existingMembership.role,
          class_id: classData.id
        } as EnrollmentResponse),
        { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Get valid enrollment tokens for this class
    const { data: tokens, error: tokenError } = await supabaseService
      .from('enrollment_tokens')
      .select('id, token_hash, expires_at, max_uses, uses, is_active')
      .eq('class_id', classData.id)
      .eq('is_active', true)

    if (tokenError || !tokens || tokens.length === 0) {
      console.error('❌ No valid tokens found:', tokenError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'No active enrollment tokens available' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log(`🔍 Checking ${tokens.length} active tokens`)

    // Find matching token
    let validToken = null
    for (const dbToken of tokens) {
      try {
        // Check if token has expired
        if (dbToken.expires_at && new Date(dbToken.expires_at) < new Date()) {
          console.log('⏰ Token expired:', dbToken.id)
          continue
        }

        // Check usage limits
        if (dbToken.max_uses > 0 && dbToken.uses >= dbToken.max_uses) {
          console.log('📊 Token usage limit reached:', dbToken.id)
          continue
        }

        // Compare token hash
        const tokenHash = await hashToken(token)
        const isMatch = tokenHash === dbToken.token_hash
        if (isMatch) {
          validToken = dbToken
          console.log('✅ Valid token found:', dbToken.id)
          break
        }
      } catch (error) {
        console.error('❌ Error comparing token:', error)
        continue
      }
    }

    if (!validToken) {
      console.log('❌ Invalid enrollment token')
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Invalid or expired enrollment token' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Start transaction: add user to class and update token usage
    const { error: enrollError } = await supabaseService
      .from('class_members')
      .insert({
        class_id: classData.id,
        user_id: user.id,
        role: 'student',
        joined_at: new Date().toISOString()
      })

    if (enrollError) {
      console.error('❌ Failed to enroll user:', enrollError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Failed to enroll in class' 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Update token usage count
    const { error: tokenUpdateError } = await supabaseService
      .from('enrollment_tokens')
      .update({ uses: validToken.uses + 1 })
      .eq('id', validToken.id)

    if (tokenUpdateError) {
      console.warn('⚠️ Failed to update token usage count:', tokenUpdateError)
      // Don't fail the enrollment for this
    }

    console.log('🎉 User successfully enrolled as student')

    return new Response(
      JSON.stringify({ 
        success: true,
        message: `Successfully enrolled in ${classData.title}!`,
        role: 'student',
        class_id: classData.id
      } as EnrollmentResponse),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('❌ Unexpected error in /enroll:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: 'Internal server error' 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})