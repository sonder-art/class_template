---
title: "Student Dashboard"
protected: true
---

# 🎓 Student Dashboard

<div id="debugBanner" style="display: none;" class="debug-banner">
    <strong>🔍 DEBUG MODE</strong>
    <span id="debugInfo"></span>
    <button onclick="exitDebugMode()">Exit Debug Mode</button>
</div>

<div id="studentDashboard">
<!-- Loading State -->
<div id="loadingState">
<div class="loading-message">
<p>🔄 Loading your dashboard...</p>
</div>
</div>

<!-- Main Dashboard (hidden initially) -->
<div id="dashboardContent" style="display: none;">

<!-- Student Header -->
<div class="dashboard-header">
<h2>Welcome back, <span id="studentName">Student</span>!</h2>
<p class="student-info">
<span id="githubUsername"></span> | 
<span id="className"></span>
</p>
</div>

<!-- Grade Overview Card -->
<div class="dashboard-section grade-overview">
<h3>📊 Your Grade</h3>
<div class="grade-display">
<div class="overall-grade">
<span class="grade-percentage" id="overallGrade">--</span>
<span class="grade-label">Overall</span>
</div>
<div class="grade-stats">
<div class="stat">
<span id="gradedCount">0</span>
<span>Graded</span>
</div>
<div class="stat">
<span id="pendingCount">0</span>
<span>Pending</span>
</div>
</div>
</div>
</div>

<!-- Upcoming Work -->
<div class="dashboard-section upcoming-work">
<h3>📌 Upcoming Assignments</h3>
<div id="upcomingList" class="upcoming-list">
<p>Loading assignments...</p>
</div>
</div>

<!-- Recent Grades -->
<div class="dashboard-section recent-grades">
<h3>✅ Recent Grades</h3>
<div id="recentGradesList" class="grades-list">
<p>Loading recent grades...</p>
</div>
</div>

<!-- Quick Actions -->
<div class="dashboard-section quick-actions">
<h3>⚡ Quick Actions</h3>
<div class="action-buttons">
<button onclick="navigateToGrades()">📊 View All Grades</button>
<button onclick="navigateToSubmit()">📤 Submit Assignment</button>
<button onclick="navigateToNotes()">📚 Class Notes</button>
</div>
</div>
</div>

<!-- Error State -->
<div id="errorState" style="display: none;">
<div class="error-message">
<h3>⚠️ Unable to Load Dashboard</h3>
<p id="errorMessage"></p>
<button onclick="window.location.reload()">🔄 Retry</button>
</div>
</div>
</div>

<script>
// Main dashboard initialization
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        initializeStudentDashboard();
    }, 500); // Small delay for auth state to be ready
});

async function initializeStudentDashboard() {
    // Check for debug session first
    const debugSession = sessionStorage.getItem('professor_debug_session');
    let targetStudentId = null;
    
    if (debugSession) {
        const session = JSON.parse(debugSession);
        
        // Check expiration
        if (new Date(session.expires_at) < new Date()) {
            sessionStorage.removeItem('professor_debug_session');
        } else {
            // Show debug banner
            document.getElementById('debugBanner').style.display = 'block';
            document.getElementById('debugInfo').textContent = 
                session.mode === 'self' 
                    ? 'Viewing as Professor (test data)' 
                    : `Viewing as Student ID: ${session.target_student_id}`;
            
            targetStudentId = session.mode === 'self' ? null : session.target_student_id;
        }
    }
    
    try {
        // Check authentication
        if (!window.authState || !window.authState.isAuthenticated) {
            showError('Please log in to view your dashboard');
            return;
        }
        
        // The framework's authState.client should already be initialized and authenticated
        
        // Load all dashboard data
        await Promise.all([
            loadStudentInfo(targetStudentId),
            loadGradeOverview(targetStudentId),
            loadUpcomingWork(),
            loadRecentGrades(targetStudentId)
        ]);
        
        // Show dashboard
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('dashboardContent').style.display = 'block';
        
    } catch (error) {
        console.error('Dashboard initialization failed:', error);
        showError(error.message);
    }
}

