import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

interface TokenRequest {
  class_slug: string
  expires_in_days?: number
  max_uses?: number
}

interface TokenResponse {
  success: boolean
  token?: string
  expires_at?: string
  max_uses?: number
  message?: string
  error?: string
}

/**
 * Generate a random enrollment token
 */
function generateRandomToken(): string {
  const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
  const segments = 4
  const segmentLength = 4
  const separator = '-'
  
  const token = Array.from({ length: segments }, () => {
    return Array.from({ length: segmentLength }, () => 
      chars[Math.floor(Math.random() * chars.length)]
    ).join('')
  }).join(separator)
  
  return token
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

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🔗 /generate-token endpoint called')
    
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
    let requestBody: TokenRequest
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

    const { class_slug, expires_in_days = 30, max_uses = 0 } = requestBody
    
    console.log('📋 Token generation request:', { class_slug, expires_in_days, max_uses })
    
    // Validate input
    if (!class_slug) {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Missing required field: class_slug' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

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

    // Verify user is a professor of this class
    const { data: membership, error: membershipError } = await supabaseService
      .from('class_members')
      .select('role')
      .eq('class_id', classData.id)
      .eq('user_id', user.id)
      .eq('role', 'professor')
      .single()

    if (membershipError || !membership) {
      console.error('❌ User is not a professor of this class:', membershipError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Only professors can generate enrollment tokens' 
        }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ User authorized as professor')

    // Generate random token
    const plainToken = generateRandomToken()
    console.log('🔑 Generated token:', plainToken)

    // Hash the token for storage using crypto.subtle
    console.log('🔐 Hashing token with crypto.subtle...')
    const tokenHash = await hashToken(plainToken)
    console.log('✅ Token hashed successfully')

    // Calculate expiration date
    const expiresAt = new Date()
    expiresAt.setDate(expiresAt.getDate() + expires_in_days)

    // Store token in database
    console.log('💾 Attempting to insert token into database...')
    const insertData = {
      class_id: classData.id,
      token_hash: tokenHash,
      expires_at: expiresAt.toISOString(),
      max_uses: max_uses,
      uses: 0,
      created_by: user.id,
      is_active: true
    }
    console.log('📝 Insert data:', { ...insertData, token_hash: '[HIDDEN]' })

    const { data: tokenData, error: tokenError } = await supabaseService
      .from('enrollment_tokens')
      .insert(insertData)
      .select('id, expires_at, max_uses')
      .single()

    if (tokenError || !tokenData) {
      console.error('❌ Database insert failed:', tokenError)
      console.error('❌ Token error details:', {
        message: tokenError?.message,
        details: tokenError?.details,
        hint: tokenError?.hint,
        code: tokenError?.code
      })
      return new Response(
        JSON.stringify({ 
          success: false,
          error: `Database error: ${tokenError?.message || 'Unknown error'}` 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('🎉 Token created successfully:', tokenData.id)

    return new Response(
      JSON.stringify({ 
        success: true,
        token: plainToken,
        expires_at: tokenData.expires_at,
        max_uses: tokenData.max_uses,
        message: 'Enrollment token generated successfully'
      } as TokenResponse),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('❌ Unexpected error in /generate-token:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: `Internal server error: ${error.message}` 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})