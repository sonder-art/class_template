/**
 * Authentication API Client
 * Handles communication with Supabase Edge Functions for authentication
 */

window.AuthClient = (function() {
    'use strict';

    // Configuration
    const CONFIG = {
        baseUrl: 'https://levybxqsltedfjtnkntm.supabase.co/functions/v1',
        timeout: 10000 // 10 seconds
    };

    /**
     * Make an authenticated API call to an Edge Function
     */
    async function callEndpoint(endpoint, options = {}) {
        const token = window.authState?.session?.access_token;
        console.log('🔍 DEBUG: callEndpoint called with:', endpoint);
        console.log('🔍 DEBUG: Token exists:', !!token);
        console.log('🔍 DEBUG: Token length:', token?.length);
        console.log('🔍 DEBUG: Request options:', options);
        
        if (!token) {
            throw new Error('Not authenticated - no access token available');
        }

        // Prepare request options
        const requestOptions = {
            ...options,
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json',
                'x-client-info': 'class-template-framework',
                ...options.headers
            }
        };

        // Add timeout
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), CONFIG.timeout);
        requestOptions.signal = controller.signal;

        try {
            const fullUrl = `${CONFIG.baseUrl}${endpoint}`;
            console.log(`🔗 API Call: ${endpoint}`);
            console.log(`🔗 Full URL: ${fullUrl}`);
            console.log(`🔗 Request headers:`, requestOptions.headers);
            
            const response = await fetch(fullUrl, requestOptions);
            
            clearTimeout(timeoutId);

            // Log response status
            console.log(`📡 Response: ${response.status} ${response.statusText}`);
            console.log(`📡 Response headers:`, Object.fromEntries(response.headers.entries()));

            if (!response.ok) {
                // Try to get error details from response body
                let errorMessage = `API Error: ${response.status}`;
                let errorData = null;
                try {
                    const responseText = await response.text();
                    console.log('📡 Error response body:', responseText);
                    errorData = JSON.parse(responseText);
                    errorMessage = errorData.error?.message || errorData.error || errorMessage;
                } catch (e) {
                    console.log('📡 Could not parse error response as JSON:', e);
                    // If we can't parse error as JSON, use status text
                    errorMessage = `${errorMessage} ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const responseData = await response.json();
            console.log('📡 Success response:', responseData);
            return responseData;

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please try again');
            }
            
            // Re-throw with context
            console.error(`❌ API Error on ${endpoint}:`, error);
            console.error(`❌ Error details:`, {
                name: error.name,
                message: error.message,
                stack: error.stack
            });
            throw error;
        }
    }

    /**
     * Get user context and class membership
     */
    async function getMe(classSlug = 'class_template') {
        try {
            const context = await callEndpoint(`/me?class_slug=${encodeURIComponent(classSlug)}`);
            console.log('👤 User context loaded:', context);
            return context;
        } catch (error) {
            console.warn('⚠️ Could not fetch user context:', error.message);
            throw error;
        }
    }

    /**
     * Enroll in a class using a token
     */
    async function enroll(classSlug, token) {
        if (!classSlug || !token) {
            throw new Error('Class slug and enrollment token are required');
        }

        try {
            const result = await callEndpoint('/enroll', {
                method: 'POST',
                body: JSON.stringify({ 
                    class_slug: classSlug, 
                    token: token.trim() 
                })
            });
            console.log('🎓 Enrollment successful:', result);
            return result;
        } catch (error) {
            console.error('❌ Enrollment failed:', error.message);
            throw error;
        }
    }

    /**
     * Get current class slug from URL or default
     */
    function getCurrentClassSlug() {
        // Try to extract class slug from URL path
        const pathParts = window.location.pathname.split('/').filter(Boolean);
        
        console.log('🔍 URL Analysis:');
        console.log('  - Full pathname:', window.location.pathname);
        console.log('  - Path parts:', pathParts);
        
        // If the first path part looks like a class slug, use it
        if (pathParts.length > 0 && pathParts[0] !== 'auth' && pathParts[0] !== 'dashboard') {
            console.log('  - Detected class slug:', pathParts[0]);
            return pathParts[0];
        }
        
        // Default to class_template
        console.log('  - Using default class slug: class_template');
        return 'class_template';
    }

    /**
     * Generate enrollment token for a class (professors only)
     */
    async function generateToken(classSlug, options = {}) {
        if (!classSlug) {
            throw new Error('Class slug is required');
        }
        
        const { expiresInDays = 30, maxUses = 0 } = options;
        
        try {
            const result = await callEndpoint('/generate-token', {
                method: 'POST',
                body: JSON.stringify({ 
                    class_slug: classSlug, 
                    expires_in_days: expiresInDays,
                    max_uses: maxUses
                })
            });
            console.log('🔗 Token generated successfully:', { ...result, token: '***' });
            return result;
        } catch (error) {
            console.error('❌ Token generation failed:', error.message);
            throw error;
        }
    }

    /**
     * Get class roster (professors only)
     */
    async function getRoster(classSlug) {
        if (!classSlug) {
            throw new Error('Class slug is required');
        }
        
        console.log('🔍 DEBUG: getRoster called with classSlug:', classSlug);
        console.log('🔍 DEBUG: Current auth state:', window.authState?.isAuthenticated);
        console.log('🔍 DEBUG: Access token available:', !!window.authState?.session?.access_token);
        
        try {
            const endpoint = `/class-roster?class_slug=${encodeURIComponent(classSlug)}`;
            console.log('🔍 DEBUG: Calling endpoint:', endpoint);
            
            const result = await callEndpoint(endpoint);
            console.log('👥 Roster loaded successfully:', result);
            return result;
        } catch (error) {
            console.error('❌ Roster loading failed - Full error:', error);
            console.error('❌ Error message:', error.message);
            console.error('❌ Error stack:', error.stack);
            throw error;
        }
    }

    /**
     * Get enrollment tokens for a class (professors only)
     */
    async function getTokens(classSlug) {
        if (!classSlug) {
            throw new Error('Class slug is required');
        }
        
        try {
            const result = await callEndpoint(`/manage-tokens?class_slug=${encodeURIComponent(classSlug)}`);
            console.log('🔧 Tokens loaded successfully:', result.stats);
            return result;
        } catch (error) {
            console.error('❌ Token loading failed:', error.message);
            throw error;
        }
    }

    /**
     * Deactivate an enrollment token (professors only)
     */
    async function deactivateToken(classSlug, tokenId) {
        if (!classSlug || !tokenId) {
            throw new Error('Class slug and token ID are required');
        }
        
        try {
            const result = await callEndpoint(`/manage-tokens?class_slug=${encodeURIComponent(classSlug)}`, {
                method: 'PUT',
                body: JSON.stringify({ 
                    class_slug: classSlug,
                    token_id: tokenId
                })
            });
            console.log('🔒 Token deactivated successfully');
            return result;
        } catch (error) {
            console.error('❌ Token deactivation failed:', error.message);
            throw error;
        }
    }

    /**
     * Check if the API is available (basic connectivity test)
     */
    async function healthCheck() {
        try {
            // We'll implement a health endpoint later, for now just return true
            return true;
        } catch (error) {
            console.warn('⚠️ API health check failed:', error.message);
            return false;
        }
    }

    // Public API
    return {
        getMe,
        enroll,
        generateToken,
        getRoster,
        getTokens,
        deactivateToken,
        getCurrentClassSlug,
        healthCheck,
        
        // Advanced usage
        callEndpoint,
        
        // Configuration access (read-only)
        getConfig: () => ({ ...CONFIG })
    };
})();

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🔗 AuthClient initialized');
});