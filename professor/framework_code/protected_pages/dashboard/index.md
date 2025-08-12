---
title: "Dashboard"
protected: true
---

# 📊 Dashboard

Welcome to your class dashboard! This area requires authentication.

<!-- KEEP:START dashboard-content -->
## User Context

<div id="userContext">
    <p>🔄 Loading your profile and class information...</p>
</div>

## Role-Based Tools


<div id="professorTools" style="display: none;">
    <h3>👨‍🏫 Professor Tools</h3>
    <div class="dashboard-section">
        <h4>Class Management</h4>
        <ul>
            <li><button id="generateTokenBtn">🔗 Generate Enrollment Token</button></li>
            <li><button id="viewStudentsBtn">👥 View Class Roster</button></li>
            <li><a href="{{ .Site.BaseURL }}upload/">📁 Upload Files</a></li>
        </ul>
    </div>

<div id="enrollmentTokenSection" class="dashboard-section" style="display: none;">
    <h4>Enrollment Token</h4>
    <div id="tokenOutput" class="token-display"></div>
</div>

<div id="classRosterSection" class="dashboard-section" style="display: none;">
    <h4>Class Roster</h4>
    <div id="rosterList" class="roster-display"></div>
</div>
</div>

<div id="studentTools" style="display: none;">
    <h3>🎓 Student Tools</h3>
    <div class="dashboard-section">
        <h4>Class Resources</h4>
        <ul>
            <li><a href="{{ .Site.BaseURL }}class_notes/">📚 Class Notes</a></li>
            <li><a href="{{ .Site.BaseURL }}framework_tutorials/">📖 Tutorials</a></li>
            <li><a href="{{ .Site.BaseURL }}upload/">📤 Submit Assignment</a></li>
        </ul>
        
        <h4>Your Progress</h4>
        <div id="studentProgress">
            <p>Progress tracking coming soon...</p>
        </div>
    </div>
</div>

<div id="enrollmentTools" style="display: none;">
    <h3>🔑 Class Enrollment</h3>
    <div class="dashboard-section">
        <h4>Join This Class</h4>
        <p>You're not currently enrolled in this class. Enter an enrollment token provided by your instructor to join:</p>
        
        <div class="enrollment-form">
            <label for="dashboardEnrollmentToken">Enrollment Token:</label>
            <input type="text" 
                   id="dashboardEnrollmentToken" 
                   name="dashboardEnrollmentToken"
                   placeholder="Enter your enrollment token" 
                   autocomplete="off" />
            <button id="dashboardEnrollBtn">
                <span id="dashboardEnrollBtnText">🎓 Join Class</span>
                <span id="dashboardEnrollBtnSpinner" style="display: none;">🔄 Enrolling...</span>
            </button>
        </div>
        
        <div id="dashboardEnrollmentResult"></div>
        
        <div class="enrollment-help">
            <p><strong>💡 Need help?</strong></p>
            <ul>
                <li>Ask your instructor for an enrollment token</li>
                <li>Tokens are usually in format: XXXX-XXXX-XXXX-XXXX</li>
                <li>Each token can be used once or multiple times depending on settings</li>
            </ul>
        </div>
    </div>
</div>

<div id="errorSection" style="display: none;">
    <h3>⚠️ Connection Issue</h3>
    <div class="dashboard-section">
        <p>Unable to load your class information. You can still browse available content:</p>
        <ul>
            <li><a href="{{ .Site.BaseURL }}framework_documentation/">📋 Documentation</a></li>
            <li><a href="{{ .Site.BaseURL }}framework_tutorials/">📖 Tutorials</a></li>
        </ul>
        <button id="retryBtn">🔄 Retry</button>
    </div>
</div>
<!-- KEEP:END dashboard-content -->

<script>
// Dashboard Authentication and Role-Based UI
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Dashboard page loaded');
    
    // Wait for auth state to be ready
    setTimeout(() => {
        // Check authentication status
        if (!window.authState || !window.authState.isAuthenticated) {
            console.warn('🚫 Unauthorized access to dashboard - redirecting to login');
            // Use the base URL from auth config to ensure proper routing
            const baseUrl = window.authConfig?.base_url || '';
            const homeUrl = new URL('./', window.location.origin + baseUrl).toString();
            window.location.href = homeUrl;
            return;
        }
        
        console.log('✅ User authenticated, setting up dashboard');
        initializeDashboard();
    }, 500);
    
    // Listen for auth state changes
    window.addEventListener('authStateChanged', function(event) {
        if (event.detail.user) {
            console.log('🔄 Auth state changed, refreshing dashboard');
            initializeDashboard();
        }
    });
});

