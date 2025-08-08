/**
 * Supabase Authentication Module
 * Framework-native authentication with PKCE flow
 * Integrates with Hugo site parameters and framework components
 */

// Ensure auth utilities are loaded
if (!window.AuthUtils) {
    console.error('AuthUtils not loaded. Authentication may not work correctly.');
}

// Global authentication state
window.authState = {
    client: null,
    user: null,
    session: null,
    isAuthenticated: false,
    isLoading: false
};

/**
 * Compute the site base path from the configured BaseURL.
 * Returns a path that always starts and ends with '/'.
 */
function getSiteBasePath() {
    const configuredBaseUrl = (window.authConfig && window.authConfig.base_url) ? String(window.authConfig.base_url) : '';

    // 1) Try path from configured BaseURL
    const pathFromConfig = (function() {
        if (!configuredBaseUrl) return '';
        try {
            const url = new URL(configuredBaseUrl);
            return url.pathname || '/';
        } catch (_) {
            // configuredBaseUrl might be a path-only value
            const p = configuredBaseUrl.startsWith('/') ? configuredBaseUrl : '/' + configuredBaseUrl;
            return p;
        }
    })();
    if (pathFromConfig && pathFromConfig !== '/') {
        return pathFromConfig.endsWith('/') ? pathFromConfig : pathFromConfig + '/';
    }

    // 2) Infer from current script src (prefix before /assets/)
    try {
        const currentScript = document.currentScript;
        if (currentScript && currentScript.src) {
            const pathname = new URL(currentScript.src).pathname;
            const idx = pathname.indexOf('/assets/');
            if (idx > 0) {
                const prefix = pathname.substring(0, idx + 1);
                return prefix.endsWith('/') ? prefix : prefix + '/';
            }
        }
    } catch (_) { /* no-op */ }

    // 3) Fallback to root
    return '/';
}

/**
 * Build a fully-qualified URL using the current origin + site base path + given path.
 * The provided path can be absolute (starts with '/') or relative.
 */
function buildSiteUrl(pathname) {
    const origin = window.location.origin;
    const basePath = getSiteBasePath();
    const normalizedPath = pathname && pathname.startsWith('/') ? pathname : `/${pathname || ''}`;
    // Use URL to safely join and preserve any existing query/hash in pathname
    return new URL(normalizedPath, origin + basePath).toString();
}

/**
 * Initialize Supabase client with PKCE flow
 */
function initializeSupabaseAuth() {
    // Check if authentication is enabled
    if (!window.authConfig || !window.authConfig.enabled) {
        console.log('🔐 Authentication disabled in framework configuration');
        return;
    }

    console.log('🔐 Initializing Supabase authentication...');

    try {
        // Initialize Supabase client with PKCE
        window.authState.client = supabase.createClient(
            window.authConfig.supabase_url,
            window.authConfig.supabase_anon_key,
            {
                auth: {
                    flowType: 'pkce',
                    autoRefreshToken: true,
                    persistSession: true,
                    detectSessionInUrl: true
                }
            }
        );

        console.log('✅ Supabase client initialized');
        
        // Listen for auth state changes
        window.authState.client.auth.onAuthStateChange((event, session) => {
            console.log('🔐 Auth state changed:', event);
            handleAuthStateChange(event, session);
        });

        // Check initial session
        checkInitialSession();

    } catch (error) {
        console.error('❌ Failed to initialize Supabase:', error);
    }
}

/**
 * Check for existing session on page load
 */
async function checkInitialSession() {
    try {
        const { data: { session }, error } = await window.authState.client.auth.getSession();
        
        if (error) {
            console.error('❌ Error checking session:', error);
            return;
        }

        if (session) {
            console.log('✅ Found existing session');
            updateAuthState(session.user, session);
        } else {
            console.log('🔐 No existing session found');
        }
    } catch (error) {
        console.error('❌ Error checking initial session:', error);
    }
}

/**
 * Handle authentication state changes
 */
function handleAuthStateChange(event, session) {
    switch (event) {
        case 'SIGNED_IN':
            console.log('✅ User signed in');
            updateAuthState(session.user, session);
            break;
        case 'SIGNED_OUT':
            console.log('🚪 User signed out');
            updateAuthState(null, null);
            break;
        case 'TOKEN_REFRESHED':
            console.log('🔄 Token refreshed');
            updateAuthState(session.user, session);
            break;
        default:
            console.log('🔐 Auth event:', event);
    }
}

/**
 * Update global authentication state
 */
