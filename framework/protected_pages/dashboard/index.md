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
            <li><button id="manageTokensBtn">🔧 Manage Enrollment Tokens</button></li>
            <li><button id="uploadFilesBtn">📁 Upload Files</button></li>
        </ul>
    </div>

<div class="dashboard-section">
    <h4>📊 Grading & Assessments</h4>
    <ul>
        <li><button id="openGradingBtn">📊 Grading Interface</button></li>
        <li><button id="openGradingSyncBtn">🔄 Sync Grading System</button></li>
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

<div id="tokenManagementSection" class="dashboard-section" style="display: none;">
    <h4>Token Management</h4>
    <div id="tokenManagementContent" class="token-management-display"></div>
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
</div>

<div class="dashboard-section">
    <h4>📊 Academic Progress</h4>
    <ul>
        <li><button id="viewMyGradesBtn">📊 View My Grades</button></li>
        <li><button id="mySubmissionsBtn">📝 My Submissions</button></li>
    </ul>
    
<div id="studentProgress">
    <p>🔄 Loading your grade summary...</p>
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
                <h4>👤 @${user.user_metadata?.user_name || userContext.github_username || 'Unknown'}</h4>
                <p><strong>Email:</strong> ${user.email}</p>
                <p><strong>Role:</strong> ${userContext.role || 'Unknown'}</p>
                <p><strong>Class:</strong> ${userContext.class_title || 'Not enrolled'}</p>
                <p><strong>Status:</strong> ${userContext.is_member ? '✅ Active Member' : '❌ Not enrolled'}</p>
            </div>
        `;
    } else {
        contextEl.innerHTML = `
            <div class="user-card">
                <h4>👤 @${user.user_metadata?.user_name || 'Unknown'}</h4>
                <p><strong>Email:</strong> ${user.email}</p>
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
    } else if (userContext.role === 'student' && userContext.is_member) {
        setupStudentHandlers();
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
    const manageTokensBtn = document.getElementById('manageTokensBtn');
    const uploadFilesBtn = document.getElementById('uploadFilesBtn');
    
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
        viewStudentsBtn.onclick = async () => {
            console.log('👥 Loading class roster...');
            
            try {
                // Show loading state
                viewStudentsBtn.disabled = true;
                viewStudentsBtn.textContent = '🔄 Loading...';
                
                // Get current class slug with debugging
                const pathParts = window.location.pathname.split('/');
                console.log('🔍 DEBUG: Current URL:', window.location.href);
                console.log('🔍 DEBUG: Pathname:', window.location.pathname);
                console.log('🔍 DEBUG: Path parts:', pathParts);
                
                const classSlug = pathParts[1] || 'class_template';
                console.log('🔍 DEBUG: Detected class slug:', classSlug);
                
                // Fetch roster data
                const rosterData = await window.AuthClient.getRoster(classSlug);
                
                // Display roster
                displayClassRoster(rosterData);
                
                // Show the roster section
                document.getElementById('classRosterSection').style.display = 'block';
                
            } catch (error) {
                console.error('❌ Failed to load roster:', error);
                document.getElementById('rosterList').innerHTML = `
                    <div class="roster-error">
                        <h5>❌ Failed to Load Roster</h5>
                        <p>Error: ${error.message}</p>
                        <p>Please try again or check your permissions.</p>
                    </div>
                `;
                document.getElementById('classRosterSection').style.display = 'block';
                
            } finally {
                // Reset button state
                viewStudentsBtn.disabled = false;
                viewStudentsBtn.textContent = '👥 View Class Roster';
            }
        };
    }
    
    if (manageTokensBtn) {
        manageTokensBtn.onclick = async () => {
            console.log('🔧 Loading token management...');
            
            try {
                // Show loading state
                manageTokensBtn.disabled = true;
                manageTokensBtn.textContent = '🔄 Loading...';
                
                // Get current class slug
                const pathParts = window.location.pathname.split('/');
                const classSlug = pathParts[1] || 'class_template';
                
                // Fetch token data
                const tokenData = await window.AuthClient.getTokens(classSlug);
                
                // Display token management interface
                displayTokenManagement(tokenData);
                
                // Show the token management section
                document.getElementById('tokenManagementSection').style.display = 'block';
                
            } catch (error) {
                console.error('❌ Failed to load tokens:', error);
                document.getElementById('tokenManagementContent').innerHTML = `
                    <div class="token-error">
                        <h5>❌ Failed to Load Tokens</h5>
                        <p>Error: ${error.message}</p>
                        <p>Please try again or check your permissions.</p>
                    </div>
                `;
                document.getElementById('tokenManagementSection').style.display = 'block';
                
            } finally {
                // Reset button state
                manageTokensBtn.disabled = false;
                manageTokensBtn.textContent = '🔧 Manage Enrollment Tokens';
            }
        };
    }
    
    if (uploadFilesBtn) {
        uploadFilesBtn.onclick = () => {
            const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
            window.location.href = `${baseUrl}/upload/`;
        };
    }
    
}

