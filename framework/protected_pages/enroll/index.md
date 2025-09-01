---
title: "Join Class"
---

# 🎓 Join This Class

Welcome! To join this class, you'll need an enrollment token from your instructor.

## How to Enroll

1. **Get an enrollment token** from your instructor (format: XXXX-XXXX-XXXX-XXXX)
2. **Login with GitHub** (required for class access)  
3. **Enter your token** in the form below
4. **Start learning!** Access class materials and submit assignments

## Need Help?

- **No token?** Contact your instructor: {{ .Site.Params.professor_name }} ({{ .Site.Params.professor_email }})
- **Technical issues?** Make sure you're logged in with the GitHub account you want to use for this class
- **Lost token?** Your instructor can generate a new one for you

<!-- KEEP:START enrollment-content -->
<div id="enrollmentStatus">
<p>🔄 Checking your enrollment status...</p>
</div>

<div id="enrollmentForm" style="display: none;">
<div class="enrollment-card">
<h3>📝 Enter Enrollment Token</h3>
<p>Your instructor should have provided you with an enrollment token. Enter it below to join the class.</p>

<form id="tokenForm">
<div class="form-group">
<label for="enrollmentToken">Enrollment Token:</label>
<input type="text" id="enrollmentToken" name="enrollmentToken" 
       placeholder="Enter your enrollment token" 
       required autocomplete="off">
</div>

<div class="form-actions">
<button type="submit" id="enrollBtn">
<span id="enrollBtnText">🎓 Join Class</span>
<span id="enrollBtnSpinner" style="display: none;">🔄 Enrolling...</span>
</button>
</div>
</form>

<div id="enrollmentResult"></div>
</div>
</div>

<div id="alreadyEnrolled" style="display: none;">
<div class="status-card success">
<h3>✅ Already Enrolled</h3>
<p>You're already a member of this class!</p>
<div class="form-actions">
<a href="{{ .Site.BaseURL }}dashboard/" class="btn-primary">Go to Dashboard</a>
</div>
</div>
</div>

<div id="enrollmentError" style="display: none;">
<div class="status-card error">
<h3>⚠️ Unable to Load Enrollment</h3>
<p>There was an error checking your enrollment status. Please try refreshing the page.</p>
<div class="form-actions">
<button id="retryBtn" class="btn-secondary">🔄 Retry</button>
</div>
</div>
</div>
<!-- KEEP:END enrollment-content -->

<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log('🎓 Enrollment page loaded');
    
    // Wait for auth state to be ready
    setTimeout(() => {
        // Check authentication status
        if (!window.authState || !window.authState.isAuthenticated) {
            console.log('🔐 User not authenticated, showing login prompt');
            showLoginPrompt();
            return;
        }
        
        console.log('✅ User authenticated, checking enrollment status');
        checkEnrollmentStatus();
    }, 500);
});

/**
 * Show login prompt for unauthenticated users
 */
function showLoginPrompt() {
    const statusEl = document.getElementById('enrollmentStatus');
    const formEl = document.getElementById('enrollmentForm');
    const enrolledEl = document.getElementById('alreadyEnrolled');
    const errorEl = document.getElementById('enrollmentError');
    
    // Hide other sections
    formEl.style.display = 'none';
    enrolledEl.style.display = 'none';
    errorEl.style.display = 'none';
    
    // Show login prompt
    statusEl.innerHTML = `
        <div class="enrollment-card">
            <h3>🔐 Login Required</h3>
            <p>To join this class, you need to login with your GitHub account first.</p>
            <p>This allows us to:</p>
            <ul style="text-align: left; margin: 1rem 0;">
                <li>Verify your identity</li>
                <li>Track your progress and submissions</li>
                <li>Provide personalized access to class materials</li>
            </ul>
            <div class="form-actions">
                <button onclick="loginAndReturnToEnroll()" class="btn-primary">
                    🔐 Login with GitHub
                </button>
            </div>
        </div>
    `;
}

/**
 * Login and return to enrollment
 */
function loginAndReturnToEnroll() {
    if (window.supabaseAuth && window.supabaseAuth.login) {
        // Store current page to return after login
        sessionStorage.setItem('post_login_redirect', window.location.pathname + window.location.search);
        window.supabaseAuth.login();
    } else {
        alert('Authentication system not ready. Please refresh the page and try again.');
    }
}

/**
 * Check if user is already enrolled in this class
 */
async function checkEnrollmentStatus() {
    try {
        console.log('🔍 Checking enrollment status...');
        
        if (!window.AuthClient) {
            throw new Error('AuthClient not available');
        }
        
        // Get current class slug from auth config
        const baseUrl = window.authConfig?.base_url || '';
        let classSlug = 'class_template'; // default
        if (baseUrl) {
            try {
                const url = new URL(baseUrl);
                const pathSegments = url.pathname.split('/').filter(s => s);
                classSlug = pathSegments[pathSegments.length - 1] || 'class_template';
            } catch {
                // Fallback to default if URL parsing fails
                classSlug = 'class_template';
            }
        }
        
        // Check current enrollment status
        const context = await window.AuthClient.getMe(classSlug);
        console.log('📋 User context:', context);
        
        // Update enrollment status display
        updateEnrollmentStatusDisplay(context);
        
    } catch (error) {
        console.error('❌ Error checking enrollment status:', error);
        showEnrollmentError(error.message);
    }
}

