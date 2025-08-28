/**
 * Authentication Utilities Module
 * Provides consistent URL handling and environment detection for the framework
 */

window.AuthUtils = (function() {
    'use strict';

    /**
     * Detect the current environment (development or production)
     */
    function getEnvironment() {
        const hostname = window.location.hostname;
        
        // Common development hostnames
        if (hostname === 'localhost' || 
            hostname === '127.0.0.1' || 
            hostname.includes('.local') ||
            window.location.port === '1313' || 
            window.location.port === '1314') {
            return 'development';
        }
        
        return 'production';
    }

    /**
     * Get the base path for the current site
     * This handles multi-repo deployments where the site might be at /repo-name/
     */
    function getBasePath() {
        // In development, always use root path
        if (getEnvironment() === 'development') {
            console.log('🔍 AuthUtils: Development environment detected, using root path');
            return '/';
        }

        // In production, try to get from Hugo configuration first
        if (window.authConfig && window.authConfig.base_url) {
            try {
                const url = new URL(window.authConfig.base_url);
                const basePath = url.pathname.endsWith('/') ? url.pathname : url.pathname + '/';
                console.log('🔍 AuthUtils: Production base path from config:', basePath);
                return basePath;
            } catch {
                // If base_url is just a path, use it
                const path = window.authConfig.base_url;
                if (path.startsWith('/')) {
                    const basePath = path.endsWith('/') ? path : path + '/';
                    console.log('🔍 AuthUtils: Production base path from config (fallback):', basePath);
                    return basePath;
                }
            }
        }

        // Try to infer from current URL
        // Look for common patterns like /class_template/ or /repo-name/
        const path = window.location.pathname;
        const match = path.match(/^(\/[^\/]+\/)/);
        if (match && match[1] !== '/auth/') {
            console.log('🔍 AuthUtils: Base path inferred from URL:', match[1]);
            return match[1];
        }

        console.log('🔍 AuthUtils: Using default root path');
        return '/';
    }

    /**
     * Build a full URL for the site
     */
    function buildSiteUrl(path) {
        const basePath = getBasePath();
        const origin = window.location.origin;
        
        // Ensure path starts with /
        if (!path.startsWith('/')) {
            path = '/' + path;
        }
        
        // Remove duplicate slashes
        const fullPath = (basePath + path).replace(/\/+/g, '/');
        
        return origin + fullPath;
    }

    /**
     * Get Supabase callback URL based on environment
     */
    function getCallbackUrl() {
        const env = getEnvironment();
        const basePath = getBasePath();
        
        if (env === 'development') {
            // In development, use localhost with root path (no subpath needed)
            const callbackUrl = window.location.origin + '/auth/callback/';
            console.log('🔍 AuthUtils: Development callback URL:', callbackUrl);
            return callbackUrl;
        }
        
        // In production, use the configured base URL with subpath
        const callbackUrl = buildSiteUrl('auth/callback/');
        console.log('🔍 AuthUtils: Production callback URL:', callbackUrl);
        return callbackUrl;
    }

    /**
     * Validate a redirect path for security
     */
    function validateRedirectPath(path) {
        if (!path) return null;
        
        // Must be a relative path starting with /
        if (!path.startsWith('/')) return null;
        
        // Prevent protocol-relative URLs
        if (path.startsWith('//')) return null;
        
        // Prevent javascript: URLs
        if (path.toLowerCase().includes('javascript:')) return null;
        
        // Prevent data: URLs
        if (path.toLowerCase().includes('data:')) return null;
        
        return path;
    }

    /**
     * Generate a secure state parameter for CSRF protection
     */
    function generateState() {
        const array = new Uint8Array(32);
        crypto.getRandomValues(array);
        return btoa(String.fromCharCode.apply(null, array))
            .replace(/\+/g, '-')
            .replace(/\//g, '_')
            .replace(/=/g, '');
    }

    /**
     * Store state in sessionStorage with expiry
     */
    function storeState(state, data) {
        const item = {
            state: state,
            data: data,
            expiry: Date.now() + (10 * 60 * 1000) // 10 minutes
        };
        sessionStorage.setItem('auth_state_' + state, JSON.stringify(item));
    }

    /**
     * Retrieve and validate state from sessionStorage
     */
    function retrieveState(state) {
        const key = 'auth_state_' + state;
        const item = sessionStorage.getItem(key);
        
        if (!item) return null;
        
        try {
            const data = JSON.parse(item);
            
            // Check expiry
            if (Date.now() > data.expiry) {
                sessionStorage.removeItem(key);
                return null;
            }
            
            // Remove from storage (one-time use)
            sessionStorage.removeItem(key);
            
            return data.data;
        } catch {
            return null;
        }
    }

    // Public API
    return {
        getEnvironment: getEnvironment,
        getBasePath: getBasePath,
        buildSiteUrl: buildSiteUrl,
        getCallbackUrl: getCallbackUrl,
        validateRedirectPath: validateRedirectPath,
        generateState: generateState,
        storeState: storeState,
        retrieveState: retrieveState
    };
})();