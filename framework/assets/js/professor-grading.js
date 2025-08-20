/**
 * Professor Grading Interface
 * Handles professor grading of student item submissions and manual grade entry
 * Includes proper security verification and class context
 */

class ProfessorGradingInterface {
    constructor() {
        this.classContext = null;
        this.supabaseClient = null;
        this.currentUser = null;
        this.submissions = [];
        this.students = [];
        
        this.init();
    }

    async init() {
        // Get class context
        this.classContext = this.getClassContext();
        
        if (!this.classContext) {
            console.error('Missing class context - grading interface disabled');
            this.showError('Class context not found. Please refresh the page.');
            return;
        }

        // Initialize Supabase
        this.initializeSupabase();

        // Check authentication and professor status
        const isProfessor = await this.verifyProfessorAccess();
        if (!isProfessor) {
            this.showAccessDenied();
            return;
        }

        // Load initial data
        await this.loadInitialData();

        // Set up UI event handlers
        this.setupEventHandlers();

        console.log('Professor grading interface initialized for class:', this.classContext.repo_name);
    }

    getClassContext() {
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
        const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
        const supabaseAnonKey = document.querySelector('meta[name="supabase-anon-key"]')?.content;

        if (!supabaseUrl || !supabaseAnonKey || typeof window.supabase === 'undefined') {
            console.error('Missing Supabase configuration or library');
            this.showError('Configuration error. Please contact system administrator.');
            return;
        }

        this.supabaseClient = window.supabase.createClient(supabaseUrl, supabaseAnonKey);
    }

    async verifyProfessorAccess() {
        if (!this.supabaseClient) return false;

        try {
            const { data: { user }, error } = await this.supabaseClient.auth.getUser();
            
            if (error || !user) {
                this.showAuthenticationRequired();
                return false;
            }

            this.currentUser = user;

            // Check if user is professor of this class
            const { data: membership, error: membershipError } = await this.supabaseClient
                .from('class_members')
                .select(`
                    role,
                    enrollment_status,
                    classes!inner (
                        professor_github_username
                    )
                `)
                .eq('user_id', user.id)
                .eq('class_id', this.classContext.class_id)
                .eq('role', 'professor')
                .eq('enrollment_status', 'active')
                .single();

            if (membershipError || !membership) {
                console.error('Professor verification failed:', membershipError);
                return false;
            }

            // Verify GitHub username matches
            const userGithub = user.user_metadata?.user_name;
            const expectedGithub = membership.classes.professor_github_username;

            if (userGithub !== expectedGithub) {
                console.error('GitHub username mismatch:', userGithub, 'vs', expectedGithub);
                return false;
            }

            return true;

        } catch (error) {
            console.error('Professor access verification failed:', error);
            return false;
        }
    }

    async loadInitialData() {
        await Promise.all([
            this.loadSubmissions(),
            this.loadStudents(),
            this.loadItems()
        ]);

        this.renderGradingInterface();
    }

    async loadSubmissions() {
        try {
            const { data: submissions, error } = await this.supabaseClient
                .from('student_submissions')
                .select(`
                    id,
                    student_id,
                    item_id,
                    attempt_number,
                    submission_data,
                    submitted_at,
                    raw_score,
                    adjusted_score,
                    feedback,
                    graded_at,
                    grader_id,
                    profiles!student_submissions_student_id_fkey (
                        full_name,
                        raw_user_meta_data
                    ),
                    homework_items!student_submissions_item_id_fkey (
                        title,
                        points,
                        constituent_slug,
                        submission_type
                    )
                `)
                .eq('class_id', this.classContext.class_id)
                .order('submitted_at', { ascending: false });

            if (error) {
                console.error('Error loading submissions:', error);
                this.showError('Failed to load submissions');
                return;
            }

            this.submissions = submissions || [];
            console.log(`Loaded ${this.submissions.length} submissions`);

        } catch (error) {
            console.error('Failed to load submissions:', error);
        }
    }

    async loadStudents() {
        try {
            const { data: students, error } = await this.supabaseClient
                .from('class_members')
                .select(`
                    user_id,
                    enrollment_status,
                    profiles!class_members_user_id_fkey (
                        full_name,
                        raw_user_meta_data
                    )
                `)
                .eq('class_id', this.classContext.class_id)
                .eq('role', 'student')
                .eq('enrollment_status', 'active');

            if (error) {
                console.error('Error loading students:', error);
                return;
            }

            this.students = students || [];
            console.log(`Loaded ${this.students.length} students`);

        } catch (error) {
            console.error('Failed to load students:', error);
        }
    }

