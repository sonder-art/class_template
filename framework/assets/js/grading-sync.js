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
            // Load grading data from generated JSON files
            const [modulesResponse, constituentsResponse, itemsResponse, classResponse] = await Promise.all([
                fetch('/class_template/data/modules.json').catch(() => ({ ok: false })),
                fetch('/class_template/data/constituents.json').catch(() => ({ ok: false })),
                fetch('/class_template/data/items.json'),
                fetch('/class_template/data/class_context.json')
            ]);
            
            // Parse responses
            const modules = modulesResponse.ok ? await modulesResponse.json() : { modules: [] };
            const constituents = constituentsResponse.ok ? await constituentsResponse.json() : { constituents: [] };
            const items = await itemsResponse.json();
            const classContext = await classResponse.json();
            
            // Combine all data
            this.gradingData = {
                modules: modules.modules || [],
                constituents: constituents.constituents || [],
                items: items.items || [],
                metadata: {
                    generated_at: items.generated_at,
                    total_items: items.total_items,
                    class_id: this.classId
                }
            };
            
            console.log('✅ Grading data loaded:', {
                modules: this.gradingData.modules.length,
                constituents: this.gradingData.constituents.length,
                items: this.gradingData.items.length
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
            throw new Error(`Failed to load grading data: ${error.message}`);
        }
    }
    
    async loadDatabaseState() {
        console.log('📊 Loading current database state...');
        
        const [modules, constituents, items] = await Promise.all([
            this.supabase.from('modules').select('*').eq('class_id', this.classId),
            this.supabase.from('constituents').select('*').eq('class_id', this.classId), 
            this.supabase.from('items').select('*').eq('class_id', this.classId)
        ]);
        
        this.databaseState = {
            modules: modules.data || [],
            constituents: constituents.data || [],
            items: items.data || []
        };
        
        console.log('✅ Database state loaded:', {
            modules: this.databaseState.modules.length,
            constituents: this.databaseState.constituents.length,
            items: this.databaseState.items.length
        });
    }
    
    detectChanges() {
        console.log('🔍 Detecting sync status...');
        
        // Compare what's in files vs what's current in database
        const currentDbModules = this.databaseState.modules.filter(m => m.is_current);
        const currentDbConstituents = this.databaseState.constituents.filter(c => c.is_current);
        const currentDbItems = this.databaseState.items.filter(i => i.is_current);
        
        this.changes = {
            modules: {
                new: this.gradingData.modules.filter(m => 
                    !currentDbModules.find(db => db.id === m.id)),
                modified: this.gradingData.modules.filter(m => {
                    const dbModule = currentDbModules.find(db => db.id === m.id);
                    return dbModule && this.hasChanged(m, dbModule);
                }),
                will_deactivate: currentDbModules.filter(db => 
                    !this.gradingData.modules.find(m => m.id === db.id))
            },
            constituents: {
                new: this.gradingData.constituents.filter(c => 
                    !currentDbConstituents.find(db => db.id === c.id)),
                modified: this.gradingData.constituents.filter(c => {
                    const dbConstituent = currentDbConstituents.find(db => db.id === c.id);
                    return dbConstituent && this.hasChanged(c, dbConstituent);
                }),
                will_deactivate: currentDbConstituents.filter(db => 
                    !this.gradingData.constituents.find(c => c.id === db.id))
            },
            items: {
                new: this.gradingData.items.filter(i => 
                    !currentDbItems.find(db => db.id === i.item_id)),
                modified: this.gradingData.items.filter(i => {
                    const dbItem = currentDbItems.find(db => db.id === i.item_id);
                    return dbItem && this.hasChanged(i, dbItem);
                }),
                will_deactivate: currentDbItems.filter(db => 
                    !this.gradingData.items.find(i => i.item_id === db.id))
            }
        };
        
        console.log('✅ Sync status analyzed:', {
            modules: Object.values(this.changes.modules).flat().length,
            constituents: Object.values(this.changes.constituents).flat().length,
            items: Object.values(this.changes.items).flat().length
        });
    }
    
    hasChanged(fileItem, dbItem) {
        // Compare actual item fields that exist
        const itemFields = ['points', 'title', 'delivery_type', 'due_date', 'constituent_slug'];
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
            
            return fileVal !== dbVal;
        });
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
            items: this.changes.items
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
            const totalSteps = 4;
            
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
            const totalSteps = 4;
            
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
        const [modulesResult, constituentsResult, itemsResult] = await Promise.all([
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
        
        console.log('✅ All items marked as not current');
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
            is_active: true,
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