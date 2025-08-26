/**
 * Student Grades Interface
 * Handles student view of their own grades, submissions, and academic progress
 * Includes proper security verification and class context
 */

class StudentGradesInterface {
    constructor() {
        this.classContext = null;
        this.supabaseClient = null;
        this.currentUser = null;
        this.grades = [];
        this.submissions = [];
        this.modules = [];
        this.currentTab = 'overview';
        
        this.init();
    }

    async init() {
        // Get class context
        this.classContext = this.getClassContext();
        
        if (!this.classContext) {
            console.error('Missing class context - grades interface disabled');
            this.showError('Class context not found. Please refresh the page.');
            return;
        }

        // Initialize Supabase
        this.initializeSupabase();

        // Check authentication
        const isAuthenticated = await this.verifyStudentAccess();
        if (!isAuthenticated) {
            this.showAuthenticationRequired();
            return;
        }

        // Load initial data
        await this.loadInitialData();

        // Set up UI event handlers
        this.setupEventHandlers();

        // Render the interface
        this.renderGradesInterface();

        console.log('Student grades interface initialized for class:', this.classContext.repo_name);
    }

    getClassContext() {
        // Use FrameworkConfig directly to avoid race conditions with meta tag injection
        if (window.FrameworkConfig && window.FrameworkConfig.classContext) {
            const ctx = window.FrameworkConfig.classContext;
            return {
                class_id: ctx.classId,
                repo_name: ctx.repoName,
                professor_github: ctx.professorGithub
            };
        }
        
        // Fallback to meta tags if FrameworkConfig not available
        const classId = document.querySelector('meta[name="class-id"]')?.content;
        const repoName = document.querySelector('meta[name="repo-name"]')?.content;
        const professorGithub = document.querySelector('meta[name="professor-github"]')?.content;

        if (!classId || !repoName) {
            return null;
        }

        return {
            class_id: classId,
            repo_name: repoName,
            professor_github: professorGithub
        };
    }

    initializeSupabase() {
        let supabaseUrl, supabaseAnonKey;
        
        // Use FrameworkConfig if available
        if (window.FrameworkConfig && window.FrameworkConfig.supabase) {
            supabaseUrl = window.FrameworkConfig.supabase.url;
            supabaseAnonKey = window.FrameworkConfig.supabase.anonKey;
        } else {
            // Fallback to meta tags
            supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
            supabaseAnonKey = document.querySelector('meta[name="supabase-anon-key"]')?.content;
        }

        if (!supabaseUrl || !supabaseAnonKey || typeof window.supabase === 'undefined') {
            console.error('Missing Supabase configuration or library');
            this.showError('Configuration error. Please contact system administrator.');
            return;
        }

        this.supabaseClient = supabase.createClient(supabaseUrl, supabaseAnonKey);
    }

