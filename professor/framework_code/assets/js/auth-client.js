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
            console.log(`🔗 API Call: ${endpoint}`);
            
            const response = await fetch(`${CONFIG.baseUrl}${endpoint}`, requestOptions);
            
            clearTimeout(timeoutId);

            // Log response status
            console.log(`📡 Response: ${response.status} ${response.statusText}`);

            if (!response.ok) {
                // Try to get error details from response body
                let errorMessage = `API Error: ${response.status}`;
                try {
                    const errorData = await response.json();
                    errorMessage = errorData.error?.message || errorData.error || errorMessage;
                } catch (e) {
                    // If we can't parse error as JSON, use status text
                    errorMessage = `${errorMessage} ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            return await response.json();

        } catch (error) {
            clearTimeout(timeoutId);
            
            if (error.name === 'AbortError') {
                throw new Error('Request timeout - please try again');
            }
            
            // Re-throw with context
            console.error(`❌ API Error on ${endpoint}:`, error);
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