async function loadStudentInfo(targetStudentId) {
    const user = window.authState?.user;
    const userContext = window.authState?.userContext;
    
    if (user && userContext) {
        document.getElementById('studentName').textContent = 
            userContext.full_name || user.email?.split('@')[0] || 'Student';
        document.getElementById('githubUsername').textContent = 
            `@${userContext.github_username || 'unknown'}`;
        document.getElementById('className').textContent = 
            userContext.class_title || 'Class';
    }
}

async function loadGradeOverview(targetStudentId) {
    try {
        // Build URL with student_id if provided (for professor debug mode)
        let gradesUrl = 'https://levybxqsltedfjtnkntm.supabase.co/functions/v1/student-grades?level=module';
        if (targetStudentId) {
            gradesUrl += `&student_id=${targetStudentId}`;
        }
        
        const response = await fetch(gradesUrl, {
            headers: {
                'Authorization': `Bearer ${window.authState.session.access_token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            updateGradeDisplay(data);
        } else {
            console.warn('Failed to load grade overview:', response.status);
            // Show default/empty state
            updateGradeDisplay({ summary: { average_score: 0, total_grades: 0 } });
        }
    } catch (error) {
        console.error('Failed to load grade overview:', error);
        updateGradeDisplay({ summary: { average_score: 0, total_grades: 0 } });
    }
}

async function loadUpcomingWork() {
    try {
        // Use the framework's authenticated Supabase client
        if (!window.authState?.client) {
            console.warn('Framework Supabase client not available');
            document.getElementById('upcomingList').innerHTML = '<p>Unable to load upcoming assignments</p>';
            return;
        }
        
        const { data: items, error } = await window.authState.client
            .from('items')
            .select('id, title, points, due_date, constituent_slug')
            .gt('due_date', new Date().toISOString())
            .eq('is_current', true)
            .order('due_date', { ascending: true })
            .limit(5);
        
        if (!error && items) {
            displayUpcomingWork(items);
        } else {
            console.warn('No upcoming items found or error:', error);
            document.getElementById('upcomingList').innerHTML = '<p>No upcoming assignments found</p>';
        }
    } catch (error) {
        console.error('Failed to load upcoming work:', error);
        document.getElementById('upcomingList').innerHTML = '<p>Unable to load upcoming assignments</p>';
    }
}

async function loadRecentGrades(targetStudentId) {
    try {
        // Use the framework's authenticated Supabase client
        if (!window.authState?.client) {
            console.warn('Framework Supabase client not available');
            document.getElementById('recentGradesList').innerHTML = '<p>Unable to load recent grades</p>';
            return;
        }
        
        const studentId = targetStudentId || window.authState?.user?.id;
        if (!studentId) {
            document.getElementById('recentGradesList').innerHTML = '<p>Unable to determine student ID</p>';
            return;
        }
        
        const { data: submissions, error } = await window.authState.client
            .from('student_submissions')
            .select(`
                id,
                item_id,
                raw_score,
                adjusted_score,
                graded_at,
                items!inner (title, points, is_current)
            `)
            .eq('student_id', studentId)
            .eq('items.is_current', true)
            .not('graded_at', 'is', null)
            .order('graded_at', { ascending: false })
            .limit(5);
        
        if (!error && submissions) {
            displayRecentGrades(submissions);
        } else {
            console.warn('No recent grades found or error:', error);
            document.getElementById('recentGradesList').innerHTML = '<p>No graded items yet</p>';
        }
    } catch (error) {
        console.error('Failed to load recent grades:', error);
        document.getElementById('recentGradesList').innerHTML = '<p>Unable to load recent grades</p>';
    }
}

function updateGradeDisplay(gradeData) {
    const summary = gradeData.summary || {};
    const grades = gradeData.grades || [];
    
    // Update overall grade
    const overallGrade = summary.average_score || 0;
    const gradeEl = document.getElementById('overallGrade');
    gradeEl.textContent = `${overallGrade.toFixed(1)}%`;
    
    // Apply color based on grade
    if (overallGrade >= 90) gradeEl.style.color = 'var(--eva-green-primary)';
    else if (overallGrade >= 80) gradeEl.style.color = 'var(--eva-cyan-primary)';
    else if (overallGrade >= 70) gradeEl.style.color = 'var(--eva-yellow-primary)';
    else gradeEl.style.color = 'var(--eva-red-accent)';
    
    // Update counts
    document.getElementById('gradedCount').textContent = summary.total_grades || 0;
    document.getElementById('pendingCount').textContent = 0; // Will calculate from submissions later
}

function displayUpcomingWork(items) {
    const container = document.getElementById('upcomingList');
    
    if (items.length === 0) {
        container.innerHTML = '<p>No upcoming assignments</p>';
        return;
    }
    
    container.innerHTML = items.map(item => {
        const dueDate = new Date(item.due_date);
        const daysUntil = Math.ceil((dueDate - new Date()) / (1000 * 60 * 60 * 24));
        const urgency = daysUntil <= 1 ? 'urgent' : daysUntil <= 3 ? 'soon' : '';
        
        return `
            <div class="upcoming-item ${urgency}">
                <div class="item-info">
                    <strong>${item.title}</strong>
                    <span class="points">${item.points} pts</span>
                </div>
                <div class="due-info">
                    Due: ${dueDate.toLocaleDateString()}
                    ${daysUntil === 0 ? '(Today!)' : daysUntil === 1 ? '(Tomorrow)' : `(${daysUntil} days)`}
                </div>
            </div>
        `;
    }).join('');
}

function displayRecentGrades(submissions) {
    const container = document.getElementById('recentGradesList');
    
    if (submissions.length === 0) {
        container.innerHTML = '<p>No graded items yet</p>';
        return;
    }
    
    container.innerHTML = submissions.map(sub => {
        const score = sub.adjusted_score || sub.raw_score;
        const maxPoints = sub.items?.points || 100;
        const percentage = ((score / maxPoints) * 100).toFixed(1);
        
        return `
            <div class="grade-item">
                <div class="grade-info">
                    <strong>${sub.items?.title || 'Unknown'}</strong>
                    <span class="score">${score}/${maxPoints} (${percentage}%)</span>
                </div>
                <div class="grade-date">
                    ${new Date(sub.graded_at).toLocaleDateString()}
                </div>
            </div>
        `;
    }).join('');
}

// Navigation functions
function navigateToGrades() {
    // Use relative URL to work in all environments
    window.location.href = '../my-grades/';
}

function navigateToSubmit() {
    // Use relative URL to work in all environments
    window.location.href = '../upload/';
}

function navigateToNotes() {
    // Use relative URL to work in all environments  
    window.location.href = '../class_notes/';
}

function showError(message) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('dashboardContent').style.display = 'none';
    document.getElementById('errorState').style.display = 'block';
    document.getElementById('errorMessage').textContent = message;
}

// Keep existing debug mode functions
function exitDebugMode() {
    sessionStorage.removeItem('professor_debug_session');
    const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
    window.location.href = `${baseUrl}/dashboard/`;
}

function exitDebugMode() {
    sessionStorage.removeItem('professor_debug_session');
    const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
    window.location.href = `${baseUrl}/dashboard/`;
}
</script>

<!-- Additional styling for debug banner -->
<style>
.debug-banner {
    background-color: var(--eva-orange-primary);
    color: var(--bg-color);
    padding: 10px 20px;
    margin: 10px 0;
    border-radius: 6px;
    font-weight: bold;
    text-align: center;
    box-shadow: 0 2px 8px rgba(239, 134, 68, 0.3);
}

.debug-banner button {
    background-color: var(--bg-color);
    color: var(--eva-orange-primary);
    border: none;
    padding: 5px 10px;
    border-radius: 4px;
    margin-left: 10px;
    cursor: pointer;
    font-size: 0.9em;
}

.debug-banner button:hover {
    background-color: var(--surface-color);
}

.grade-widget {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.grade-item {
    background-color: var(--elevated-color);
    padding: 15px;
    border-radius: 6px;
    border: 1px solid var(--border-default);
    flex: 1;
    min-width: 200px;
}

.grade-label {
    display: block;
    color: var(--text-secondary);
    font-size: 0.9em;
    margin-bottom: 5px;
}

.grade-value {
    display: block;
    color: var(--eva-cyan-primary);
    font-size: 1.5em;
    font-weight: bold;
}

.error {
    color: var(--eva-red-accent);
    font-style: italic;
}
</style>