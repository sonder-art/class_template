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
        this.constituents = [];
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

            console.log(`✅ Loaded grades:`, this.grades);
            console.log(`📊 Module grades sample:`, this.grades.modules[0]);
            console.log(`📝 Item grades sample:`, this.grades.items[0]);

        } catch (error) {
            console.error('Failed to load grades:', error);
            this.showError(`Failed to load grades: ${error.message}`);
        }
    }

    async fetchGradesData(classSlug, level) {
        if (!window.AuthClient) {
            throw new Error('AuthClient not available');
        }

        try {
            const result = await window.AuthClient.callEndpoint(
                `/student-grades?class_slug=${classSlug}&level=${level}`
            );
            
            console.log(`✅ Fetched ${level} grades for class ${classSlug}:`, result);
            return result;
        } catch (error) {
            console.error(`❌ Failed to fetch ${level} grades:`, error);
            throw new Error(`Failed to fetch ${level} grades: ${error.message}`);
        }
    }

    async loadSubmissions() {
        try {
            const { data: allSubmissions, error } = await this.supabaseClient
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
                        delivery_type,
                        is_current
                    )
                `)
                .eq('student_id', this.currentUser.id)
                .eq('class_id', this.classContext.class_id)
                .order('submitted_at', { ascending: false });

            if (error) {
                console.error('Error loading submissions:', error);
                return;
            }

            // Filter out submissions for non-current items after the join
            const currentSubmissions = (allSubmissions || []).filter(submission => 
                submission.items && submission.items.is_current === true
            );

            this.submissions = this.getLatestSubmissions(currentSubmissions);
            console.log(`Loaded ${allSubmissions?.length || 0} total submissions, ${currentSubmissions.length} for current items, ${this.submissions.length} latest submissions`);

        } catch (error) {
            console.error('Failed to load submissions:', error);
        }
    }

    async loadModules() {
        try {
            // Get module structure from class_template data
            // Use relative URL from current page base
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            const baseUrl = pathParts.length > 0 ? `/${pathParts[0]}/` : '/';
            const modulesUrl = `${baseUrl}data/modules.json`;
            const constituentsUrl = `${baseUrl}data/constituents.json`;
            
            console.log('🔍 Loading modules from:', modulesUrl);
            const classTemplateResponse = await fetch(modulesUrl);
            if (classTemplateResponse.ok) {
                const modulesData = await classTemplateResponse.json();
                this.modules = modulesData.modules || [];
                console.log('✅ Loaded modules:', this.modules);
            } else {
                console.warn('⚠️ Could not load modules.json, continuing without module data');
            }
            
            console.log('🔍 Loading constituents from:', constituentsUrl);
            const constituentsResponse = await fetch(constituentsUrl);
            if (constituentsResponse.ok) {
                const constituentsData = await constituentsResponse.json();
                this.constituents = constituentsData.constituents || [];
                console.log('✅ Loaded constituents:', this.constituents);
            } else {
                console.warn('⚠️ Could not load constituents.json, continuing without constituent data');
            }
        } catch (error) {
            console.error('Failed to load modules/constituents:', error);
        }
    }

    /**
     * Filter submissions to show only the latest attempt per item
     */
    getLatestSubmissions(allSubmissions) {
        const submissionGroups = {};
        
        // Group submissions by item_id
        allSubmissions.forEach(submission => {
            const itemId = submission.item_id;
            if (!submissionGroups[itemId]) {
                submissionGroups[itemId] = [];
            }
            submissionGroups[itemId].push(submission);
        });
        
        // For each item, get the latest submission (highest attempt_number or latest submitted_at)
        const latestSubmissions = [];
        Object.values(submissionGroups).forEach(group => {
            // Sort by attempt_number (descending), then by submitted_at (descending)
            group.sort((a, b) => {
                const attemptDiff = (b.attempt_number || 1) - (a.attempt_number || 1);
                if (attemptDiff !== 0) return attemptDiff;
                return new Date(b.submitted_at) - new Date(a.submitted_at);
            });
            
            // Take the first (latest) submission
            latestSubmissions.push(group[0]);
        });
        
        return latestSubmissions;
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
                <div class="profile-avatar">👤</div>
                <div class="profile-details">
                    <h2>${user.email}</h2>
                    <p class="student-meta">@${userContext.github_username || 'Unknown'} • ${userContext.class_title || 'GitHub Class Template'}</p>
                </div>
            `;
        }
    }

    updateGradeSummary() {
        const gradeSummary = document.getElementById('gradeSummary');
        
        if (!gradeSummary || !this.gradeSummary.modules) {
            return;
        }

        const summary = this.gradeSummary.modules;
        const lastUpdated = summary.last_updated ? 
            new Date(summary.last_updated).toLocaleDateString() : 'Never';
        
        // Update individual summary cards
        const overallGradeCard = gradeSummary.querySelector('.overall-grade .grade-number');
        const pointsEarned = gradeSummary.querySelector('.points-earned');
        const pointsTotal = gradeSummary.querySelector('.points-total');
        const countNumber = gradeSummary.querySelector('.count-number');
        const timeText = gradeSummary.querySelector('.time-text');
        
        if (overallGradeCard) {
            overallGradeCard.textContent = summary.average_score?.toFixed(1) || '--';
        }
        
        if (pointsEarned && pointsTotal) {
            pointsEarned.textContent = summary.total_score?.toFixed(0) || '--';
            pointsTotal.textContent = summary.max_points?.toFixed(0) || '--';
        }
        
        if (countNumber) {
            countNumber.textContent = summary.total_grades || '--';
        }
        
        if (timeText) {
            timeText.textContent = lastUpdated;
        }
    }

    renderTabContent(tabName) {
        this.currentTab = tabName;
        
        // Update tab buttons
        document.querySelectorAll('.nav-tab').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab panels
        document.querySelectorAll('.tab-panel').forEach(panel => {
            panel.classList.toggle('active', panel.id === `${tabName}-panel`);
        });

        // Show/hide nav controls based on tab
        const navControls = document.getElementById('navControls');
        if (navControls) {
            navControls.style.display = (tabName === 'modules' || tabName === 'submissions') ? 'flex' : 'none';
        }

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
        
        // Add error handling for missing container
        if (!container) {
            console.error('overviewContent container not found - interface may not be ready');
            setTimeout(() => this.renderOverviewTab(), 100); // Retry after 100ms
            return;
        }
        
        const moduleGrades = this.grades.modules || [];
        const itemGrades = this.grades.items || [];
        
        if (moduleGrades.length === 0 && itemGrades.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <h3>No Grades Yet</h3>
                    <p>Complete assignments to see your grades and progress here.</p>
                </div>
            `;
            return;
        }

        const recentGrades = itemGrades.slice(0, 6);
        
        container.innerHTML = `
            <div class="overview-layout">
                <!-- Recent Grades Section -->
                <section class="overview-section">
                    <div class="section-header">
                        <h3>📝 Recent Grades</h3>
                        <span class="item-count">${recentGrades.length} items</span>
                    </div>
                    <div class="recent-grades-grid">
                        ${recentGrades.map(grade => this.renderRecentGradeCard(grade)).join('')}
                    </div>
                </section>
                
                <!-- Module Performance Section -->
                <section class="overview-section">
                    <div class="section-header">
                        <h3>📚 Module Performance</h3>
                        <span class="item-count">${moduleGrades.length} modules</span>
                    </div>
                    <div class="module-performance-grid">
                        ${moduleGrades.map(module => this.renderModulePerformanceCard(module)).join('')}
                    </div>
                </section>
                
                <!-- Quick Stats Section -->
                <section class="overview-section">
                    <div class="section-header">
                        <h3>📈 Quick Stats</h3>
                    </div>
                    <div class="quick-stats">
                        ${this.renderQuickStats()}
                    </div>
                </section>
            </div>
        `;
    }

    renderModulesTab() {
        const container = document.getElementById('modulesContent');
        
        // Add error handling for missing container
        if (!container) {
            console.error('modulesContent container not found - interface may not be ready');
            setTimeout(() => this.renderModulesTab(), 100);
            return;
        }
        
        const moduleGrades = this.grades.modules || [];
        
        container.innerHTML = `
            <div class="modules-grid">
                ${moduleGrades.map(module => this.renderModulePerformanceCard(module)).join('')}
            </div>
        `;
    }

    renderSubmissionsTab() {
        const container = document.getElementById('submissionsContent');
        
        // Add error handling for missing container
        if (!container) {
            console.error('submissionsContent container not found - interface may not be ready');
            setTimeout(() => this.renderSubmissionsTab(), 100);
            return;
        }
        
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
                        ${(this.modules || []).map(module => 
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
        
        // Add error handling for missing container
        if (!container) {
            console.error('progressContent container not found - interface may not be ready');
            setTimeout(() => this.renderProgressTab(), 100);
            return;
        }
        
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
        const percentage = maxPoints > 0 ? ((score / maxPoints) * 100).toFixed(1) : 0;
        
        // Extract nested data from JSON objects
        const itemTitle = grade.items?.title || grade.item_title || 'Unknown Item';
        const moduleName = grade.modules?.name || 'Unknown Module';
        const constituentName = grade.constituents?.name || 'Unknown Section';
        
        return `
            <div class="grade-item">
                <div class="grade-info">
                    <span class="item-title">${itemTitle}</span>
                    <span class="grade-meta">${moduleName} › ${constituentName}</span>
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

    // New enhanced rendering methods for the redesigned interface

    renderRecentGradeCard(grade) {
        const gradeDate = new Date(grade.computed_at).toLocaleDateString();
        const score = grade.final_score || grade.raw_score || 0;
        const maxPoints = grade.max_points || 100;
        const percentage = maxPoints > 0 ? ((score / maxPoints) * 100).toFixed(1) : 0;
        
        const itemTitle = grade.items?.title || grade.item_title || 'Unknown Item';
        const moduleName = grade.modules?.name || 'Unknown Module';
        const constituentName = grade.constituents?.name || 'Unknown Section';
        
        // Get grade color based on percentage
        let gradeColor = '#10B981'; // Green for good grades
        if (percentage < 60) gradeColor = '#EF4444'; // Red for failing
        else if (percentage < 70) gradeColor = '#F59E0B'; // Yellow for concerning
        else if (percentage < 85) gradeColor = '#6B7280'; // Gray for average
        
        return `
            <div class="grade-card recent-grade-card">
                <div class="card-header">
                    <div class="item-info">
                        <h4 class="item-title">${itemTitle}</h4>
                        <p class="item-path">${moduleName} › ${constituentName}</p>
                    </div>
                    <div class="grade-badge" style="background-color: ${gradeColor}">
                        ${percentage}%
                    </div>
                </div>
                <div class="card-footer">
                    <span class="points-detail">${score}/${maxPoints} pts</span>
                    <span class="grade-date">${gradeDate}</span>
                </div>
            </div>
        `;
    }

    renderModulePerformanceCard(moduleGrade) {
        const score = moduleGrade.final_score || 0;
        const maxPoints = moduleGrade.max_points || 1;
        const progress = ((score / maxPoints) * 100).toFixed(1);
        const moduleName = moduleGrade.modules?.name || 'Unknown Module';
        const moduleColor = moduleGrade.modules?.color || '#6B7280';
        const moduleIcon = moduleGrade.modules?.icon || '📚';
        
        // Get grade letter
        let gradeLetter = 'N/A';
        let gradeColor = '#6B7280';
        if (progress >= 97) { gradeLetter = 'A+'; gradeColor = '#10B981'; }
        else if (progress >= 93) { gradeLetter = 'A'; gradeColor = '#10B981'; }
        else if (progress >= 90) { gradeLetter = 'A-'; gradeColor = '#10B981'; }
        else if (progress >= 87) { gradeLetter = 'B+'; gradeColor = '#3B82F6'; }
        else if (progress >= 83) { gradeLetter = 'B'; gradeColor = '#3B82F6'; }
        else if (progress >= 80) { gradeLetter = 'B-'; gradeColor = '#3B82F6'; }
        else if (progress >= 77) { gradeLetter = 'C+'; gradeColor = '#F59E0B'; }
        else if (progress >= 73) { gradeLetter = 'C'; gradeColor = '#F59E0B'; }
        else if (progress >= 70) { gradeLetter = 'C-'; gradeColor = '#F59E0B'; }
        else if (progress >= 60) { gradeLetter = 'D'; gradeColor = '#EF4444'; }
        else { gradeLetter = 'F'; gradeColor = '#EF4444'; }
        
        return `
            <div class="module-card performance-card" style="border-left: 4px solid ${moduleColor}">
                <div class="module-header">
                    <div class="module-info">
                        <span class="module-icon">${moduleIcon}</span>
                        <div>
                            <h4 class="module-name">${moduleName}</h4>
                            <p class="module-progress-text">${progress}% complete</p>
                        </div>
                    </div>
                    <div class="grade-display" style="color: ${gradeColor}">
                        <span class="grade-letter">${gradeLetter}</span>
                        <span class="grade-percentage">${progress}%</span>
                    </div>
                </div>
                <div class="progress-bar-container">
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: ${progress}%; background-color: ${moduleColor}"></div>
                    </div>
                </div>
                <div class="module-stats">
                    <span class="stat-item">${score.toFixed(0)}/${maxPoints.toFixed(0)} pts</span>
                </div>
            </div>
        `;
    }

    renderQuickStats() {
        const itemGrades = this.grades.items || [];
        const moduleGrades = this.grades.modules || [];
        
        // Calculate stats
        const totalItems = itemGrades.length;
        const avgModuleGrade = moduleGrades.length > 0 ? 
            moduleGrades.reduce((sum, m) => sum + ((m.final_score / m.max_points) * 100), 0) / moduleGrades.length : 0;
        
        const excellentGrades = itemGrades.filter(g => ((g.final_score / g.max_points) * 100) >= 90).length;
        const needsImprovementGrades = itemGrades.filter(g => ((g.final_score / g.max_points) * 100) < 70).length;
        
        return `
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon">🎯</div>
                    <div class="stat-info">
                        <span class="stat-number">${avgModuleGrade.toFixed(1)}%</span>
                        <span class="stat-label">Avg Module Grade</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">⭐</div>
                    <div class="stat-info">
                        <span class="stat-number">${excellentGrades}</span>
                        <span class="stat-label">Excellent Grades</span>
                    </div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon">📈</div>
                    <div class="stat-info">
                        <span class="stat-number">${totalItems}</span>
                        <span class="stat-label">Total Items</span>
                    </div>
                </div>
                <div class="stat-card ${needsImprovementGrades > 0 ? 'stat-warning' : ''}">
                    <div class="stat-icon">${needsImprovementGrades > 0 ? '⚠️' : '✅'}</div>
                    <div class="stat-info">
                        <span class="stat-number">${needsImprovementGrades}</span>
                        <span class="stat-label">Need Improvement</span>
                    </div>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        // Tab switching - updated for new nav-tab class
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-tab') || e.target.closest('.nav-tab')) {
                const tab = e.target.closest('.nav-tab') || e.target;
                this.renderTabContent(tab.dataset.tab);
            }
        });

        // Search functionality
        document.addEventListener('input', (e) => {
            if (e.target.id === 'gradesSearch') {
                this.performSearch(e.target.value);
            }
        });

        // Filter handlers
        document.addEventListener('change', (e) => {
            if (e.target.id === 'gradeFilter') {
                this.applyGradeFilter(e.target.value);
            }
            if (e.target.id === 'submission-status-filter' || e.target.id === 'submission-module-filter') {
                this.filterSubmissions();
            }
        });
    }

    // New search and filter functionality
    performSearch(searchTerm) {
        if (!searchTerm.trim()) {
            // Show all items when search is empty
            this.renderTabContent(this.currentTab);
            return;
        }

        const term = searchTerm.toLowerCase();
        
        // Filter based on current tab
        if (this.currentTab === 'modules') {
            this.filterModules(term);
        } else if (this.currentTab === 'submissions') {
            this.filterSubmissions(term);
        }
    }

    applyGradeFilter(filterValue) {
        // Apply grade-based filtering
        if (this.currentTab === 'modules' || this.currentTab === 'submissions') {
            this.renderTabContent(this.currentTab);
        }
    }

    filterModules(searchTerm = '') {
        const container = document.getElementById('modulesContent');
        const moduleGrades = this.grades.modules || [];
        
        let filteredModules = moduleGrades;
        
        if (searchTerm) {
            filteredModules = moduleGrades.filter(module => {
                const moduleName = (module.modules?.name || '').toLowerCase();
                return moduleName.includes(searchTerm);
            });
        }
        
        container.innerHTML = `
            <div class="modules-grid">
                ${filteredModules.map(module => this.renderModulePerformanceCard(module)).join('')}
            </div>
        `;
    }

    filterSubmissions() {
        const statusFilter = document.getElementById('submission-status-filter')?.value;
        const moduleFilter = document.getElementById('submission-module-filter')?.value;
        
        // Start with all submissions
        let filteredSubmissions = [...this.submissions];
        
        // Apply status filter
        if (statusFilter === 'graded') {
            filteredSubmissions = filteredSubmissions.filter(s => s.raw_score !== null);
        } else if (statusFilter === 'ungraded') {
            filteredSubmissions = filteredSubmissions.filter(s => s.raw_score === null);
        }
        
        // Apply module filter
        if (moduleFilter) {
            filteredSubmissions = filteredSubmissions.filter(submission => {
                // Find which module this submission belongs to by matching constituent_slug
                const constituentSlug = submission.items?.constituent_slug;
                if (!constituentSlug) return false;
                
                // Find the constituent that matches this slug
                const constituent = this.constituents.find(c => c.slug === constituentSlug);
                if (!constituent) return false;
                
                // Check if the constituent's module_id matches the selected module filter
                return constituent.module_id === moduleFilter;
            });
        }
        
        // Update the submissions list
        const submissionsList = document.querySelector('.submissions-list');
        if (submissionsList) {
            if (filteredSubmissions.length === 0) {
                submissionsList.innerHTML = `
                    <div class="empty-state">
                        <div class="empty-icon">📋</div>
                        <h4>No submissions match your filters</h4>
                        <p>Try adjusting your filter selections.</p>
                    </div>
                `;
            } else {
                submissionsList.innerHTML = filteredSubmissions
                    .map(submission => this.renderSubmissionCard(submission))
                    .join('');
            }
        }
    }

    // Public method for manual refresh
    async refresh() {
        console.log('🔄 Refreshing student grades data...');
        try {
            await this.loadInitialData();
            this.renderGradesInterface();
            console.log('✅ Student grades refreshed successfully');
        } catch (error) {
            console.error('❌ Failed to refresh grades:', error);
            this.showError(`Failed to refresh grades: ${error.message}`);
            throw error;
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