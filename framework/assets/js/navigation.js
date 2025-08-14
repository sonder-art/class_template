/**
 * Navigation System - Framework Module
 * Handles mobile navigation, sidebar toggle, and responsive navigation behavior
 * Extracted from baseof.html for better modularity and maintainability
 */



// Clean Navigation System
console.log('✅ Navigation JS loaded successfully');

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initNavigation);
} else {
    initNavigation();
}

function initNavigation() {
    console.log('🔥 Initializing navigation system');
    
    const navToggle = document.getElementById('navToggle');
    const navOverlay = document.getElementById('navOverlay');
    const siteContainer = document.body;
    const breadcrumbNav = document.getElementById('breadcrumbNav');

    if (!navToggle) {
        console.error('❌ navToggle element not found');
        return;
    }

    console.log('✅ Navigation elements found, setting up listeners');
    
    // Navigation state management - SIMPLE
    let navState = 'nav-full'; // nav-full or nav-collapsed only
    
    // Get initial state based on screen size and saved preference
    function getInitialNavState() {
        const savedState = localStorage.getItem('navState');
        const screenWidth = window.innerWidth;
        
        if (screenWidth <= 768) {
            return 'nav-collapsed'; // Always start collapsed on mobile
        } else {
            return savedState || 'nav-full'; // Default to full on desktop/tablet
        }
    }
    
    // Set navigation state
    function setNavState(state) {
        // Remove all nav state classes
        siteContainer.classList.remove('nav-full', 'nav-collapsed', 'nav-open');
        
        // Add new state
        siteContainer.classList.add(state);
        
        // On mobile, add nav-open class when showing navigation
        if (window.innerWidth <= 768 && state === 'nav-full') {
            siteContainer.classList.add('nav-open');
        }
        
        navState = state;
        
        // Manual CSS application for reliable behavior
        const sidebar = document.querySelector('.site-sidebar');
        const mainContent = document.querySelector('.site-main');
        
        if (state === 'nav-collapsed') {
            // Collapse sidebar and expand content
            sidebar.style.transform = 'translateX(-100%)';
            if (mainContent) mainContent.style.marginLeft = 'var(--space-8)'; /* Comfortable left spacing */
        } else {
            // Show sidebar and constrain content
            sidebar.style.transform = 'translateX(0)';
            if (mainContent) mainContent.style.marginLeft = 'var(--sidebar-width)';
        }
        
        // Update toggle button aria-expanded
        const isOpen = state !== 'nav-collapsed';
        navToggle.setAttribute('aria-expanded', isOpen);
        
        // Show/hide breadcrumb navigation
        if (state === 'nav-collapsed') {
            updateBreadcrumb();
            breadcrumbNav.classList.add('visible');
        } else {
            breadcrumbNav.classList.remove('visible');
        }
        
        // Show/hide overlay on mobile
        if (window.innerWidth <= 768) {
            if (state !== 'nav-collapsed') {
                navOverlay.classList.add('active');
            } else {
                navOverlay.classList.remove('active');
            }
        }
        
        // Save state (except on mobile where it's always collapsed by default)
        if (window.innerWidth > 768) {
            localStorage.setItem('navState', state);
        }
    }
    
    // Toggle navigation - SIMPLE: just full or hidden
    function toggleNavigation() {
        if (navState === 'nav-collapsed') {
            setNavState('nav-full');
        } else {
            setNavState('nav-collapsed');
        }
    }
    
    // Update breadcrumb navigation
    function updateBreadcrumb() {
        const currentPageTitle = document.title.split(' - ')[0];
        const breadcrumbCurrent = breadcrumbNav.querySelector('.breadcrumb-current');
        if (breadcrumbCurrent) {
            breadcrumbCurrent.textContent = currentPageTitle;
        }
    }
    
    // Event listeners
    navToggle.addEventListener('click', toggleNavigation);
    
    // Close navigation when clicking overlay (mobile)
    navOverlay.addEventListener('click', function() {
        if (window.innerWidth <= 768) {
            setNavState('nav-collapsed');
        }
    });
    
    // Close navigation when clicking a nav link on mobile
    document.addEventListener('click', function(e) {
        if (window.innerWidth <= 768 && e.target.matches('.nav-page, .nav-category-link')) {
            setTimeout(() => setNavState('nav-collapsed'), 150);
        }
    });
    
    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        // Ctrl/Cmd + \ to toggle navigation
        if ((e.ctrlKey || e.metaKey) && e.key === '\\') {
            e.preventDefault();
            toggleNavigation();
        }
        
        // Escape to close navigation
        if (e.key === 'Escape' && navState !== 'nav-collapsed') {
            setNavState('nav-collapsed');
        }
    });
    
    // Handle window resize
    let resizeTimeout;
    window.addEventListener('resize', function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(function() {
            const newState = getInitialNavState();
            setNavState(newState);
        }, 250);
    });
    
    // Initialize navigation state
    const initialState = getInitialNavState();
    setNavState(initialState);
    
    // Auto-collapse after inactivity (optional reading mode)
    let inactivityTimer;
    function resetInactivityTimer() {
        clearTimeout(inactivityTimer);
        if (window.innerWidth > 768 && navState === 'nav-full') {
            inactivityTimer = setTimeout(() => {
                if (document.hasFocus()) {
                    setNavState('nav-collapsed');
                }
            }, 120000); // 2 minutes of inactivity
        }
    }
    
    // Track user activity for auto-collapse (optional feature)
    ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart'].forEach(event => {
        document.addEventListener(event, resetInactivityTimer, { passive: true });
    });
    
    resetInactivityTimer();
} 