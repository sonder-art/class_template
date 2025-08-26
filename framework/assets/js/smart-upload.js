/**
 * Smart Upload Interface
 * Comprehensive assignment submission interface for students
 * Lists all items, shows submission status, provides quick submit
 */

class SmartUploadManager {
    constructor() {
        this.items = [];
        this.submissions = [];
        this.modules = [];
        this.constituents = [];
        this.currentUser = null;
        this.filteredItems = [];
        
        this.init();
    }

    async init() {
        console.log('🚀 Smart Upload Manager initializing...');
        
        try {
            // Check authentication first
            await this.checkAuthentication();
            
            // Load data from multiple sources
            await this.loadData();
            
            // Setup UI
            this.setupEventListeners();
            this.renderInterface();
            
            console.log('✅ Smart Upload Manager initialized');
            
        } catch (error) {
            console.error('❌ Smart Upload Manager initialization failed:', error);
            this.showError(error.message);
        }
    }

    async checkAuthentication() {
        // Wait for auth state to be ready
        if (!window.authState || !window.authState.isAuthenticated) {
            console.warn('🚫 User not authenticated');
            this.showAuthRequired();
            throw new Error('Authentication required');
        }
        
        this.currentUser = window.authState.user;
        console.log('✅ User authenticated:', this.currentUser?.user_metadata?.user_name);
    }

    async loadData() {
        console.log('📊 Loading assignment data...');
        
        // Load items from generated JSON (build-time data)
        const itemsResponse = await fetch(`${window.location.origin}${window.authConfig?.base_url || ''}/data/items.json`);
        if (!itemsResponse.ok) {
            throw new Error('Failed to load items data');
        }
        const itemsData = await itemsResponse.json();
        this.items = itemsData.items || [];
        
        // Load modules and constituents for organization
        try {
            const [modulesResponse, constituentsResponse] = await Promise.all([
                fetch(`${window.location.origin}${window.authConfig?.base_url || ''}/data/modules.json`),
                fetch(`${window.location.origin}${window.authConfig?.base_url || ''}/data/constituents.json`)
            ]);
            
            if (modulesResponse.ok) {
                const modulesData = await modulesResponse.json();
                this.modules = modulesData.modules || [];
            }
            
            if (constituentsResponse.ok) {
                const constituentsData = await constituentsResponse.json();
                this.constituents = constituentsData.constituents || [];
            }
        } catch (error) {
            console.warn('⚠️ Could not load modules/constituents data:', error);
        }
        
        // Load existing submissions from database
        await this.loadSubmissions();
        
        console.log(`📈 Data loaded: ${this.items.length} items, ${this.submissions.length} submissions`);
    }