    async loadItems() {
        try {
            const { data: items, error } = await this.supabaseClient
                .from('homework_items')
                .select(`
                    id,
                    item_id,
                    title,
                    points,
                    constituent_slug,
                    submission_type,
                    due_date,
                    item_type
                `)
                .eq('class_id', this.classContext.class_id)
                .eq('is_archived', false)
                .order('created_at', { ascending: false });

            if (error) {
                console.error('Error loading items:', error);
                return;
            }

            this.items = items || [];
            console.log(`Loaded ${this.items.length} items`);

        } catch (error) {
            console.error('Failed to load items:', error);
        }
    }

    renderGradingInterface() {
        const container = document.getElementById('grading-interface');
        if (!container) {
            console.error('Grading interface container not found');
            return;
        }

        container.innerHTML = `
            <div class="grading-header">
                <h2>🎓 Professor Grading Dashboard</h2>
                <div class="class-info">
                    <span class="class-name">${this.classContext.repo_name}</span>
                    <span class="student-count">${this.students.length} students</span>
                    <span class="submission-count">${this.submissions.length} submissions</span>
                </div>
            </div>

            <div class="grading-tabs">
                <button class="tab-btn active" data-tab="submissions">📝 Grade Submissions</button>
                <button class="tab-btn" data-tab="manual">➕ Add Manual Grades</button>
                <button class="tab-btn" data-tab="overview">📊 Class Overview</button>
            </div>

            <div class="tab-content active" id="submissions-tab">
                ${this.renderSubmissionsTab()}
            </div>

            <div class="tab-content" id="manual-tab">
                ${this.renderManualGradesTab()}
            </div>

            <div class="tab-content" id="overview-tab">
                ${this.renderOverviewTab()}
            </div>
        `;
    }

    renderSubmissionsTab() {
        const ungradedSubmissions = this.submissions.filter(s => s.raw_score === null);
        const gradedSubmissions = this.submissions.filter(s => s.raw_score !== null);

        return `
            <div class="submissions-section">
                <div class="section-header">
                    <h3>⏳ Ungraded Submissions (${ungradedSubmissions.length})</h3>
                    <div class="filter-controls">
                        <select id="item-filter">
                            <option value="">All Items</option>
                            ${this.items.map(item => 
                                `<option value="${item.id}">${item.title}</option>`
                            ).join('')}
                        </select>
                        <select id="student-filter">
                            <option value="">All Students</option>
                            ${this.students.map(student => 
                                `<option value="${student.user_id}">${this.getStudentDisplayName(student)}</option>`
                            ).join('')}
                        </select>
                    </div>
                </div>

                <div class="submissions-grid" id="ungraded-submissions">
                    ${ungradedSubmissions.map(submission => this.renderSubmissionCard(submission, false)).join('')}
                </div>

                <div class="section-header">
                    <h3>✅ Graded Submissions (${gradedSubmissions.length})</h3>
                </div>

                <div class="submissions-grid" id="graded-submissions">
                    ${gradedSubmissions.map(submission => this.renderSubmissionCard(submission, true)).join('')}
                </div>
            </div>
        `;
    }

    renderSubmissionCard(submission, isGraded) {
        const studentName = this.getStudentDisplayName(submission.profiles);
        const itemTitle = submission.homework_items?.title || 'Unknown Item';
        const submittedDate = new Date(submission.submitted_at).toLocaleString();
        const maxPoints = submission.homework_items?.points || 100;

        return `
            <div class="submission-card ${isGraded ? 'graded' : 'ungraded'}" data-submission-id="${submission.id}">
                <div class="submission-header">
                    <div class="student-info">
                        <strong>${studentName}</strong>
                        <span class="item-title">${itemTitle}</span>
                    </div>
                    <div class="submission-meta">
                        <span class="attempt">Attempt ${submission.attempt_number}</span>
                        <span class="date">${submittedDate}</span>
                    </div>
                </div>

                <div class="submission-content">
                    ${this.renderSubmissionData(submission.submission_data)}
                </div>

                <div class="grading-section">
                    ${isGraded ? this.renderGradedInfo(submission) : this.renderGradingForm(submission, maxPoints)}
                </div>
            </div>
        `;
    }