/**
 * Update the enrollment status display based on user context
 */
function updateEnrollmentStatusDisplay(userContext) {
    const statusEl = document.getElementById('enrollmentStatus');
    const formEl = document.getElementById('enrollmentForm');
    const enrolledEl = document.getElementById('alreadyEnrolled');
    const errorEl = document.getElementById('enrollmentError');
    
    // Hide status loading message
    statusEl.style.display = 'none';
    
    if (userContext && userContext.is_member) {
        // User is already enrolled
        console.log('✅ User already enrolled as:', userContext.role);
        enrolledEl.style.display = 'block';
        formEl.style.display = 'none';
        errorEl.style.display = 'none';
    } else {
        // User needs to enroll
        console.log('📝 User needs to enroll');
        formEl.style.display = 'block';
        enrolledEl.style.display = 'none';
        errorEl.style.display = 'none';
        setupEnrollmentForm();
    }
}

/**
 * Show error state
 */
function showEnrollmentError(errorMessage) {
    const statusEl = document.getElementById('enrollmentStatus');
    const formEl = document.getElementById('enrollmentForm');
    const enrolledEl = document.getElementById('alreadyEnrolled');
    const errorEl = document.getElementById('enrollmentError');
    
    statusEl.style.display = 'none';
    formEl.style.display = 'none';
    enrolledEl.style.display = 'none';
    errorEl.style.display = 'block';
    
    // Setup retry button
    const retryBtn = document.getElementById('retryBtn');
    if (retryBtn) {
        retryBtn.onclick = () => {
            console.log('🔄 Retrying enrollment status check');
            checkEnrollmentStatus();
        };
    }
}

/**
 * Setup enrollment form handlers
 */
function setupEnrollmentForm() {
    const form = document.getElementById('tokenForm');
    const tokenInput = document.getElementById('enrollmentToken');
    const enrollBtn = document.getElementById('enrollBtn');
    const btnText = document.getElementById('enrollBtnText');
    const btnSpinner = document.getElementById('enrollBtnSpinner');
    const resultDiv = document.getElementById('enrollmentResult');
    
    if (!form || !tokenInput || !enrollBtn) return;
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const token = tokenInput.value.trim();
        if (!token) {
            showEnrollmentMessage('Please enter an enrollment token', 'error');
            return;
        }
        
        try {
            console.log('🎓 Attempting enrollment with token...');
            
            // Show loading state
            enrollBtn.disabled = true;
            btnText.style.display = 'none';
            btnSpinner.style.display = 'inline';
            resultDiv.innerHTML = '';
            
            // Get current class slug from auth config
            const baseUrl = window.authConfig?.base_url || '';
            let classSlug = 'class_template'; // default
            if (baseUrl) {
                try {
                    const url = new URL(baseUrl);
                    const pathSegments = url.pathname.split('/').filter(s => s);
                    classSlug = pathSegments[pathSegments.length - 1] || 'class_template';
                } catch {
                    // Fallback to default if URL parsing fails
                    classSlug = 'class_template';
                }
            }
            
            // Call enrollment API
            console.log('🎓 Attempting enrollment with class slug:', classSlug);
            const result = await window.AuthClient.enroll(classSlug, token);
            console.log('✅ Enrollment successful:', result);
            
            // Show success message
            showEnrollmentMessage('🎉 Successfully enrolled in the class!', 'success');
            
            // Redirect to dashboard after a short delay
            setTimeout(() => {
                // Use the base URL from auth config to ensure proper routing
                const baseUrl = window.authConfig?.base_url || '';
                const dashboardUrl = new URL('dashboard/', window.location.origin + baseUrl).toString();
                window.location.href = dashboardUrl;
            }, 2000);
            
        } catch (error) {
            console.error('❌ Enrollment failed:', error);
            showEnrollmentMessage(`❌ Enrollment failed: ${error.message}`, 'error');
        } finally {
            // Reset button state
            enrollBtn.disabled = false;
            btnText.style.display = 'inline';
            btnSpinner.style.display = 'none';
        }
    });
    
    // Allow Enter key to submit
    tokenInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !enrollBtn.disabled) {
            form.requestSubmit();
        }
    });
}

/**
 * Show enrollment result message
 */
function showEnrollmentMessage(message, type = 'info') {
    const resultDiv = document.getElementById('enrollmentResult');
    if (resultDiv) {
        resultDiv.innerHTML = `<p class="message ${type}">${message}</p>`;
    }
}
</script>

<!-- Enrollment styling is handled by evangelion theme components/enrollment.css -->