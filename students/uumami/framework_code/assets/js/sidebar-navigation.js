/* Sidebar Navigation System - Framework Component
 * Provides VSCode-style persistent navigation with state management
 * 
 * Features:
 * - Persistent expansion state using localStorage
 * - Auto-expansion of current page hierarchy
 * - Click handlers for folders and chapters
 * - State synchronization
 */

document.addEventListener('DOMContentLoaded', function() {
    const STORAGE_KEY = 'vscode-nav-state';
    
    // Load saved expansion state
    function loadNavigationState() {
        try {
            const saved = localStorage.getItem(STORAGE_KEY);
            return saved ? JSON.parse(saved) : {};
        } catch (e) {
            return {};
        }
    }
    
    // Save expansion state
    function saveNavigationState(state) {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
        } catch (e) {
            // Ignore storage errors
        }
    }
    
    // Get current expansion state
    function getCurrentState() {
        const state = {};
        document.querySelectorAll('[data-target]').forEach(element => {
            const target = element.getAttribute('data-target');
            const content = document.getElementById(target);
            if (content) {
                state[target] = content.style.display === 'block';
            }
        });
        return state;
    }
    
    // Apply expansion state
    function applyNavigationState(state) {
        Object.keys(state).forEach(target => {
            const content = document.getElementById(target);
            const header = document.querySelector(`[data-target="${target}"]`);
            if (content && header) {
                const icon = header.querySelector('.folder-icon') || header.querySelector('.chapter-icon');
                if (state[target]) {
                    content.style.display = 'block';
                    if (icon) icon.textContent = '▼';
                } else {
                    content.style.display = 'none';
                    if (icon) icon.textContent = '▶';
                }
            }
        });
    }
    
    // Auto-expand hierarchy for current page
    function autoExpandCurrentHierarchy() {
        // Note: This function needs Hugo context for currentSection
        // In the HTML, this should be injected as a data attribute
        const sidebarNav = document.querySelector('.sidebar-nav');
        const currentSection = sidebarNav ? sidebarNav.getAttribute('data-current-section') : '';
        const savedState = loadNavigationState();
        
        if (currentSection) {
            // Always expand current category (parent hierarchy)
            savedState[`category-${currentSection}`] = true;
            
            // Find active file and expand its chapter (parent hierarchy)
            const activeFile = document.querySelector('.file-item.active');
            if (activeFile) {
                const chapterContent = activeFile.closest('.chapter-content');
                if (chapterContent) {
                    savedState[chapterContent.id] = true;
                }
            }
        }
        
        return savedState;
    }
    
    // Toggle expansion and save state
    function toggleExpansion(icon, targetId) {
        const content = document.getElementById(targetId);
        if (!content) return;
        
        const isExpanded = content.style.display === 'block';
        
        if (isExpanded) {
            content.style.display = 'none';
            icon.textContent = '▶';
        } else {
            content.style.display = 'block';
            icon.textContent = '▼';
        }
        
        // Save current state
        saveNavigationState(getCurrentState());
    }
    
    // Initialize file tree with persistent state
    function initializeFileTree() {
        // Load and merge saved state with auto-expanded hierarchy
        const savedState = autoExpandCurrentHierarchy();
        applyNavigationState(savedState);
        saveNavigationState(savedState);
        
        // Handle folder icons (categories)
        document.querySelectorAll('.folder-icon').forEach(icon => {
            icon.addEventListener('click', function(e) {
                e.stopPropagation();
                const header = this.parentElement;
                const targetId = header.getAttribute('data-target');
                toggleExpansion(this, targetId);
            });
        });
        
        // Handle chapter icons
        document.querySelectorAll('.chapter-icon').forEach(icon => {
            icon.addEventListener('click', function(e) {
                e.stopPropagation();
                const header = this.parentElement;
                const targetId = header.getAttribute('data-target');
                toggleExpansion(this, targetId);
            });
        });
        
        // Handle folder title clicks (navigate + auto-expand children)
        document.querySelectorAll('.folder-name-link').forEach(link => {
            link.addEventListener('click', function(e) {
                // Let the navigation happen, but first expand immediate children
                const header = this.closest('.folder-header');
                const targetId = header.getAttribute('data-target');
                const content = document.getElementById(targetId);
                const icon = header.querySelector('.folder-icon');
                
                if (content && content.style.display !== 'block') {
                    content.style.display = 'block';
                    if (icon) icon.textContent = '▼';
                    saveNavigationState(getCurrentState());
                }
            });
        });
        
        // Handle chapter title clicks (navigate + auto-expand children)
        document.querySelectorAll('.chapter-name-link').forEach(link => {
            link.addEventListener('click', function(e) {
                // Let the navigation happen, but first expand immediate children
                const header = this.closest('.chapter-header');
                const targetId = header.getAttribute('data-target');
                const content = document.getElementById(targetId);
                const icon = header.querySelector('.chapter-icon');
                
                if (content && content.style.display !== 'block') {
                    content.style.display = 'block';
                    if (icon) icon.textContent = '▼';
                    saveNavigationState(getCurrentState());
                }
            });
        });
    }
    
    initializeFileTree();
}); 