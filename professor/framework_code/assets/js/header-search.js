/**
 * Header Search Functionality
 * Provides basic content search capabilities in the header
 */

(function() {
    'use strict';
    
    let searchInput;
    let searchClear;
    let searchResults = [];
    
    // Initialize search functionality when DOM is ready
    function initSearch() {
        searchInput = document.getElementById('headerSearch');
        searchClear = document.getElementById('searchClear');
        
        if (!searchInput || !searchClear) {
            console.log('Header search elements not found');
            return;
        }
        
        // Set up event listeners
        searchInput.addEventListener('input', handleSearchInput);
        searchInput.addEventListener('keydown', handleSearchKeydown);
        searchClear.addEventListener('click', clearSearch);
        
        console.log('Header search initialized');
    }
    
    // Handle search input changes
    function handleSearchInput(event) {
        const query = event.target.value.trim();
        
        if (query.length === 0) {
            clearSearchResults();
            return;
        }
        
        if (query.length < 2) {
            return; // Wait for at least 2 characters
        }
        
        performSearch(query);
    }
    
    // Handle keyboard navigation in search
    function handleSearchKeydown(event) {
        if (event.key === 'Escape') {
            clearSearch();
        }
        
        if (event.key === 'Enter') {
            event.preventDefault();
            const query = event.target.value.trim();
            if (query) {
                // Navigate to first result or perform site-wide search
                window.location.href = `/search?q=${encodeURIComponent(query)}`;
            }
        }
    }
    
    // Clear search input and results
    function clearSearch() {
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
            clearSearchResults();
        }
    }
    
    // Clear search results
    function clearSearchResults() {
        // Remove any existing search results dropdown
        const existingDropdown = document.querySelector('.search-dropdown');
        if (existingDropdown) {
            existingDropdown.remove();
        }
    }
    
    // Perform basic content search
    function performSearch(query) {
        const results = searchContent(query);
        displaySearchResults(results, query);
    }
    
    // Simple content search function
    function searchContent(query) {
        const results = [];
        const lowercaseQuery = query.toLowerCase();
        
        // Search in page content
        const contentElements = document.querySelectorAll('h1, h2, h3, h4, h5, h6, p, .lesson-content, .python-output');
        
        contentElements.forEach((element, index) => {
            const text = element.textContent || element.innerText;
            if (text && text.toLowerCase().includes(lowercaseQuery)) {
                const preview = getTextPreview(text, lowercaseQuery, 60);
                results.push({
                    title: getElementTitle(element),
                    preview: preview,
                    element: element,
                    score: calculateRelevance(text, lowercaseQuery)
                });
            }
        });
        
        // Sort by relevance
        results.sort((a, b) => b.score - a.score);
        
        // Return top 5 results
        return results.slice(0, 5);
    }
    
    // Get a preview of text around the search term
    function getTextPreview(text, query, maxLength) {
        const index = text.toLowerCase().indexOf(query.toLowerCase());
        if (index === -1) return text.substring(0, maxLength) + '...';
        
        const start = Math.max(0, index - 20);
        const end = Math.min(text.length, index + query.length + 40);
        
        let preview = text.substring(start, end);
        if (start > 0) preview = '...' + preview;
        if (end < text.length) preview = preview + '...';
        
        // Highlight the search term
        const regex = new RegExp(`(${query})`, 'gi');
        preview = preview.replace(regex, '<mark>$1</mark>');
        
        return preview;
    }
    
    // Get title for an element (find nearest heading)
    function getElementTitle(element) {
        // If element itself is a heading, use it
        if (/^H[1-6]$/i.test(element.tagName)) {
            return element.textContent.substring(0, 50);
        }
        
        // Look for previous heading
        let current = element;
        while (current && current.previousElementSibling) {
            current = current.previousElementSibling;
            if (/^H[1-6]$/i.test(current.tagName)) {
                return current.textContent.substring(0, 50);
            }
        }
        
        // Look for parent heading
        current = element.parentElement;
        while (current) {
            const heading = current.querySelector('h1, h2, h3, h4, h5, h6');
            if (heading) {
                return heading.textContent.substring(0, 50);
            }
            current = current.parentElement;
        }
        
        return 'Content';
    }
    
    // Calculate search relevance score
    function calculateRelevance(text, query) {
        const lowercaseText = text.toLowerCase();
        const lowercaseQuery = query.toLowerCase();
        
        let score = 0;
        
        // Exact match bonus
        if (lowercaseText.includes(lowercaseQuery)) {
            score += 10;
        }
        
        // Word boundary match bonus
        const wordBoundaryRegex = new RegExp(`\\b${query}\\b`, 'gi');
        const wordMatches = lowercaseText.match(wordBoundaryRegex);
        if (wordMatches) {
            score += wordMatches.length * 5;
        }
        
        // Heading bonus
        if (text.length < 100) {
            score += 3;
        }
        
        return score;
    }
    
    // Display search results dropdown
    function displaySearchResults(results, query) {
        clearSearchResults();
        
        if (results.length === 0) {
            return;
        }
        
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown';
        dropdown.innerHTML = `
            <div class="search-dropdown-header">
                <span>Search results for "${query}"</span>
                <a href="/search?q=${encodeURIComponent(query)}" class="view-all">View all</a>
            </div>
            <div class="search-dropdown-results">
                ${results.map(result => `
                    <div class="search-result-item" data-element-index="${Array.from(document.querySelectorAll('*')).indexOf(result.element)}">
                        <div class="search-result-title">${result.title}</div>
                        <div class="search-result-preview">${result.preview}</div>
                    </div>
                `).join('')}
            </div>
        `;
        
        // Position dropdown
        const searchContainer = searchInput.closest('.header-search');
        searchContainer.appendChild(dropdown);
        
        // Add click handlers for results
        dropdown.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', () => {
                const elementIndex = parseInt(item.getAttribute('data-element-index'));
                const element = document.querySelectorAll('*')[elementIndex];
                if (element) {
                    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    clearSearch();
                }
            });
        });
        
        // Close dropdown when clicking outside
        setTimeout(() => {
            document.addEventListener('click', function closeDropdown(event) {
                if (!searchContainer.contains(event.target)) {
                    clearSearchResults();
                    document.removeEventListener('click', closeDropdown);
                }
            });
        }, 100);
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSearch);
    } else {
        initSearch();
    }
    
})();