/**
 * Initialize dashboard with user context
 */
function initializeDashboard() {
    const userContext = window.authState?.userContext;
    const user = window.authState?.user;
    
    console.log('📋 Initializing dashboard with context:', userContext);
    
    // Update user context display
    updateUserContextDisplay(user, userContext);
    
    if (userContext) {
        // Show role-based tools based on user context
        showRoleBasedTools(userContext);
        setupRoleSpecificHandlers(userContext);
    } else {
        // Try to fetch user context if not available
        console.log('🔄 User context not available, attempting to fetch...');
        if (window.AuthClient) {
            fetchAndDisplayUserContext();
        } else {
            showErrorSection('AuthClient not available');
        }
    }
}

/**
 * Update the user context display section
 */
function updateUserContextDisplay(user, userContext) {
    const contextEl = document.getElementById('userContext');
    if (!contextEl) return;
    
    if (userContext) {
        contextEl.innerHTML = `
            <div class="user-card">
                <h4>👤 ${user.email}</h4>
                <p><strong>GitHub:</strong> @${userContext.github_username || 'Unknown'}</p>
                <p><strong>Role:</strong> ${userContext.role || 'Unknown'}</p>
                <p><strong>Class:</strong> ${userContext.class_title || 'Not enrolled'}</p>
                <p><strong>Status:</strong> ${userContext.is_member ? '✅ Active Member' : '❌ Not enrolled'}</p>
            </div>
        `;
    } else {
        contextEl.innerHTML = `
            <div class="user-card">
                <h4>👤 ${user.email}</h4>
                <p>🔄 Loading class information...</p>
            </div>
        `;
    }
}

/**
 * Show appropriate tools based on user role
 */
function showRoleBasedTools(userContext) {
    // Hide all sections first
    hideAllSections();
    
    if (!userContext.is_member) {
        // User is not a member of this class
        document.getElementById('enrollmentTools').style.display = 'block';
    } else if (userContext.role === 'professor') {
        // Show professor tools
        document.getElementById('professorTools').style.display = 'block';
    } else if (userContext.role === 'student') {
        // Show student tools
        document.getElementById('studentTools').style.display = 'block';
    } else {
        // Unknown role but is a member
        document.getElementById('studentTools').style.display = 'block';
    }
}

/**
 * Hide all role-based sections
 */
function hideAllSections() {
    document.getElementById('professorTools').style.display = 'none';
    document.getElementById('studentTools').style.display = 'none';
    document.getElementById('enrollmentTools').style.display = 'none';
    document.getElementById('errorSection').style.display = 'none';
}

/**
 * Setup event handlers for role-specific buttons
 */
function setupRoleSpecificHandlers(userContext) {
    if (userContext.role === 'professor') {
        setupProfessorHandlers();
    } else if (!userContext.is_member) {
        setupEnrollmentHandlers();
    }
    
    // Setup retry button
    const retryBtn = document.getElementById('retryBtn');
    if (retryBtn) {
        retryBtn.onclick = () => {
            console.log('🔄 Retrying user context fetch');
            fetchAndDisplayUserContext();
        };
    }
}

/**
 * Setup professor-specific button handlers
 */