    renderSubmissionData(submissionData) {
        if (!submissionData) return '<p>No submission data</p>';

        const data = typeof submissionData === 'string' ? JSON.parse(submissionData) : submissionData;

        switch (data.type) {
            case 'text':
                return `<div class="text-submission">${this.escapeHtml(data.content || '')}</div>`;
            
            case 'url':
                return `
                    <div class="url-submission">
                        <a href="${data.url}" target="_blank" rel="noopener">${data.url}</a>
                        ${data.description ? `<p>${this.escapeHtml(data.description)}</p>` : ''}
                    </div>
                `;
            
            case 'code':
                return `
                    <div class="code-submission">
                        <div class="language">${data.language || 'Unknown'}</div>
                        <pre><code>${this.escapeHtml(data.code || '')}</code></pre>
                        ${data.explanation ? `<p>${this.escapeHtml(data.explanation)}</p>` : ''}
                    </div>
                `;
            
            case 'file':
                return `
                    <div class="file-submission">
                        <span class="file-name">📎 ${data.file_name || 'File Upload'}</span>
                        ${data.description ? `<p>${this.escapeHtml(data.description)}</p>` : ''}
                    </div>
                `;
            
            default:
                return `<div class="unknown-submission">Submission type: ${data.type}</div>`;
        }
    }

    renderGradingForm(submission, maxPoints) {
        return `
            <form class="grading-form" data-submission-id="${submission.id}">
                <div class="score-input">
                    <label>Score (out of ${maxPoints}):</label>
                    <input type="number" name="raw_score" min="0" max="${maxPoints * 1.5}" step="0.1" required />
                </div>
                <div class="feedback-input">
                    <label>Feedback (optional):</label>
                    <textarea name="feedback" rows="3" placeholder="Provide feedback to the student..."></textarea>
                </div>
                <div class="grading-actions">
                    <button type="submit" class="grade-btn">💾 Save Grade</button>
                    <button type="button" class="defer-btn">⏭️ Skip for Now</button>
                </div>
            </form>
        `;
    }

    renderGradedInfo(submission) {
        const gradedDate = submission.graded_at ? new Date(submission.graded_at).toLocaleString() : 'Unknown';
        
        return `
            <div class="graded-info">
                <div class="grade-display">
                    <span class="score">${submission.adjusted_score || submission.raw_score} points</span>
                    <span class="graded-date">Graded: ${gradedDate}</span>
                </div>
                ${submission.feedback ? `<div class="feedback-display">${this.escapeHtml(submission.feedback)}</div>` : ''}
                <button class="regrade-btn" data-submission-id="${submission.id}">✏️ Edit Grade</button>
            </div>
        `;
    }

    renderManualGradesTab() {
        return `
            <div class="manual-grades-section">
                <div class="section-header">
                    <h3>➕ Add Manual Grades</h3>
                    <p>Add grades for exams, participation, in-class activities, etc.</p>
                </div>

                <form class="manual-grade-form" id="manual-grade-form">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="manual-item-type">Grade Type:</label>
                            <select name="item_type" id="manual-item-type" required>
                                <option value="exam">📝 Exam</option>
                                <option value="participation">🙋 Participation</option>
                                <option value="in_class">🏫 In-Class Activity</option>
                                <option value="project">📂 Project</option>
                                <option value="bonus">⭐ Bonus</option>
                                <option value="manual">📊 Other</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="manual-constituent">Constituent:</label>
                            <select name="constituent_slug" id="manual-constituent" required>
                                <option value="">Select constituent...</option>
                                <!-- Will be populated dynamically -->
                            </select>
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="manual-item-id">Item ID:</label>
                            <input type="text" name="item_id" id="manual-item-id" required 
                                   placeholder="e.g., midterm_exam_1" />
                        </div>
                        <div class="form-group">
                            <label for="manual-title">Title:</label>
                            <input type="text" name="title" id="manual-title" required 
                                   placeholder="e.g., Midterm Exam" />
                        </div>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label for="manual-points">Points:</label>
                            <input type="number" name="points" id="manual-points" required 
                                   min="1" max="1000" placeholder="100" />
                        </div>
                        <div class="form-group">
                            <label for="manual-description">Description (optional):</label>
                            <input type="text" name="description" id="manual-description" 
                                   placeholder="Brief description..." />
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="submit" class="create-btn">🎯 Create Manual Item</button>
                        <button type="button" class="bulk-grade-btn">📊 Bulk Grade Entry</button>
                    </div>
                </form>

                <div class="bulk-grading-section" id="bulk-grading" style="display: none;">
                    <!-- Bulk grading interface will be shown here -->
                </div>
            </div>
        `;
    }

    renderOverviewTab() {
        const stats = this.calculateClassStats();

        return `
            <div class="overview-section">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-value">${stats.totalSubmissions}</div>
                        <div class="stat-label">Total Submissions</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.ungradedCount}</div>
                        <div class="stat-label">Ungraded</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.averageGrade.toFixed(1)}%</div>
                        <div class="stat-label">Average Grade</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-value">${stats.activeStudents}</div>
                        <div class="stat-label">Active Students</div>
                    </div>
                </div>

                <div class="charts-section">
                    <!-- Grade distribution chart would go here -->
                    <div class="chart-placeholder">
                        <h4>📊 Grade Distribution</h4>
                        <p>Chart visualization would be implemented here</p>
                    </div>
                </div>

                <div class="export-section">
                    <h4>📥 Export Options</h4>
                    <button class="export-btn" id="export-grades-csv">📊 Export Grades (CSV)</button>
                    <button class="export-btn" id="export-submissions-csv">📋 Export Submissions (CSV)</button>
                </div>
            </div>
        `;
    }

