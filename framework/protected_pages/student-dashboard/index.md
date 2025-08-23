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
    <h2>Welcome, <span id="studentName">Student</span>!</h2>
    
<div class="dashboard-section">
<h3>📊 Grade Summary</h3>
<div id="gradeSummary">Loading grades...</div>
</div>

<div class="dashboard-section">
<h3>📝 Recent Submissions</h3>
<div id="recentSubmissions">Loading submissions...</div>
</div>

<div class="dashboard-section">
<h3>⚡ Quick Actions</h3>
<button onclick="window.location.href='{{ .Site.BaseURL }}upload/'">📤 Submit Assignment</button>
<button onclick="window.location.href='{{ .Site.BaseURL }}my-grades/'">📊 View Detailed Grades</button>
<button onclick="window.location.href='{{ .Site.BaseURL }}class_notes/'">📚 Class Notes</button>
</div>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    // Wait a bit for auth state to be ready
    setTimeout(() => {
        initializeStudentDashboard();
    }, 1000);
});

async function initializeStudentDashboard() {
    // Check for debug session
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
    
    // Load student data
    await loadStudentData(targetStudentId);
}

async function loadStudentData(studentId) {
    try {
        // Check if required elements exist
        const gradeSummaryEl = document.getElementById('gradeSummary');
        const studentNameEl = document.getElementById('studentName');
        const recentSubmissionsEl = document.getElementById('recentSubmissions');
        
        if (!gradeSummaryEl || !studentNameEl || !recentSubmissionsEl) {
            console.error('Required DOM elements not found');
            return;
        }

        // Check if we have a valid auth session
        if (!window.authState || !window.authState.session || !window.authState.session.access_token) {
            console.log('No auth session available, showing offline mode');
            showOfflineMode();
            return;
        }
        
        // Build URL with student_id if provided
        let gradesUrl = 'https://levybxqsltedfjtnkntm.supabase.co/functions/v1/student-grades?level=module';
        if (studentId) {
            gradesUrl += `&student_id=${studentId}`;
        }
        
        const response = await fetch(gradesUrl, {
            headers: {
                'Authorization': `Bearer ${window.authState.session.access_token}`,
                'Content-Type': 'application/json'
            }
        });
        
        if (response.ok) {
            const data = await response.json();
            displayGradeSummary(data.summary);
        } else {
            console.log(`API request failed with status ${response.status}, showing offline mode`);
            showOfflineMode();
            return;
        }
        
        // Update student name
        const userContext = window.authState?.userContext;
        if (userContext) {
            studentNameEl.textContent = 
                userContext.full_name || userContext.github_username || 'Student';
        }
        
        // Load recent submissions placeholder
        recentSubmissionsEl.innerHTML = 
            '<p>View your recent submissions in the <a href="{{ .Site.BaseURL }}my-grades/">grades page</a>.</p>';
        
    } catch (error) {
        console.log('Failed to load student data, showing offline mode:', error.message);
        showOfflineMode();
    }
}

function showOfflineMode() {
    // Show mock data when offline
    const studentNameEl = document.getElementById('studentName');
    const gradeSummaryEl = document.getElementById('gradeSummary');
    const recentSubmissionsEl = document.getElementById('recentSubmissions');
    
    if (studentNameEl) studentNameEl.textContent = 'Professor (Test Mode)';
    
    if (gradeSummaryEl) {
        gradeSummaryEl.innerHTML = `
            <div class="grade-widget">
                <div class="grade-item">
                    <span class="grade-label">Overall Grade:</span>
                    <span class="grade-value">85.2%</span>
                    <small style="display: block; color: #666; margin-top: 5px;">[Test Data - API Offline]</small>
                </div>
                <div class="grade-item">
                    <span class="grade-label">Graded Items:</span>
                    <span class="grade-value">12</span>
                    <small style="display: block; color: #666; margin-top: 5px;">[Test Data - API Offline]</small>
                </div>
            </div>
        `;
    }
    
    if (recentSubmissionsEl) {
        recentSubmissionsEl.innerHTML = `
            <div style="background: #fff3cd; padding: 10px; border-radius: 4px; border: 1px solid #ffeaa7;">
                <strong>⚠️ API Connection Issue</strong><br>
                Showing test data. In a real environment, this would show your recent submissions.
            </div>
        `;
    }
}

function showErrorState(errorMessage) {
    const gradeSummaryEl = document.getElementById('gradeSummary');
    if (gradeSummaryEl) {
        gradeSummaryEl.innerHTML = `
            <div class="error">
                <p><strong>Unable to load grade data</strong></p>
                <p>Error: ${errorMessage}</p>
                <button onclick="window.location.reload()">🔄 Retry</button>
            </div>
        `;
    }
}

function displayGradeSummary(summary) {
    const html = `
        <div class="grade-widget">
            <div class="grade-item">
                <span class="grade-label">Overall Grade:</span>
                <span class="grade-value">${summary?.average_score?.toFixed(1) || 'N/A'}%</span>
            </div>
            <div class="grade-item">
                <span class="grade-label">Graded Items:</span>
                <span class="grade-value">${summary?.total_grades || 0}</span>
            </div>
        </div>
    `;
    document.getElementById('gradeSummary').innerHTML = html;
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