    async loadSubmissions() {
        if (!window.authState?.client || !this.currentUser) {
            console.warn('⚠️ Cannot load submissions: missing auth client or user');
            return;
        }

        try {
            // Get all submissions for current user
            const { data: submissions, error } = await window.authState.client
                .from('student_submissions')
                .select('*')
                .eq('student_id', this.currentUser.id)
                .order('submitted_at', { ascending: false });

            if (error) {
                console.warn('⚠️ Error loading submissions:', error);
                return;
            }

            this.submissions = submissions || [];
            console.log(`✅ Loaded ${this.submissions.length} existing submissions`);

        } catch (error) {
            console.warn('⚠️ Failed to load submissions:', error);
        }
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('moduleFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('statusFilter').addEventListener('change', () => this.applyFilters());
        document.getElementById('searchFilter').addEventListener('input', () => this.applyFilters());
        
        // Listen for successful submissions to refresh data
        window.addEventListener('itemSubmitted', () => {
            console.log('🔄 Item submitted, refreshing data...');
            this.loadSubmissions().then(() => this.renderInterface());
        });
    }

    renderInterface() {
        // Hide loading, show interface
        document.getElementById('loadingState').style.display = 'none';
        document.getElementById('submissionsInterface').style.display = 'block';
        
        // Render summary stats
        this.renderStats();
        
        // Render module filter options
        this.renderModuleFilter();
        
        // Apply filters and render items
        this.applyFilters();
    }

    renderStats() {
        const submitted = this.items.filter(item => this.getSubmissionStatus(item.item_id) === 'submitted').length;
        const graded = this.items.filter(item => this.getSubmissionStatus(item.item_id) === 'graded').length;
        const overdue = this.items.filter(item => this.isOverdue(item)).length;
        const pending = this.items.length - submitted;

        document.getElementById('totalItems').textContent = this.items.length;
        document.getElementById('submittedItems').textContent = submitted + graded;
        document.getElementById('pendingItems').textContent = pending;
        document.getElementById('overdueItems').textContent = overdue;
    }

    renderModuleFilter() {
        const moduleFilter = document.getElementById('moduleFilter');
        
        // Clear existing options except "All"
        while (moduleFilter.children.length > 1) {
            moduleFilter.removeChild(moduleFilter.lastChild);
        }
        
        // Add module options
        this.modules.forEach(module => {
            const option = document.createElement('option');
            option.value = module.id;
            option.textContent = `${module.icon || '📚'} ${module.name}`;
            moduleFilter.appendChild(option);
        });
    }

    applyFilters() {
        const moduleFilter = document.getElementById('moduleFilter').value;
        const statusFilter = document.getElementById('statusFilter').value;
        const searchTerm = document.getElementById('searchFilter').value.toLowerCase();

        this.filteredItems = this.items.filter(item => {
            // Module filter
            if (moduleFilter !== 'all') {
                const constituent = this.constituents.find(c => c.slug === item.constituent_slug);
                if (!constituent || constituent.module_id !== moduleFilter) {
                    return false;
                }
            }

            // Status filter
            if (statusFilter !== 'all') {
                const status = this.getSubmissionStatus(item.item_id);
                if (statusFilter === 'not_submitted' && (status === 'submitted' || status === 'graded')) {
                    return false;
                }
                if (statusFilter === 'submitted' && status !== 'submitted') {
                    return false;
                }
                if (statusFilter === 'graded' && status !== 'graded') {
                    return false;
                }
                if (statusFilter === 'overdue' && !this.isOverdue(item)) {
                    return false;
                }
            }

            // Search filter
            if (searchTerm && !item.title.toLowerCase().includes(searchTerm)) {
                return false;
            }

            return true;
        });

        this.renderItems();
    }

    renderItems() {
        const itemsList = document.getElementById('itemsList');
        
        if (this.filteredItems.length === 0) {
            itemsList.innerHTML = `
                <div class="no-items">
                    <p>📭 No assignments match your current filters</p>
                    <button onclick="document.getElementById('moduleFilter').value='all'; document.getElementById('statusFilter').value='all'; document.getElementById('searchFilter').value=''; window.smartUpload.applyFilters();">Clear Filters</button>
                </div>
            `;
            return;
        }

        // Group items by module → constituent
        const grouped = this.groupItemsByHierarchy(this.filteredItems);
        
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
                    html += this.renderItemCard(item);
                });
                
