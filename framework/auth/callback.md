---
title: "Authentication Callback"
url: "/auth/callback/"
sitemap_ignore: true
robots: "noindex, nofollow"
---

# Processing Authentication

<div id="authStatus" class="auth-status">
    <div class="auth-loading">
        <span class="auth-spinner">🔄</span>
        <p>Verifying your credentials...</p>
    </div>
</div>

<div id="authError" class="auth-error" style="display: none;">
    <span class="auth-icon">❌</span>
    <h2>Authentication Failed</h2>
    <p id="errorMessage">Something went wrong during authentication.</p>
    <button id="retryButton" class="auth-button">Try Again</button>
</div>

<div id="authSuccess" class="auth-success" style="display: none;">
    <span class="auth-icon">✅</span>
    <h2>Welcome!</h2>
    <p>Authentication successful. Redirecting you now...</p>
</div>

<style>
.auth-status {
    text-align: center;
    padding: 2rem;
}

.auth-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 1rem;
}

.auth-spinner {
    font-size: 2rem;
    animation: spin 2s linear infinite;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.auth-error,
.auth-success {
    text-align: center;
    padding: 2rem;
}

.auth-icon {
    font-size: 3rem;
    display: block;
    margin-bottom: 1rem;
}

.auth-button {
    background: var(--color-primary, #007acc);
    color: white;
    border: none;
    border-radius: 0.375rem;
    padding: 0.75rem 1.5rem;
    cursor: pointer;
    font-size: 1rem;
    margin-top: 1rem;
    transition: all 0.2s;
}

.auth-button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
</style>

<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log('Auth callback: Processing authentication...');
    handleAuthCallback();
});

async function handleAuthCallback() {
    const authStatusEl = document.getElementById('authStatus');
    const authErrorEl = document.getElementById('authError');
    const authSuccessEl = document.getElementById('authSuccess');
    const errorMessageEl = document.getElementById('errorMessage');
    const retryButtonEl = document.getElementById('retryButton');

    try {
        // Check URL parameters
        const urlParams = new URLSearchParams(window.location.search);
        const authCode = urlParams.get('code');
        const redirectPath = urlParams.get('redirect');
        
        console.log('Auth callback: Code present:', !!authCode);
        console.log('Auth callback: Return path:', redirectPath || 'none');

        // Check if we actually have an auth code (real callback scenario)
        if (!authCode) {
            throw new Error('No auth code in URL - not a real OAuth callback');
        }

        // Wait for framework to process authentication automatically
        console.log('Auth callback: Waiting for framework authentication...');
        
        for (let attempt = 0; attempt < 20; attempt++) {
            await new Promise(resolve => setTimeout(resolve, 250));
            
            const currentSession = localStorage.getItem('sb-levybxqsltedfjtnkntm-auth-token');
            
            if (currentSession) {
                const sessionData = JSON.parse(currentSession);
                
                if (sessionData.access_token) {
                    console.log('Auth callback: Authentication successful');
                    
                    // Show success and redirect
                    authStatusEl.style.display = 'none';
                    authSuccessEl.style.display = 'block';
                    
                    setTimeout(() => {
                        // Check for stored post-login redirect (from enrollment page)
                        const storedRedirect = sessionStorage.getItem('post_login_redirect');
                        if (storedRedirect) {
                            sessionStorage.removeItem('post_login_redirect');
                            console.log('Auth callback: Using stored redirect:', storedRedirect);
                            const basePath = window.location.pathname.replace('/auth/callback/', '');
                            const baseUrl = window.location.origin + basePath;
                            const finalUrl = new URL(storedRedirect, baseUrl).toString();
                            window.location.href = finalUrl;
                            return;
                        }
                        
                        // Determine where to redirect with smart defaults
                        let targetPath = redirectPath;
                        
                        // Validate the redirect path for security
                        if (!targetPath || !targetPath.startsWith('/') || targetPath.startsWith('//')) {
                            // Default: send to dashboard (which now shows appropriate view)
                            targetPath = '/dashboard/';
                        }
                        
                        // Get the base path for the site
                        const basePath = window.location.pathname.replace('/auth/callback/', '');
                        const baseUrl = window.location.origin + basePath;
                        
                        // Build the final redirect URL
                        const finalUrl = new URL(targetPath, baseUrl).toString();
                        
                        console.log('Auth callback: Redirecting to:', finalUrl);
                        window.location.href = finalUrl;
                    }, 1500);
                    
                    return; // Exit function - no manual processing needed
                }
            }
        }
        
        // Fallback: Try manual processing if framework didn't complete
        console.log('Auth callback: Attempting manual authentication...');
        
        let supabaseClient;
        if (window.authState && window.authState.client) {
            supabaseClient = window.authState.client;
        } else {
            // Create fallback client
            supabaseClient = supabase.createClient(
                window.authConfig.supabase_url,
                window.authConfig.supabase_anon_key,
                {
                    auth: {
                        storageKey: 'sb-levybxqsltedfjtnkntm-auth-token',
                        flowType: 'pkce',
                        autoRefreshToken: true,
                        persistSession: true,
                        detectSessionInUrl: true
                    }
                }
            );
        }

        const { data, error } = await supabaseClient.auth.exchangeCodeForSession(window.location.href);
        
        if (error) {
            throw error;
        }

        if (data.session) {
            console.log('✅ Session established successfully');
            
            // Show success message
            authStatusEl.style.display = 'none';
            authSuccessEl.style.display = 'block';
            
            // Redirect with smart routing
            setTimeout(() => {
                // Check for stored post-login redirect first
                const storedRedirect = sessionStorage.getItem('post_login_redirect');
                if (storedRedirect) {
                    sessionStorage.removeItem('post_login_redirect');
                    console.log('Auth callback: Using stored redirect:', storedRedirect);
                    const basePath = window.location.pathname.replace('/auth/callback/', '');
                    const baseUrl = window.location.origin + basePath;
                    const finalUrl = new URL(storedRedirect, baseUrl).toString();
                    window.location.href = finalUrl;
                    return;
                }
                
                let targetPath = redirectPath;
                
                // Validate redirect path with smart defaults
                if (!targetPath || !targetPath.startsWith('/') || targetPath.startsWith('//')) {
                    targetPath = '/dashboard/';
                }
                
                const basePath = window.location.pathname.replace('/auth/callback/', '');
                const baseUrl = window.location.origin + basePath;
                const finalUrl = new URL(targetPath, baseUrl).toString();
                
                console.log('Auth callback: Redirecting to:', finalUrl);
                window.location.href = finalUrl;
            }, 1500);
        } else {
            throw new Error('No session received');
        }
        
    } catch (error) {
        console.error('❌ Auth callback error:', error);
        
        // Show error message
        authStatusEl.style.display = 'none';
        authErrorEl.style.display = 'block';
        errorMessageEl.textContent = error.message || 'Authentication failed';
        
        // Set up retry button
        retryButtonEl.addEventListener('click', function() {
            window.location.href = window.authConfig.logout_redirect || '/';
        });
    }
}
</script>