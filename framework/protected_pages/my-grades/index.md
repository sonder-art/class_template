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
<div class="header-main">
<div class="student-profile" id="studentInfo">
<div class="profile-avatar">👤</div>
<div class="profile-details">
<h2>Loading your information...</h2>
<p class="student-meta">GitHub Class Template</p>
</div>
</div>
<div class="header-controls">
<button class="refresh-btn" onclick="refreshGrades()" title="Refresh grades">
<span class="btn-icon">🔄</span>
<span class="btn-text">Refresh</span>
</button>
</div>
</div>

<div class="grade-summary-cards" id="gradeSummary">
<div class="summary-card overall-grade">
<div class="card-header">
<span class="card-icon">🎯</span>
<span class="card-title">Overall Grade</span>
</div>
<div class="grade-display">
<span class="grade-number">--</span>
<span class="grade-unit">%</span>
</div>
</div>

<div class="summary-card total-points">
<div class="card-header">
<span class="card-icon">📊</span>
<span class="card-title">Points Earned</span>
</div>
<div class="points-display">
<span class="points-earned">--</span>
<span class="points-separator">/</span>
<span class="points-total">--</span>
</div>
</div>

<div class="summary-card graded-items">
<div class="card-header">
<span class="card-icon">✅</span>
<span class="card-title">Modules Graded</span>
</div>
<div class="count-display">
<span class="count-number">--</span>
<span class="count-label">modules</span>
</div>
</div>

<div class="summary-card last-updated">
<div class="card-header">
<span class="card-icon">🕒</span>
<span class="card-title">Last Updated</span>
</div>
<div class="time-display">
<span class="time-text">Loading...</span>
</div>
</div>
</div>
</div>

<nav class="grades-navigation">
<div class="nav-tabs">
<button class="nav-tab active" data-tab="overview" data-icon="📊">
<span class="tab-icon">📊</span>
<span class="tab-label">Overview</span>
</button>
<button class="nav-tab" data-tab="modules" data-icon="📚">
<span class="tab-icon">📚</span>
<span class="tab-label">Modules</span>
</button>
<button class="nav-tab" data-tab="submissions" data-icon="📝">
<span class="tab-icon">📝</span>
<span class="tab-label">Submissions</span>
</button>
<button class="nav-tab" data-tab="progress" data-icon="📈">
<span class="tab-icon">📈</span>
<span class="tab-label">Progress</span>
</button>
</div>

<div class="nav-controls" id="navControls" style="display: none;">
<div class="search-box">
<input type="text" id="gradesSearch" placeholder="Search grades..." />
<span class="search-icon">🔍</span>
</div>
<div class="filter-dropdown">
<select id="gradeFilter">
<option value="">All Grades</option>
<option value="excellent">Excellent (A)</option>
<option value="good">Good (B)</option>
<option value="satisfactory">Satisfactory (C)</option>
<option value="needs-improvement">Needs Improvement</option>
</select>
</div>
</div>
</nav>

<div class="tab-panels">
<div class="tab-panel active" id="overview-panel">
<div id="overviewContent">
<div class="content-loading">
<div class="loading-spinner">🔄</div>
<p>Loading your grade overview...</p>
</div>
</div>
</div>

<div class="tab-panel" id="modules-panel">
<div id="modulesContent">
<div class="content-loading">
<div class="loading-spinner">🔄</div>
<p>Loading module grades...</p>
</div>
</div>
</div>

<div class="tab-panel" id="submissions-panel">
<div id="submissionsContent">
<div class="content-loading">
<div class="loading-spinner">🔄</div>
<p>Loading submissions...</p>
</div>
</div>
</div>

<div class="tab-panel" id="progress-panel">
<div id="progressContent">
<div class="content-loading">
<div class="loading-spinner">🔄</div>
<p>Loading progress data...</p>
</div>
</div>
</div>
</div>

</div>
</div>

