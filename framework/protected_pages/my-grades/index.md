---
title: "My Grades"
protected: true
---

# 📊 My Grades

View your current grades, submission history, and academic progress.

<!-- Authentication status check -->
<div id="authCheck" style="display: none;">
    <div class="auth-error">
        <h3>🔐 Authentication Required</h3>
        <p>Please log in to view your grades.</p>
        <button onclick="window.location.href='{{ .Site.BaseURL }}auth/login/'">Log In with GitHub</button>
    </div>
</div>

<!-- Not enrolled message -->
<div id="notEnrolled" style="display: none;">
    <div class="enrollment-error">
        <h3>🎓 Not Enrolled</h3>
        <p>You're not enrolled in this class. Please use an enrollment token to join.</p>
        <a href="{{ .Site.BaseURL }}enroll/">🔑 Enroll in Class</a>
    </div>
</div>

<!-- Main grades interface -->
<div id="grades-interface" style="display: none;">
    <div class="grades-header">
        <div class="student-info" id="studentInfo">
            <h3>Loading your information...</h3>
        </div>
        <div class="grade-summary" id="gradeSummary">
            <div class="loading">🔄 Calculating grades...</div>
        </div>
    </div>

<div class="grades-tabs">
    <button class="tab-btn active" data-tab="overview">📊 Overview</button>
    <button class="tab-btn" data-tab="modules">📚 By Module</button>
    <button class="tab-btn" data-tab="submissions">📝 Submissions</button>
    <button class="tab-btn" data-tab="progress">📈 Progress</button>
</div>

<div class="tab-content active" id="overview-tab">
    <div id="overviewContent">Loading overview...</div>
</div>

<div class="tab-content" id="modules-tab">
    <div id="modulesContent">Loading module grades...</div>
</div>

<div class="tab-content" id="submissions-tab">
    <div id="submissionsContent">Loading submissions...</div>
</div>

<div class="tab-content" id="progress-tab">
    <div id="progressContent">Loading progress...</div>
</div>
</div>

<script>
// Student grades page initialization
document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Student grades page loaded');
    
    // Wait for auth state to be ready
    setTimeout(() => {
        initializeStudentGrades();
    }, 500);
    
    // Listen for auth state changes
    window.addEventListener('authStateChanged', function(event) {
        if (event.detail.user) {
            console.log('🔄 Auth state changed, reinitializing grades');
            initializeStudentGrades();
        }
    });
});

/**
 * Initialize the student grades page
 */
async function initializeStudentGrades() {
    // Check authentication
    if (!window.authState || !window.authState.isAuthenticated) {
        console.warn('🚫 User not authenticated');
        showGradesSection('authCheck');
        return;
    }
    
    // Check if user context is available, if not fetch it
    let userContext = window.authState.userContext;
    if (!userContext) {
        console.log('🔄 Fetching user context...');
        try {
            await fetchStudentUserContext();
            userContext = window.authState.userContext;
        } catch (error) {
            console.error('❌ Failed to fetch user context:', error);
            showGradesSection('notEnrolled');
            return;
        }
    }
    
    // Check enrollment
    if (!userContext || !userContext.is_member) {
        console.warn('🚫 User not enrolled in class');
        showGradesSection('notEnrolled');
        return;
    }
    
    console.log('✅ Student access verified, loading grades interface');
    showGradesSection('grades-interface');
    
    // Initialize the student grades interface
    if (window.StudentGradesInterface) {
        new window.StudentGradesInterface();
    } else {
        console.error('StudentGradesInterface not loaded');
        document.getElementById('grades-interface').innerHTML = 
            '<div class="error">StudentGradesInterface not available. Please refresh the page.</div>';
    }
}

/**
 * Fetch user context for student
 */
async function fetchStudentUserContext() {
    if (!window.AuthClient) {
        throw new Error('AuthClient not available');
    }
    
    const pathParts = window.location.pathname.split('/');
    const classSlug = pathParts[1] || 'class_template';
    
    console.log('🌐 Fetching user context for class:', classSlug);
    const context = await window.AuthClient.getMe(classSlug);
    
    // Store in auth state
    window.authState.userContext = context;
    console.log('✅ User context fetched:', context);
}

/**
 * Show specific section and hide others
 */
function showGradesSection(sectionId) {
    const sections = ['authCheck', 'notEnrolled', 'grades-interface'];
    sections.forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.style.display = id === sectionId ? 'block' : 'none';
        }
    });
}
</script>