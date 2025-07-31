/**
 * Table of Contents Generator
 * Automatically generates a table of contents from page headings
 * and provides smooth scrolling navigation with active section highlighting
 */

(function() {
    'use strict';
    
    let tocNav;
    let headings = [];
    let activeLink = null;
    let scrollspyEnabled = true;
    let observer = null;
    let isManualNavigation = false;
    let scrollTimeout = null;
    let tocContainer = null;
    let isUserScrollingTOC = false;
    let tocScrollTimeout = null;
    
    // Initialize TOC when DOM is ready
    function initTOC() {
        tocNav = document.getElementById('tocNav');
        tocContainer = document.getElementById('tocSidebar');
        
        if (!tocNav || !tocContainer) {
            console.log('TOC navigation element not found');
            return;
        }
        
        generateTOC();
        
        if (headings.length > 0) {
            setupScrollspy();
            setupTOCScrollDetection();
            console.log(`Table of Contents generated with ${headings.length} headings`);
        } else {
            hideTOC();
        }
    }
    
    // Generate table of contents from page headings
    function generateTOC() {
        // Find all headings in the main content (skip h1 as it's usually the page title)
        const contentArea = document.querySelector('.main-content') || document.querySelector('.content') || document.body;
        const headingElements = contentArea.querySelectorAll('h2, h3, h4, h5, h6');
        
        if (headingElements.length === 0) {
            return;
        }
        
        // Process headings and generate IDs if needed
        headingElements.forEach((heading, index) => {
            // Create ID if it doesn't exist
            if (!heading.id) {
                heading.id = generateHeadingId(heading.textContent, index);
            }
            
            headings.push({
                element: heading,
                id: heading.id,
                text: heading.textContent.trim(),
                level: parseInt(heading.tagName.charAt(1))
            });
        });
        
        // Build TOC HTML
        const tocHTML = buildTOCHTML(headings);
        tocNav.innerHTML = tocHTML;
        
        // Add click handlers
        setupTOCLinks();
    }
    
    // Generate a clean ID from heading text
    function generateHeadingId(text, index) {
        const cleanText = text
            .toLowerCase()
            .replace(/[^\w\s-]/g, '') // Remove special characters
            .replace(/\s+/g, '-')     // Replace spaces with hyphens
            .replace(/--+/g, '-')     // Replace multiple hyphens with single
            .replace(/^-|-$/g, '');   // Remove leading/trailing hyphens
        
        return cleanText || `heading-${index}`;
    }
    
    // Build HTML for the table of contents
    function buildTOCHTML(headings) {
        let html = '<ul>';
        let currentLevel = 0;
        
        headings.forEach((heading, index) => {
            const level = heading.level;
            
            if (level > currentLevel) {
                // Opening nested lists
                for (let i = currentLevel; i < level; i++) {
                    if (i > 0) html += '<ul>';
                }
            } else if (level < currentLevel) {
                // Closing nested lists
                for (let i = currentLevel; i > level; i--) {
                    html += '</ul>';
                }
            }
            
            html += `
                <li>
                    <a href="#${heading.id}" 
                       class="toc-link toc-h${level}" 
                       data-heading-id="${heading.id}">
                        ${heading.text}
                    </a>
                </li>
            `;
            
            currentLevel = level;
        });
        
        // Close remaining lists
        for (let i = currentLevel; i > 0; i--) {
            html += '</ul>';
        }
        
        return html;
    }
    
    // Setup click handlers for TOC links
    function setupTOCLinks() {
        const tocLinks = tocNav.querySelectorAll('.toc-link');
        
        tocLinks.forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                
                const targetId = link.getAttribute('data-heading-id');
                const targetElement = document.getElementById(targetId);
                
                if (targetElement) {
                    // Set manual navigation flag
                    isManualNavigation = true;
                    
                    // Clear any pending scroll updates
                    if (scrollTimeout) {
                        clearTimeout(scrollTimeout);
                    }
                    
                    // Remove focus from the clicked link to prevent focus outline
                    link.blur();
                    
                    // Immediately update active state (forced update)
                    updateActiveLink(link, true);
                    
                    // Perform smooth scroll
                    smoothScrollToElement(targetElement);
                    
                    // Reset manual navigation flag after scroll completes and force update
                    setTimeout(() => {
                        isManualNavigation = false;
                        // Force an immediate update based on current scroll position
                        setTimeout(updateActiveFromScroll, 100);
                    }, 1000); // Reduced timeout for faster handoff
                }
            });
        });
    }
    
    // Smooth scroll to element with offset for fixed header
    function smoothScrollToElement(element) {
        const headerHeight = document.querySelector('.site-header')?.offsetHeight || 60;
        const elementTop = element.getBoundingClientRect().top + window.pageYOffset;
        const offsetTop = elementTop - headerHeight - 20; // Extra padding
        
        window.scrollTo({
            top: offsetTop,
            behavior: 'smooth'
        });
    }
    
    // Setup scrollspy to highlight active section
    function setupScrollspy() {
        const options = {
            root: null,
            rootMargin: '-80px 0px -50% 0px', // Account for header and show active section earlier
            threshold: [0, 0.1, 0.5]
        };
        
        observer = new IntersectionObserver(handleIntersection, options);
        
        headings.forEach(heading => {
            observer.observe(heading.element);
        });
        
        // Initial active state
        updateActiveFromScroll();
        
        // Fallback scroll listener for better responsiveness
        window.addEventListener('scroll', () => {
            if (!scrollspyEnabled) return;
            
            clearTimeout(scrollTimeout);
            // Use shorter delay during manual navigation for better responsiveness
            const delay = isManualNavigation ? 50 : 150;
            scrollTimeout = setTimeout(updateActiveFromScroll, delay);
        });
    }
    
    // Update the active link styling
    function updateActiveLink(newActiveLink, isForced = false) {
        // Prevent updates during manual navigation unless it's forced (from manual click) or same link
        if (isManualNavigation && !isForced && activeLink && newActiveLink !== activeLink) {
            return;
        }
        
        // Remove previous active state
        if (activeLink) {
            activeLink.classList.remove('active');
        }
        
        // Set new active state
        activeLink = newActiveLink;
        if (activeLink) {
            activeLink.classList.add('active');
            
            // Auto-scroll TOC to show active item (with delay for smooth UX)
            if (!isUserScrollingTOC && !isManualNavigation) {
                clearTimeout(tocScrollTimeout);
                tocScrollTimeout = setTimeout(() => {
                    scrollTOCToActiveItem(activeLink);
                }, 300); // Small delay to avoid jarring movement
            }
        }
    }
    
    // Handle intersection observer updates
    function handleIntersection(entries) {
        // Skip intersection updates during manual navigation
        if (isManualNavigation) return;
        
        // Find the most relevant intersecting heading (usually the first one in view)
        let topMostEntry = null;
        let topMostPosition = Infinity;
        
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const rect = entry.target.getBoundingClientRect();
                const position = Math.abs(rect.top);
                
                if (position < topMostPosition) {
                    topMostPosition = position;
                    topMostEntry = entry;
                }
            }
        });
        
        // Only update if we found a clear top-most heading and not during manual nav
        if (topMostEntry && !isManualNavigation) {
            const headingId = topMostEntry.target.id;
            const tocLink = tocNav.querySelector(`[data-heading-id="${headingId}"]`);
            if (tocLink && tocLink !== activeLink) {
                updateActiveLink(tocLink);
            }
        }
    }
    
    // Update active link based on scroll position
    function updateActiveFromScroll() {
        if (!scrollspyEnabled) return;
        
        const scrollTop = window.pageYOffset;
        const headerHeight = document.querySelector('.site-header')?.offsetHeight || 60;
        const viewportHeight = window.innerHeight;
        
        let activeHeading = null;
        let closestDistance = Infinity;
        
        // Find the heading closest to the ideal viewing position (top 1/4 of viewport)
        const idealViewPosition = headerHeight + (viewportHeight * 0.25);
        
        headings.forEach(heading => {
            const rect = heading.element.getBoundingClientRect();
            const elementTop = rect.top;
            
            // Only consider visible headings
            if (elementTop <= viewportHeight && rect.bottom >= 0) {
                const distanceFromIdeal = Math.abs(elementTop - idealViewPosition);
                
                if (distanceFromIdeal < closestDistance) {
                    closestDistance = distanceFromIdeal;
                    activeHeading = heading;
                }
            }
        });
        
        // Fallback: use the traditional approach if no heading is in ideal position
        if (!activeHeading) {
            for (let i = headings.length - 1; i >= 0; i--) {
                const heading = headings[i];
                const elementTop = heading.element.getBoundingClientRect().top + scrollTop;
                
                if (scrollTop >= elementTop - headerHeight - 100) {
                    activeHeading = heading;
                    break;
                }
            }
        }
        
        if (activeHeading) {
            const tocLink = tocNav.querySelector(`[data-heading-id="${activeHeading.id}"]`);
            if (tocLink && tocLink !== activeLink) {
                updateActiveLink(tocLink);
            }
        }
    }
    
    // Detect when user is manually scrolling the TOC
    function setupTOCScrollDetection() {
        if (!tocContainer) return;
        
        tocContainer.addEventListener('scroll', () => {
            isUserScrollingTOC = true;
            
            // Reset flag after user stops scrolling
            clearTimeout(tocScrollTimeout);
            tocScrollTimeout = setTimeout(() => {
                isUserScrollingTOC = false;
            }, 1000);
        });
    }
    
    // Auto-scroll TOC to keep active item visible
    function scrollTOCToActiveItem(activeLink) {
        if (!tocContainer || !activeLink || isUserScrollingTOC) return;
        
        const containerRect = tocContainer.getBoundingClientRect();
        const linkRect = activeLink.getBoundingClientRect();
        
        // Check if the active link is visible in the TOC container
        const linkTop = linkRect.top - containerRect.top;
        const linkBottom = linkRect.bottom - containerRect.top;
        const containerHeight = containerRect.height;
        
        // Define comfortable margins (show some context above/below)
        const topMargin = 60;  // Space from top
        const bottomMargin = 60; // Space from bottom
        
        let scrollTarget = null;
        
        // If link is above visible area
        if (linkTop < topMargin) {
            scrollTarget = tocContainer.scrollTop + linkTop - topMargin;
        }
        // If link is below visible area  
        else if (linkBottom > containerHeight - bottomMargin) {
            scrollTarget = tocContainer.scrollTop + linkBottom - containerHeight + bottomMargin;
        }
        
        // Smooth scroll to target position
        if (scrollTarget !== null) {
            tocContainer.scrollTo({
                top: scrollTarget,
                behavior: 'smooth'
            });
        }
    }
    
    // Hide TOC if no headings found
    function hideTOC() {
        const tocSidebar = document.getElementById('tocSidebar');
        if (tocSidebar) {
            tocSidebar.style.display = 'none';
        }
        
        // Adjust content wrapper to single column
        const contentWrapper = document.querySelector('.content-wrapper');
        if (contentWrapper) {
            contentWrapper.style.gridTemplateColumns = '1fr';
            contentWrapper.style.gridTemplateAreas = '"content"';
        }
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initTOC);
    } else {
        initTOC();
    }
    
})();