                html += `
                        </div>
                    </div>
                `;
            }
            
            html += `</div>`;
        }
        
        itemsList.innerHTML = html;
        
        // Initialize submission forms for newly rendered items
        if (window.ItemSubmissionHandler) {
            // Re-run item detection for new elements
            setTimeout(() => {
                const submissionHandler = new ItemSubmissionHandler();
            }, 100);
        }
    }

    groupItemsByHierarchy(items) {
        const grouped = {};
        
        items.forEach(item => {
            const constituent = this.constituents.find(c => c.slug === item.constituent_slug);
            const moduleId = constituent?.module_id || 'unknown';
            
            if (!grouped[moduleId]) {
                grouped[moduleId] = {};
            }
            
            if (!grouped[moduleId][item.constituent_slug]) {
                grouped[moduleId][item.constituent_slug] = [];
            }
            
            grouped[moduleId][item.constituent_slug].push(item);
        });
        
        return grouped;
    }

    renderItemCard(item) {
        const status = this.getSubmissionStatus(item.item_id);
        const submission = this.getSubmission(item.item_id);
        const isOverdue = this.isOverdue(item);
        
        const statusClass = isOverdue ? 'overdue' : status;
        const statusText = this.getStatusText(status, isOverdue);
        const dueDateText = this.formatDueDate(item.due_date);
        
        return `
            <div class="item-card ${statusClass}" data-item-id="${item.item_id}" data-constituent="${item.constituent_slug}" data-delivery-type="${item.delivery_type}">
                <div class="item-header">
                    <h5>${item.title}</h5>
                    <span class="status-badge ${statusClass}">${statusText}</span>
                </div>
                <div class="item-details">
                    <div class="item-meta">
                        <span class="points">${item.points} points</span>
                        ${dueDateText ? `<span class="due-date">${dueDateText}</span>` : ''}
                        <span class="delivery-type">${this.getDeliveryIcon(item.delivery_type)} ${item.delivery_type}</span>
                    </div>
                    ${submission ? this.renderSubmissionInfo(submission) : ''}
                </div>
                <div class="item-actions">
                    ${status === 'graded' ? 
                        `<span class="grade">${submission.adjusted_score || submission.raw_score}/${item.points}</span>` : 
                        `<button class="submit-btn" onclick="window.smartUpload.openSubmissionForm('${item.item_id}')">
                            ${status === 'submitted' ? '📝 Resubmit' : '📤 Submit'}
                        </button>`
                    }
                </div>
            </div>
        `;
    }

    renderSubmissionInfo(submission) {
        return `
            <div class="submission-info">
                <small>
                    Submitted: ${new Date(submission.submitted_at).toLocaleDateString()}
                    ${submission.feedback ? `<br>Feedback available` : ''}
                </small>
            </div>
        `;
    }

    getSubmissionStatus(itemId) {
        const submission = this.getSubmission(itemId);
        if (!submission) return 'not_submitted';
        if (submission.graded_at && (submission.raw_score !== null || submission.adjusted_score !== null)) return 'graded';
        return 'submitted';
    }

    getSubmission(itemId) {
        return this.submissions.find(s => s.item_id === itemId);
    }

    isOverdue(item) {
        if (!item.due_date) return false;
        return new Date(item.due_date) < new Date();
    }

    getStatusText(status, isOverdue) {
        if (isOverdue && status === 'not_submitted') return '⏰ Overdue';
        const statusMap = {
            'not_submitted': '📋 Not Submitted',
            'submitted': '✅ Submitted',
            'graded': '🎯 Graded'
        };
        return statusMap[status] || status;
    }

    formatDueDate(dueDateStr) {
        if (!dueDateStr) return null;
        const date = new Date(dueDateStr);
        const now = new Date();
        const diffDays = Math.ceil((date - now) / (1000 * 60 * 60 * 24));
        
        if (diffDays < 0) return `Due ${Math.abs(diffDays)} days ago`;
        if (diffDays === 0) return 'Due today';
        if (diffDays === 1) return 'Due tomorrow';
        return `Due in ${diffDays} days`;
    }

    getDeliveryIcon(deliveryType) {
        const iconMap = {
            'url': '🔗',
            'upload': '📎',
            'file': '📎',
            'code': '💻',
            'text': '📝',
            'presentation': '🎤',
            'video': '📹'
        };
        return iconMap[deliveryType] || '📋';
    }

    openSubmissionForm(itemId) {
        // Find the item card and trigger the submission form
        const itemCard = document.querySelector(`[data-item-id="${itemId}"]`);
        if (itemCard) {
            // Add graded-item class if not present (for compatibility)
            itemCard.classList.add('graded-item');
            
            // Scroll to the item
            itemCard.scrollIntoView({ behavior: 'smooth', block: 'center' });
            
            // Highlight the item
            itemCard.classList.add('highlighted');
            setTimeout(() => itemCard.classList.remove('highlighted'), 3000);
            
            // If submission handler is available, trigger form creation
            if (window.ItemSubmissionHandler) {
                const handler = new ItemSubmissionHandler();
            }
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

// SmartUploadManager class - initialized by page-level script