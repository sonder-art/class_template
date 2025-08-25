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
            
            // Load class members (simplified query to avoid 400 errors)
            (async () => {
                try {
                    return await this.supabase
                        .from('class_members')
                        .select('*')
                        .eq('class_id', this.classId)
                        .eq('role', 'student');
                } catch (e) {
                    console.warn('⚠️ Failed to load students:', e);
                    return { data: [] };
                }
            })(),
            
            // Load modules from JSON (build-time data)
            (() => {
                const modulesUrl = `${window.location.origin}${window.authConfig?.base_url || ''}/data/modules.json`;
                console.log('🔍 Debug - Loading modules from:', modulesUrl);
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
                const constituentsUrl = `${window.location.origin}${window.authConfig?.base_url || ''}/data/constituents.json`;
                console.log('🔍 Debug - Loading constituents from:', constituentsUrl);
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
        this.submissions = submissionsResult.data || [];
        this.students = studentsResult.data || [];
        
        console.log('🔍 Debug - Raw modulesResult:', modulesResult);
        console.log('🔍 Debug - Raw constituentsResult:', constituentsResult);
        
        this.modules = modulesResult.modules || [];
        this.constituents = constituentsResult.constituents || [];
        
        console.log(`📈 Loaded: ${this.items.length} items, ${this.submissions.length} submissions, ${this.students.length} students, ${this.modules.length} modules, ${this.constituents.length} constituents`);
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
        
        // Apply filter if active
        if (this.filterMode === 'student' && this.filterValue) {
            pending = pending.filter(s => s.student_id === this.filterValue);
        } else if (this.filterMode === 'item' && this.filterValue) {
            pending = pending.filter(s => s.item_id === this.filterValue);
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
                        <img src="${student.profiles?.avatar_url || '/default-avatar.png'}" 
                             class="student-avatar" alt="Avatar">
                        <div class="student-info">
                            <h5>${student.profiles?.full_name || 'Unknown Student'}</h5>
                            <p>@${student.profiles?.github_username || 'unknown'}</p>
                        </div>
                    </div>
                    <div class="student-stats">
                        <span class="stat pending">${pending} pending</span>
                        <span class="stat graded">${graded} graded</span>
                    </div>
                    <button class="view-student-btn" 
                            onclick="window.professorGrading.viewStudentSubmissions('${student.user_id}')">
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
                                    onclick="window.professorGrading.viewItemSubmissions('${item.id}')">
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

    renderSubmissionCard(submission, isGraded = false) {
        const item = this.items.find(i => i.id === submission.item_id);
        const submissionData = submission.submission_data || {};
        const studentName = submission.profiles?.full_name || 'Unknown Student';
        const githubUsername = submission.profiles?.github_username || 'unknown';
        const submittedDate = new Date(submission.submitted_at).toLocaleDateString();
        
        const gradeDisplay = isGraded ? `
            <div class="submission-grade">
                <span class="grade-score">${submission.adjusted_score || submission.raw_score}/${item?.points || '?'}</span>
                <small>Graded ${new Date(submission.graded_at).toLocaleDateString()}</small>
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
                        ${this.renderSubmissionContent(submissionData)}
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
                return `<a href="${submissionData.url}" target="_blank" class="submission-link">🔗 ${submissionData.url}</a>`;
            case 'text':
                return `<p class="submission-text">${submissionData.content || submissionData.text || 'No content'}</p>`;
            case 'file':
            case 'upload':
                return `<span class="submission-file">📎 ${submissionData.filename || 'Uploaded file'}</span>`;
            case 'code':
                return `<code class="submission-code">${submissionData.code || 'No code provided'}</code>`;
            default:
                return `<span class="submission-generic">${JSON.stringify(submissionData)}</span>`;
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
            // Call the professor-grade-item Edge Function
            const response = await fetch('https://levybxqsltedfjtnkntm.supabase.co/functions/v1/professor-grade-item', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${window.authState.session.access_token}`,
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    class_id: this.classId,
                    repo_name: window.authState.userContext?.repo_name || 'class_template',
                    submission_id: this.currentSubmission.id,
                    grading_data: {
                        raw_score: score,
                        feedback: feedback || null
                    }
                })
            });
            
            if (!response.ok) {
                const error = await response.text();
                throw new Error(`Grading failed: ${error}`);
            }
            
            console.log('✅ Grade submitted successfully');
            
            // Update local data
            const submissionIndex = this.submissions.findIndex(s => s.id === this.currentSubmission.id);
            if (submissionIndex >= 0) {
                this.submissions[submissionIndex] = {
                    ...this.submissions[submissionIndex],
                    raw_score: score,
                    adjusted_score: score,
                    feedback: feedback || null,
                    graded_at: new Date().toISOString(),
                    grader_id: window.authState.user.id
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
        this.filterMode = 'student';
        this.filterValue = studentId;
        this.switchTab('pending');
        this.renderCurrentTab();
        this.addFilterIndicator(`Student: ${this.getStudentName(studentId)}`);
    }

    viewItemSubmissions(itemId) {
        console.log('🔍 Viewing submissions for item:', itemId);
        this.filterMode = 'item';
        this.filterValue = itemId;
        this.switchTab('pending');
        this.renderCurrentTab();
        this.addFilterIndicator(`Item: ${this.getItemName(itemId)}`);
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