    async verifyStudentAccess() {
        if (!this.supabaseClient) return false;

        try {
            const { data: { user }, error } = await this.supabaseClient.auth.getUser();
            
            if (error || !user) {
                return false;
            }

            this.currentUser = user;
            return true;

        } catch (error) {
            console.error('Student access verification failed:', error);
            return false;
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadGrades(),
            this.loadSubmissions(),
            this.loadModules()
        ]);
    }

    async loadGrades() {
        try {
            // Use the student-grades Edge Function
            const pathParts = window.location.pathname.split('/');
            const classSlug = pathParts[1] || 'class_template';
            
            if (!window.AuthClient) {
                throw new Error('AuthClient not available');
            }

            // Get module-level grades
            const moduleGrades = await this.fetchGradesData(classSlug, 'module');
            // Get constituent-level grades  
            const constituentGrades = await this.fetchGradesData(classSlug, 'constituent');
            // Get item-level grades
            const itemGrades = await this.fetchGradesData(classSlug, 'item');

            this.grades = {
                modules: moduleGrades.grades || [],
                constituents: constituentGrades.grades || [],
                items: itemGrades.grades || []
            };

            this.gradeSummary = {
                modules: moduleGrades.summary || {},
                constituents: constituentGrades.summary || {},
                items: itemGrades.summary || {}
            };

            console.log(`Loaded grades:`, this.grades);

        } catch (error) {
            console.error('Failed to load grades:', error);
            this.showError(`Failed to load grades: ${error.message}`);
        }
    }

    async fetchGradesData(classSlug, level) {
        const response = await fetch(`/functions/v1/student-grades?level=${level}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${window.authState.session.access_token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error(`Failed to fetch ${level} grades: ${response.statusText}`);
        }

        return await response.json();
    }

    async loadSubmissions() {
        try {
            const { data: submissions, error } = await this.supabaseClient
                .from('student_submissions')
                .select(`
                    id,
                    item_id,
                    attempt_number,
                    submission_data,
                    submitted_at,
                    raw_score,
                    adjusted_score,
                    feedback,
                    graded_at,
                    items!student_submissions_item_id_fkey (
                        title,
                        points,
                        constituent_slug,
                        delivery_type
                    )
                `)
                .eq('student_id', this.currentUser.id)
                .eq('class_id', this.classContext.class_id)
                .order('submitted_at', { ascending: false });

            if (error) {
                console.error('Error loading submissions:', error);
                return;
            }

            this.submissions = submissions || [];
            console.log(`Loaded ${this.submissions.length} submissions`);

        } catch (error) {
            console.error('Failed to load submissions:', error);
        }
    }

    async loadModules() {
        try {
            // Get module structure from class_template data
            const classTemplateResponse = await fetch(`{{ .Site.BaseURL }}data/modules.json`);
            if (classTemplateResponse.ok) {
                this.modules = await classTemplateResponse.json();
            }
        } catch (error) {
            console.error('Failed to load modules:', error);
        }
    }

    renderGradesInterface() {
        const container = document.getElementById('grades-interface');
        if (!container) {
            console.error('Grades interface container not found');
            return;
        }

        // Update student info section
        this.updateStudentInfo();
        this.updateGradeSummary();

        // Render initial tab content
        this.renderTabContent(this.currentTab);
    }

    updateStudentInfo() {
        const studentInfo = document.getElementById('studentInfo');
        const user = window.authState?.user;
        const userContext = window.authState?.userContext;

        if (studentInfo && user && userContext) {
            studentInfo.innerHTML = `
                <h3>👤 ${user.email}</h3>
                <p><strong>GitHub:</strong> @${userContext.github_username || 'Unknown'}</p>
                <p><strong>Class:</strong> ${userContext.class_title || 'Unknown'}</p>
            `;
        }
    }

    updateGradeSummary() {
        const gradeSummary = document.getElementById('gradeSummary');
        
        if (!gradeSummary || !this.gradeSummary.modules) {
            return;
        }

        const summary = this.gradeSummary.modules;
        
        gradeSummary.innerHTML = `
            <div class="summary-card">
                <div class="overall-grade">
                    <span class="grade-number">${summary.average_score?.toFixed(1) || 'N/A'}%</span>
                    <span class="grade-label">Overall Grade</span>
                </div>
                <div class="grade-stats">
                    <div class="stat">
                        <span class="stat-number">${summary.total_grades || 0}</span>
                        <span class="stat-label">Graded Items</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${Object.keys(summary.grade_distribution || {}).length}</span>
                        <span class="stat-label">Grade Types</span>
                    </div>
                </div>
            </div>
        `;
    }

    renderTabContent(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });

        // Render specific tab content
        switch(tabName) {
            case 'overview':
                this.renderOverviewTab();
                break;
            case 'modules':
                this.renderModulesTab();
                break;
            case 'submissions':
                this.renderSubmissionsTab();
                break;
            case 'progress':
                this.renderProgressTab();
                break;
        }
    }

    renderOverviewTab() {
        const container = document.getElementById('overviewContent');
        const moduleGrades = this.grades.modules || [];
        
        if (moduleGrades.length === 0) {
            container.innerHTML = `
                <div class="no-grades">
                    <div class="empty-icon">📊</div>
                    <h4>No Grades Yet</h4>
                    <p>You don't have any graded items yet. Complete assignments to see your grades here.</p>
                </div>
            `;
            return;
        }

        const recentGrades = this.grades.items.slice(0, 5);
        
        container.innerHTML = `
            <div class="overview-grid">
                <div class="recent-grades">
                    <h4>📝 Recent Grades</h4>
                    <div class="grades-list">
                        ${recentGrades.map(grade => this.renderGradeItem(grade)).join('')}
                    </div>
                </div>
                
                <div class="grade-distribution">
                    <h4>📊 Grade Distribution</h4>
                    <div class="distribution-chart">
                        ${this.renderGradeDistribution()}
                    </div>
                </div>
                
                <div class="upcoming-items">
                    <h4>⏰ Upcoming Items</h4>
                    <div class="upcoming-list">
                        ${this.renderUpcomingItems()}
                    </div>
                </div>
            </div>
        `;
    }

    renderModulesTab() {
        const container = document.getElementById('modulesContent');
        const moduleGrades = this.grades.modules || [];
        
        container.innerHTML = `
            <div class="modules-grid">
                ${moduleGrades.map(moduleGrade => this.renderModuleCard(moduleGrade)).join('')}
            </div>
        `;
    }

    renderSubmissionsTab() {
        const container = document.getElementById('submissionsContent');
        
        container.innerHTML = `
            <div class="submissions-section">
                <div class="submissions-filters">
                    <select id="submission-status-filter">
                        <option value="">All Submissions</option>
                        <option value="graded">Graded</option>
                        <option value="ungraded">Pending Grade</option>
                    </select>
                    <select id="submission-module-filter">
                        <option value="">All Modules</option>
                        ${this.modules.map(module => 
                            `<option value="${module.id}">${module.name}</option>`
                        ).join('')}
                    </select>
                </div>
                
                <div class="submissions-list">
                    ${this.submissions.map(submission => this.renderSubmissionCard(submission)).join('')}
                </div>
            </div>
        `;
    }

    renderProgressTab() {
        const container = document.getElementById('progressContent');
        
        container.innerHTML = `
            <div class="progress-section">
                <div class="progress-overview">
                    <h4>🎯 Course Progress</h4>
                    <div class="progress-chart">
                        ${this.renderProgressChart()}
                    </div>
                </div>
                
                <div class="module-progress">
                    <h4>📚 Module Progress</h4>
                    <div class="module-progress-list">
                        ${this.renderModuleProgress()}
                    </div>
                </div>
            </div>
        `;
    }

    renderGradeItem(grade) {
        const gradeDate = new Date(grade.computed_at).toLocaleDateString();
        const score = grade.final_score || grade.raw_score || 0;
        const maxPoints = grade.max_points || 100;
        const percentage = ((score / maxPoints) * 100).toFixed(1);
        
        return `
            <div class="grade-item">
                <div class="grade-info">
                    <span class="item-title">${grade.item_title || 'Unknown Item'}</span>
                    <span class="grade-date">${gradeDate}</span>
                </div>
                <div class="grade-score">
                    <span class="score">${score}/${maxPoints}</span>
                    <span class="percentage">(${percentage}%)</span>
                </div>
            </div>
        `;
    }

    renderModuleCard(moduleGrade) {
        const progress = ((moduleGrade.final_score / moduleGrade.max_points) * 100).toFixed(1);
        
        return `
            <div class="module-card">
                <div class="module-header">
                    <h4>${moduleGrade.modules?.name || 'Unknown Module'}</h4>
                    <span class="module-grade">${moduleGrade.final_score}/${moduleGrade.max_points}</span>
                </div>
                <div class="module-progress">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-text">${progress}%</span>
                </div>
                ${moduleGrade.letter_grade ? `<div class="letter-grade">${moduleGrade.letter_grade}</div>` : ''}
            </div>
        `;
    }

    renderSubmissionCard(submission) {
        const submittedDate = new Date(submission.submitted_at).toLocaleDateString();
        const isGraded = submission.raw_score !== null;
        const score = submission.adjusted_score || submission.raw_score;
        const maxPoints = submission.items?.points || 100;
        
        return `
            <div class="submission-card ${isGraded ? 'graded' : 'ungraded'}">
                <div class="submission-header">
                    <h5>${submission.items?.title || 'Unknown Item'}</h5>
                    <span class="submission-date">${submittedDate}</span>
                </div>
                
                <div class="submission-details">
                    <span class="attempt">Attempt ${submission.attempt_number}</span>
                    <span class="type">${submission.items?.delivery_type || 'Unknown'}</span>
                </div>
                
                <div class="submission-grade">
                    ${isGraded ? 
                        `<div class="grade-display">
                            <span class="score">${score}/${maxPoints}</span>
                            <span class="percentage">(${((score/maxPoints)*100).toFixed(1)}%)</span>
                        </div>` :
                        `<div class="pending-grade">⏳ Pending Grade</div>`
                    }
                </div>
                
                ${submission.feedback ? 
                    `<div class="feedback">
                        <strong>Feedback:</strong>
                        <p>${this.escapeHtml(submission.feedback)}</p>
                    </div>` : ''
                }
            </div>
        `;
    }

    renderGradeDistribution() {
        const distribution = this.gradeSummary.items?.grade_distribution || {};
        
        if (Object.keys(distribution).length === 0) {
            return '<p>No grade data available</p>';
        }
        
        return Object.entries(distribution)
            .map(([grade, count]) => 
                `<div class="distribution-item">
                    <span class="grade-letter">${grade}</span>
                    <span class="grade-count">${count}</span>
                </div>`
            ).join('');
    }

    renderUpcomingItems() {
        // Filter items that are due soon and not yet submitted
        const now = new Date();
        const upcoming = this.submissions
            .filter(sub => sub.items?.due_date && new Date(sub.items.due_date) > now)
            .slice(0, 3);

        if (upcoming.length === 0) {
            return '<p>No upcoming items</p>';
        }

        return upcoming.map(item => {
            const dueDate = new Date(item.items.due_date).toLocaleDateString();
            return `
                <div class="upcoming-item">
                    <span class="item-name">${item.items.title}</span>
                    <span class="due-date">Due: ${dueDate}</span>
                </div>
            `;
        }).join('');
    }

    renderProgressChart() {
        const moduleGrades = this.grades.modules || [];
        
        if (moduleGrades.length === 0) {
            return '<p>No progress data available</p>';
        }
        
        return moduleGrades.map(module => {
            const progress = ((module.final_score / module.max_points) * 100).toFixed(1);
            return `
                <div class="progress-item">
                    <span class="module-name">${module.modules?.name || 'Unknown'}</span>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%"></div>
                    </div>
                    <span class="progress-percentage">${progress}%</span>
                </div>
            `;
        }).join('');
    }

    renderModuleProgress() {
        return this.renderProgressChart(); // Same implementation for now
    }

    setupEventHandlers() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.renderTabContent(e.target.dataset.tab);
            }
        });

        // Filter handlers
        document.addEventListener('change', (e) => {
            if (e.target.id === 'submission-status-filter' || e.target.id === 'submission-module-filter') {
                this.filterSubmissions();
            }
        });
    }

    filterSubmissions() {
        const statusFilter = document.getElementById('submission-status-filter')?.value;
        const moduleFilter = document.getElementById('submission-module-filter')?.value;
        
        // Re-render submissions with filters applied
        let filteredSubmissions = this.submissions;
        
        if (statusFilter === 'graded') {
            filteredSubmissions = filteredSubmissions.filter(s => s.raw_score !== null);
        } else if (statusFilter === 'ungraded') {
            filteredSubmissions = filteredSubmissions.filter(s => s.raw_score === null);
        }
        
        // Update the submissions list
        const submissionsList = document.querySelector('.submissions-list');
        if (submissionsList) {
            submissionsList.innerHTML = filteredSubmissions
                .map(submission => this.renderSubmissionCard(submission))
                .join('');
        }
    }

    // Utility methods
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        const container = document.getElementById('grades-interface');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    <h3>⚠️ Error</h3>
                    <p>${message}</p>
                    <button onclick="window.location.reload()">🔄 Retry</button>
                </div>
            `;
        }
    }

    showAuthenticationRequired() {
        const container = document.getElementById('grades-interface');
        if (container) {
            container.innerHTML = `
                <div class="auth-required">
                    <h3>🔐 Authentication Required</h3>
                    <p>Please log in to view your grades.</p>
                    <button onclick="window.location.href='{{ .Site.BaseURL }}auth/login/'">Log In with GitHub</button>
                </div>
            `;
        }
    }
}

// Make available globally for the my-grades page
window.StudentGradesInterface = StudentGradesInterface;