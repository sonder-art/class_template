/**
 * Professor Grading Interface
 * Complete grading workflow for professors
 * Integrates with existing professor-grade-item Edge Function
 */

class ProfessorGradingInterface {
    constructor() {
        this.classId = null;
        this.supabase = null;
        this.items = [];
        this.submissions = [];
        this.students = [];
        this.modules = [];
        this.constituents = [];
        this.currentTab = 'pending';
        this.currentSubmission = null;
        this.filterMode = null; // 'student' or 'item' or null
        this.filterValue = null; // student_id or item_id
        this.selectedItemId = null; // Track which item is selected for detail view
        this.itemViewMode = 'list'; // 'list' or 'detail' - controls what renderItemsView shows
        
        // Initialize asynchronously to handle auth waiting
        this.init().catch(error => {
            console.error('❌ Professor grading interface initialization failed:', error);
            this.showError(error.message);
        });
    }

    async init() {
        console.log('🎯 Professor Grading Interface initializing...');
        
        try {
            // Check authentication and professor access
            await this.checkProfessorAccess();
            
            // Initialize Supabase client
            this.initializeSupabase();
            
            // Load all grading data
            await this.loadGradingData();
            
            // Setup UI
            this.setupEventListeners();
            this.renderInterface();
            
            console.log('✅ Professor grading interface initialized');
            
        } catch (error) {
            console.error('❌ Error in init method:', error);
            throw error; // Re-throw so constructor catch can handle it
        }
    }

    async checkProfessorAccess() {
        // First, let's see what we have right away
        console.log('🔍 Debug - Initial check:');
        console.log('  - window.authState exists:', !!window.authState);
        console.log('  - window.authState:', window.authState);
        console.log('  - window.authState.isLoading:', window.authState?.isLoading);
        console.log('  - window.authState.isAuthenticated:', window.authState?.isAuthenticated);
        
        // Wait for auth state to be available with timeout
        let attempts = 0;
        const maxAttempts = 50; // 10 seconds total
        
        while ((!window.authState || window.authState.isLoading) && attempts < maxAttempts) {
            console.log(`🔄 Waiting for auth state... (${attempts + 1}/${maxAttempts})`);
            console.log('  - Current authState:', window.authState);
            await new Promise(resolve => setTimeout(resolve, 200));
            attempts++;
        }
        
        console.log('🔍 Debug - After waiting:');
        console.log('  - window.authState:', window.authState);
        console.log('  - attempts used:', attempts);
        
        // Check authentication first
        if (!window.authState || !window.authState.isAuthenticated) {
            console.warn('🚫 User not authenticated');
            console.warn('  - authState exists:', !!window.authState);
            console.warn('  - isAuthenticated:', window.authState?.isAuthenticated);
            this.showAuthRequired();
            throw new Error('Authentication required');
        }
        
        // Get or fetch user context
        let userContext = window.authState.userContext;
        console.log('🔍 Debug - initial userContext:', userContext);
        
        // If userContext is not available, try to fetch it
        if (!userContext && window.AuthClient) {
            console.log('🔍 Debug - userContext not available, fetching...');
            try {
                const pathParts = window.location.pathname.split('/');
                const classSlug = pathParts[1] || 'class_template';
                userContext = await window.AuthClient.getMe(classSlug);
                
                // Store in auth state for future use
                if (userContext) {
                    window.authState.userContext = userContext;
                    console.log('🔍 Debug - fetched userContext:', userContext);
                }
            } catch (error) {
                console.error('🚫 Failed to fetch user context:', error);
                this.showAuthRequired();
                throw new Error('Unable to verify user permissions');
            }
        }
        
        console.log('🔍 Debug - final userContext:', userContext);
        console.log('🔍 Debug - userContext.role:', userContext?.role);
        
        if (!userContext || userContext.role !== 'professor') {
            console.warn('🚫 User is not a professor', { userContext, role: userContext?.role });
            this.showAuthRequired();
            throw new Error('Professor access required');
        }
        
        console.log('✅ Professor access verified:', userContext.github_username);
    }

    initializeSupabase() {
        // Get class ID from meta tags or config
        this.classId = document.querySelector('meta[name="class-id"]')?.content;
        let url = document.querySelector('meta[name="supabase-url"]')?.content;
        let key = document.querySelector('meta[name="supabase-anon-key"]')?.content;
        
        // Fallback to FrameworkConfig
        if (!this.classId && window.FrameworkConfig) {
            this.classId = window.FrameworkConfig.classContext?.classId;
            url = window.FrameworkConfig.supabase?.url;
            key = window.FrameworkConfig.supabase?.anonKey;
        }
        
        if (!this.classId || !url || !key) {
            throw new Error('Missing configuration: class ID or Supabase config');
        }
        
        this.supabase = supabase.createClient(url, key);
        console.log('✅ Supabase client initialized for class:', this.classId);
    }

