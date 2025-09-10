/**
 * Student Grades Interface
 * Handles student view of their own grades, submissions, and academic progress
 * CACHE BUSTER: 2025-09-05-T00:28 - Fixed actual inline rendering code in constituent details
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
        this.selectedModuleId = null; // For the new split layout
        
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

        // Load metadata (constituents and modules) first - needed for lookups
        console.log('🔄 Loading metadata before initializing grades...');
        await this.loadMetadata();

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

            // Try to load each grade level independently with fallbacks
            let moduleGrades = { grades: [], summary: {} };
            let constituentGrades = { grades: [], summary: {} };
            let itemGrades = { grades: [], summary: {} };

            // Load module grades with fallback
            try {
                console.log('🔄 Loading module grades...');
                moduleGrades = await this.fetchGradesData(classSlug, 'module');
                console.log('✅ Module grades loaded successfully');
            } catch (error) {
                console.warn('⚠️ Failed to load module grades:', error.message);
                // Continue with empty module grades
            }

            // Load constituent grades with fallback
            try {
                console.log('🔄 Loading constituent grades...');
                constituentGrades = await this.fetchGradesData(classSlug, 'constituent');
                console.log('✅ Constituent grades loaded successfully');
            } catch (error) {
                console.warn('⚠️ Failed to load constituent grades:', error.message);
                // Continue with empty constituent grades
            }

            // Load item grades with fallback
            try {
                console.log('🔄 Loading item grades...');
                itemGrades = await this.fetchGradesData(classSlug, 'item');
                console.log('✅ Item grades loaded successfully');
            } catch (error) {
                console.warn('⚠️ Failed to load item grades:', error.message);
                console.log('🔄 Falling back to static items for item grades...');
                // Force fallback to static items when API fails
                try {
                    const staticItems = await this.loadStaticItems();
                    itemGrades = { grades: staticItems, summary: {} };
                    console.log(`✅ Using ${staticItems.length} static items as fallback`);
                } catch (staticError) {
                    console.error('❌ Static fallback also failed:', staticError);
                    itemGrades = { grades: [], summary: {} };
                }
            }

            // Load static items if we haven't already done so in fallback
            let staticItems = itemGrades.grades || [];
            if (staticItems.length === 0) {
                console.log('🔄 Loading items from static data as final fallback...');
                try {
                    staticItems = await this.loadStaticItems();
                    console.log(`✅ Loaded ${staticItems.length} items from static data`);
                } catch (error) {
                    console.warn('⚠️ Failed to load static items:', error.message);
                    staticItems = [];
                }
            }

            this.grades = {
                modules: moduleGrades.grades || [],
                constituents: constituentGrades.grades || [],
                items: staticItems
            };

            this.gradeSummary = {
                modules: moduleGrades.summary || {},
                constituents: constituentGrades.summary || {},
                items: itemGrades.summary || {}
            };

            const modulesLoaded = this.grades.modules?.length || 0;
            const constituentsLoaded = this.grades.constituents?.length || 0;
            const itemsLoaded = this.grades.items?.length || 0;

            console.log(`✅ Grades loaded: ${modulesLoaded} modules, ${constituentsLoaded} constituents, ${itemsLoaded} items`);

            // Validate and fix data consistency after loading
            this.validateDataConsistency();

            // Show a warning if some data failed to load
            if (modulesLoaded === 0 && constituentsLoaded === 0 && itemsLoaded === 0) {
                throw new Error('No grade data could be loaded. Please check your connection and try again.');
            }

        } catch (error) {
            console.error('Failed to load grades:', error);
            this.showError(`Failed to load grades: ${error.message}`);
        }
    }

    async fetchGradesData(classSlug, level, retryCount = 0) {
        const maxRetries = 2;
        
        if (!window.AuthClient) {
            throw new Error('AuthClient not available');
        }

        try {
            console.log(`🔄 Fetching ${level} grades (attempt ${retryCount + 1}/${maxRetries + 1})`);
            
            const result = await window.AuthClient.callEndpoint(
                `/student-grades?class_slug=${classSlug}&level=${level}`
            );
            
            console.log(`✅ Fetched ${level} grades: ${result.grades?.length || 0} items`);
            return result;
        } catch (error) {
            console.error(`❌ Failed to fetch ${level} grades (attempt ${retryCount + 1}):`, error);
            
            // Retry on timeout or network errors
            if (retryCount < maxRetries && (
                error.message.includes('timeout') || 
                error.message.includes('network') ||
                error.message.includes('fetch')
            )) {
                console.log(`⏳ Retrying ${level} grades in ${(retryCount + 1) * 2} seconds...`);
                await new Promise(resolve => setTimeout(resolve, (retryCount + 1) * 2000));
                return this.fetchGradesData(classSlug, level, retryCount + 1);
            }
            
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
                console.log(`✅ Loaded ${this.modules.length} modules`);
            } else {
                console.warn('⚠️ Could not load modules.json, continuing without module data');
            }
            
            console.log('🔍 Loading constituents from:', constituentsUrl);
            const constituentsResponse = await fetch(constituentsUrl);
            if (constituentsResponse.ok) {
                const constituentsData = await constituentsResponse.json();
                this.constituents = constituentsData.constituents || [];
                console.log(`✅ Loaded ${this.constituents.length} constituents`);
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
            // Use GitHub profile picture if available, otherwise fallback to placeholder
            const avatarUrl = userContext.avatar_url || '/assets/images/profile-placeholder.svg';
            const displayName = userContext.full_name || userContext.github_username || user.email;
            const githubUsername = userContext.github_username || 'Unknown';
            
            studentInfo.innerHTML = `
                <div class="profile-avatar">
                    <img src="${avatarUrl}" alt="Profile" class="avatar-img" onerror="this.style.display='none'; this.nextElementSibling.style.display='block';">
                    <div class="avatar-fallback" style="display:none;">👤</div>
                </div>
                <div class="profile-details">
                    <h2>${displayName}</h2>
                    <p class="student-meta">@${githubUsername} • ${userContext.class_title || 'GitHub Class Template'}</p>
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
        const currentScore = gradeSummary.querySelector('.current-score');
        const totalPossible = gradeSummary.querySelector('.total-possible');
        const percentageText = gradeSummary.querySelector('.percentage-text');
        const countNumber = gradeSummary.querySelector('.count-number');
        const timeText = gradeSummary.querySelector('.time-text');
        
        // Hide Overall Grade card as it's confusing
        const overallCard = gradeSummary.querySelector('.overall-grade');
        if (overallCard) {
            overallCard.style.display = 'none';
        }
        
        // Dynamic calculation: Use actual module weights from SQL
        const moduleGrades = this.grades.modules || [];
        
        let totalEarnedPoints = 0;
        let totalPossiblePoints = 0;
        
        moduleGrades.forEach(module => {
            const score = parseFloat(module.final_score || 0); // 0-10 scale
            
            // Get weight ONLY from module configuration in database
            let weight = 0;
            if (module.modules?.weight) {
                weight = parseFloat(module.modules.weight);
            } else if (module.weight) {
                weight = parseFloat(module.weight);
            }
            // Removed max_points fallback - it represents item points, not module weight!
            
            // Only include modules that have valid weights
            if (weight > 0) {
                // Convert: if student got 9/10 in a module worth 25%, they earned 22.5 points
                const earnedPoints = (score / 10) * weight;
                totalEarnedPoints += earnedPoints;
                totalPossiblePoints += weight;
            }
        });
        
        // Update display
        if (currentScore) {
            currentScore.textContent = totalEarnedPoints.toFixed(1);
        }
        
        if (totalPossible) {
            totalPossible.textContent = totalPossiblePoints > 0 ? totalPossiblePoints.toString() : '60';
        }
        
        if (percentageText) {
            const percentage = ((totalEarnedPoints / totalPossiblePoints) * 100).toFixed(1);
            percentageText.textContent = percentage;
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

        // DEBUG: Overview tab data analysis
        console.group('📋 OVERVIEW TAB DEBUG');
        console.log('📈 Total itemGrades:', itemGrades.length);
        console.log('🔍 First grade sample:', itemGrades[0]);
        console.groupEnd();
        
        // Filter for items that actually have grades (submitted work) vs just item definitions
        const actualGrades = itemGrades.filter(grade => 
            grade.computed_at || grade.submitted_at || (grade.final_score && grade.final_score > 0)
        );
        
        console.log('✅ Actual grades found:', actualGrades.length);
        console.log('📅 Using fallback (static items):', actualGrades.length === 0);
        
        // If we have actual grades, show those. Otherwise show recent upcoming items
        const recentGrades = actualGrades.length > 0 
            ? actualGrades.slice(0, 6)
            : itemGrades.slice(0, 6); // Show upcoming items as fallback
        
        container.innerHTML = `
            <div class="overview-layout">
                <!-- Recent Grades Section -->
                <section class="overview-section">
                    <div class="section-header">
                        <h3>${actualGrades.length > 0 ? '📝 Recent Grades' : '📅 Upcoming Items'}</h3>
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
        
        // If no module is selected, select the first one by default
        if (!this.selectedModuleId && moduleGrades.length > 0) {
            this.selectedModuleId = moduleGrades[0].modules?.id || moduleGrades[0].module_id;
        }
        
        container.innerHTML = `
            <div class="modules-split-layout">
                <div class="modules-sidebar">
                    <div class="modules-sidebar-header">
                        <h3>📚 Modules</h3>
                        <span class="module-count">${moduleGrades.length} modules</span>
                    </div>
                    <div class="modules-list">
                        ${moduleGrades.map(module => {
                            const moduleId = module.modules?.id || module.module_id;
                            const isSelected = moduleId === this.selectedModuleId;
                            return this.renderSimpleModuleCard(module, isSelected);
                        }).join('')}
                    </div>
                </div>
                <div class="module-details-panel">
                    ${this.renderModuleDetails(this.selectedModuleId)}
                </div>
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
        // DEBUG: Easy-to-copy console output for grade data analysis
        console.group('🔍 GRADE DEBUG:', grade.title || grade.item_id || 'unknown');
        console.log('📊 GRADE OBJECT:', JSON.stringify(grade, null, 2));
        console.log('📅 Has computed_at:', !!grade.computed_at);
        console.log('📅 Has submitted_at:', !!grade.submitted_at);
        console.log('📝 Has final_score:', !!grade.final_score);
        console.groupEnd();
        
        // Handle both real submission data and mock static data
        let gradeDate, score, maxPoints, percentage;
        
        if (grade.computed_at || grade.submitted_at) {
            // Real submission data
            gradeDate = new Date(grade.computed_at || grade.submitted_at).toLocaleDateString();
            score = grade.final_score || grade.raw_score || 0;
            maxPoints = grade.max_points || grade.points || 100;
            percentage = maxPoints > 0 ? ((score / maxPoints) * 100).toFixed(1) : 0;
        } else {
            // Static item data - show as pending/not submitted
            gradeDate = grade.due_date ? `Due: ${new Date(grade.due_date).toLocaleDateString()}` : 'No date';
            score = 0;
            maxPoints = grade.points || 100;
            percentage = 'Pending'; // Show as "Pending" instead of 0.0%
            console.log('🟡 USING STATIC DATA - Set percentage to:', percentage);
        }
        
        // DEBUG: Show final calculated values
        console.log('🎯 FINAL VALUES:', {
            percentage,
            score,
            maxPoints,
            gradeDate,
            codeVersion: '2025-09-05-T00:05' // Cache buster
        });
        
        // Defensive checks for data structure variations
        const itemTitle = grade.items?.title || grade.item_title || grade.title || 'Unknown Item';
        const constituentSlug = grade.items?.constituent_slug || grade.constituent_slug;
        
        if (!constituentSlug) {
            console.warn('⚠️ Missing constituent_slug for item:', itemTitle);
        }
        
        // Look up constituent and module info using the constituent_slug
        const constituent = this.constituents.find(c => c.slug === constituentSlug);
        const constituentName = constituent?.name || 'Unknown Section';
        
        // Look up module info using the constituent's module_id
        const moduleId = constituent?.module_id;
        const module = this.modules.find(m => m.id === moduleId);
        const moduleName = module?.name || 'Unknown Module';
        
        // Get grade color based on percentage
        let gradeColor = '#10B981'; // Green for good grades
        if (percentage === 'Pending' || percentage === '0.0' || percentage === 0) {
            gradeColor = '#9CA3AF'; // Gray for pending/unsubmitted
        } else if (percentage < 60) {
            gradeColor = '#EF4444'; // Red for failing
        } else if (percentage < 70) {
            gradeColor = '#F59E0B'; // Yellow for concerning
        } else if (percentage < 85) {
            gradeColor = '#6B7280'; // Gray for average
        }
        
        return `
            <div class="grade-card recent-grade-card">
                <div class="card-header">
                    <div class="item-info">
                        <h4 class="item-title">${itemTitle}</h4>
                        <p class="item-path">${moduleName} › ${constituentName}</p>
                    </div>
                    <div class="grade-badge" style="background-color: ${gradeColor}">
                        ${percentage === 'Pending' ? 'Pending' : percentage + '%'}
                        <small style="font-size: 8px; display: block;">[v00:20]</small>
                    </div>
                </div>
                <div class="card-footer">
                    <span class="points-detail">${score}/${maxPoints} pts</span>
                    <span class="grade-date">${gradeDate}</span>
                </div>
            </div>
        `;
    }

    // New simplified module card for split layout
    renderSimpleModuleCard(moduleGrade, isSelected = false) {
        const score = parseFloat(moduleGrade.final_score || 0); // 0-10 scale
        const moduleName = moduleGrade.modules?.name || 'Unknown Module';
        const moduleColor = moduleGrade.modules?.color || '#6B7280';
        const moduleIcon = moduleGrade.modules?.icon || '📚';
        const moduleId = moduleGrade.modules?.id || moduleGrade.module_id;
        const moduleWeight = parseFloat(moduleGrade.modules?.weight || 0);
        
        // Calculate earned weight (score/10 * weight)
        const earnedWeight = (score / 10) * moduleWeight;
        const performancePercentage = score * 10; // 0-10 to percentage
        
        return `
            <div class="simple-module-card ${isSelected ? 'selected' : ''}" 
                 onclick="window.selectModule('${moduleId}')"
                 data-module-id="${moduleId}">
                <div class="module-card-content">
                    <div class="module-header-simple">
                        <span class="module-icon-simple">${moduleIcon}</span>
                        <div class="module-info-simple">
                            <h4 class="module-name-simple">${moduleName}</h4>
                            <div class="module-grade-simple">
                                <span class="grade-fraction">${earnedWeight.toFixed(1)}/${moduleWeight}</span>
                                <span class="grade-percentage">${performancePercentage.toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>
                    <div class="module-status-indicator" style="background-color: ${moduleColor}"></div>
                </div>
            </div>
        `;
    }

    // Render detailed view for selected module
    renderModuleDetails(moduleId) {
        if (!moduleId) {
            return `
                <div class="module-details-empty">
                    <div class="empty-state">
                        <span class="empty-icon">📚</span>
                        <h3>Select a Module</h3>
                        <p>Click on a module from the left to view detailed information</p>
                    </div>
                </div>
            `;
        }

        // Find the selected module
        const moduleGrade = this.grades.modules?.find(m => 
            (m.modules?.id || m.module_id) === moduleId
        );
        
        if (!moduleGrade) {
            return `
                <div class="module-details-empty">
                    <div class="empty-state">
                        <span class="empty-icon">❌</span>
                        <h3>Module Not Found</h3>
                        <p>The selected module could not be found</p>
                    </div>
                </div>
            `;
        }

        // Calculate module statistics
        const score = parseFloat(moduleGrade.final_score || 0);
        const moduleName = moduleGrade.modules?.name || 'Unknown Module';
        const moduleColor = moduleGrade.modules?.color || '#6B7280';
        const moduleIcon = moduleGrade.modules?.icon || '📚';
        const moduleWeight = parseFloat(moduleGrade.modules?.weight || 0);
        const earnedWeight = (score / 10) * moduleWeight;
        const performancePercentage = score * 10;
        const stats = this.calculateModuleStatistics(moduleId);


        return `
            <div class="module-details-content">
                <div class="module-details-header" style="border-left: 4px solid ${moduleColor}">
                    <div class="module-title-section">
                        <span class="module-icon-large">${moduleIcon}</span>
                        <div class="module-title-info">
                            <h2>${moduleName}</h2>
                            <div class="module-grade-display">
                                <span class="grade-main">${earnedWeight.toFixed(1)}/${moduleWeight}</span>
                                <span class="grade-percentage-main">${performancePercentage.toFixed(0)}%</span>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="module-stats-section">
                    <div class="stat-card-detail">
                        <span class="stat-label">Grade</span>
                        <span class="stat-value">${earnedWeight.toFixed(1)}/${moduleWeight} (${performancePercentage.toFixed(0)}%)</span>
                    </div>
                    <div class="stat-card-detail">
                        <span class="stat-label">Items Delivered</span>
                        <span class="stat-value">${stats.submitted}/${stats.total} (${stats.submittedPercent}%)</span>
                    </div>
                    <div class="stat-card-detail">
                        <span class="stat-label">Missing Items</span>
                        <span class="stat-value">${stats.missing}/${stats.total} (${stats.missingPercent}%)</span>
                    </div>
                </div>

                <div class="constituents-section">
                    <h3>📋 Constituents & Items</h3>
                    <div class="constituents-detail-list">
                        ${this.renderConstituentsDirectly(moduleId)}
                    </div>
                </div>
            </div>
        `;
    }

    renderModulePerformanceCard(moduleGrade) {
        // Handle 0-10 grading scale properly
        const score = parseFloat(moduleGrade.final_score || 0); // 0-10 scale
        const moduleName = moduleGrade.modules?.name || 'Unknown Module';
        const moduleColor = moduleGrade.modules?.color || '#6B7280';
        const moduleIcon = moduleGrade.modules?.icon || '📚';
        const moduleId = moduleGrade.modules?.id || moduleGrade.module_id;
        const moduleWeight = parseFloat(moduleGrade.modules?.weight || 0);
        
        // Calculate earned weight (score/10 * weight)
        const earnedWeight = (score / 10) * moduleWeight;
        const performancePercentage = score * 10; // 0-10 to percentage
        
        // Get submission statistics
        const stats = this.calculateModuleStatistics(moduleId);
        
        return `
            <div class="module-card performance-card expandable-card" style="border-left: 4px solid ${moduleColor}" data-module-id="${moduleId}">
                <div class="module-header clickable-header" onclick="window.toggleModuleExpansion('${moduleId}')">
                    <div class="module-info">
                        <span class="module-icon">${moduleIcon}</span>
                        <div>
                            <h4 class="module-name">${moduleName}</h4>
                            <div class="module-metrics-summary">
                                <span class="grade-summary">${earnedWeight.toFixed(1)}/${moduleWeight} (${performancePercentage.toFixed(0)}%)</span>
                            </div>
                        </div>
                    </div>
                    <div class="header-right">
                        <div class="grade-display">
                            <span class="grade-percentage">${performancePercentage.toFixed(0)}%</span>
                        </div>
                        <span class="expand-icon">▶</span>
                    </div>
                </div>
                <div class="module-details" id="module-details-${moduleId}" style="display: none;">
                    <div class="module-metrics-grid">
                        <div class="metric-row">
                            <span class="metric-label">Grade:</span>
                            <span class="metric-value">${earnedWeight.toFixed(1)}/${moduleWeight}</span>
                            <span class="metric-percentage">(${performancePercentage.toFixed(0)}%)</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Items Delivered:</span>
                            <span class="metric-value">${stats.submitted}/${stats.total}</span>
                            <span class="metric-percentage">(${stats.submittedPercent}%)</span>
                        </div>
                        <div class="metric-row">
                            <span class="metric-label">Missing Items:</span>
                            <span class="metric-value">${stats.missing}/${stats.total}</span>
                            <span class="metric-percentage">(${stats.missingPercent}%)</span>
                        </div>
                    </div>
                    <div class="module-constituents" id="constituents-${moduleId}">
                        <div class="constituents-loading">Loading constituent details...</div>
                    </div>
                </div>
            </div>
        `;
    }

    renderQuickStats() {
        const itemGrades = this.grades.items || [];
        const moduleGrades = this.grades.modules || [];
        
        // Calculate stats with proper 0-10 scale handling
        const totalItems = itemGrades.length;
        const avgModuleGrade = moduleGrades.length > 0 ? 
            moduleGrades.reduce((sum, m) => {
                const percentage = m.percentage ? parseFloat(m.percentage) : (parseFloat(m.final_score || 0) * 10);
                return sum + percentage;
            }, 0) / moduleGrades.length : 0;
        
        const excellentGrades = itemGrades.filter(g => {
            const percentage = g.percentage ? parseFloat(g.percentage) : ((g.final_score / g.max_points) * 100);
            return percentage >= 90;
        }).length;
        
        const needsImprovementGrades = itemGrades.filter(g => {
            const percentage = g.percentage ? parseFloat(g.percentage) : ((g.final_score / g.max_points) * 100);
            return percentage < 70;
        }).length;
        
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

    async loadMetadata() {
        try {
            // Get the base URL for data files
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            const baseUrl = pathParts.length > 0 ? `/${pathParts[0]}/` : '/';
            
            console.group('🗂️ LOADING METADATA');
            
            // Load constituents
            const constituentsUrl = `${baseUrl}data/constituents.json`;
            console.log(`🔄 Loading constituents from ${constituentsUrl}`);
            
            const constituentsResponse = await fetch(constituentsUrl);
            if (constituentsResponse.ok) {
                const constituentsData = await constituentsResponse.json();
                this.constituents = constituentsData.constituents || [];
                console.log(`✅ Loaded ${this.constituents.length} constituents`);
            } else {
                console.warn('⚠️ Could not load constituents.json');
                this.constituents = [];
            }
            
            // Load modules (check if modules.json exists, otherwise derive from constituents)
            const modulesUrl = `${baseUrl}data/modules.json`;
            console.log(`🔄 Attempting to load modules from ${modulesUrl}`);
            
            try {
                const modulesResponse = await fetch(modulesUrl);
                if (modulesResponse.ok) {
                    const modulesData = await modulesResponse.json();
                    this.modules = modulesData.modules || [];
                    console.log(`✅ Loaded ${this.modules.length} modules from modules.json`);
                } else {
                    throw new Error('modules.json not found');
                }
            } catch (error) {
                // Derive modules from constituents
                console.log(`📋 Deriving modules from constituents (modules.json not found)`);
                const moduleMap = new Map();
                
                this.constituents.forEach(constituent => {
                    if (constituent.module_id && !moduleMap.has(constituent.module_id)) {
                        moduleMap.set(constituent.module_id, {
                            id: constituent.module_id,
                            name: constituent.module_id.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
                        });
                    }
                });
                
                this.modules = Array.from(moduleMap.values());
                console.log(`✅ Derived ${this.modules.length} modules from constituents`);
            }
            
            console.groupEnd();
            
        } catch (error) {
            console.error('❌ Failed to load metadata:', error);
            this.constituents = [];
            this.modules = [];
        }
    }

    async loadStaticItems() {
        try {
            // Get the base URL for data files
            const pathParts = window.location.pathname.split('/').filter(Boolean);
            const baseUrl = pathParts.length > 0 ? `/${pathParts[0]}/` : '/';
            const itemsUrl = `${baseUrl}data/items.json`;
            
            console.log(`🔄 Loading static items from ${itemsUrl}`);
            const response = await fetch(itemsUrl);
            
            if (!response.ok) {
                throw new Error(`Failed to load items: ${response.status}`);
            }
            
            const data = await response.json();
            const items = data.items || [];
            
            // Return items in BOTH flat and nested structure for compatibility
            return items.map(item => ({
                item_id: item.item_id,
                // Flat structure for new direct rendering
                constituent_slug: item.constituent_slug,
                title: item.title,
                points: item.points,
                delivery_type: item.delivery_type,
                due_date: item.due_date,
                important: item.important,
                file_path: item.file_path,
                // Nested structure for existing code compatibility
                items: {
                    id: item.item_id,
                    title: item.title,
                    points: item.points,
                    constituent_slug: item.constituent_slug,
                    delivery_type: item.delivery_type,
                    due_date: item.due_date,
                    important: item.important,
                    is_current: true,
                    file_path: item.file_path
                },
                // No grade data since these come from static files
                final_score: 0,
                max_points: item.points,
                percentage: "0"
            }));
            
        } catch (error) {
            console.error('Failed to load static items:', error);
            throw error;
        }
    }

    validateDataConsistency() {
        console.log('🔍 Validating data consistency...');
        
        // Check constituent-item linking
        const itemsByConstituent = new Map();
        const submissionsByItem = new Map();
        
        // Group items by constituent slug
        this.grades.items.forEach(item => {
            const slug = item.items?.constituent_slug;
            if (slug) {
                if (!itemsByConstituent.has(slug)) {
                    itemsByConstituent.set(slug, []);
                }
                itemsByConstituent.get(slug).push(item);
            } else {
                console.warn('⚠️ Item without constituent_slug:', item);
            }
        });
        
        // Group submissions by item_id
        this.submissions.forEach(submission => {
            const itemId = submission.item_id;
            if (itemId) {
                submissionsByItem.set(itemId, submission);
            }
        });
        
        // Check each constituent has items
        this.constituents.forEach(constituent => {
            const items = itemsByConstituent.get(constituent.slug) || [];
            console.log(`📋 Constituent ${constituent.slug} (${constituent.name}): ${items.length} items`);
            
            if (items.length === 0) {
                console.warn(`⚠️ Constituent ${constituent.slug} has no items`);
            } else {
                // Check submissions for each item
                const submittedCount = items.filter(item => 
                    submissionsByItem.has(item.item_id)
                ).length;
                console.log(`   └─ ${submittedCount}/${items.length} items have submissions`);
            }
        });
        
        // Check for orphaned submissions (submissions without items)
        const knownItemIds = new Set(this.grades.items.map(item => item.item_id));
        const orphanedSubmissions = this.submissions.filter(sub => 
            !knownItemIds.has(sub.item_id)
        );
        
        if (orphanedSubmissions.length > 0) {
            console.warn(`⚠️ Found ${orphanedSubmissions.length} submissions for items not in current data:`, 
                orphanedSubmissions.map(sub => sub.item_id));
        }
        
        console.log('✅ Data consistency validation complete');
        
        return {
            itemsByConstituent,
            submissionsByItem,
            orphanedSubmissions
        };
    }

    // Utility methods
    calculateModuleStatistics(moduleId) {
        if (!moduleId) return { submitted: 0, total: 0, missing: 0, submittedPercent: 0, missingPercent: 0 };
        
        // Get all constituents for this module
        const moduleConstituents = this.constituents.filter(c => c.module_id === moduleId);
        
        if (moduleConstituents.length === 0) {
            console.warn(`⚠️ No constituents found for module: ${moduleId}`);
            return { submitted: 0, total: 0, missing: 0, submittedPercent: 0, missingPercent: 0 };
        }
        
        // Get all items for these constituents
        let moduleItems = [];
        moduleConstituents.forEach(constituent => {
            const itemsData = this.grades.items || [];
            const constituentItems = itemsData.filter(item => {
                return item.items?.constituent_slug === constituent.slug;
            });
            moduleItems = moduleItems.concat(constituentItems.map(item => ({
                id: item.item_id,
                constituent_slug: item.items?.constituent_slug,
                title: item.items?.title
            })));
        });
        
        // Get submissions for items in this module (including submissions for items not in current grades)
        const moduleSubmissions = this.submissions.filter(sub => {
            const itemConstituent = sub.items?.constituent_slug;
            return moduleConstituents.some(c => c.slug === itemConstituent);
        });
        
        // Get unique item IDs that have submissions
        const submittedItemIds = new Set(moduleSubmissions.map(sub => sub.item_id));
        
        // Calculate totals with proper validation
        const totalItems = Math.max(moduleItems.length, submittedItemIds.size);
        const submittedItems = submittedItemIds.size;
        const missingItems = Math.max(0, totalItems - submittedItems); // Ensure never negative
        
        const submittedPercent = totalItems > 0 ? Math.round((submittedItems / totalItems) * 100) : 0;
        const missingPercent = totalItems > 0 ? Math.round((missingItems / totalItems) * 100) : 0;
        
        console.log(`📊 Module ${moduleId} stats: ${submittedItems}/${totalItems} submitted, ${missingItems} missing`);
        
        return {
            submitted: submittedItems,
            total: totalItems,
            missing: missingItems,
            submittedPercent,
            missingPercent
        };
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Module expansion functionality
    toggleModuleExpansion(moduleId) {
        const detailsElement = document.getElementById(`module-details-${moduleId}`);
        const expandIcon = document.querySelector(`[data-module-id="${moduleId}"] .expand-icon`);
        
        if (!detailsElement) return;
        
        const isExpanded = detailsElement.style.display !== 'none';
        
        if (isExpanded) {
            // Collapse
            detailsElement.style.display = 'none';
            expandIcon.style.transform = 'rotate(0deg)';
        } else {
            // Expand
            detailsElement.style.display = 'block';
            expandIcon.style.transform = 'rotate(90deg)';
            
            // Load constituent details if not loaded
            this.loadConstituentDetails(moduleId);
        }
    }

    renderConstituentsDirectly(moduleId) {
        // Get constituents for this module
        const moduleConstituents = this.constituents.filter(c => c.module_id === moduleId);
        
        if (moduleConstituents.length === 0) {
            return '<div class="no-constituents">No constituents found for this module</div>';
        }
        
        // Render each constituent with its items
        const constituentsHtml = moduleConstituents.map(constituent => {
            return this.renderConstituentDetailsSimple(constituent);
        }).join('');
        
        return `
            <div class="constituents-list">
                <h5>📋 Constituents & Items</h5>
                ${constituentsHtml}
            </div>
        `;
    }

    loadConstituentDetails(moduleId) {
        // Prevent multiple simultaneous loads for the same module
        const loadingKey = `loading-${moduleId}`;
        if (this[loadingKey]) {
            console.log(`⏸️ Already loading constituents for module ${moduleId}, skipping...`);
            return;
        }
        this[loadingKey] = true;
        
        console.log(`🔄 Loading constituent details for module: ${moduleId}`);
        const container = document.getElementById(`constituents-${moduleId}`);
        
        if (!container) {
            console.error(`❌ Container not found: constituents-${moduleId}`);
            this[loadingKey] = false;
            return;
        }
        
        console.log(`✅ Container found for module ${moduleId}`);
        
        // Get constituents for this module
        const moduleConstituents = this.constituents.filter(c => c.module_id === moduleId);
        console.log(`📋 Found ${moduleConstituents.length} constituents for module ${moduleId}:`, moduleConstituents);
        
        if (moduleConstituents.length === 0) {
            console.warn(`⚠️ No constituents found for module ${moduleId}`);
            container.innerHTML = '<div class="no-constituents">No constituents found</div>';
            this[loadingKey] = false;
            return;
        }
        
        try {
            // Render constituents with their items
            const constituentsHtml = moduleConstituents.map(constituent => {
                console.log(`🔧 Rendering constituent: ${constituent.slug}`);
                return this.renderConstituentDetails(constituent);
            }).join('');
            
            container.innerHTML = `
                <div class="constituents-list">
                    <h5>📋 Constituents & Items</h5>
                    ${constituentsHtml}
                </div>
            `;
            console.log(`✅ Successfully loaded constituents for module ${moduleId}`);
            this[loadingKey] = false;
        } catch (error) {
            console.error(`❌ Error rendering constituents for module ${moduleId}:`, error);
            container.innerHTML = '<div class="error-constituents">Error loading constituent details</div>';
            this[loadingKey] = false;
        }
    }

    renderConstituentDetailsSimple(constituent) {
        // CLEAN DEBUG OUTPUT - Easy to filter and copy
        console.log(`CONSTITUENT_DEBUG_START: ${constituent.slug}`);
        
        if (this.grades.items.length > 0) {
            const sample = this.grades.items[0];
            console.log('SAMPLE_ITEM_STRUCTURE:', JSON.stringify({
                item_id: sample.item_id,
                constituent_paths: {
                    flat: sample.constituent_slug,
                    items_nested: sample.items?.constituent_slug,
                    constituents_slug: sample.constituents?.slug,
                    constituents_nested: sample.constituents?.constituent_slug
                },
                full_constituents: sample.constituents,
                full_items: sample.items
            }, null, 2));
        }
        
        // Get items for this constituent - try multiple matching strategies
        const constituentItems = this.grades.items.filter(item => {
            // Strategy 1: Direct slug matching (static data)
            const directSlug = item.constituent_slug || item.items?.constituent_slug || item.constituents?.slug || item.constituents?.constituent_slug;
            
            // Strategy 2: Match by constituent name (convert to slug format)
            const constituentName = item.constituents?.name;
            const nameToSlug = constituentName ? constituentName.toLowerCase().replace(/\s+/g, '-') : null;
            
            // Strategy 3: Reverse lookup - find constituent by item_id
            const foundConstituent = this.constituents.find(c => c.slug === constituent.slug);
            const nameMatch = constituentName === foundConstituent?.name;
            
            const match = directSlug === constituent.slug || nameToSlug === constituent.slug || nameMatch;
            
            if (match) {
                console.log(`MATCH_FOUND: ${constituent.slug} (via direct:${directSlug}, name:${nameToSlug}, nameMatch:${nameMatch})`);
            }
            return match;
        });
        
        console.log(`CONSTITUENT_RESULT: ${constituent.slug} = ${constituentItems.length} items`);
        console.log(`CONSTITUENT_DEBUG_END: ${constituent.slug}`);
        
        // Calculate constituent stats
        const totalItems = constituentItems.length;
        const submittedItems = constituentItems.filter(item => {
            return this.submissions.some(sub => sub.item_id === item.item_id);
        }).length;
        
        // Calculate earned points using simple structure
        let earnedPoints = 0;
        let totalPoints = 0;
        constituentItems.forEach(item => {
            const itemPoints = parseFloat(item.points || 0);
            totalPoints += itemPoints;
            
            const submission = this.submissions.find(sub => sub.item_id === item.item_id);
            if (submission && submission.raw_score !== null) {
                earnedPoints += parseFloat(submission.adjusted_score || submission.raw_score || 0);
            }
        });
        
        const percentage = totalPoints > 0 ? (earnedPoints / totalPoints * 100) : 0;
        
        // Render items using correct Edge Function data structure
        const itemsHtml = constituentItems.map(item => {
            const submission = this.submissions.find(sub => sub.item_id === item.item_id);
            const isSubmitted = submission !== undefined;
            
            // Handle Edge Function data structure
            const points = parseFloat(item.max_points || item.items?.points || item.points || 0);
            const earnedPoints = parseFloat(item.final_score || submission?.adjusted_score || submission?.raw_score || 0);
            const itemTitle = item.items?.title || item.title || `Item ${item.item_id}`;
            const filePath = item.items?.file_path || item.file_path || '';
            const itemPath = filePath || `#${item.item_id}`;
            
            return `
                <div class="item-row ${isSubmitted ? 'submitted' : 'not-submitted'}" onclick="window.navigateToItem('${itemPath}')">
                    <div class="item-info">
                        <span class="item-status">${isSubmitted ? '✅' : '⭕'}</span>
                        <span class="item-title">${itemTitle}</span>
                    </div>
                    <div class="item-score">
                        ${isSubmitted ? 
                            `<span class="score">${earnedPoints}/${points}</span>` :
                            `<span class="score pending">--/${points}</span>`
                        }
                    </div>
                </div>
            `;
        }).join('');
        
        // Show appropriate message if no items
        let emptyMessage = '<div class="no-items">No items found</div>';
        if (constituentItems.length === 0 && this.grades.items.length === 0) {
            emptyMessage = '<div class="no-items">Items loading...</div>';
        } else if (constituentItems.length === 0) {
            emptyMessage = '<div class="no-items">No items defined for this constituent</div>';
        }
        
        return `
            <div class="constituent-section">
                <div class="constituent-header">
                    <span class="constituent-name">📂 ${constituent.name || 'Unknown Constituent'}</span>
                    <span class="constituent-score">${earnedPoints.toFixed(1)}/${totalPoints} (${percentage.toFixed(0)}%)</span>
                </div>
                <div class="items-list">
                    ${itemsHtml || emptyMessage}
                </div>
            </div>
        `;
    }

    renderConstituentDetails(constituent) {
        // SIMPLE DEBUG - Show only the first item structure once
        if (constituent.slug === 'auth-setup' && this.grades.items.length > 0) {
            console.log('🐛 STATIC ITEM STRUCTURE:', JSON.stringify(this.grades.items[0], null, 2));
            console.log('🐛 LOOKING FOR CONSTITUENT SLUG:', constituent.slug);
        }
        
        // Get items for this constituent - try multiple matching strategies
        let constituentItems = this.grades.items.filter(item => {
            // Strategy 1: Direct slug matching (static data)
            const directSlug = item.constituent_slug || item.items?.constituent_slug || item.constituents?.slug || item.constituents?.constituent_slug;
            
            // Strategy 2: Match by constituent name (convert to slug format)
            const constituentName = item.constituents?.name;
            const nameToSlug = constituentName ? constituentName.toLowerCase().replace(/\s+/g, '-') : null;
            
            // Strategy 3: Reverse lookup - find constituent by item_id
            const foundConstituent = this.constituents.find(c => c.slug === constituent.slug);
            const nameMatch = constituentName === foundConstituent?.name;
            
            return directSlug === constituent.slug || nameToSlug === constituent.slug || nameMatch;
        });
        
        // Calculate constituent stats
        const totalItems = constituentItems.length;
        const submittedItems = constituentItems.filter(item => {
            return this.submissions.some(sub => sub.item_id === item.item_id);
        }).length;
        
        // Calculate earned points - handle both data structures
        let earnedPoints = 0;
        let totalPoints = 0;
        constituentItems.forEach(item => {
            const itemPoints = parseFloat(item.items?.points || item.points || 0);
            totalPoints += itemPoints;
            
            const submission = this.submissions.find(sub => sub.item_id === item.item_id);
            if (submission && submission.raw_score !== null) {
                earnedPoints += parseFloat(submission.adjusted_score || submission.raw_score || 0);
            }
        });
        
        const percentage = totalPoints > 0 ? (earnedPoints / totalPoints * 100) : 0;
        
        const itemsHtml = constituentItems.map(item => {
            return this.renderItemRow(item);
        }).join('');
        
        // Show different messages based on the situation
        let emptyMessage = '<div class="no-items">No items found</div>';
        if (constituentItems.length === 0 && this.grades.items.length === 0) {
            emptyMessage = '<div class="no-items">Items loading...</div>';
        } else if (constituentItems.length === 0) {
            emptyMessage = '<div class="no-items">No items defined for this constituent</div>';
        }
        
        return `
            <div class="constituent-section">
                <div class="constituent-header">
                    <span class="constituent-name">📂 ${constituent.name || 'Unknown Constituent'}</span>
                    <span class="constituent-score">${earnedPoints.toFixed(1)}/${totalPoints} (${percentage.toFixed(0)}%)</span>
                </div>
                <div class="items-list">
                    ${itemsHtml || emptyMessage}
                </div>
            </div>
        `;
    }

    renderItemRow(item) {
        console.log('RENDERITEMROW_CALLED with item_id:', item?.item_id);
        
        // Safety check for undefined item
        if (!item || !item.item_id) {
            console.error('RENDERITEMROW_ERROR - Invalid item:', item);
            return '<div class="item-row error">Invalid item data</div>';
        }
        
        const submission = this.submissions.find(sub => sub.item_id === item.item_id);
        const isSubmitted = submission !== undefined;
        
        // DEBUG: Log first item structure
        if (!window.ITEM_LOGGED) {
            console.log('ITEMDATA_FULL:', JSON.stringify(item, null, 2));
            window.ITEM_LOGGED = true;
        }
        
        // Handle both nested and flat data structures - try more paths
        const points = parseFloat(item.max_points || item.items?.max_points || item.points || item.items?.points || 0);
        const earnedPoints = parseFloat(item.final_score || 0);
        const itemTitle = item.items?.title || item.title || `Item ${item.item_id}`;
        const filePath = item.items?.file_path || item.file_path || '';
        
        // Create navigation path
        const itemPath = filePath || `#${item.item_id}`;
        
        return `
            <div class="item-row ${isSubmitted ? 'submitted' : 'not-submitted'}" onclick="window.navigateToItem('${itemPath}')">
                <div class="item-info">
                    <span class="item-status">${isSubmitted ? '✅' : '⭕'}</span>
                    <span class="item-title">${itemTitle}</span>
                </div>
                <div class="item-score">
                    ${isSubmitted ? 
                        `<span class="score">${earnedPoints}/${points}</span>` :
                        `<span class="score pending">--/${points}</span>`
                    }
                </div>
            </div>
        `;
    }

    navigateToItem(itemPath) {
        if (itemPath && itemPath !== '#') {
            window.location.href = itemPath;
        }
    }

    // Module selection for split layout
    selectModule(moduleId) {
        console.log('🔍 Module selected:', moduleId);
        this.selectedModuleId = moduleId;
        // Re-render the modules tab to update selection and details
        this.renderModulesTab();
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
// Make functions globally available
window.StudentGradesInterface = StudentGradesInterface;

// Global functions for module expansion
window.toggleModuleExpansion = function(moduleId) {
    if (window.studentGradesInstance && window.studentGradesInstance.toggleModuleExpansion) {
        window.studentGradesInstance.toggleModuleExpansion(moduleId);
    }
};

window.navigateToItem = function(itemPath) {
    if (window.studentGradesInstance && window.studentGradesInstance.navigateToItem) {
        window.studentGradesInstance.navigateToItem(itemPath);
    }
};

window.selectModule = function(moduleId) {
    if (window.studentGradesInstance && window.studentGradesInstance.selectModule) {
        window.studentGradesInstance.selectModule(moduleId);
    }
};