function updateAuthState(user, session) {
    window.authState.user = user;
    window.authState.session = session;
    window.authState.isAuthenticated = !!user;
    
    // Update UI
    updateAuthUI();
    
    // Dispatch custom event for other components
    window.dispatchEvent(new CustomEvent('authStateChanged', {
        detail: {
            user: user,
            session: session,
            isAuthenticated: !!user
        }
    }));
}

/**
 * Update authentication UI elements
 */
function updateAuthUI() {
    const authButton = document.getElementById('authButton');
    const authIcon = document.getElementById('authIcon');
    
    if (!authButton || !authIcon) return;

    if (window.authState.isAuthenticated) {
        // User is authenticated - show logout
        authIcon.textContent = window.authConfig.logout_icon;
        authButton.title = 'Logout';
        authButton.classList.add('authenticated');
        authButton.classList.remove('loading');
    } else {
        // User is not authenticated - show login
        authIcon.textContent = window.authConfig.login_icon;
        authButton.title = 'Login';
        authButton.classList.remove('authenticated');
        authButton.classList.remove('loading');
    }
}

/**
 * Handle login action
 */
async function handleLogin() {
    if (!window.authState.client) {
        console.error('❌ Supabase client not initialized');
        return;
    }

    console.log('🔐 Starting login process...');
    setLoadingState(true);

    try {
        // Store the current page path to return to after authentication
        const currentPath = window.location.pathname + window.location.search + window.location.hash;
        
        // Use AuthUtils if available, fallback to basic logic
        let callbackUrl;
        if (window.AuthUtils) {
            callbackUrl = new URL(window.AuthUtils.getCallbackUrl());
            
            // Validate and add redirect parameter
            const validatedPath = window.AuthUtils.validateRedirectPath(currentPath);
            if (validatedPath && validatedPath !== '/auth/callback/') {
                callbackUrl.searchParams.set('redirect', validatedPath);
            }
        } else {
            // Fallback to original logic
            callbackUrl = new URL(window.authConfig.login_redirect || '/auth/callback/', window.location.origin);
            if (currentPath && currentPath !== '/auth/callback/') {
                callbackUrl.searchParams.set('redirect', currentPath);
            }
        }

        console.log('Auth: Initiating login, will return to:', currentPath);

        const { data, error } = await window.authState.client.auth.signInWithOAuth({
            provider: 'github',
            options: {
                redirectTo: callbackUrl.toString()
            }
        });

        if (error) {
            console.error('❌ Login error:', error);
            setLoadingState(false);
            return;
        }

        console.log('🔐 Login initiated, redirecting...');
    } catch (error) {
        console.error('❌ Login failed:', error);
        setLoadingState(false);
    }
}

/**
 * Handle logout action
 */
async function handleLogout() {
    if (!window.authState.client) {
        console.error('❌ Supabase client not initialized');
        return;
    }

    console.log('🚪 Logging out...');
    setLoadingState(true);

    try {
        const { error } = await window.authState.client.auth.signOut();
        
        if (error) {
            console.error('❌ Logout error:', error);
        } else {
            console.log('✅ Logged out successfully');
            // Stay on the current page after logout (just reload to update UI)
            window.location.reload();
        }
    } catch (error) {
        console.error('❌ Logout failed:', error);
    }
    
    setLoadingState(false);
}

/**
 * Set loading state for authentication button
 */
function setLoadingState(isLoading) {
    window.authState.isLoading = isLoading;
    const authButton = document.getElementById('authButton');
    
    if (authButton) {
        if (isLoading) {
            authButton.classList.add('loading');
            authButton.title = 'Loading...';
        } else {
            authButton.classList.remove('loading');
            updateAuthUI();
        }
    }
}

/**
 * Initialize authentication when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    // Load auth config from Hugo site params
    window.authConfig = window.authConfig || {};
    
    // Get config from Hugo if available
    if (typeof Hugo !== 'undefined' && Hugo.params && Hugo.params.authentication) {
        window.authConfig = Hugo.params.authentication;
    }

    // Initialize authentication
    initializeSupabaseAuth();
    
    // Set up auth button click handler
    const authButton = document.getElementById('authButton');
    if (authButton) {
        authButton.addEventListener('click', function() {
            if (window.authState.isLoading) return;
            
            if (window.authState.isAuthenticated) {
                handleLogout();
            } else {
                handleLogin();
            }
        });
    }
});

// Export functions for external use
window.supabaseAuth = {
    login: handleLogin,
    logout: handleLogout,
    getUser: () => window.authState.user,
    getSession: () => window.authState.session,
    isAuthenticated: () => window.authState.isAuthenticated
};