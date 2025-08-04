---
title: "Authentication Callback"
url: "/auth/callback/"
sitemap_ignore: true
robots: "noindex, nofollow"
---

# 🚨 UPDATED VERSION 4.0 - PROCESSING AUTHENTICATION 🚨

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
alert('🚨 JAVASCRIPT IS RUNNING - VERSION 4.0! 🚨');
try {
    console.log('🚨🚨🚨 JAVASCRIPT EXECUTING - v4.0 🚨🚨🚨');
    console.warn('🚨 WARNING MESSAGE TEST 🚨');
    console.error('🚨 ERROR MESSAGE TEST 🚨');
} catch(e) {
    alert('Console.log failed: ' + e.message);
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚨🚨🚨 DOM LOADED - LATEST VERSION LOADED - PKCE DEBUG v3.0 🚨🚨🚨');
    console.log('🔍 window.authConfig exists:', !!window.authConfig);
    console.log('🔍 window.supabase exists:', !!window.supabase);
    
    // Try direct call to new function
    console.log('🔄 Starting NEW auth callback DIRECTLY...');
    handleAuthCallbackNEW();
});

async function handleAuthCallbackNEW() {
    const authStatusEl = document.getElementById('authStatus');
    const authErrorEl = document.getElementById('authError');
    const authSuccessEl = document.getElementById('authSuccess');
    const errorMessageEl = document.getElementById('errorMessage');
    const retryButtonEl = document.getElementById('retryButton');

    try {
        console.warn('🔥 STARTING handleAuthCallbackNEW 🔥');
        
        // Check what's available
        console.warn('🔍 window.authState:', !!window.authState);
        console.warn('🔍 window.authState type:', typeof window.authState);
        console.warn('🔍 window.authState keys:', window.authState ? Object.keys(window.authState) : 'null');
        console.warn('🔍 window.authState.client:', !!window.authState?.client);
        console.warn('🔍 window.authConfig:', !!window.authConfig);
        console.warn('🔍 window.supabase:', !!window.supabase);
        
        // Check localStorage
        const authKeys = Object.keys(localStorage).filter(key => key.includes('supabase') || key.includes('auth'));
        console.warn('🔍 Auth localStorage keys:', authKeys);
        
        // Check specific localStorage values
        authKeys.forEach(key => {
            const value = localStorage.getItem(key);
            console.warn(`🔍 ${key}:`, value ? 'EXISTS' : 'NULL');
        });
        
        // Check URL
        const urlParams = new URLSearchParams(window.location.search);
        const authCode = urlParams.get('code');
        console.warn('🔍 Auth code from URL:', authCode);

        // Check if we actually have an auth code (real callback scenario)
        if (!authCode) {
            throw new Error('No auth code in URL - not a real OAuth callback');
        }

        console.warn('🔄 Waiting for automatic framework authentication...');
        
        // Wait and check if framework already processed the authentication
        for (let attempt = 0; attempt < 20; attempt++) {
            await new Promise(resolve => setTimeout(resolve, 250)); // Wait 250ms
            
            // Check if we now have a session (framework processed it)
            const currentSession = localStorage.getItem('sb-levybxqsltedfjtnkntm-auth-token');
            console.warn(`🔍 Attempt ${attempt + 1}: Session exists:`, !!currentSession);
            
            if (currentSession) {
                console.warn('✅ Framework automatically completed authentication!');
                const sessionData = JSON.parse(currentSession);
                
                if (sessionData.access_token) {
                    console.warn('🎉 Authentication successful! Access token found.');
                    
                    // Show success and redirect
                    authStatusEl.style.display = 'none';
                    authSuccessEl.style.display = 'block';
                    
                    setTimeout(() => {
                        const redirectUrl = new URLSearchParams(window.location.search).get('redirect') || 
                                          window.authConfig.protected_redirect || 
                                          '/';
                        console.warn('🔄 Redirecting to:', redirectUrl);
                        window.location.href = redirectUrl;
                    }, 2000);
                    
                    return; // Exit function - no manual processing needed
                }
            }
        }
        
        console.warn('⚠️ Framework did not complete authentication, trying manual processing...');
        
        // Fallback: Try manual processing (but this might fail due to consumed code)
        let supabaseClient;
        if (window.authState && window.authState.client) {
            console.warn('🔄 Using existing framework client...');
            supabaseClient = window.authState.client;
        } else {
            console.warn('⚠️ Creating fallback client...');
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

        console.warn('🔄 Manual exchangeCodeForSession...');
        const { data, error } = await supabaseClient.auth.exchangeCodeForSession(window.location.href);
        
        if (error) {
            throw error;
        }

        if (data.session) {
            console.log('✅ Session established successfully');
            
            // Show success message
            authStatusEl.style.display = 'none';
            authSuccessEl.style.display = 'block';
            
            // Redirect after a short delay
            setTimeout(() => {
                const redirectUrl = new URLSearchParams(window.location.search).get('redirect') || 
                                  window.authConfig.protected_redirect || 
                                  '/';
                console.log('🔄 Redirecting to:', redirectUrl);
                window.location.href = redirectUrl;
            }, 2000);
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