/**
 * Item Submission Handler
 * Handles student submissions for all item types (homework, projects, assignments, etc.)
 * Includes proper security and class context verification
 */

class ItemSubmissionHandler {
    constructor() {
        this.classContext = null;
        this.supabaseClient = null;
        this.currentUser = null;
        this.submissionForms = new Map();
        
        this.init();
    }

    async init() {
        console.log('🔍 ItemSubmissionHandler.init() starting...');
        
        // Get class context from meta tags (injected during build)
        this.classContext = this.getClassContext();
        console.log('🔍 Class context:', this.classContext);
        
        if (!this.classContext) {
            console.error('❌ Missing class context - submission disabled');
            this.showError('Class context not found. Please refresh the page.');
            return;
        }

        // Initialize Supabase client
        console.log('🔍 Initializing Supabase client...');
        this.initializeSupabase();

        // Check authentication
        console.log('🔍 Checking authentication...');
        await this.checkAuthentication();

        // Find and enhance all item elements on the page
        console.log('🔍 Detecting and enhancing items...');
        this.detectAndEnhanceItems();

        console.log('✅ Item submission handler initialized for class:', this.classContext.repo_name);
    }

    getClassContext() {
        // Try meta tags first (if they exist)
        const classId = document.querySelector('meta[name="class-id"]')?.content;
        const repoName = document.querySelector('meta[name="repo-name"]')?.content;
        const professorGithub = document.querySelector('meta[name="professor-github"]')?.content;

        if (classId && repoName) {
            return {
                class_id: classId,
                repo_name: repoName,
                professor_github: professorGithub
            };
        }

        // FALLBACK: Use FrameworkConfig if meta tags don't exist
        if (window.FrameworkConfig && window.FrameworkConfig.classContext) {
            console.log('🔄 Using FrameworkConfig for class context');
            const config = window.FrameworkConfig.classContext;
            return {
                class_id: config.classId,
                repo_name: config.repoName,
                professor_github: config.professorGithub
            };
        }

        return null;
    }

    initializeSupabase() {
        // Get Supabase config from meta tags
        const supabaseUrl = document.querySelector('meta[name="supabase-url"]')?.content;
        const supabaseAnonKey = document.querySelector('meta[name="supabase-anon-key"]')?.content;

        if (!supabaseUrl || !supabaseAnonKey) {
            console.error('Missing Supabase configuration');
            this.showError('Configuration error. Please contact your instructor.');
            return;
        }

        // Initialize Supabase client (assumes Supabase JS library is loaded)
        if (typeof supabase !== 'undefined') {
            this.supabaseClient = supabase.createClient(supabaseUrl, supabaseAnonKey);
        } else {
            console.error('Supabase client library not loaded');
            this.showError('Required libraries not loaded. Please refresh the page.');
        }
    }

    async checkAuthentication() {
        if (!this.supabaseClient) return;

        try {
            const { data: { user }, error } = await this.supabaseClient.auth.getUser();
            
            if (error || !user) {
                this.showAuthenticationRequired();
                return;
            }

            this.currentUser = user;
            console.log('User authenticated:', user.user_metadata?.user_name || user.email);
        } catch (error) {
            console.error('Authentication check failed:', error);
            this.showError('Authentication check failed. Please refresh and try again.');
        }
    }

    detectAndEnhanceItems() {
        // Find all item elements (created by Hugo shortcodes)
        const itemElements = document.querySelectorAll('.graded-item');
        
        console.log(`Found ${itemElements.length} graded items on page`);

        itemElements.forEach((element, index) => {
            this.enhanceItemElement(element, index);
        });
    }

    enhanceItemElement(element, index) {
        const itemId = element.dataset.itemId;
        const constituentSlug = element.dataset.constituent;
        const deliveryType = element.dataset.deliveryType;

        if (!itemId || !constituentSlug || !deliveryType) {
            console.warn('Item element missing required data attributes:', element);
            return;
        }

        // Create submission interface
        const submissionContainer = this.createSubmissionInterface(
            itemId, 
            constituentSlug, 
            deliveryType,
            index
        );

        // Add to the item element
        element.appendChild(submissionContainer);

        // Load existing submissions
        this.loadExistingSubmissions(itemId, submissionContainer);
    }