    async loadGradingData() {
        console.log('📊 Loading grading data...');
        
        try {
        
        // Load data in parallel
        const [itemsResult, submissionsResult, studentsResult, modulesResult, constituentsResult] = await Promise.all([
            // Load active items
            (async () => {
                try {
                    return await this.supabase
                        .from('items')
                        .select('*')
                        .eq('class_id', this.classId)
                        .eq('is_current', true)
                        .order('title');
                } catch (e) {
                    console.warn('⚠️ Failed to load items from database:', e);
                    return { data: [] };
                }
            })(),
            
            // Load all submissions (simplified query to avoid 400 errors)
            (async () => {
                try {
                    return await this.supabase
                        .from('student_submissions')
                        .select('*')
                        .eq('class_id', this.classId)
                        .order('submitted_at', { ascending: false });
                } catch (e) {
                    console.warn('⚠️ Failed to load submissions:', e);
                    return { data: [] };
                }
            })(),
            
            // Load class members (all roles - including professors who might submit)
            (async () => {
                try {
                    return await this.supabase
                        .from('class_members')
                        .select('*')
                        .eq('class_id', this.classId);
                } catch (e) {
                    console.warn('⚠️ Failed to load students:', e);
                    return { data: [] };
                }
            })(),
            
            // Load modules from JSON (build-time data)
            (() => {
                // Use hardcoded path to ensure it works
                const modulesUrl = '/class_template/data/modules.json';
                console.log('🔍 Debug - Loading modules from:', modulesUrl);
                console.log('🔍 Debug - window.authConfig:', window.authConfig);
                return fetch(modulesUrl)
                    .then(r => {
                        console.log('🔍 Debug - Modules response status:', r.status, r.ok);
                        if (r.ok) return r.json();
                        console.warn('⚠️ modules.json not found, using empty array');
                        return { modules: [] };
                    }).catch(e => {
                        console.warn('⚠️ Failed to load modules.json:', e);
                        return { modules: [] };
                    });
            })(),
            
            // Load constituents from JSON (build-time data)  
            (() => {
                // Use hardcoded path to ensure it works
                const constituentsUrl = '/class_template/data/constituents.json';
                console.log('🔍 Debug - Loading constituents from:', constituentsUrl);
                console.log('🔍 Debug - window.authConfig:', window.authConfig);
                return fetch(constituentsUrl)
                    .then(r => {
                        console.log('🔍 Debug - Constituents response status:', r.status, r.ok);
                        if (r.ok) return r.json();
                        console.warn('⚠️ constituents.json not found, using empty array');
                        return { constituents: [] };
                    }).catch(e => {
                        console.warn('⚠️ Failed to load constituents.json:', e);
                        return { constituents: [] };
                    });
            })()
        ]);

        // Process results
        this.items = itemsResult.data || [];
        this.submissions = (submissionsResult.data || []).map(submission => {
            // Parse JSON submission_data if it's a string
            if (submission.submission_data && typeof submission.submission_data === 'string') {
                try {
                    submission.submission_data = JSON.parse(submission.submission_data);
                } catch (e) {
                    console.warn('Failed to parse submission_data for submission', submission.id, ':', e);
                    submission.submission_data = {};
                }
            }
            return submission;
        });
        
        // Apply grade persistence logic in JavaScript
        this.applyGradePersistence();
        
        // Get all unique user IDs from both class members and actual submitters
        const rawStudents = studentsResult.data || [];
        const submitterIds = [...new Set(this.submissions.map(s => s.student_id))];
        const memberIds = rawStudents.map(s => s.user_id);
        const allUserIds = [...new Set([...memberIds, ...submitterIds])];
        
        
        // Add current user as fallback if they're testing (like old code)
        if (window.authState?.user?.id && !allUserIds.includes(window.authState.user.id)) {
            console.log('🔄 Adding current user as fallback for testing:', window.authState.user.id);
            allUserIds.push(window.authState.user.id);
        }
        
        // Load profiles for ALL relevant users efficiently using .in() query (like old code)
        let profiles = [];
        if (allUserIds.length > 0) {
            const profilesResult = await this.supabase
                .from('profiles')
                .select('*')
                .in('user_id', allUserIds);
            profiles = profilesResult.data || [];
        }
        
        // Create unified students list that includes everyone who matters
        this.students = allUserIds.map(userId => {
            const member = rawStudents.find(m => m.user_id === userId);
            const profile = profiles.find(p => p.user_id === userId);
            return {
                user_id: userId,
                role: member?.role || 'submitter', // Could be student, professor, or just submitter
                profile: profile || null,
                ...member // Include any other member data
            };
        });
        
        
        this.modules = modulesResult.modules || [];
        this.constituents = constituentsResult.constituents || [];
        
        console.log(`📈 Loaded: ${this.items.length} items, ${this.submissions.length} submissions, ${this.students.length} students, ${this.modules.length} modules, ${this.constituents.length} constituents`);
        
        // Debug submissions and their student IDs
        if (this.submissions.length > 0) {
            console.log('🔍 Submissions sample:', this.submissions.slice(0, 2));
            const submissionStudentIds = [...new Set(this.submissions.map(s => s.student_id))];
            console.log('🔍 Unique student IDs in submissions:', submissionStudentIds);
            const studentUserIds = this.students.map(s => s.user_id);
            console.log('🔍 User IDs in students array:', studentUserIds);
            console.log('🔍 Missing student IDs:', submissionStudentIds.filter(id => !studentUserIds.includes(id)));
        }
        console.log('🔍 Items sample:', this.items.slice(0, 2));
        console.log('🔍 Modules sample:', this.modules.slice(0, 2));
        console.log('🔍 Constituents sample:', this.constituents.slice(0, 2));
        
        // Debug specific constituent slugs for mapping
        if (this.constituents.length > 0) {
            console.log('🔍 All constituent slugs:', this.constituents.map(c => c.slug));
            console.log('🔍 Constituents details:', this.constituents);
        }
        if (this.items.length > 0) {
            console.log('🔍 All item constituent_slugs:', [...new Set(this.items.map(i => i.constituent_slug))]);
            console.log('🔍 Items details:', this.items.slice(0, 2));
        }
        
        // Check for mismatches
        const itemSlugs = new Set(this.items.map(i => i.constituent_slug));
        const constituentSlugs = new Set(this.constituents.map(c => c.slug));
        const missingConstituents = [...itemSlugs].filter(slug => !constituentSlugs.has(slug));
        if (missingConstituents.length > 0) {
            console.warn('⚠️ Items reference constituents that don\'t exist:', missingConstituents);
        }
        
        } catch (error) {
            console.error('❌ Error loading grading data:', error);
            throw error;
        }
    }