/**
 * Setup student-specific button handlers
 */
function setupStudentHandlers() {
    const viewMyGradesBtn = document.getElementById('viewMyGradesBtn');
    const mySubmissionsBtn = document.getElementById('mySubmissionsBtn');
    
    if (viewMyGradesBtn) {
        viewMyGradesBtn.onclick = () => {
            const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
            window.location.href = `${baseUrl}/my-grades/`;
        };
    }
    
    if (mySubmissionsBtn) {
        mySubmissionsBtn.onclick = () => {
            const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
            window.location.href = `${baseUrl}/my-grades/?tab=submissions`;
        };
    }
    
    // Load and display grade summary in dashboard
    loadStudentGradeSummary();
}

// Quick links for grading pages as buttons
document.addEventListener('DOMContentLoaded', () => {
    const openGradingBtn = document.getElementById('openGradingBtn');
    if (openGradingBtn) {
        openGradingBtn.onclick = () => {
            const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
            window.location.href = `${baseUrl}/grading/`;
        };
    }
    const openGradingSyncBtn = document.getElementById('openGradingSyncBtn');
    if (openGradingSyncBtn) {
        openGradingSyncBtn.onclick = () => {
            const baseUrl = window.location.origin + (window.location.pathname.split('/').slice(0, 2).join('/'));
            window.location.href = `${baseUrl}/grading-sync/`;
        };
    }
});

/**
 * Load and display student grade summary in dashboard
 */