<style>
/* Modern Grades Dashboard Styles */
.grades-interface {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* Header Section */
.grades-header {
    background: linear-gradient(135deg, var(--primary-color, #2E3440) 0%, var(--accent-color, #5E81AC) 100%);
    color: white;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.header-main {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
}

.student-profile {
    display: flex;
    align-items: center;
    gap: 1rem;
}

.profile-avatar {
    width: 60px;
    height: 60px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    backdrop-filter: blur(10px);
    position: relative;
    overflow: hidden;
}

.profile-avatar .avatar-img {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    object-fit: cover;
}

.profile-avatar .avatar-fallback {
    font-size: 1.5rem;
    color: rgba(255,255,255,0.8);
}

.profile-details h2 {
    margin: 0 0 0.25rem 0;
    font-size: 1.5rem;
    font-weight: 600;
}

.student-meta {
    margin: 0;
    opacity: 0.9;
    font-size: 0.9rem;
}

.header-controls .refresh-btn {
    background: rgba(255,255,255,0.2);
    color: white;
    border: none;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.3);
}

.header-controls .refresh-btn:hover {
    background: rgba(255,255,255,0.3);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
}

.header-controls .refresh-btn:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
}

/* Grade Summary Cards */
.grade-summary-cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
}

.summary-card {
    background: rgba(255,255,255,0.15);
    backdrop-filter: blur(10px);
    border-radius: 10px;
    padding: 1.25rem;
    border: 1px solid rgba(255,255,255,0.2);
    transition: transform 0.2s ease;
}

.summary-card:hover {
    transform: translateY(-2px);
}

.card-header {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
    font-size: 0.85rem;
    opacity: 0.9;
}

.card-icon {
    font-size: 1rem;
}

.grade-display {
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
}

.grade-number {
    font-size: 2.5rem;
    font-weight: 700;
    line-height: 1;
}

.grade-unit {
    font-size: 1.2rem;
    opacity: 0.8;
}

.points-display {
    display: flex;
    align-items: baseline;
    gap: 0.25rem;
    font-size: 1.5rem;
    font-weight: 600;
}

.points-separator {
    opacity: 0.6;
    margin: 0 0.25rem;
}

.count-display {
    display: flex;
    align-items: baseline;
    gap: 0.5rem;
}

.count-number {
    font-size: 2rem;
    font-weight: 600;
}

.count-label {
    opacity: 0.8;
    font-size: 0.9rem;
}

.time-display .time-text {
    font-size: 0.9rem;
    opacity: 0.9;
}

/* Navigation */
.grades-navigation {
    background: white;
    border-radius: 12px;
    padding: 1rem;
    margin-bottom: 2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
}

.nav-tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
}