    applyGradePersistence() {
        // Group submissions by student_id and item_id
        const submissionGroups = {};
        
        this.submissions.forEach(submission => {
            const key = `${submission.student_id}-${submission.item_id}`;
            if (!submissionGroups[key]) {
                submissionGroups[key] = [];
            }
            submissionGroups[key].push(submission);
        });
        
        // For each group, apply grade persistence logic
        Object.values(submissionGroups).forEach(group => {
            if (group.length <= 1) return; // Single submission, no inheritance needed
            
            // Sort by attempt_number (descending to get latest first)
            group.sort((a, b) => (b.attempt_number || 1) - (a.attempt_number || 1));
            
            // Find the most recent graded submission
            const gradedSubmission = group.find(s => s.graded_at);
            if (!gradedSubmission) return; // No graded submission found
            
            // Get the latest (highest attempt_number) submission
            const latestSubmission = group[0];
            
            // If latest submission is not the graded one, inherit the grade
            if (latestSubmission.id !== gradedSubmission.id) {
                // Inherit grade data but preserve original submission data
                latestSubmission.raw_score = gradedSubmission.raw_score;
                latestSubmission.adjusted_score = gradedSubmission.adjusted_score;
                latestSubmission.feedback = gradedSubmission.feedback;
                latestSubmission.graded_at = gradedSubmission.graded_at;
                latestSubmission.grader_id = gradedSubmission.grader_id;
                latestSubmission.graded_attempt_number = gradedSubmission.attempt_number;
                latestSubmission.has_newer_version = false; // This IS the newer version
                
                // Mark the graded submission as having a newer version
                gradedSubmission.has_newer_version = true;
                
                console.log(`🔄 Grade inherited: ${latestSubmission.item_id} from attempt ${gradedSubmission.attempt_number} to ${latestSubmission.attempt_number}`);
            }
        });
    }