    createSubmissionInterface(itemId, constituentSlug, deliveryType, index) {
        const container = document.createElement('div');
        container.className = 'submission-interface';
        container.id = `submission-${itemId}-${index}`;

        // Create form based on delivery type
        const form = this.createSubmissionForm(itemId, constituentSlug, deliveryType);
        
        // Create status area
        const statusArea = document.createElement('div');
        statusArea.className = 'submission-status';
        statusArea.id = `status-${itemId}-${index}`;

        // Create submissions history area
        const historyArea = document.createElement('div');
        historyArea.className = 'submission-history';
        historyArea.id = `history-${itemId}-${index}`;
        historyArea.innerHTML = '<h4>Previous Submissions</h4><div class="submissions-list"></div>';

        container.appendChild(statusArea);
        container.appendChild(form);
        container.appendChild(historyArea);

        return container;
    }

    createSubmissionForm(itemId, constituentSlug, deliveryType) {
        const form = document.createElement('form');
        form.className = 'item-submission-form';
        form.id = `form-${itemId}`;

        // Form header
        const header = document.createElement('div');
        header.className = 'submission-form-header';
        header.innerHTML = `
            <h4>📝 Submit ${this.getDeliveryTypeIcon(deliveryType)} ${this.formatDeliveryType(deliveryType)}</h4>
            <p class="submission-instructions">Submit your work for this item.</p>
        `;

        // Create form fields based on delivery type
        const fieldsContainer = this.createFormFields(deliveryType);

        // Submit button
        const submitButton = document.createElement('button');
        submitButton.type = 'submit';
        submitButton.className = 'submit-btn';
        submitButton.innerHTML = '🚀 Submit Item';

        // Assemble form
        form.appendChild(header);
        form.appendChild(fieldsContainer);
        form.appendChild(submitButton);

        // Add event listener
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            this.handleSubmission(itemId, constituentSlug, deliveryType, form);
        });

        return form;
    }

    createFormFields(deliveryType) {
        const container = document.createElement('div');
        container.className = 'form-fields';

        switch (deliveryType) {
            case 'text':
                container.innerHTML = `
                    <div class="field-group">
                        <label for="submission-text">Your Answer:</label>
                        <textarea 
                            id="submission-text" 
                            name="content" 
                            rows="8" 
                            maxlength="50000"
                            required
                            placeholder="Enter your answer here..."
                        ></textarea>
                        <div class="char-counter">0 / 50,000 characters</div>
                    </div>
                `;
                // Add character counter
                const textarea = container.querySelector('textarea');
                const counter = container.querySelector('.char-counter');
                textarea.addEventListener('input', (e) => {
                    counter.textContent = `${e.target.value.length} / 50,000 characters`;
                });
                break;

            case 'url':
                container.innerHTML = `
                    <div class="field-group">
                        <label for="submission-url">URL:</label>
                        <input 
                            type="url" 
                            id="submission-url" 
                            name="url" 
                            required
                            placeholder="https://example.com/your-work"
                        />
                        <small>Provide a link to your work (GitHub repo, deployed site, document, etc.)</small>
                    </div>
                    <div class="field-group">
                        <label for="submission-description">Description (optional):</label>
                        <textarea 
                            id="submission-description" 
                            name="description" 
                            rows="3"
                            maxlength="1000"
                            placeholder="Brief description of what you're submitting..."
                        ></textarea>
                    </div>
                `;
                break;

            case 'file':
            case 'upload':
                container.innerHTML = `
                    <div class="field-group">
                        <label for="submission-file">Upload File:</label>
                        <input 
                            type="file" 
                            id="submission-file" 
                            name="file" 
                            required
                            accept=".pdf,.doc,.docx,.txt,.zip,.py,.js,.html,.css,.md"
                        />
                        <small>Accepted formats: PDF, Word docs, text files, code files, archives (max 10MB)</small>
                    </div>
                    <div class="field-group">
                        <label for="file-description">File Description (optional):</label>
                        <textarea 
                            id="file-description" 
                            name="description" 
                            rows="2"
                            maxlength="500"
                            placeholder="Describe what you're submitting..."
                        ></textarea>
                    </div>
                `;
                // Add file validation
                const fileInput = container.querySelector('input[type="file"]');
                fileInput.addEventListener('change', this.validateFileUpload.bind(this));
                break;

            case 'code':
                container.innerHTML = `
                    <div class="field-group">
                        <label for="submission-code">Your Code:</label>
                        <select id="code-language" name="language">
                            <option value="javascript">JavaScript</option>
                            <option value="python">Python</option>
                            <option value="html">HTML</option>
                            <option value="css">CSS</option>
                            <option value="sql">SQL</option>
                            <option value="markdown">Markdown</option>
                            <option value="other">Other</option>
                        </select>
                        <textarea 
                            id="submission-code" 
                            name="code" 
                            rows="15" 
                            required
                            placeholder="Paste your code here..."
                            style="font-family: 'Courier New', monospace;"
                        ></textarea>
                    </div>
                    <div class="field-group">
                        <label for="code-explanation">Code Explanation (optional):</label>
                        <textarea 
                            id="code-explanation" 
                            name="explanation" 
                            rows="4"
                            maxlength="2000"
                            placeholder="Explain how your code works, any challenges you faced, etc."
                        ></textarea>
                    </div>
                `;
                break;

            default:
                container.innerHTML = `
                    <div class="field-group">
                        <label for="submission-general">Your Submission:</label>
                        <textarea 
                            id="submission-general" 
                            name="content" 
                            rows="6" 
                            required
                            placeholder="Enter your submission here..."
                        ></textarea>
                    </div>
                `;
        }

        return container;
    }

    async handleSubmission(itemId, constituentSlug, deliveryType, form) {
        if (!this.currentUser) {
            this.showError('You must be logged in to submit items.');
            return;
        }

        // Show loading state
        const submitButton = form.querySelector('.submit-btn');
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '⏳ Submitting...';
        submitButton.disabled = true;

        try {
            // Collect form data
            const formData = new FormData(form);
            const submissionData = this.collectSubmissionData(formData, deliveryType);

            // Prepare submission request
            const submissionRequest = {
                class_id: this.classContext.class_id,
                repo_name: this.classContext.repo_name,
                item_id: itemId,
                submission_data: submissionData
            };

            // Submit to Edge Function
            const response = await this.submitToServer(submissionRequest);

            if (response.success) {
                this.showSuccess(`Item submitted successfully! Attempt ${response.submission.attempt_number}`);
                form.reset();
                
                // Reload submissions history
                const container = form.closest('.submission-interface');
                this.loadExistingSubmissions(itemId, container);
            } else {
                this.showError(response.error || 'Submission failed');
            }

        } catch (error) {
            console.error('Submission error:', error);
            this.showError('Submission failed. Please check your connection and try again.');
        } finally {
            // Reset button
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }
    }

    collectSubmissionData(formData, deliveryType) {
        const submissionData = {
            type: deliveryType
        };

        switch (deliveryType) {
            case 'text':
                submissionData.content = formData.get('content');
                break;

            case 'url':
                submissionData.url = formData.get('url');
                submissionData.description = formData.get('description');
                break;

            case 'file':
            case 'upload':
                // File handling will be implemented separately
                // For now, we'll handle it as a placeholder
                submissionData.file_name = formData.get('file')?.name || 'file';
                submissionData.description = formData.get('description');
                break;

            case 'code':
                submissionData.code = formData.get('code');
                submissionData.language = formData.get('language');
                submissionData.explanation = formData.get('explanation');
                break;

            default:
                submissionData.content = formData.get('content');
        }

        return submissionData;
    }

    async submitToServer(submissionRequest) {
        if (!this.supabaseClient) {
            throw new Error('Supabase client not initialized');
        }

        // Get current session
        const { data: { session } } = await this.supabaseClient.auth.getSession();
        
        if (!session) {
            throw new Error('No authentication session');
        }

        // Get next attempt number
        const { data: existingSubmissions } = await this.supabaseClient
            .from('student_submissions')
            .select('attempt_number')
            .eq('student_id', session.user.id)
            .eq('item_id', submissionRequest.item_id)
            .order('attempt_number', { ascending: false })
            .limit(1);

        const nextAttempt = existingSubmissions && existingSubmissions.length > 0 
            ? existingSubmissions[0].attempt_number + 1 
            : 1;

        // Submit directly to Supabase
        const { data, error } = await this.supabaseClient
            .from('student_submissions')
            .insert({
                class_id: submissionRequest.class_id,
                student_id: session.user.id,
                item_id: submissionRequest.item_id,
                attempt_number: nextAttempt,
                submission_data: JSON.stringify(submissionRequest.submission_data),
                submitted_at: new Date().toISOString()
            })
            .select()
            .single();

        if (error) {
            throw new Error(error.message);
        }

        return {
            success: true,
            submission: data
        };
    }

    async loadExistingSubmissions(itemId, container) {
        if (!this.currentUser || !this.supabaseClient) return;

        try {
            // Query existing submissions using Supabase client
            const { data: submissions, error } = await this.supabaseClient
                .from('student_submissions')
                .select(`
                    id,
                    attempt_number,
                    submission_data,
                    submitted_at,
                    raw_score,
                    adjusted_score,
                    feedback,
                    graded_at
                `)
                .eq('student_id', this.currentUser.id)
                .eq('item_id', itemId)
                .order('attempt_number', { ascending: false });

            if (error) {
                console.error('Error loading submissions:', error);
                return;
            }

            this.displaySubmissionsHistory(submissions, container);

        } catch (error) {
            console.error('Failed to load submissions:', error);
        }
    }

    displaySubmissionsHistory(submissions, container) {
        const historyArea = container.querySelector('.submissions-list');
        
        if (!submissions || submissions.length === 0) {
            historyArea.innerHTML = '<p class="no-submissions">No submissions yet.</p>';
            return;
        }

        const submissionsHtml = submissions.map(submission => {
            const submittedDate = new Date(submission.submitted_at).toLocaleString();
            const gradeInfo = submission.raw_score !== null 
                ? `<span class="grade">Grade: ${submission.adjusted_score || submission.raw_score} points</span>`
                : '<span class="ungraded">Not graded yet</span>';

            return `
                <div class="submission-item">
                    <div class="submission-header">
                        <span class="attempt">Attempt ${submission.attempt_number}</span>
                        <span class="date">${submittedDate}</span>
                        ${gradeInfo}
                    </div>
                    ${submission.feedback ? `<div class="feedback">${submission.feedback}</div>` : ''}
                </div>
            `;
        }).join('');

        historyArea.innerHTML = submissionsHtml;
    }

    // Utility methods
    getDeliveryTypeIcon(type) {
        const icons = {
            'text': '📝',
            'url': '🔗', 
            'file': '📎',
            'upload': '📎',
            'code': '💻'
        };
        return icons[type] || '📋';
    }

    formatDeliveryType(type) {
        const labels = {
            'text': 'Text Response',
            'url': 'URL Submission',
            'file': 'File Upload',
            'upload': 'File Upload', 
            'code': 'Code Submission'
        };
        return labels[type] || 'Submission';
    }

    validateFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;

        const maxSize = 10 * 1024 * 1024; // 10MB
        if (file.size > maxSize) {
            this.showError('File size must be less than 10MB');
            event.target.value = '';
            return;
        }

        // Additional validation could be added here
        console.log('File selected:', file.name, file.size);
    }

    showAuthenticationRequired() {
        const message = document.createElement('div');
        message.className = 'auth-required-message';
        message.innerHTML = `
            <h3>🔐 Authentication Required</h3>
            <p>Please log in to submit items.</p>
            <button onclick="window.location.href='/auth/login'" class="login-btn">
                Log In with GitHub
            </button>
        `;
        
        // Replace all submission interfaces with auth message
        document.querySelectorAll('.submission-interface').forEach(interfaceEl => {
            interfaceEl.innerHTML = message.innerHTML;
        });
    }

    showError(message) {
        // Show error in all status areas or create a global error
        const statusAreas = document.querySelectorAll('.submission-status');
        if (statusAreas.length > 0) {
            statusAreas.forEach(area => {
                area.innerHTML = `<div class="error-message">❌ ${message}</div>`;
            });
        } else {
            console.error('Submission Error:', message);
            alert(`Error: ${message}`);
        }
    }

    showSuccess(message) {
        const statusAreas = document.querySelectorAll('.submission-status');
        statusAreas.forEach(area => {
            area.innerHTML = `<div class="success-message">✅ ${message}</div>`;
            // Clear after 5 seconds
            setTimeout(() => {
                area.innerHTML = '';
            }, 5000);
        });
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    // Debug logging
    console.log('🔍 Item Submission JS: DOM ready, checking for graded items...');
    
    const items = document.querySelectorAll('.graded-item');
    console.log('🔍 Found graded items:', items.length);
    
    // Log item details
    items.forEach((item, index) => {
        console.log(`🔍 Item ${index + 1}:`, {
            id: item.dataset.itemId,
            constituent: item.dataset.constituent,
            deliveryType: item.dataset.deliveryType
        });
    });
    
    // Only initialize if we're on a page with graded items
    if (items.length > 0) {
        console.log('✅ Initializing ItemSubmissionHandler...');
        new ItemSubmissionHandler();
    } else {
        console.log('ℹ️ No graded items found on this page');
    }
});// Force rebuild Sun Aug 17 05:41:36 PM CST 2025