.nav-tab {
    background: none;
    border: none;
    padding: 1rem 1.5rem;
    border-radius: 8px;
    cursor: pointer;
    font-size: 0.9rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.2s ease;
    color: var(--text-color, #333);
}

.nav-tab:hover {
    background: var(--accent-color-light, #E5F0FF);
    transform: translateY(-1px);
}

.nav-tab.active {
    background: var(--accent-color, #5E81AC);
    color: white;
    box-shadow: 0 2px 8px rgba(94, 129, 172, 0.3);
}

.tab-icon {
    font-size: 1rem;
}

.nav-controls {
    display: flex;
    gap: 1rem;
    align-items: center;
    padding-top: 1rem;
    border-top: 1px solid rgba(0,0,0,0.1);
}

.search-box {
    position: relative;
    flex: 1;
    max-width: 300px;
}

.search-box input {
    width: 100%;
    padding: 0.75rem 1rem 0.75rem 2.5rem;
    border: 2px solid rgba(0,0,0,0.1);
    border-radius: 8px;
    font-size: 0.9rem;
    transition: border-color 0.2s ease;
}

.search-box input:focus {
    outline: none;
    border-color: var(--accent-color, #5E81AC);
}

.search-icon {
    position: absolute;
    left: 0.75rem;
    top: 50%;
    transform: translateY(-50%);
    font-size: 0.9rem;
    opacity: 0.5;
}

.filter-dropdown select {
    padding: 0.75rem 1rem;
    border: 2px solid rgba(0,0,0,0.1);
    border-radius: 8px;
    font-size: 0.9rem;
    background: white;
    cursor: pointer;
    transition: border-color 0.2s ease;
}

.filter-dropdown select:focus {
    outline: none;
    border-color: var(--accent-color, #5E81AC);
}

/* Tab Panels */
.tab-panels {
    min-height: 400px;
}

.tab-panel {
    display: none;
}

.tab-panel.active {
    display: block;
}

.content-loading {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 4rem 2rem;
    text-align: center;
    color: var(--text-muted, #666);
}

.loading-spinner {
    font-size: 2rem;
    animation: spin 1s linear infinite;
    margin-bottom: 1rem;
}

@keyframes spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

/* Responsive Design */
@media (max-width: 768px) {
    .grades-header {
        padding: 1.5rem;
    }
    
    .header-main {
        flex-direction: column;
        gap: 1rem;
    }
    
    .grade-summary-cards {
        grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    }
    
    .nav-tabs {
        flex-wrap: wrap;
        gap: 0.25rem;
    }
    
    .nav-tab {
        padding: 0.75rem 1rem;
        font-size: 0.85rem;
    }
    
    .nav-controls {
        flex-direction: column;
        gap: 0.75rem;
    }
    
    .search-box {
        max-width: none;
    }
}

@media (max-width: 480px) {
    .grade-summary-cards {
        grid-template-columns: 1fr 1fr;
    }
    
    .nav-tab .tab-label {
        display: none;
    }
    
    .nav-tab {
        padding: 0.75rem;
        justify-content: center;
    }
}

/* Dark mode support */
@media (prefers-color-scheme: dark) {
    .grades-navigation {
        background: var(--dark-surface, #3B4252);
        border-color: var(--dark-border, #4C566A);
    }
    
    .nav-tab {
        color: var(--dark-text, #ECEFF4);
    }
    
    .nav-tab:hover {
        background: var(--dark-hover, #434C5E);
    }
    
    .search-box input,
    .filter-dropdown select {
        background: var(--dark-input, #3B4252);
        color: var(--dark-text, #ECEFF4);
        border-color: var(--dark-border, #4C566A);
    }
    
    .content-loading {
        color: var(--dark-text-muted, #D8DEE9);
    }
}

/* Enhanced Content Styles for New Design */

/* Overview Layout */
.overview-layout {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.overview-section {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.08);
    border: 1px solid rgba(0,0,0,0.05);
}

.section-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 2px solid rgba(0,0,0,0.05);
}

.section-header h3 {
    margin: 0;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-color, #333);
}

.item-count {
    font-size: 0.85rem;
    color: var(--text-muted, #666);
    background: rgba(0,0,0,0.05);
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
}

/* Recent Grades Grid */
.recent-grades-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1rem;
}

.grade-card {
    background: white;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    padding: 1rem;
    transition: all 0.2s ease;
    box-shadow: 0 1px 6px rgba(0,0,0,0.05);
}

.grade-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0,0,0,0.12);
    border-color: var(--accent-color, #5E81AC);
}

.grade-card .card-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.item-info h4 {
    margin: 0 0 0.25rem 0;
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-color, #333);
}

.item-path {
    margin: 0;
    font-size: 0.8rem;
    color: var(--text-muted, #666);
    opacity: 0.8;
}

.grade-badge {
    padding: 0.5rem 0.75rem;
    border-radius: 6px;
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
    text-align: center;
    min-width: 50px;
}

.grade-card .card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-muted, #666);
}

.points-detail {
    font-weight: 500;
}

.grade-date {
    opacity: 0.7;
}

/* Module Performance Cards */
.module-performance-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
}

.performance-card {
    background: white;
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 12px;
    padding: 1.5rem;
    transition: all 0.2s ease;
}

.performance-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(0,0,0,0.12);
}

.module-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
}

.module-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
}

.module-icon {
    font-size: 1.5rem;
}

.module-name {
    margin: 0 0 0.25rem 0;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--text-color, #333);
}

.module-progress-text {
    margin: 0;
    font-size: 0.85rem;
    color: var(--text-muted, #666);
}

.grade-display {
    text-align: right;
}

.grade-letter {
    display: block;
    font-size: 1.5rem;
    font-weight: 700;
    line-height: 1;
    margin-bottom: 0.25rem;
}

.grade-percentage {
    font-size: 0.9rem;
    opacity: 0.8;
}

.progress-bar-container {
    margin: 1rem 0;
}

.progress-bar {
    width: 100%;
    height: 8px;
    background: rgba(0,0,0,0.1);
    border-radius: 4px;
    overflow: hidden;
}

.progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.3s ease;
}

.module-stats {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.85rem;
    color: var(--text-muted, #666);
}

/* Quick Stats Grid */
.stats-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 1rem;
}

.stat-card {
    background: rgba(94, 129, 172, 0.05);
    border: 1px solid rgba(94, 129, 172, 0.1);
    border-radius: 10px;
    padding: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
    transition: all 0.2s ease;
}

.stat-card:hover {
    background: rgba(94, 129, 172, 0.1);
    transform: translateY(-1px);
}

.stat-card.stat-warning {
    background: rgba(239, 68, 68, 0.05);
    border-color: rgba(239, 68, 68, 0.2);
}

.stat-card.stat-warning:hover {
    background: rgba(239, 68, 68, 0.1);
}

.stat-icon {
    font-size: 1.5rem;
}

.stat-number {
    display: block;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--text-color, #333);
    line-height: 1;
    margin-bottom: 0.25rem;
}

.stat-label {
    font-size: 0.75rem;
    color: var(--text-muted, #666);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* Modules Grid */
.modules-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
    gap: 1.5rem;
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    color: var(--text-muted, #666);
}

.empty-icon {
    font-size: 4rem;
    margin-bottom: 1rem;
    opacity: 0.5;
}

.empty-state h3 {
    margin: 0 0 1rem 0;
    color: var(--text-color, #333);
}

.empty-state p {
    margin: 0;
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
}

/* Enhanced Responsive Design */
@media (max-width: 768px) {
    .overview-section {
        padding: 1rem;
    }
    
    .recent-grades-grid {
        grid-template-columns: 1fr;
    }
    
    .module-performance-grid {
        grid-template-columns: 1fr;
    }
    
    .stats-grid {
        grid-template-columns: repeat(2, 1fr);
    }
    
    .section-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }
}

@media (max-width: 480px) {
    .grade-card .card-header {
        flex-direction: column;
        gap: 0.75rem;
        align-items: stretch;
    }
    
    .grade-badge {
        align-self: flex-end;
        width: fit-content;
        margin-left: auto;
    }
    
    .module-header {
        flex-direction: column;
        gap: 1rem;
    }
    
    .grade-display {
        text-align: left;
        display: flex;
        align-items: center;
        gap: 1rem;
    }
    
    .grade-letter {
        margin-bottom: 0;
    }
    
    .stats-grid {
        grid-template-columns: 1fr;
    }
}

/* Dark mode enhancements */
@media (prefers-color-scheme: dark) {
    .overview-section,
    .grade-card,
    .performance-card {
        background: var(--dark-surface, #3B4252);
        border-color: var(--dark-border, #4C566A);
    }
    
    .section-header {
        border-bottom-color: var(--dark-border, #4C566A);
    }
    
    .item-count {
        background: rgba(255,255,255,0.1);
        color: var(--dark-text-muted, #D8DEE9);
    }
    
    .progress-bar {
        background: rgba(255,255,255,0.1);
    }
    
    .stat-card {
        background: rgba(136, 192, 208, 0.1);
        border-color: rgba(136, 192, 208, 0.2);
    }
    
    .stat-card:hover {
        background: rgba(136, 192, 208, 0.15);
    }
}
</style>

<script>
// Student grades page initialization - singleton pattern to prevent multiple instances
let studentGradesInstance = null;

document.addEventListener('DOMContentLoaded', function() {
    console.log('📊 Student grades page loaded');
    
    // Wait longer for DOM to be fully ready and auth state to initialize
    setTimeout(() => {
        console.log('🔄 Attempting to initialize student grades...');
        initializeStudentGrades();
    }, 1000); // Increased delay
    
    // Listen for auth state changes - but don't reinitialize if already loaded
    window.addEventListener('authStateChanged', function(event) {
        if (event.detail.user && !studentGradesInstance) {
            console.log('🔄 Auth state changed, initializing grades');
            // Add delay here too
            setTimeout(() => {
                initializeStudentGrades();
            }, 500);
        }
    });
});

/**
 * Initialize the student grades page (singleton pattern)
 */
async function initializeStudentGrades() {
    // If already initialized, don't create another instance
    if (studentGradesInstance) {
        console.log('✅ Student grades already initialized');
        showGradesSection('grades-interface');
        return;
    }

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
    
    // Initialize the student grades interface (singleton)
    if (window.StudentGradesInterface) {
        studentGradesInstance = new window.StudentGradesInterface();
        console.log('✅ Student grades interface created');
    } else {
        console.error('StudentGradesInterface not loaded');
        document.getElementById('grades-interface').innerHTML = 
            '<div class="error">StudentGradesInterface not available. Please refresh the page.</div>';
    }
}

/**
 * Manual refresh function for grades
 */
async function refreshGrades() {
    const refreshBtn = document.querySelector('.refresh-btn');
    
    if (!studentGradesInstance || typeof studentGradesInstance.refresh !== 'function') {
        console.warn('⚠️ Student grades instance not available for refresh');
        return;
    }
    
    // Disable button and show loading state
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = '⏳ Refreshing...';
    
    console.log('🔄 Manual grades refresh requested');
    
    try {
        await studentGradesInstance.refresh();
        console.log('✅ Grades refreshed successfully');
    } catch (error) {
        console.error('❌ Failed to refresh grades:', error);
    } finally {
        // Re-enable button
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '🔄 Refresh';
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