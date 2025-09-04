class GradingSyncManager {
    constructor() {
        this.supabase = null;
        this.classId = null;
        this.professorGithub = null;
        this.currentUser = null;
        this.gradingData = null;
        this.databaseState = null;
        this.changes = null;
        
        this.init();
    }
    
    async init() {
        console.log('🔧 Grading sync manager initializing...');
        
        try {
            // Load configuration
            await this.loadConfiguration();
            
            // Verify security
            await this.verifyProfessorAccess();
            
            // Load grading data
            await this.loadGradingData();
            
            // Setup UI
            this.setupEventListeners();
            this.renderSyncInterface();
            
        } catch (error) {
            this.showError(`Initialization failed: ${error.message}`);
        }
    }
    
    async loadConfiguration() {
        // Try FrameworkConfig first
        if (window.FrameworkConfig) {
            this.classId = window.FrameworkConfig.classContext?.classId;
            this.professorGithub = window.FrameworkConfig.classContext?.professorGithub;
            
            const url = window.FrameworkConfig.supabase?.url;
            const key = window.FrameworkConfig.supabase?.anonKey;
            
            if (url && key) {
                this.supabase = supabase.createClient(url, key);
            }
        }
        
        // Fallback to meta tags
        if (!this.classId) {
            this.classId = document.querySelector('meta[name="class-id"]')?.content;
        }
        
        if (!this.supabase) {
            const url = document.querySelector('meta[name="supabase-url"]')?.content;
            const key = document.querySelector('meta[name="supabase-anon-key"]')?.content;
            if (url && key) {
                this.supabase = supabase.createClient(url, key);
            }
        }
        
        if (!this.classId || !this.supabase || !this.professorGithub) {
            throw new Error('Missing configuration: classId, supabase, or professorGithub');
        }
        
        console.log('✅ Configuration loaded:', {
            classId: this.classId,
            professorGithub: this.professorGithub
        });
    }
    
    async verifyProfessorAccess() {
        document.getElementById('auth-verification').innerHTML = 
            '<div class="spinner"></div><p>🔐 Checking authentication...</p>';
        
        // Check if user is authenticated
        console.log('🔐 Attempting to get user...');
        const { data: { user }, error: authError } = await this.supabase.auth.getUser();
        
        console.log('🔐 Auth result:', { user: !!user, error: authError });
        
        if (authError || !user) {
            console.error('❌ Authentication failed:', authError);
            throw new Error(`Not authenticated: ${authError?.message || 'Please log in first'}`);
        }
        
        this.currentUser = user;
        console.log('✅ User authenticated:', user.user_metadata?.user_name);
        
        // Check if user is professor for this class
        const { data: membership, error: memberError } = await this.supabase
            .from('class_members')
            .select('role')
            .eq('user_id', user.id)
            .eq('class_id', this.classId)
            .single();
        
        if (memberError || !membership || membership.role !== 'professor') {
            throw new Error('Access denied: Professor role required for this class');
        }
        
        // Verify GitHub username matches
        const githubUsername = user.user_metadata?.user_name;
        if (githubUsername !== this.professorGithub) {
            throw new Error(`Access denied: GitHub user (${githubUsername}) does not match class professor (${this.professorGithub})`);
        }
        
        console.log('✅ Professor access verified');
        
        // Hide auth verification, show main content
        document.getElementById('auth-verification').style.display = 'none';
        document.getElementById('sync-content').style.display = 'block';
    }
    
    async loadGradingData() {
        console.log('📊 Loading grading data...');
        
        try {
            // Load grading data from generated files
            const [gradingResponse, classResponse] = await Promise.all([
                fetch('/class_template/data/grading_complete.json'),
                fetch('/class_template/data/class_context.json')
            ]);
            
            if (!gradingResponse.ok) {
                throw new Error(`Failed to load grading data: ${gradingResponse.status}`);
            }
            
            const gradingData = await gradingResponse.json();
            const classContext = await classResponse.json();
            
            // Extract data from the structured response (including grading policies)
            this.gradingData = {
                modules: gradingData.data?.modules || [],
                constituents: gradingData.data?.constituents || [],
                items: gradingData.data?.items || [],
                grading_policies: gradingData.data?.grading_policies || [],
                metadata: {
                    generated_at: gradingData.generated_at,
                    total_items: gradingData.counts?.items || 0,
                    class_id: this.classId
                }
            };
            
            console.log('✅ Grading data loaded:', {
                modules: this.gradingData.modules.length,
                constituents: this.gradingData.constituents.length,
                items: this.gradingData.items.length,
                grading_policies: this.gradingData.grading_policies?.length || 0
            });
            
            // Debug: Show detailed items data
            console.log('🔍 DEBUG: Detailed items data from JSON:');
            this.gradingData.items.forEach((item, index) => {
                console.log(`  [${index}] Item:`, {
                    item_id: item.item_id,
                    constituent_slug: item.constituent_slug,
                    title: item.title,
                    points: item.points,
                    delivery_type: item.delivery_type,
                    due_date: item.due_date
                });
            });
            
            console.log('🔍 DEBUG: Class ID being used for sync:', this.classId);
            
        } catch (error) {
            console.error('❌ Failed to load grading data:', error);
            
            // Fallback: Create minimal data structure to prevent crashes
            this.gradingData = {
                modules: [],
                constituents: [],
                items: [],
                grading_policies: [],
                metadata: {
                    generated_at: new Date().toISOString(),
                    total_items: 0,
                    class_id: this.classId
                }
            };
            
            console.log('⚠️ Using fallback data structure');
            this.showError(`Failed to load grading data: ${error.message}`);
        }
    }
    
    async loadDatabaseState() {
        console.log('📊 Loading current database state...');
        
        try {
            // Handle grading_policies separately with proper error handling
            let policies = { data: [] };
            try {
                policies = await this.supabase.from('grading_policies').select('*').eq('class_id', this.classId);
            } catch (policiesError) {
                console.warn('⚠️ grading_policies table may not exist:', policiesError);
                policies = { data: [] };
            }
            
            const [modules, constituents, items] = await Promise.all([
                this.supabase.from('modules').select('*').eq('class_id', this.classId),
                this.supabase.from('constituents').select('*').eq('class_id', this.classId), 
                this.supabase.from('items').select('*').eq('class_id', this.classId)
            ]);
            
            this.databaseState = {
                modules: modules.data || [],
                constituents: constituents.data || [],
                items: items.data || [],
                policies: policies.data || []
            };
        } catch (error) {
            console.error('❌ Failed to load database state:', error);
            // Fallback to empty state
            this.databaseState = {
                modules: [],
                constituents: [],
                items: [],
                policies: []
            };
        }
        
        console.log('✅ Database state loaded:', {
            modules: this.databaseState.modules.length,
            constituents: this.databaseState.constituents.length,
            items: this.databaseState.items.length,
            policies: this.databaseState.policies.length
        });
    }
    
    detectChanges() {
        console.log('🔍 Detecting sync status...');
        console.log('📊 Database state:', {
            modules: this.databaseState.modules.length,
            constituents: this.databaseState.constituents.length,
            items: this.databaseState.items.length,
            policies: this.databaseState.policies.length
        });
        
        // Compare what's in files vs what's current in database
        const currentDbModules = this.databaseState.modules.filter(m => m.is_current);
        const currentDbConstituents = this.databaseState.constituents.filter(c => c.is_current);
        const currentDbItems = this.databaseState.items.filter(i => i.is_current);
        const currentDbPolicies = this.databaseState.policies.filter(p => p.is_active);
        
        console.log('📊 Current database state (is_current=true):', {
            modules: currentDbModules.length,
            constituents: currentDbConstituents.length,
            items: currentDbItems.length,
            policies: currentDbPolicies.length
        });
        console.log('📊 File data counts:', {
            modules: this.gradingData.modules.length,
            constituents: this.gradingData.constituents.length,
            items: this.gradingData.items.length,
            policies: (this.gradingData.grading_policies || []).length
        });
        
        this.changes = {
            modules: {
                new: this.gradingData.modules.filter(m => 
                    !currentDbModules.find(db => db.id === m.id)),
                modified: this.gradingData.modules.filter(m => {
                    const dbModule = currentDbModules.find(db => db.id === m.id);
                    const hasChanged = dbModule && this.hasChanged(m, dbModule);
                    if (hasChanged) {
                        console.log('🔧 Module changed:', m.id, {file: m, db: dbModule});
                    }
                    return hasChanged;
                }),
                will_deactivate: currentDbModules.filter(db => 
                    !this.gradingData.modules.find(m => m.id === db.id))
            },
            constituents: {
                new: this.gradingData.constituents.filter(c => 
                    !currentDbConstituents.find(db => db.id === c.id)),
                modified: this.gradingData.constituents.filter(c => {
                    const dbConstituent = currentDbConstituents.find(db => db.id === c.id);
                    const hasChanged = dbConstituent && this.hasChanged(c, dbConstituent);
                    if (hasChanged) {
                        console.log('🔧 Constituent changed:', c.id, {file: c, db: dbConstituent});
                    }
                    return hasChanged;
                }),
                will_deactivate: currentDbConstituents.filter(db => 
                    !this.gradingData.constituents.find(c => c.id === db.id))
            },
            items: {
                new: this.gradingData.items.filter(i => 
                    !currentDbItems.find(db => db.id === i.item_id)),
                modified: this.gradingData.items.filter(i => {
                    const dbItem = currentDbItems.find(db => db.id === i.item_id);
                    const hasChanged = dbItem && this.hasChanged(i, dbItem);
                    if (hasChanged) {
                        console.log('🔧 Item changed:', i.item_id, {file: i, db: dbItem});
                    }
                    return hasChanged;
                }),
                will_deactivate: currentDbItems.filter(db => 
                    !this.gradingData.items.find(i => i.item_id === db.id))
            },
            policies: {
                new: (this.gradingData.grading_policies || []).filter(p => {
                    const key = p.module_id || 'universal';
                    return !currentDbPolicies.find(db => 
                        (db.module_id === p.module_id) && (db.version === p.version)
                    );
                }),
                modified: (this.gradingData.grading_policies || []).filter(p => {
                    const dbPolicy = currentDbPolicies.find(db => 
                        (db.module_id === p.module_id) && (db.version === p.version)
                    );
                    return dbPolicy && this.hasPolicyChanged(p, dbPolicy);
                }),
                will_deactivate: currentDbPolicies.filter(db => 
                    !(this.gradingData.grading_policies || []).find(p => 
                        (p.module_id === db.module_id) && (p.version === db.version)
                    ))
            }
        };
        
        console.log('✅ Sync status analyzed - DETAILED:', {
            modules: {
                new: this.changes.modules.new.length,
                modified: this.changes.modules.modified.length,
                will_deactivate: this.changes.modules.will_deactivate.length,
                total: Object.values(this.changes.modules).flat().length
            },
            constituents: {
                new: this.changes.constituents.new.length,
                modified: this.changes.constituents.modified.length,
                will_deactivate: this.changes.constituents.will_deactivate.length,
                total: Object.values(this.changes.constituents).flat().length
            },
            items: {
                new: this.changes.items.new.length,
                modified: this.changes.items.modified.length,
                will_deactivate: this.changes.items.will_deactivate.length,
                total: Object.values(this.changes.items).flat().length
            },
            policies: {
                new: this.changes.policies.new.length,
                modified: this.changes.policies.modified.length,
                will_deactivate: this.changes.policies.will_deactivate.length,
                total: Object.values(this.changes.policies).flat().length
            }
        });
        
        // Log specific items if there are changes
        const totalChanges = Object.values(this.changes).reduce((sum, category) => 
            sum + Object.values(category).flat().length, 0);
        
        if (totalChanges > 0) {
            console.log('🚨 FOUND CHANGES - Details:');
            if (this.changes.modules.new.length > 0) console.log('🆕 New modules:', this.changes.modules.new.map(m => m.id));
            if (this.changes.modules.modified.length > 0) console.log('✏️ Modified modules:', this.changes.modules.modified.map(m => m.id));
            if (this.changes.modules.will_deactivate.length > 0) console.log('🗑️ Will deactivate modules:', this.changes.modules.will_deactivate.map(m => m.id));
            
            if (this.changes.constituents.new.length > 0) console.log('🆕 New constituents:', this.changes.constituents.new.map(c => c.id));
            if (this.changes.constituents.modified.length > 0) console.log('✏️ Modified constituents:', this.changes.constituents.modified.map(c => c.id));
            if (this.changes.constituents.will_deactivate.length > 0) console.log('🗑️ Will deactivate constituents:', this.changes.constituents.will_deactivate.map(c => c.id));
            
            if (this.changes.items.new.length > 0) console.log('🆕 New items:', this.changes.items.new.map(i => i.item_id));
            if (this.changes.items.modified.length > 0) console.log('✏️ Modified items:', this.changes.items.modified.map(i => i.item_id));
            if (this.changes.items.will_deactivate.length > 0) console.log('🗑️ Will deactivate items:', this.changes.items.will_deactivate.map(i => i.id));
            
            if (this.changes.policies.new.length > 0) console.log('🆕 New policies:', this.changes.policies.new.map(p => p.policy_name));
            if (this.changes.policies.modified.length > 0) console.log('✏️ Modified policies:', this.changes.policies.modified.map(p => p.policy_name));
            if (this.changes.policies.will_deactivate.length > 0) console.log('🗑️ Will deactivate policies:', this.changes.policies.will_deactivate.map(p => p.policy_name));
        } else {
            console.log('✅ No changes detected - database is in sync');
        }
    }
    
    hasChanged(fileItem, dbItem) {
        // Compare actual item fields that exist
        const itemFields = ['points', 'title', 'delivery_type', 'due_date', 'constituent_slug', 'is_active'];
        return itemFields.some(key => {
            const fileVal = fileItem[key];
            const dbVal = dbItem[key];
            
            // Handle numeric comparison for points
            if (key === 'points') {
                return parseFloat(fileVal || 0) !== parseFloat(dbVal || 0);
            }
            
            // Handle date comparison  
            if (key === 'due_date') {
                // Normalize date strings or handle nulls
                const fDate = fileVal ? new Date(fileVal).toISOString() : null;
                const dDate = dbVal ? new Date(dbVal).toISOString() : null;
                return fDate !== dDate;
            }
            
            // Handle boolean comparison for is_active
            if (key === 'is_active') {
                return Boolean(fileVal) !== Boolean(dbVal);
            }
            
            return fileVal !== dbVal;
        });
    }
    
    hasPolicyChanged(filePolicy, dbPolicy) {
        // Compare policy fields
        if (filePolicy.policy_name !== dbPolicy.policy_name) return true;
        if (filePolicy.version !== dbPolicy.version) return true;
        
        // Deep comparison - File uses policy_data, Database uses policy_rules
        const fileRules = filePolicy.policy_data?.grading_rules || [];
        const dbRules = dbPolicy.policy_rules?.grading_rules || [];
        
        // Normalize objects by sorting keys recursively to avoid key ordering issues
        const normalizeObject = (obj) => {
            if (Array.isArray(obj)) {
                return obj.map(normalizeObject);
            } else if (obj !== null && typeof obj === 'object') {
                return Object.keys(obj).sort().reduce((result, key) => {
                    result[key] = normalizeObject(obj[key]);
                    return result;
                }, {});
            }
            return obj;
        };
        
        const normalizedFileRules = JSON.stringify(normalizeObject(fileRules));
        const normalizedDbRules = JSON.stringify(normalizeObject(dbRules));
        
        const hasChanged = normalizedFileRules !== normalizedDbRules;
        if (hasChanged) {
            console.log('🔧 Policy changed - detailed comparison:', {
                policy_name: filePolicy.policy_name,
                file_version: filePolicy.version,
                db_version: dbPolicy.version,
                file_rules_length: fileRules.length,
                db_rules_length: dbRules.length,
                fileRules: normalizedFileRules.substring(0, 200) + '...',
                dbRules: normalizedDbRules.substring(0, 200) + '...'
            });
        } else {
            console.log('✅ Policy unchanged after normalization:', filePolicy.policy_name);
        }
        
        return hasChanged;
    }
    
    setupEventListeners() {
        document.getElementById('preview-changes-btn')?.addEventListener('click', 
            () => this.previewChanges());
        document.getElementById('sync-now-btn')?.addEventListener('click', 
            () => this.syncNow());
        document.getElementById('force-sync-btn')?.addEventListener('click', 
            () => this.forceSyncNow());
    }
    
    async renderSyncInterface() {
        await this.loadDatabaseState();
        this.detectChanges();
        
        // Render status card
        this.renderStatusCard();
        
        // Render data tree
        this.renderDataTree();
        
        // Update controls
        this.updateControls();
    }
    
    renderStatusCard() {
        const totalChanges = Object.values(this.changes).reduce((sum, category) => 
            sum + Object.values(category).flat().length, 0);
        
        const statusHtml = `
            <div class="sync-status-header">
                <h3>📊 Sync Status</h3>
                <div class="status-indicator ${totalChanges > 0 ? 'changes-detected' : 'in-sync'}">
                    ${totalChanges > 0 ? `⚠️ ${totalChanges} changes detected` : '✅ Database in sync'}
                </div>
            </div>
            <div class="status-grid">
                <div class="stat-card">
                    <span class="count">${this.gradingData.modules.length}</span>
                    <span class="label">Modules</span>
                    <span class="changes">${this.countChanges('modules')} changes</span>
                </div>
                <div class="stat-card">
                    <span class="count">${this.gradingData.constituents.length}</span>
                    <span class="label">Constituents</span>
                    <span class="changes">${this.countChanges('constituents')} changes</span>
                </div>
                <div class="stat-card">
                    <span class="count">${this.gradingData.items.length}</span>
                    <span class="label">Items</span>
                    <span class="changes">${this.countChanges('items')} changes</span>
                </div>
            </div>
        `;
        
        document.getElementById('sync-status-card').innerHTML = statusHtml;
    }
    
    renderDataTree() {
        const treeHtml = this.gradingData.modules.map(module => {
            const moduleConstituents = this.gradingData.constituents.filter(c => c.module_id === module.id);
            const moduleStatus = this.getItemStatus('modules', module.id);
            
            return `
                <div class="tree-module ${moduleStatus}">
                    <div class="tree-header" onclick="this.parentElement.classList.toggle('expanded')">
                        <span class="tree-icon">${module.icon || '📦'}</span>
                        <span class="tree-title">${module.name}</span>
                        <span class="tree-weight">(${module.weight}%)</span>
                        <span class="tree-status-badge">${this.getStatusBadge(moduleStatus)}</span>
                    </div>
                    <div class="tree-children">
                        ${moduleConstituents.map(constituent => {
                            const constituentItems = this.gradingData.items.filter(i => i.constituent_slug === constituent.slug);
                            const constituentStatus = this.getItemStatus('constituents', constituent.id);
                            
                            return `
                                <div class="tree-constituent ${constituentStatus}">
                                    <div class="tree-header" onclick="this.parentElement.classList.toggle('expanded')">
                                        <span class="tree-icon">📋</span>
                                        <span class="tree-title">${constituent.name}</span>
                                        <span class="tree-weight">(${constituent.weight}%)</span>
                                        <span class="tree-status-badge">${this.getStatusBadge(constituentStatus)}</span>
                                    </div>
                                    <div class="tree-children">
                                        ${constituentItems.map(item => {
                                            const itemStatus = this.getItemStatus('items', item.item_id);
                                            return `
                                                <div class="tree-item ${itemStatus}">
                                                    <span class="tree-icon">📝</span>
                                                    <span class="tree-title">${item.title}</span>
                                                    <span class="tree-points">(${item.points} pts)</span>
                                                    <span class="tree-source">${item.file_path}</span>
                                                    <span class="tree-status-badge">${this.getStatusBadge(itemStatus)}</span>
                                                </div>
                                            `;
                                        }).join('')}
                                    </div>
                                </div>
                            `;
                        }).join('')}
                    </div>
                </div>
            `;
        }).join('');
        
        document.getElementById('data-tree').innerHTML = treeHtml;
    }
    
    getItemStatus(type, id) {
        if (this.changes[type].new.find(item => (item.id || item.item_id) === id)) return 'new';
        if (this.changes[type].modified.find(item => (item.id || item.item_id) === id)) return 'modified';
        if (this.changes[type].will_deactivate.find(item => (item.id || item.item_id) === id)) return 'will_deactivate';
        return 'unchanged';
    }
    
    getStatusBadge(status) {
        const badges = {
            'new': '🆕 NEW',
            'modified': '📝 MODIFIED', 
            'will_deactivate': '⏸️ DEACTIVATE',
            'unchanged': ''
        };
        return badges[status] || '';
    }
    
    countChanges(type) {
        return Object.values(this.changes[type]).flat().length;
    }
    
    updateControls() {
        const totalChanges = Object.values(this.changes).reduce((sum, category) => 
            sum + Object.values(category).flat().length, 0);
        
        const syncBtn = document.getElementById('sync-now-btn');
        if (totalChanges > 0) {
            syncBtn.disabled = false;
            syncBtn.textContent = `📤 Sync ${totalChanges} Changes`;
        } else {
            syncBtn.disabled = true;
            syncBtn.textContent = '✅ Database Up to Date';
        }
    }
    
    async previewChanges() {
        console.log('👀 Previewing changes...');
        
        const preview = {
            modules: this.changes.modules,
            constituents: this.changes.constituents,
            items: this.changes.items,
            policies: this.changes.policies
        };
        
        // Show detailed preview modal or expand tree with diff view
        console.log('Changes preview:', preview);
        
        // For now, just scroll to tree and highlight changes
        document.getElementById('data-tree').scrollIntoView({ behavior: 'smooth' });
        
        // Add highlighting class
        document.querySelectorAll('.tree-module, .tree-constituent, .tree-item').forEach(el => {
            if (el.classList.contains('new') || el.classList.contains('modified')) {
                el.classList.add('highlighted');
                setTimeout(() => el.classList.remove('highlighted'), 3000);
            }
        });
    }
    
    async syncNow() {
        console.log('🚀 Starting sync process...');
        
        const progressDiv = document.getElementById('sync-progress');
        const resultsDiv = document.getElementById('sync-results');
        
        progressDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        const syncBtn = document.getElementById('sync-now-btn');
        syncBtn.disabled = true;
        syncBtn.textContent = '🔄 Syncing...';
        
        try {
            let progress = 0;
            const totalSteps = 5;
            
            // Step 1: Mark all items as not current (soft deactivation)
            this.updateProgress(++progress, totalSteps, 'Deactivating removed items...');
            await this.deactivateAllItems();
            
            // Step 2: Sync modules (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing modules...');
            await this.syncModules();
            
            // Step 3: Sync constituents (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing constituents...');
            await this.syncConstituents();
            
            // Step 4: Sync items (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing items...');
            await this.syncItems();
            
            // Step 5: Sync grading policies (will be marked as active)
            this.updateProgress(++progress, totalSteps, 'Syncing grading policies...');
            await this.syncPolicies();
            
            // Complete
            this.updateProgress(totalSteps, totalSteps, 'Sync completed!');
            
            resultsDiv.innerHTML = `
                <div class="success-message">
                    <h3>✅ Sync Completed Successfully!</h3>
                    <p>Grading data synchronized. Only current items from files will be visible.</p>
                    <button onclick="window.location.reload()">🔄 Refresh Page</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
            
        } catch (error) {
            console.error('❌ Sync failed:', error);
            
            resultsDiv.innerHTML = `
                <div class="error-message">
                    <h3>❌ Sync Failed</h3>
                    <p>${error.message}</p>
                    <button onclick="this.parentElement.parentElement.style.display='none'">Close</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
            
        } finally {
            progressDiv.style.display = 'none';
            syncBtn.disabled = false;
            syncBtn.textContent = '📤 Sync to Database';
        }
    }

    async forceSyncNow() {
        if (!confirm('⚡ Force resync will mark all database items as inactive, then re-sync from current files. This ensures old items are hidden regardless of detected changes. Continue?')) {
            return;
        }

        console.log('⚡ Starting FORCE sync process...');
        
        const progressDiv = document.getElementById('sync-progress');
        const resultsDiv = document.getElementById('sync-results');
        
        progressDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        const forceBtn = document.getElementById('force-sync-btn');
        const syncBtn = document.getElementById('sync-now-btn');
        forceBtn.disabled = true;
        syncBtn.disabled = true;
        forceBtn.textContent = '⚡ Force Syncing...';
        
        try {
            let progress = 0;
            const totalSteps = 5;
            
            // Step 1: Mark all items as not current (soft deactivation)
            this.updateProgress(++progress, totalSteps, 'Force deactivating ALL database items...');
            await this.deactivateAllItems();
            
            // Step 2: Sync modules (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing modules...');
            await this.syncModules();
            
            // Step 3: Sync constituents (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing constituents...');
            await this.syncConstituents();
            
            // Step 4: Sync items (will be marked as current)
            this.updateProgress(++progress, totalSteps, 'Syncing items...');
            await this.syncItems();
            
            // Step 5: Sync grading policies (will be marked as active)
            this.updateProgress(++progress, totalSteps, 'Syncing grading policies...');
            await this.syncPolicies();
            
            // Complete
            this.updateProgress(totalSteps, totalSteps, 'Force sync completed!');
            
            resultsDiv.innerHTML = `
                <div class="success-message">
                    <h3>⚡ Force Sync Completed Successfully!</h3>
                    <p>Full resync completed. All old items are now hidden, only current items from files will be visible.</p>
                    <button onclick="window.location.reload()">🔄 Refresh Page</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
            
        } catch (error) {
            console.error('❌ Force sync failed:', error);
            
            resultsDiv.innerHTML = `
                <div class="error-message">
                    <h3>❌ Force Sync Failed</h3>
                    <p>${error.message}</p>
                    <button onclick="this.parentElement.parentElement.style.display='none'">Close</button>
                </div>
            `;
            resultsDiv.style.display = 'block';
            
        } finally {
            progressDiv.style.display = 'none';
            forceBtn.disabled = false;
            syncBtn.disabled = false;
            forceBtn.textContent = '⚡ Force Full Resync';
        }
    }
    
    updateProgress(current, total, message) {
        const percentage = (current / total) * 100;
        document.getElementById('progress-fill').style.width = `${percentage}%`;
        document.getElementById('progress-text').textContent = message;
    }
    
    async deactivateAllItems() {
        // Mark all existing records as not current (soft deactivation)
        const [modulesResult, constituentsResult, itemsResult, policiesResult] = await Promise.all([
            this.supabase
                .from('modules')
                .update({ is_current: false })
                .eq('class_id', this.classId),
            this.supabase
                .from('constituents')
                .update({ is_current: false })
                .eq('class_id', this.classId),
            this.supabase
                .from('items')
                .update({ is_current: false })
                .eq('class_id', this.classId),
            this.supabase
                .from('grading_policies')
                .update({ is_active: false })
                .eq('class_id', this.classId)
        ]);
        
        if (modulesResult.error) {
            throw new Error(`Failed to deactivate modules: ${modulesResult.error.message}`);
        }
        if (constituentsResult.error) {
            throw new Error(`Failed to deactivate constituents: ${constituentsResult.error.message}`);
        }
        if (itemsResult.error) {
            throw new Error(`Failed to deactivate items: ${itemsResult.error.message}`);
        }
        if (policiesResult.error) {
            throw new Error(`Failed to deactivate policies: ${policiesResult.error.message}`);
        }
        
        console.log('✅ All items and policies marked as not current');
    }
    
    async syncModules() {
        // Sync ALL modules from files (not just changes) and mark as current
        const modulesToSync = this.gradingData.modules.map(m => ({ 
            ...m, 
            class_id: this.classId,
            is_current: true
        }));
        
        if (modulesToSync.length === 0) {
            return; // No modules to sync
        }
        
        const { error } = await this.supabase
            .from('modules')
            .upsert(modulesToSync, { onConflict: 'id' });
        
        if (error) {
            throw new Error(`Failed to sync modules: ${error.message}`);
        }
        
        console.log(`✅ Synced ${modulesToSync.length} modules`);
    }
    
    async syncConstituents() {
        // Sync ALL constituents from files (not just changes) and mark as current
        const constituentsToSync = this.gradingData.constituents.map(c => ({ 
            ...c, 
            class_id: this.classId,
            is_current: true
        }));
        
        if (constituentsToSync.length === 0) {
            return; // No constituents to sync
        }
        
        // Use upsert with onConflict to handle slug uniqueness
        const { error } = await this.supabase
            .from('constituents')
            .upsert(constituentsToSync, { onConflict: 'slug' });
        
        if (error) {
            throw new Error(`Failed to sync constituents: ${error.message}`);
        }
        
        console.log(`✅ Synced ${constituentsToSync.length} constituents`);
    }
    
    async syncItems() {
        console.log('📝 Starting items sync process...');
        console.log('🔍 Raw items from local data:', this.gradingData.items);
        console.log('🔍 Class ID being used:', this.classId);
        
        // Sync ALL items from files (not just changes) and mark as current
        const itemsToSync = this.gradingData.items.map(i => ({
            id: i.item_id,
            constituent_slug: i.constituent_slug,
            title: i.title,
            points: i.points,
            delivery_type: i.delivery_type,
            instructions: i.instructions,
            due_date: i.due_date,
            is_active: i.is_active !== undefined ? i.is_active : true, // Respect is_active from JSON
            is_current: true,
            class_id: this.classId
        }));
        
        console.log('📤 Formatted items for Supabase upsert:', itemsToSync);
        
        // Specifically highlight the GitHub OAuth item
        const githubOAuthItem = itemsToSync.find(item => item.id === 'github_oauth_setup');
        if (githubOAuthItem) {
            console.log('🎯 FOUND GitHub OAuth item to sync:', githubOAuthItem);
        } else {
            console.log('⚠️ GitHub OAuth item NOT FOUND in items to sync');
        }
        
        if (itemsToSync.length === 0) {
            console.log('⚠️ No items to sync - items array is empty');
            return; // No items to sync
        }
        
        // First, let's check what's currently in the database for this class
        console.log('🔍 Querying existing items with class_id:', this.classId);
        const { data: existingItems, error: queryError } = await this.supabase
            .from('items')
            .select('*')
            .eq('class_id', this.classId);
            
        if (queryError) {
            console.error('❌ Error querying existing items:', queryError);
        } else {
            console.log('📋 Existing items in database:', existingItems);
        }
        
        // Now perform the upsert with detailed error handling
        const { data, error } = await this.supabase
            .from('items')
            .upsert(itemsToSync, { 
                onConflict: 'id',
                returning: 'representation' 
            });
        
        if (error) {
            console.error('❌ Item sync error details:', {
                message: error.message,
                details: error.details,
                hint: error.hint,
                code: error.code
            });
            console.error('❌ Items that failed to sync:', itemsToSync);
            throw new Error(`Failed to sync items: ${error.message} (${error.code})`);
        }
        
        console.log('✅ Items synced successfully:', data);
        console.log(`✅ Synced ${itemsToSync.length} items to database`);
        
        // Verify the sync by querying again
        const { data: verifyItems, error: verifyError } = await this.supabase
            .from('items')
            .select('*')
            .eq('class_id', this.classId)
            .eq('is_current', true);
            
        if (verifyError) {
            console.error('❌ Error verifying synced items:', verifyError);
        } else {
            console.log('🔍 Verification - items now in database:', verifyItems);
        }
    }
    
    async syncPolicies() {
        // Sync ALL policies from files (not just changes) and mark as active
        if (!this.gradingData.grading_policies || this.gradingData.grading_policies.length === 0) {
            console.log('📋 No grading policies to sync');
            return;
        }

        const policiesToSync = this.gradingData.grading_policies.map(p => {
            // Transform the policy data structure
            const policy_rules = {
                grading_rules: p.policy_data.grading_rules || [],
                policy_settings: p.policy_data.policy_settings || {},
                metadata: p.policy_data.policy_metadata || {}
            };

            return {
                module_id: p.module_id, // null for universal policies
                class_id: this.classId,
                policy_name: p.policy_name,
                version: p.version,
                policy_rules: policy_rules,
                description: p.policy_data.policy_metadata?.description || null,
                is_active: true
            };
        });

        console.log('📋 Policies to sync:', policiesToSync);

        const { error } = await this.supabase
            .from('grading_policies')
            .upsert(policiesToSync, { 
                onConflict: 'module_id,class_id,version',
                ignoreDuplicates: false 
            });

        if (error) {
            console.error('❌ Error syncing policies:', error);
            throw new Error(`Failed to sync grading policies: ${error.message}`);
        }

        console.log(`✅ Synced ${policiesToSync.length} grading policies`);
    }
    
    showError(message) {
        const errorDiv = document.getElementById('error-display');
        errorDiv.innerHTML = `
            <div class="error-content">
                <h3>❌ Error</h3>
                <p>${message}</p>
                <button onclick="window.location.href='../dashboard/'">← Back to Dashboard</button>
            </div>
        `;
        errorDiv.style.display = 'block';
        
        // Hide other content
        document.getElementById('auth-verification').style.display = 'none';
        document.getElementById('sync-content').style.display = 'none';
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', () => {
    if (document.getElementById('sync-app')) {
        new GradingSyncManager();
    }
});