async function loadStudentGradeSummary() {
    const progressDiv = document.getElementById('studentProgress');
    if (!progressDiv || !window.AuthClient) return;
    
    try {
        const pathParts = window.location.pathname.split('/');
        const classSlug = pathParts[1] || 'class_template';
        
        // Fetch module-level grades for summary
        const response = await fetch(`/functions/v1/student-grades?level=module`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${window.authState.session.access_token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch grades');
        }

        const gradesData = await response.json();
        const summary = gradesData.summary || {};
        
        progressDiv.innerHTML = `
            <div class="grade-summary-widget">
                <div class="summary-item">
                    <span class="summary-label">Overall Grade:</span>
                    <span class="summary-value">${summary.average_score?.toFixed(1) || 'N/A'}%</span>
                </div>
                <div class="summary-item">
                    <span class="summary-label">Graded Items:</span>
                    <span class="summary-value">${summary.total_grades || 0}</span>
                </div>
            </div>
        `;
        
    } catch (error) {
        console.error('Failed to load grade summary:', error);
        progressDiv.innerHTML = `
            <div class="grade-summary-error">
                <p>Unable to load grade summary</p>
                <button onclick="loadStudentGradeSummary()">🔄 Retry</button>
            </div>
        `;
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
 * Display class roster data in a formatted table
 */
function displayClassRoster(rosterData) {
    const rosterList = document.getElementById('rosterList');
    
    if (!rosterData || !rosterData.success || !rosterData.members) {
        rosterList.innerHTML = '<p class="roster-error">❌ No roster data available</p>';
        return;
    }
    
    const { class_info, members, stats } = rosterData;
    
    // Handle empty roster gracefully
    if (members.length === 0) {
        rosterList.innerHTML = `
            <div class="roster-empty">
                <div class="roster-header">
                    <h5>📋 ${class_info.title}</h5>
                    <div class="roster-stats">
                        <span class="stat-item">👥 Total: 0 members</span>
                    </div>
                </div>
                <div class="empty-state">
                    <div class="empty-icon">🎓</div>
                    <h6>No Students Enrolled Yet</h6>
                    <p>This class doesn't have any students enrolled yet. Generate an enrollment token to invite students to join.</p>
                    <div class="empty-actions">
                        <button onclick="document.getElementById('generateTokenBtn').click()" class="btn-primary">
                            🔗 Generate Enrollment Token
                        </button>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    // Create roster display
    let html = `
        <div class="roster-header">
            <h5>📋 ${class_info.title}</h5>
            <div class="roster-stats">
                <span class="stat-item">👥 Total: ${stats.total}</span>
                <span class="stat-item">👨‍🏫 Professors: ${stats.professors}</span>
                <span class="stat-item">🎓 Students: ${stats.students}</span>
            </div>
        </div>
        
        <div class="roster-table-container">
            <table class="roster-table">
                <thead>
                    <tr>
                        <th>Avatar</th>
                        <th>Name</th>
                        <th>Email</th>
                        <th>GitHub</th>
                        <th>Role</th>
                        <th>Enrolled</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Sort members: professors first, then students, then by enrollment date
    const sortedMembers = members.sort((a, b) => {
        if (a.role !== b.role) {
            return a.role === 'professor' ? -1 : 1;
        }
        return new Date(b.enrolled_at).getTime() - new Date(a.enrolled_at).getTime();
    });
    
    sortedMembers.forEach(member => {
        const avatarUrl = member.avatar_url || `https://github.com/${member.github_username}.png?size=40`;
        const displayName = member.full_name || member.github_username || 'Unknown';
        const roleIcon = member.role === 'professor' ? '👨‍🏫' : '🎓';
        const roleClass = member.role === 'professor' ? 'role-professor' : 'role-student';
        const enrolledDate = new Date(member.enrolled_at).toLocaleDateString();
        const githubLink = member.github_username ? 
            `<a href="https://github.com/${member.github_username}" target="_blank">@${member.github_username}</a>` : 
            'Not available';
        
        html += `
            <tr class="member-row ${roleClass}">
                <td class="avatar-cell">
                    <img src="${avatarUrl}" alt="${displayName}" class="member-avatar" 
                         onerror="this.src='https://via.placeholder.com/40/333/fff?text=${displayName.charAt(0)}'">
                </td>
                <td class="name-cell">
                    <strong>${displayName}</strong>
                </td>
                <td class="email-cell">
                    <span class="member-email">${member.email}</span>
                </td>
                <td class="github-cell">
                    ${githubLink}
                </td>
                <td class="role-cell">
                    <span class="role-badge ${roleClass}">
                        ${roleIcon} ${member.role}
                    </span>
                </td>
                <td class="enrolled-cell">
                    <span class="enrolled-date">${enrolledDate}</span>
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        
        <div class="roster-footer">
            <p class="roster-note">
                💡 <strong>Note:</strong> Only professors can view the full class roster. 
                Students can see their own enrollment status in their dashboard.
            </p>
        </div>
    `;
    
    rosterList.innerHTML = html;
}

/**
 * Display token management interface
 */
function displayTokenManagement(tokenData) {
    const tokenContent = document.getElementById('tokenManagementContent');
    
    if (!tokenData || !tokenData.success || !tokenData.tokens) {
        tokenContent.innerHTML = '<p class="token-error">❌ No token data available</p>';
        return;
    }
    
    const { tokens, stats } = tokenData;
    
    // Handle empty tokens gracefully
    if (tokens.length === 0) {
        tokenContent.innerHTML = `
            <div class="tokens-empty">
                <div class="tokens-header">
                    <h5>🔧 Token Management</h5>
                    <div class="tokens-stats">
                        <span class="stat-item">📊 Total: 0 tokens</span>
                    </div>
                </div>
                <div class="empty-state">
                    <div class="empty-icon">🔗</div>
                    <h6>No Enrollment Tokens Created Yet</h6>
                    <p>Generate your first enrollment token to allow students to join this class.</p>
                    <div class="empty-actions">
                        <button onclick="document.getElementById('generateTokenBtn').click()" class="btn-primary">
                            🔗 Generate First Token
                        </button>
                    </div>
                </div>
            </div>
        `;
        return;
    }
    
    // Create token management display
    let html = `
        <div class="tokens-header">
            <h5>🔧 Token Management</h5>
            <div class="tokens-stats">
                <span class="stat-item">📊 Total: ${stats.total}</span>
                <span class="stat-item ${stats.active > 0 ? 'stat-active' : ''}">✅ Active: ${stats.active}</span>
                <span class="stat-item ${stats.expired > 0 ? 'stat-expired' : ''}">⏰ Expired: ${stats.expired}</span>
                <span class="stat-item ${stats.disabled > 0 ? 'stat-disabled' : ''}">🚫 Disabled: ${stats.disabled}</span>
                <span class="stat-item ${stats.exhausted > 0 ? 'stat-exhausted' : ''}">📊 Exhausted: ${stats.exhausted}</span>
            </div>
        </div>
        
        <div class="tokens-table-container">
            <table class="tokens-table">
                <thead>
                    <tr>
                        <th>Token ID</th>
                        <th>Status</th>
                        <th>Uses</th>
                        <th>Expires</th>
                        <th>Created</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
    `;
    
    // Sort tokens: active first, then by creation date (newest first)
    const sortedTokens = tokens.sort((a, b) => {
        if (a.status !== b.status) {
            const statusOrder = { active: 0, expired: 1, exhausted: 2, disabled: 3 };
            return statusOrder[a.status] - statusOrder[b.status];
        }
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
    });
    
    sortedTokens.forEach(token => {
        const statusIcon = getTokenStatusIcon(token.status);
        const statusClass = `token-status-${token.status}`;
        const createdDate = new Date(token.created_at).toLocaleDateString();
        const expiresDate = new Date(token.expires_at).toLocaleDateString();
        const usesText = token.max_uses > 0 ? `${token.uses}/${token.max_uses}` : `${token.uses}/∞`;
        const tokenIdShort = token.id.toString().padStart(4, '0');
        
        // Determine if token can be deactivated
        const canDeactivate = token.status === 'active';
        const actionButton = canDeactivate 
            ? `<button onclick="deactivateToken(${token.id})" class="btn-deactivate" title="Deactivate Token">🔒 Disable</button>`
            : '<span class="action-disabled">—</span>';
        
        html += `
            <tr class="token-row ${statusClass}">
                <td class="token-id-cell">
                    <span class="token-id">#${tokenIdShort}</span>
                </td>
                <td class="status-cell">
                    <span class="token-status ${statusClass}">
                        ${statusIcon} ${token.status}
                    </span>
                </td>
                <td class="uses-cell">
                    <span class="token-uses">${usesText}</span>
                </td>
                <td class="expires-cell">
                    <span class="expires-date">${expiresDate}</span>
                </td>
                <td class="created-cell">
                    <span class="created-date">${createdDate}</span>
                </td>
                <td class="actions-cell">
                    ${actionButton}
                </td>
            </tr>
        `;
    });
    
    html += `
                </tbody>
            </table>
        </div>
        
        <div class="tokens-footer">
            <p class="tokens-note">
                💡 <strong>Note:</strong> Active tokens can be used by students to enroll. 
                Disabled tokens cannot be used but remain in the system for audit purposes.
            </p>
            <div class="token-actions">
                <button onclick="document.getElementById('generateTokenBtn').click()" class="btn-primary">
                    🔗 Generate New Token
                </button>
            </div>
        </div>
    `;
    
    tokenContent.innerHTML = html;
}

/**
 * Get status icon for token status
 */
function getTokenStatusIcon(status) {
    const icons = {
        active: '✅',
        expired: '⏰',
        disabled: '🚫',
        exhausted: '📊'
    };
    return icons[status] || '❓';
}

/**
 * Deactivate a specific token
 */
async function deactivateToken(tokenId) {
    if (!confirm('Are you sure you want to deactivate this enrollment token? This action cannot be undone.')) {
        return;
    }
    
    try {
        console.log(`🔒 Deactivating token ${tokenId}...`);
        
        // Get current class slug
        const pathParts = window.location.pathname.split('/');
        const classSlug = pathParts[1] || 'class_template';
        
        // Deactivate the token
        await window.AuthClient.deactivateToken(classSlug, tokenId);
        
        console.log(`✅ Token ${tokenId} deactivated successfully`);
        
        // Refresh the token management display
        document.getElementById('manageTokensBtn').click();
        
        // Show success message
        const successDiv = document.createElement('div');
        successDiv.className = 'token-success';
        successDiv.innerHTML = '✅ Token deactivated successfully';
        successDiv.style.cssText = 'position: fixed; top: 20px; right: 20px; background: var(--eva-green-primary); color: var(--bg-color); padding: 10px 20px; border-radius: 6px; z-index: 1000;';
        document.body.appendChild(successDiv);
        
        setTimeout(() => {
            document.body.removeChild(successDiv);
        }, 3000);
        
    } catch (error) {
        console.error('❌ Failed to deactivate token:', error);
        alert(`Failed to deactivate token: ${error.message}`);
    }
}

/**
 * Debug function to test API connectivity
 */
window.debugAPIConnectivity = async function() {
    console.log('🐛 DEBUG: Testing API connectivity...');
    
    try {
        // Test basic auth state
        console.log('🐛 Auth State:', window.authState);
        console.log('🐛 Is Authenticated:', window.authState?.isAuthenticated);
        console.log('🐛 User:', window.authState?.user);
        console.log('🐛 Session:', window.authState?.session);
        
        // Test user context first
        const classSlug = 'class_template';
        console.log('🐛 Testing getMe with class slug:', classSlug);
        
        const userContext = await window.AuthClient.getMe(classSlug);
        console.log('🐛 User context result:', userContext);
        
        // Check if user is a professor
        if (userContext.role === 'professor') {
            console.log('✅ User is confirmed as professor');
        } else {
            console.error('❌ User is not a professor, role:', userContext.role);
        }
        
        // If that works, test roster
        console.log('🐛 Testing getRoster...');
        const rosterResult = await window.AuthClient.getRoster(classSlug);
        console.log('🐛 Roster result:', rosterResult);
        
    } catch (error) {
        console.error('🐛 API Debug failed:', error);
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