function setupProfessorHandlers() {
    const generateTokenBtn = document.getElementById('generateTokenBtn');
    const viewStudentsBtn = document.getElementById('viewStudentsBtn');
    
    if (generateTokenBtn) {
        generateTokenBtn.onclick = async () => {
            console.log('🔗 Generating enrollment token...');
            
            try {
                // Show loading state
                generateTokenBtn.disabled = true;
                generateTokenBtn.textContent = '🔄 Generating...';
                
                // Get current class slug
                const pathParts = window.location.pathname.split('/');
                const classSlug = pathParts[1] || 'class_template';
                
                // Generate token with default settings (30 days, unlimited uses)
                const result = await window.AuthClient.generateToken(classSlug, {
                    expiresInDays: 30,
                    maxUses: 0 // 0 means unlimited
                });
                
                // Display the token
                const tokenOutput = document.getElementById('tokenOutput');
                const expiresDate = new Date(result.expires_at).toLocaleDateString();
                const usageInfo = result.max_uses > 0 ? `${result.max_uses} uses` : 'Unlimited uses';
                
                tokenOutput.innerHTML = `
                    <div class="token-success">
                        <h5>✅ Token Generated Successfully!</h5>
                        <div class="token-code">
                            <code id="generatedToken">${result.token}</code>
                            <button id="copyTokenBtn" onclick="copyToken()" title="Copy token">📋</button>
                        </div>
                        <div class="token-details">
                            <p><strong>Expires:</strong> ${expiresDate}</p>
                            <p><strong>Usage:</strong> ${usageInfo}</p>
                            <p class="token-instructions">
                                💡 Share this token with students so they can join the class at 
                                <strong>/enroll/</strong>
                            </p>
                        </div>
                    </div>
                `;
                
                // Show the token section
                document.getElementById('enrollmentTokenSection').style.display = 'block';
                
            } catch (error) {
                console.error('❌ Token generation failed:', error);
                
                // Show error message
                document.getElementById('tokenOutput').innerHTML = `
                    <div class="token-error">
                        <h5>❌ Token Generation Failed</h5>
                        <p>Error: ${error.message}</p>
                        <p>Please try again or check your permissions.</p>
                    </div>
                `;
                document.getElementById('enrollmentTokenSection').style.display = 'block';
                
            } finally {
                // Reset button state
                generateTokenBtn.disabled = false;
                generateTokenBtn.textContent = '🔗 Generate Enrollment Token';
            }
        };
    }
    
    if (viewStudentsBtn) {
        viewStudentsBtn.onclick = () => {
            console.log('👥 Loading class roster...');
            // TODO: Implement roster viewing
            document.getElementById('rosterList').innerHTML = 
                '<p>Class roster viewing coming in Module 5...</p>';
            document.getElementById('classRosterSection').style.display = 'block';
        };
    }
}

/**
 * Setup enrollment button handlers for dashboard enrollment
 */
function setupEnrollmentHandlers() {
    const enrollBtn = document.getElementById('dashboardEnrollBtn');
    const tokenInput = document.getElementById('dashboardEnrollmentToken');
    const resultDiv = document.getElementById('dashboardEnrollmentResult');
    
    if (enrollBtn && tokenInput && resultDiv) {
        enrollBtn.onclick = async () => {
            const token = tokenInput.value.trim();
            if (!token) {
                resultDiv.innerHTML = 
                    '<div class="enrollment-error">❌ Please enter an enrollment token</div>';
                return;
            }
            
            console.log('🔑 Attempting to enroll with token:', token);
            
            // Show loading state
            const btnText = document.getElementById('dashboardEnrollBtnText');
            const btnSpinner = document.getElementById('dashboardEnrollBtnSpinner');
            
            if (btnText) btnText.style.display = 'none';
            if (btnSpinner) btnSpinner.style.display = 'inline';
            enrollBtn.disabled = true;
            
            try {
                // Get current class slug
                const pathParts = window.location.pathname.split('/');
                const classSlug = pathParts[1] || 'class_template';
                
                // Call enrollment API
                const result = await window.AuthClient.enroll(classSlug, token);
                
                console.log('✅ Enrollment successful:', result);
                
                // Show success message
                resultDiv.innerHTML = 
                    '<div class="enrollment-success">🎉 ' + result.message + '</div>';
                
                // Clear the token input
                tokenInput.value = '';
                
                // Refresh the dashboard after a short delay to show new user context
                setTimeout(() => {
                    window.location.reload();
                }, 2000);
                
            } catch (error) {
                console.error('❌ Enrollment failed:', error);
                resultDiv.innerHTML = 
                    `<div class="enrollment-error">❌ ${error.message}</div>`;
            } finally {
                // Reset button state
                if (btnText) btnText.style.display = 'inline';
                if (btnSpinner) btnSpinner.style.display = 'none';
                enrollBtn.disabled = false;
            }
        };
        
        // Allow Enter key to submit
        tokenInput.onkeypress = (e) => {
            if (e.key === 'Enter') {
                enrollBtn.click();
            }
        };
    }
}