    setupEventListeners() {
        console.log('🔧 Setting up event listeners...');
        
        // Tab switching with error handling
        try {
            const tabButtons = document.querySelectorAll('.tab-btn');
            console.log(`📝 Found ${tabButtons.length} tab buttons`);
            
            tabButtons.forEach(btn => {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    const tabName = e.target.dataset.tab;
                    console.log(`🔄 Tab clicked: ${tabName}`);
                    this.switchTab(tabName);
                });
            });
        } catch (error) {
            console.error('❌ Error setting up tab listeners:', error);
        }
        
        // Modal close on background click
        try {
            const modal = document.getElementById('gradingModal');
            if (modal) {
                modal.addEventListener('click', (e) => {
                    if (e.target.id === 'gradingModal') {
                        this.closeGradingModal();
                    }
                });
            }
        } catch (error) {
            console.error('❌ Error setting up modal listener:', error);
        }
        
        // Event delegation for dynamically created View Submissions buttons
        try {
            document.addEventListener('click', (e) => {
                // Handle student view submissions buttons
                if (e.target.classList.contains('view-student-btn')) {
                    e.preventDefault();
                    const studentId = e.target.dataset.studentId;
                    console.log('🔍 Student button clicked, studentId:', studentId);
                    this.viewStudentSubmissions(studentId);
                    return;
                }
                
                // Handle item view submissions buttons
                if (e.target.classList.contains('view-item-btn')) {
                    e.preventDefault();
                    const itemId = e.target.dataset.itemId;
                    console.log('🔍 Item button clicked, itemId:', itemId);
                    this.viewItemSubmissions(itemId);
                    return;
                }
            });
            console.log('✅ View Submissions button event delegation set up');
        } catch (error) {
            console.error('❌ Error setting up View Submissions event delegation:', error);
        }
        
        console.log('✅ Event listeners setup complete');
    }

    renderInterface() {
        console.log('🎨 Rendering interface...');
        
        try {
            // Hide loading, show interface
            const loadingEl = document.getElementById('loadingState');
            const interfaceEl = document.getElementById('gradingInterface');
            
            if (loadingEl) loadingEl.style.display = 'none';
            if (interfaceEl) interfaceEl.style.display = 'block';
            
            // Render summary stats
            this.renderStats();
            
            // Render current tab
            this.renderCurrentTab();
            
            console.log('✅ Interface rendered successfully');
        } catch (error) {
            console.error('❌ Error rendering interface:', error);
            this.showError(`Interface rendering failed: ${error.message}`);
        }
    }

    renderStats() {
        const pendingSubmissions = this.submissions.filter(s => !s.graded_at);
        const gradedSubmissions = this.submissions.filter(s => s.graded_at);
        
        document.getElementById('pendingCount').textContent = pendingSubmissions.length;
        document.getElementById('gradedCount').textContent = gradedSubmissions.length;
        document.getElementById('studentsCount').textContent = this.students.length;
        document.getElementById('itemsCount').textContent = this.items.length;
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.tab === tabName) {
                btn.classList.add('active');
            }
        });
        
        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
        });
        document.getElementById(`${tabName}-tab`).classList.add('active');
        
        this.currentTab = tabName;
        this.renderCurrentTab();
    }

    renderCurrentTab() {
        switch (this.currentTab) {
            case 'pending':
                this.renderPendingSubmissions();
                break;
            case 'graded':
                this.renderGradedSubmissions();
                break;
            case 'students':
                this.renderStudentView();
                break;
            case 'items':
                this.renderItemsView();
                break;
        }
    }

    renderPendingSubmissions() {
        const container = document.getElementById('pendingSubmissions');
        let pending = this.submissions.filter(s => !s.graded_at);
        
        console.log('🔍 renderPendingSubmissions - total ungraded:', pending.length);
        console.log('🔍 Filter mode:', this.filterMode, 'value:', this.filterValue);
        
        // Apply filter if active
        if (this.filterMode === 'student' && this.filterValue) {
            const beforeFilter = pending.length;
            pending = pending.filter(s => s.student_id === this.filterValue);
            console.log('🔍 Student filter applied - before:', beforeFilter, 'after:', pending.length);
        } else if (this.filterMode === 'item' && this.filterValue) {
            const beforeFilter = pending.length;
            pending = pending.filter(s => s.item_id === this.filterValue);
            console.log('🔍 Item filter applied - before:', beforeFilter, 'after:', pending.length);
        } else {
            console.log('🔍 No filter applied');
        }
        
        if (pending.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">🎉</div>
                    <h4>All caught up!</h4>
                    <p>No pending submissions to grade</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="submissions-grid">';
        pending.forEach(submission => {
            html += this.renderSubmissionCard(submission);
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderGradedSubmissions() {
        const container = document.getElementById('gradedSubmissions');
        const graded = this.submissions.filter(s => s.graded_at).slice(0, 20); // Show recent 20
        
        if (graded.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <h4>No graded submissions yet</h4>
                    <p>Graded items will appear here</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="submissions-grid">';
        graded.forEach(submission => {
            html += this.renderSubmissionCard(submission, true);
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderStudentView() {
        const container = document.getElementById('studentView');
        
        if (this.students.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">👥</div>
                    <h4>No students enrolled</h4>
                    <p>Students will appear here after enrollment</p>
                </div>
            `;
            return;
        }
        
        let html = '<div class="students-grid">';
        this.students.forEach(student => {
            const studentSubmissions = this.submissions.filter(s => s.student_id === student.user_id);
            const pending = studentSubmissions.filter(s => !s.graded_at).length;
            const graded = studentSubmissions.filter(s => s.graded_at).length;
            
            html += `
                <div class="student-card">
                    <div class="student-header">
                        <img src="${student.profile?.avatar_url || '/default-avatar.png'}" 
                             class="student-avatar" alt="Avatar">
                        <div class="student-info">
                            <h5>${student.profile?.full_name || 'Unknown Student'}</h5>
                            <p>@${student.profile?.github_username || 'unknown'}</p>
                        </div>
                    </div>
                    <div class="student-stats">
                        <span class="stat pending">${pending} pending</span>
                        <span class="stat graded">${graded} graded</span>
                    </div>
                    <button class="view-student-btn" 
                            data-student-id="${student.user_id}">
                        View Submissions
                    </button>
                </div>
            `;
        });
        html += '</div>';
        
        container.innerHTML = html;
    }

    renderItemsView() {
        const container = document.getElementById('itemsView');
        
        if (this.items.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📝</div>
                    <h4>No active items</h4>
                    <p>Items need to be synced from markdown files</p>
                </div>
            `;
            return;
        }
        
        // Switch between list view and detail view
        if (this.itemViewMode === 'detail' && this.selectedItemId) {
            this.renderItemDetailView(this.selectedItemId);
        } else {
            this.renderItemListView();
        }
    }
    
    renderItemListView() {
        const container = document.getElementById('itemsView');
        
        // Group by module → constituent
        const grouped = this.groupItemsByHierarchy(this.items);
        
        let html = '';
        for (const [moduleId, moduleData] of Object.entries(grouped)) {
            const module = this.modules.find(m => m.id === moduleId) || { name: 'Unknown Module', icon: '📚' };
            
            html += `
                <div class="module-group">
                    <div class="module-header">
                        <h3>${module.icon} ${module.name}</h3>
                    </div>
            `;
            
            for (const [constituentSlug, items] of Object.entries(moduleData)) {
                const constituent = this.constituents.find(c => c.slug === constituentSlug) || { name: 'Unknown Constituent' };
                
                html += `
                    <div class="constituent-group">
                        <h4>${constituent.name}</h4>
                        <div class="items-grid">
                `;
                
                items.forEach(item => {
                    const itemSubmissions = this.submissions.filter(s => s.item_id === item.id);
                    const pending = itemSubmissions.filter(s => !s.graded_at).length;
                    const graded = itemSubmissions.filter(s => s.graded_at).length;
                    
                    html += `
                        <div class="item-card">
                            <div class="item-header">
                                <h5>${item.title}</h5>
                                <span class="item-points">${item.points} pts</span>
                            </div>
                            <div class="item-stats">
                                <span class="stat pending">${pending} pending</span>
                                <span class="stat graded">${graded} graded</span>
                            </div>
                            <button class="view-item-btn" 
                                    data-item-id="${item.id}">
                                View Submissions
                            </button>
                        </div>
                    `;
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            html += `</div>`;
        }
        
        container.innerHTML = html;
    }
    
    renderItemDetailView(itemId) {
        const container = document.getElementById('itemsView');
        const item = this.items.find(i => i.id === itemId);
        
        if (!item) {
            container.innerHTML = `
                <div class="error-state">
                    <h4>❌ Item not found</h4>
                    <button class="back-btn" onclick="window.professorGrading.backToItemsList()">← Back to All Assignments</button>
                </div>
            `;
            return;
        }
        
        // Get all submissions for this item, then filter to latest version per student
        const allSubmissions = this.submissions.filter(s => s.item_id === itemId);
        
        // Group by student_id and get only the latest attempt
        const latestSubmissions = {};
        allSubmissions.forEach(submission => {
            const studentId = submission.student_id;
            if (!latestSubmissions[studentId] || 
                (submission.attempt_number || 1) > (latestSubmissions[studentId].attempt_number || 1)) {
                latestSubmissions[studentId] = submission;
            }
        });
        
        // Convert back to array
        const itemSubmissions = Object.values(latestSubmissions);
        
        console.log('🔍 Debug - All submissions for item:', allSubmissions.length);
        console.log('🔍 Debug - Latest submissions only:', itemSubmissions.length);
        const constituent = this.constituents.find(c => c.slug === item.constituent_slug);
        const module = this.modules.find(m => m.id === constituent?.module_id);
        
        let html = `
            <div class="item-detail-view">
                <div class="item-detail-header">
                    <div class="breadcrumb">
                        <button class="back-btn" onclick="window.professorGrading.backToItemsList()">
                            ← Back to All Assignments
                        </button>
                        <span class="breadcrumb-path">
                            ${module?.name || 'Unknown Module'} > ${constituent?.name || 'Unknown Constituent'} > ${item.title}
                        </span>
                    </div>
                    <div class="item-detail-info">
                        <h2>${item.title}</h2>
                        <div class="item-meta">
                            <span class="item-points">📊 ${item.points} points</span>
                            <span class="item-due">📅 Due: ${item.due_date ? new Date(item.due_date).toLocaleDateString() : 'No due date'}</span>
                            <span class="item-type">🔖 ${item.delivery_type || 'Unknown'}</span>
                        </div>
                    </div>
                </div>
                
                <div class="submissions-table-container">
                    <h3>📋 Submissions (${itemSubmissions.length})</h3>
        `;
        
        if (itemSubmissions.length === 0) {
            html += `
                    <div class="empty-state">
                        <div class="empty-icon">📝</div>
                        <h4>No submissions yet</h4>
                        <p>Students haven't submitted work for this assignment</p>
                    </div>
            `;
        } else {
            html += `
                    <table class="submissions-table">
                        <thead>
                            <tr>
                                <th>GitHub</th>
                                <th>Submitted</th>
                                <th>Status</th>
                                <th>Grade</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            
            // Sort submissions: pending first, then by submission date
            const sortedSubmissions = itemSubmissions.sort((a, b) => {
                if (!a.graded_at && b.graded_at) return -1;
                if (a.graded_at && !b.graded_at) return 1;
                return new Date(b.submitted_at || 0) - new Date(a.submitted_at || 0);
            });
            
            sortedSubmissions.forEach(submission => {
                let student = this.students.find(s => s.user_id === submission.student_id);
                
                // Fallback: if student not found, create placeholder
                if (!student) {
                    console.log('⚠️ Student not found for submission, creating fallback:', submission.student_id);
                    student = {
                        user_id: submission.student_id,
                        role: 'unknown',
                        profile: {
                            full_name: `User ${submission.student_id.substring(0, 8)}...`,
                            github_username: `user_${submission.student_id.substring(0, 8)}`,
                            avatar_url: '/default-avatar.png'
                        }
                    };
                }
                
                const submittedDate = submission.submitted_at ? 
                    new Date(submission.submitted_at).toLocaleDateString() : 'Not submitted';
                const isGraded = !!submission.graded_at;
                const grade = submission.adjusted_score || submission.raw_score || '--';
                const hasNewerVersion = submission.has_newer_version || false;
                const versionIndicator = hasNewerVersion ? ' 🔄' : '';
                
                
                const githubUsername = student?.profile?.github_username || 'unknown';
                
                html += `
                            <tr class="${isGraded ? 'graded' : 'pending'}">
                                <td class="github-cell">@${githubUsername}</td>
                                <td class="date-cell">${submittedDate}</td>
                                <td class="status-cell">
                                    <span class="status ${isGraded ? 'graded' : 'pending'}">
                                        ${isGraded ? `✅ Graded${versionIndicator}` : '⏳ Pending'}
                                    </span>
                                </td>
                                <td class="grade-cell">
                                    ${isGraded ? `<span class="grade">${grade}/${item.points}${versionIndicator}</span>` : '--'}
                                </td>
                                <td class="actions-cell">
                                    <button class="grade-btn ${isGraded ? 'regrade' : 'grade'}" 
                                            onclick="window.professorGrading.openGradingModal('${submission.id}')">
                                        ${isGraded ? '🔄 Regrade' : '📝 Grade'}
                                    </button>
                                </td>
                            </tr>
                `;
            });
            
            html += `
                        </tbody>
                    </table>
            `;
        }
        
        html += `
                </div>
            </div>
        `;
        
        container.innerHTML = html;
    }

    renderSubmissionCard(submission, isGraded = false) {
        const item = this.items.find(i => i.id === submission.item_id);
        const submissionData = submission.submission_data || {};
        const studentName = submission.profiles?.full_name || 'Unknown Student';
        const githubUsername = submission.profiles?.github_username || 'unknown';
        const submittedDate = new Date(submission.submitted_at).toLocaleDateString();
        
        const hasNewerVersion = submission.has_newer_version || false;
        const versionIndicator = hasNewerVersion ? ' 🔄 New version submitted' : '';
        
        const gradeDisplay = isGraded ? `
            <div class="submission-grade">
                <span class="grade-score">${submission.adjusted_score || submission.raw_score}/${item?.points || '?'}</span>
                <small>Graded ${new Date(submission.graded_at).toLocaleDateString()}${versionIndicator}</small>
            </div>
        ` : `
            <button class="grade-btn" 
                    onclick="window.professorGrading.openGradingModal('${submission.id}')">
                📝 Grade Submission
            </button>
        `;
        
        return `
            <div class="submission-card ${isGraded ? 'graded' : 'pending'}">
                <div class="submission-header">
                    <div class="student-info">
                        <img src="${submission.profiles?.avatar_url || '/default-avatar.png'}" 
                             class="student-avatar-sm" alt="Avatar">
                        <div>
                            <strong>${studentName}</strong>
                            <small>@${githubUsername}</small>
                        </div>
                    </div>
                    <span class="submission-date">${submittedDate}</span>
                </div>
                <div class="submission-details">
                    <h5>${item?.title || 'Unknown Item'}</h5>
                    <div class="submission-content">
                        ${this.renderSubmissionPreview(submissionData)}
                    </div>
                </div>
                <div class="submission-actions">
                    ${gradeDisplay}
                </div>
            </div>
        `;
    }

    renderSubmissionContent(submissionData) {
        const type = submissionData.type || 'text';
        
        switch (type) {
            case 'url':
                const url = submissionData.url || 'No URL provided';
                const urlDescription = submissionData.description || '';
                return `
                    <div class="submission-url">
                        <p><strong>URL:</strong> <a href="${url}" target="_blank" class="submission-link">🔗 ${url}</a></p>
                        ${urlDescription ? `<p><strong>Description:</strong> ${urlDescription}</p>` : ''}
                    </div>
                `;
                
            case 'text':
                const content = submissionData.content || submissionData.text || 'No content provided';
                return `
                    <div class="submission-text">
                        <pre class="text-content">${content}</pre>
                    </div>
                `;
                
            case 'file':
            case 'upload':
                const fileName = submissionData.file_name || submissionData.filename || 'Uploaded file';
                const fileDescription = submissionData.description || '';
                const fileData = submissionData.file_data;
                const fileSize = submissionData.file_size || 0;
                const fileType = submissionData.file_type || 'application/octet-stream';
                
                // Format file size
                const formatFileSize = (bytes) => {
                    if (bytes === 0) return '0 Bytes';
                    const k = 1024;
                    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
                };
                
                return `
                    <div class="submission-file">
                        <p><strong>File:</strong> 📎 ${fileName}</p>
                        ${fileType ? `<p><strong>Type:</strong> ${fileType}</p>` : ''}
                        ${fileSize > 0 ? `<p><strong>Size:</strong> ${formatFileSize(fileSize)}</p>` : ''}
                        ${fileDescription ? `<p><strong>Description:</strong> ${fileDescription}</p>` : ''}
                        ${fileData ? 
                            `<a href="${fileData}" download="${fileName}" class="btn-download" style="margin-top: 8px; padding: 8px 16px; background: var(--eva-green-primary); color: white; text-decoration: none; border-radius: 4px; display: inline-block; cursor: pointer;">
                                ⬇️ Download File
                            </a>` : 
                            `<button class="btn-download" disabled style="margin-top: 8px; padding: 6px 12px; background: #ccc; border: none; border-radius: 4px; cursor: not-allowed;">
                                ⬇️ No file data available
                            </button>`
                        }
                    </div>
                `;
                
            case 'code':
                const code = submissionData.code || 'No code provided';
                const language = submissionData.language || 'text';
                const explanation = submissionData.explanation || '';
                return `
                    <div class="submission-code">
                        <p><strong>Language:</strong> ${language}</p>
                        <pre><code class="language-${language}">${code}</code></pre>
                        ${explanation ? `<p><strong>Explanation:</strong> ${explanation}</p>` : ''}
                    </div>
                `;
                
            default:
                return `
                    <div class="submission-generic">
                        <p><strong>Raw submission data:</strong></p>
                        <pre>${JSON.stringify(submissionData, null, 2)}</pre>
                    </div>
                `;
        }
    }

    renderSubmissionPreview(submissionData) {
        const type = submissionData.type || 'text';
        
        switch (type) {
            case 'url':
                const url = submissionData.url || 'No URL provided';
                const urlDescription = submissionData.description || '';
                const shortUrl = url.length > 50 ? url.substring(0, 50) + '...' : url;
                return `
                    <div class="submission-preview url-preview">
                        <p><strong>🔗 URL:</strong> <a href="${url}" target="_blank">${shortUrl}</a></p>
                        ${urlDescription ? `<p class="preview-description">${urlDescription.length > 100 ? urlDescription.substring(0, 100) + '...' : urlDescription}</p>` : ''}
                    </div>
                `;
                
            case 'text':
                const content = submissionData.content || submissionData.text || 'No content provided';
                const shortContent = content.length > 150 ? content.substring(0, 150) + '...' : content;
                return `
                    <div class="submission-preview text-preview">
                        <p><strong>📝 Text:</strong></p>
                        <p class="preview-text">${shortContent}</p>
                    </div>
                `;
                
            case 'file':
            case 'upload':
                const fileName = submissionData.file_name || submissionData.filename || 'Uploaded file';
                const fileDescription = submissionData.description || '';
                const fileSize = submissionData.file_size || 0;
                const fileType = submissionData.file_type || '';
                const hasFileData = !!submissionData.file_data;
                
                // Format file size for preview
                const formatBytes = (bytes) => {
                    if (bytes === 0) return '0 B';
                    const k = 1024;
                    const sizes = ['B', 'KB', 'MB'];
                    const i = Math.floor(Math.log(bytes) / Math.log(k));
                    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
                };
                
                return `
                    <div class="submission-preview file-preview">
                        <p><strong>📎 File:</strong> ${fileName} ${hasFileData ? '✅' : '❌'}</p>
                        ${fileSize > 0 ? `<small>${formatBytes(fileSize)} ${fileType ? `• ${fileType}` : ''}</small>` : ''}
                        ${fileDescription ? `<p class="preview-description">${fileDescription.length > 80 ? fileDescription.substring(0, 80) + '...' : fileDescription}</p>` : ''}
                    </div>
                `;
                
            case 'code':
                const language = submissionData.language || 'text';
                const code = submissionData.code || 'No code provided';
                const explanation = submissionData.explanation || '';
                const shortCode = code.length > 100 ? code.substring(0, 100) + '...' : code;
                return `
                    <div class="submission-preview code-preview">
                        <p><strong>💻 Code (${language}):</strong></p>
                        <pre class="preview-code">${shortCode}</pre>
                        ${explanation ? `<p class="preview-description">${explanation.length > 100 ? explanation.substring(0, 100) + '...' : explanation}</p>` : ''}
                    </div>
                `;
                
            default:
                return `
                    <div class="submission-preview generic-preview">
                        <p><strong>📋 Submission data:</strong></p>
                        <small>Click to grade for full details</small>
                    </div>
                `;
        }
    }

    groupItemsByHierarchy(items) {
        console.log('🔍 Debug groupItemsByHierarchy:');
        console.log('  - items:', items.length);
        console.log('  - constituents:', this.constituents.length);
        console.log('  - modules:', this.modules.length);
        
        const grouped = {};
        
        items.forEach(item => {
            const constituent = this.constituents.find(c => c.slug === item.constituent_slug);
            const moduleId = constituent?.module_id || 'unknown';
            
            console.log(`  - Item ${item.item_id}: constituent_slug=${item.constituent_slug} → constituent=${constituent?.name} → moduleId=${moduleId}`);
            
            if (!grouped[moduleId]) {
                grouped[moduleId] = {};
            }
            
            if (!grouped[moduleId][item.constituent_slug]) {
                grouped[moduleId][item.constituent_slug] = [];
            }
            
            grouped[moduleId][item.constituent_slug].push(item);
        });
        
        console.log('🔍 Debug grouped result:', grouped);
        return grouped;
    }

    async openGradingModal(submissionId) {
        const submission = this.submissions.find(s => s.id === submissionId);
        if (!submission) {
            console.error('Submission not found:', submissionId);
            return;
        }
        
        this.currentSubmission = submission;
        const item = this.items.find(i => i.id === submission.item_id);
        const studentName = submission.profiles?.full_name || 'Unknown Student';
        
        document.getElementById('modalTitle').textContent = `Grade: ${item?.title || 'Unknown Item'}`;
        
        const modalBody = document.getElementById('gradingModalBody');
        modalBody.innerHTML = `
            <div class="grading-form">
                <div class="submission-context">
                    <h4>Student: ${studentName} (@${submission.profiles?.github_username || 'unknown'})</h4>
                    <p><strong>Submitted:</strong> ${new Date(submission.submitted_at).toLocaleDateString()}</p>
                    <p><strong>Assignment:</strong> ${item?.title || 'Unknown'} (${item?.points || '?'} points)</p>
                </div>
                
                <div class="submission-content-display">
                    <h5>Submitted Work:</h5>
                    <div class="content-box">
                        ${this.renderSubmissionContent(submission.submission_data || {})}
                    </div>
                </div>
                
                <div class="grading-inputs">
                    <div class="input-group">
                        <label for="gradeScore">Score (out of ${item?.points || '?'} points):</label>
                        <input type="number" 
                               id="gradeScore" 
                               min="0" 
                               max="${item?.points || 100}" 
                               step="0.5" 
                               value="${submission.raw_score || ''}"
                               required>
                    </div>
                    
                    <div class="input-group">
                        <label for="gradeFeedback">Feedback (optional):</label>
                        <textarea id="gradeFeedback" 
                                  rows="4" 
                                  placeholder="Provide feedback to the student...">${submission.feedback || ''}</textarea>
                    </div>
                    
                    <div class="grading-actions">
                        <button class="btn-secondary" onclick="window.professorGrading.closeGradingModal()">
                            Cancel
                        </button>
                        <button class="btn-primary" onclick="window.professorGrading.submitGrade()">
                            📝 Submit Grade
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.getElementById('gradingModal').style.display = 'block';
    }

    async submitGrade() {
        console.log('🎯 Starting grade submission process...');
        console.log('🔍 Auth State:', {
            has_authState: !!window.authState,
            has_session: !!window.authState?.session,
            has_user: !!window.authState?.user,
            has_userContext: !!window.authState?.userContext,
            userContext: window.authState?.userContext
        });
        
        const score = parseFloat(document.getElementById('gradeScore').value);
        const feedback = document.getElementById('gradeFeedback').value.trim();
        
        if (isNaN(score) || score < 0) {
            alert('Please enter a valid score');
            return;
        }
        
        const item = this.items.find(i => i.id === this.currentSubmission.item_id);
        if (score > (item?.points || 100)) {
            alert(`Score cannot exceed ${item?.points || 100} points`);
            return;
        }
        
        try {
            // Use direct Supabase update with RLS security
            const { data: updatedSubmission, error } = await this.supabase
                .from('student_submissions')
                .update({
                    raw_score: score,
                    adjusted_score: score,
                    feedback: feedback || null,
                    graded_at: new Date().toISOString(),
                    grader_id: window.authState.user.id,
                    graded_attempt_number: this.currentSubmission.attempt_number,
                    has_newer_version: false  // Reset since we're grading this version
                })
                .eq('id', this.currentSubmission.id)
                .eq('class_id', this.classId)
                .select()
                .single();

            if (error) {
                console.error('❌ Grading failed:', error);
                throw new Error(`Grading failed: ${error.message}`);
            }
            
            console.log('✅ Grade submitted successfully');
            
            // Update local data with the returned data
            const submissionIndex = this.submissions.findIndex(s => s.id === this.currentSubmission.id);
            if (submissionIndex >= 0) {
                this.submissions[submissionIndex] = {
                    ...this.submissions[submissionIndex],
                    ...updatedSubmission
                };
            }
            
            // Close modal and refresh UI
            this.closeGradingModal();
            this.renderStats();
            this.renderCurrentTab();
            
        } catch (error) {
            console.error('❌ Failed to submit grade:', error);
            alert(`Failed to submit grade: ${error.message}`);
        }
    }

    closeGradingModal() {
        document.getElementById('gradingModal').style.display = 'none';
        this.currentSubmission = null;
    }

    viewStudentSubmissions(studentId) {
        console.log('🔍 Viewing submissions for student:', studentId);
        console.log('🔍 Total submissions before filter:', this.submissions.length);
        
        this.filterMode = 'student';
        this.filterValue = studentId;
        
        console.log('🔍 Filter set - mode:', this.filterMode, 'value:', this.filterValue);
        
        this.switchTab('pending');
        this.renderCurrentTab();
        this.addFilterIndicator(`Student: ${this.getStudentName(studentId)}`);
        
        console.log('🔍 viewStudentSubmissions complete');
    }

    viewItemSubmissions(itemId) {
        console.log('🔍 Viewing submissions for item:', itemId);
        console.log('🔍 Total submissions for item:', this.submissions.filter(s => s.item_id === itemId).length);
        
        // Switch to detail view mode instead of filtering pending tab
        this.selectedItemId = itemId;
        this.itemViewMode = 'detail';
        
        console.log('🔍 Item detail mode set - itemId:', this.selectedItemId, 'mode:', this.itemViewMode);
        
        // Stay in items tab but re-render to show detail view
        if (this.currentTab !== 'items') {
            this.switchTab('items');
        } else {
            this.renderCurrentTab();
        }
        
        console.log('🔍 viewItemSubmissions complete - staying in items tab');
    }
    
    getStudentName(studentId) {
        const student = this.students.find(s => s.user_id === studentId);
        return student?.profiles?.full_name || 'Unknown Student';
    }
    
    getItemName(itemId) {
        const item = this.items.find(i => i.id === itemId);
        return item?.title || 'Unknown Item';
    }
    
    clearFilter() {
        this.filterMode = null;
        this.filterValue = null;
        this.removeFilterIndicator();
        this.renderCurrentTab();
    }
    
    backToItemsList() {
        console.log('🔍 Returning to items list view');
        this.selectedItemId = null;
        this.itemViewMode = 'list';
        this.renderCurrentTab();
    }
    
    addFilterIndicator(filterText) {
        const container = document.querySelector('.grading-header');
        let indicator = document.getElementById('filterIndicator');
        
        if (!indicator) {
            indicator = document.createElement('div');
            indicator.id = 'filterIndicator';
            indicator.className = 'filter-indicator';
            container.appendChild(indicator);
        }
        
        indicator.innerHTML = `
            <span class="filter-text">📋 Filtered by: ${filterText}</span>
            <button class="clear-filter-btn" onclick="window.professorGrading.clearFilter()">
                ✕ Clear Filter
            </button>
        `;
    }
    
    removeFilterIndicator() {
        const indicator = document.getElementById('filterIndicator');
        if (indicator) {
            indicator.remove();
        }
    }

    showAuthRequired() {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('authCheck').style.display = 'block';
    }

    showError(message) {
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('errorState').style.display = 'block';
        document.getElementById('errorMessage').textContent = message;
    }
}

// ProfessorGradingManager class - initialized by page-level script