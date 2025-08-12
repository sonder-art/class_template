import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
  'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
  'Access-Control-Max-Age': '86400',
}

interface TokenInfo {
  id: number
  token_hash: string
  expires_at: string
  max_uses: number
  uses: number
  is_active: boolean
  created_at: string
  created_by: string
  status: 'active' | 'expired' | 'disabled' | 'exhausted'
}

interface TokenManagementResponse {
  success: boolean
  action?: string
  tokens?: TokenInfo[]
  stats?: {
    total: number
    active: number
    expired: number
    disabled: number
    exhausted: number
  }
  message?: string
  error?: string
}

interface DeactivateRequest {
  token_id: number
  class_slug: string
}

serve(async (req: Request) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    console.log('🔧 /manage-tokens endpoint called:', req.method)
    
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

    console.log('📋 Token management request for class:', classSlug)

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
          error: 'Only professors can manage enrollment tokens' 
        }),
        { status: 403, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ User authorized as professor')

    // Handle different HTTP methods
    if (req.method === 'GET') {
      // List all tokens for the class
      return await handleListTokens(supabaseService, classData.id)
    } else if (req.method === 'PUT') {
      // Deactivate a token
      return await handleDeactivateToken(req, supabaseService, classData.id)
    } else {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Method not allowed' 
        }),
        { status: 405, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

  } catch (error) {
    console.error('❌ Unexpected error in /manage-tokens:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: `Internal server error: ${error.message}` 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
})

/**
 * Handle listing all enrollment tokens for a class
 */
async function handleListTokens(supabaseService: any, classId: string): Promise<Response> {
  console.log('📋 Listing tokens for class:', classId)
  
  try {
    // Fetch all tokens for this class
    const { data: tokensData, error: tokensError } = await supabaseService
      .from('enrollment_tokens')
      .select('id, token_hash, expires_at, max_uses, uses, is_active, created_at, created_by')
      .eq('class_id', classId)
      .order('created_at', { ascending: false })

    if (tokensError) {
      console.error('❌ Failed to fetch tokens:', tokensError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Failed to fetch enrollment tokens' 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Process tokens and determine their status
    const now = new Date()
    const tokens: TokenInfo[] = (tokensData || []).map(token => {
      let status: 'active' | 'expired' | 'disabled' | 'exhausted' = 'active'
      
      if (!token.is_active) {
        status = 'disabled'
      } else if (new Date(token.expires_at) < now) {
        status = 'expired'
      } else if (token.max_uses > 0 && token.uses >= token.max_uses) {
        status = 'exhausted'
      }
      
      return {
        ...token,
        status
      }
    })

    // Calculate statistics
    const stats = {
      total: tokens.length,
      active: tokens.filter(t => t.status === 'active').length,
      expired: tokens.filter(t => t.status === 'expired').length,
      disabled: tokens.filter(t => t.status === 'disabled').length,
      exhausted: tokens.filter(t => t.status === 'exhausted').length
    }

    console.log('📊 Token stats:', stats)

    const response: TokenManagementResponse = {
      success: true,
      action: 'list',
      tokens,
      stats
    }

    return new Response(
      JSON.stringify(response),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('❌ Error listing tokens:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: `Failed to list tokens: ${error.message}` 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
}

/**
 * Handle deactivating an enrollment token
 */
async function handleDeactivateToken(req: Request, supabaseService: any, classId: string): Promise<Response> {
  console.log('🔒 Deactivating token for class:', classId)
  
  try {
    // Parse request body
    let requestBody: DeactivateRequest
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

    const { token_id } = requestBody

    if (!token_id) {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Missing required field: token_id' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Verify the token belongs to this class
    const { data: tokenData, error: tokenError } = await supabaseService
      .from('enrollment_tokens')
      .select('id, is_active')
      .eq('id', token_id)
      .eq('class_id', classId)
      .single()

    if (tokenError || !tokenData) {
      console.error('❌ Token not found:', tokenError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Token not found or access denied' 
        }),
        { status: 404, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    if (!tokenData.is_active) {
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Token is already deactivated' 
        }),
        { status: 400, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    // Deactivate the token
    const { error: updateError } = await supabaseService
      .from('enrollment_tokens')
      .update({ is_active: false })
      .eq('id', token_id)
      .eq('class_id', classId)

    if (updateError) {
      console.error('❌ Failed to deactivate token:', updateError)
      return new Response(
        JSON.stringify({ 
          success: false,
          error: 'Failed to deactivate token' 
        }),
        { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
      )
    }

    console.log('✅ Token deactivated successfully:', token_id)

    const response: TokenManagementResponse = {
      success: true,
      action: 'deactivate',
      message: 'Token deactivated successfully'
    }

    return new Response(
      JSON.stringify(response),
      { status: 200, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )

  } catch (error) {
    console.error('❌ Error deactivating token:', error)
    return new Response(
      JSON.stringify({ 
        success: false,
        error: `Failed to deactivate token: ${error.message}` 
      }),
      { status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' } }
    )
  }
}