/**
 * Fetch user context and update dashboard
 */
async function fetchAndDisplayUserContext() {
    try {
        const pathParts = window.location.pathname.split('/');
        const classSlug = pathParts[1] || 'class_template';
        
        console.log('🌐 Fetching user context for class:', classSlug);
        const context = await window.AuthClient.getMe(classSlug);
        
        // Store in auth state
        window.authState.userContext = context;
        
        console.log('✅ User context fetched:', context);
        
        // Update dashboard
        updateUserContextDisplay(window.authState.user, context);
        showRoleBasedTools(context);
        setupRoleSpecificHandlers(context);
        
    } catch (error) {
        console.error('❌ Failed to fetch user context:', error);
        showErrorSection(error.message);
    }
}

/**
 * Show error section when API calls fail
 */
function showErrorSection(errorMessage) {
    hideAllSections();
    document.getElementById('errorSection').style.display = 'block';
    
    // Update user context to show error
    const contextEl = document.getElementById('userContext');
    if (contextEl) {
        contextEl.innerHTML = `
            <div class="user-card error">
                <h4>⚠️ Connection Error</h4>
                <p>Unable to load class information: ${errorMessage}</p>
            </div>
        `;
    }
}

/**
 * Copy enrollment token to clipboard
 */
function copyToken() {
    const tokenElement = document.getElementById('generatedToken');
    if (tokenElement) {
        const token = tokenElement.textContent;
        
        // Use the modern clipboard API if available
        if (navigator.clipboard && window.isSecureContext) {
            navigator.clipboard.writeText(token).then(() => {
                showTokenCopyFeedback('✅ Token copied to clipboard!');
            }).catch(() => {
                fallbackCopyToken(token);
            });
        } else {
            fallbackCopyToken(token);
        }
    }
}

/**
 * Fallback method for copying token (older browsers)
 */
function fallbackCopyToken(token) {
    // Create temporary textarea
    const textarea = document.createElement('textarea');
    textarea.value = token;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    document.body.appendChild(textarea);
    
    // Select and copy
    textarea.select();
    try {
        document.execCommand('copy');
        showTokenCopyFeedback('✅ Token copied to clipboard!');
    } catch (error) {
        showTokenCopyFeedback('❌ Failed to copy token');
    }
    
    // Clean up
    document.body.removeChild(textarea);
}

/**
 * Show copy feedback message
 */
function showTokenCopyFeedback(message) {
    const copyBtn = document.getElementById('copyTokenBtn');
    if (copyBtn) {
        const originalText = copyBtn.textContent;
        copyBtn.textContent = message.includes('✅') ? '✅' : '❌';
        copyBtn.disabled = true;
        
        setTimeout(() => {
            copyBtn.textContent = '📋';
            copyBtn.disabled = false;
        }, 2000);
    }
}

/**
 * Debug function to test token generation with detailed logging
 */
window.debugTokenGeneration = async function() {
    console.log('🐛 DEBUG: Starting token generation test...');
    
    // Check auth state
    console.log('🔍 Auth State Check:');
    console.log('  - isAuthenticated:', window.authState?.isAuthenticated);
    console.log('  - user:', window.authState?.user?.email);
    console.log('  - userContext:', window.authState?.userContext);
    console.log('  - session token length:', window.authState?.session?.access_token?.length);
    
    // Test class slug detection
    const classSlug = window.AuthClient.getCurrentClassSlug();
    console.log('  - detected class slug:', classSlug);
    
    try {
        console.log('🔗 Making API call to generate-token...');
        const result = await window.AuthClient.generateToken(classSlug, {
            expiresInDays: 1,
            maxUses: 5
        });
        console.log('✅ SUCCESS:', result);
        return result;
    } catch (error) {
        console.error('❌ DETAILED ERROR:', error);
        console.error('❌ ERROR MESSAGE:', error.message);
        console.error('❌ ERROR STACK:', error.stack);
        return { error: error.message };
    }
};
</script>

<!-- Dashboard styling is handled by evangelion theme components/dashboard.css -->