    setupEventHandlers() {
        // Tab switching
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('tab-btn')) {
                this.switchTab(e.target.dataset.tab);
            }
        });

        // Grading form submission
        document.addEventListener('submit', (e) => {
            if (e.target.classList.contains('grading-form')) {
                e.preventDefault();
                this.handleGradeSubmission(e.target);
            }
        });

        // Manual grade form submission
        document.addEventListener('submit', (e) => {
            if (e.target.id === 'manual-grade-form') {
                e.preventDefault();
                this.handleManualGradeCreation(e.target);
            }
        });

        // Regrade button
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('regrade-btn')) {
                this.handleRegrade(e.target.dataset.submissionId);
            }
        });

        // Export buttons
        document.addEventListener('click', (e) => {
            if (e.target.id === 'export-grades-csv') {
                this.exportGrades();
            } else if (e.target.id === 'export-submissions-csv') {
                this.exportSubmissions();
            }
        });
    }

    switchTab(tabName) {
        // Update tab buttons
        document.querySelectorAll('.tab-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.tab === tabName);
        });

        // Update tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.toggle('active', content.id === `${tabName}-tab`);
        });
    }

    async handleGradeSubmission(form) {
        const submissionId = form.dataset.submissionId;
        const formData = new FormData(form);

        const gradingData = {
            raw_score: parseFloat(formData.get('raw_score')),
            feedback: formData.get('feedback') || null
        };

        try {
            const result = await this.submitGrade(submissionId, gradingData);
            
            if (result.success) {
                this.showSuccess('Grade saved successfully!');
                // Reload submissions to reflect changes
                await this.loadSubmissions();
                this.renderGradingInterface();
            } else {
                this.showError(result.error || 'Failed to save grade');
            }

        } catch (error) {
            console.error('Grading error:', error);
            this.showError('Failed to save grade. Please try again.');
        }
    }

    async submitGrade(submissionId, gradingData) {
        if (!this.supabaseClient) {
            throw new Error('Supabase client not initialized');
        }

        const { data: { session } } = await this.supabaseClient.auth.getSession();
        
        if (!session) {
            throw new Error('No authentication session');
        }

        const gradingRequest = {
            class_id: this.classContext.class_id,
            repo_name: this.classContext.repo_name,
            submission_id: submissionId,
            grading_data: gradingData
        };

        const response = await fetch('/functions/v1/professor-grade-item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${session.access_token}`,
                'X-Class-Context': this.classContext.class_id
            },
            body: JSON.stringify(gradingRequest)
        });

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            throw new Error(errorData.error || `Server error: ${response.status}`);
        }

        return await response.json();
    }

    // Utility methods
    getStudentDisplayName(studentProfile) {
        if (!studentProfile) return 'Unknown Student';
        
        return studentProfile.full_name || 
               studentProfile.raw_user_meta_data?.full_name ||
               studentProfile.raw_user_meta_data?.user_name ||
               'Student';
    }

    calculateClassStats() {
        const gradedSubmissions = this.submissions.filter(s => s.raw_score !== null);
        const totalGrade = gradedSubmissions.reduce((sum, s) => sum + (s.adjusted_score || s.raw_score), 0);
        
        return {
            totalSubmissions: this.submissions.length,
            ungradedCount: this.submissions.length - gradedSubmissions.length,
            averageGrade: gradedSubmissions.length > 0 ? (totalGrade / gradedSubmissions.length) : 0,
            activeStudents: this.students.length
        };
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        // Implementation for showing error messages
        console.error('Error:', message);
    }

    showSuccess(message) {
        // Implementation for showing success messages
        console.log('Success:', message);
    }

    showAccessDenied() {
        document.getElementById('grading-interface').innerHTML = `
            <div class="access-denied">
                <h2>🚫 Access Denied</h2>
                <p>You must be the professor of this class to access the grading interface.</p>
            </div>
        `;
    }

    showAuthenticationRequired() {
        document.getElementById('grading-interface').innerHTML = `
            <div class="auth-required">
                <h2>🔐 Authentication Required</h2>
                <p>Please log in as the class professor to access grading tools.</p>
                <button onclick="window.location.href='/auth/login'">Log In with GitHub</button>
            </div>
        `;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on professor grading pages
    if (document.getElementById('grading-interface')) {
        new ProfessorGradingInterface();
    }
});