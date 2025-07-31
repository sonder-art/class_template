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
                // Navigate to dedicated search page
                window.location.href = `/search/?q=${encodeURIComponent(query)}`;
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
    
    // Perform Hugo-powered content search
    async function performSearch(query) {
        const results = await searchContent(query);
        displaySearchResults(results, query);
    }
    
    // Hugo search data cache
    let searchData = null;
    
    // Load Hugo search index
    async function loadSearchData() {
        if (searchData) return searchData;
        
        try {
            const response = await fetch('/search-index.json');
            searchData = await response.json();
            console.log(`Loaded ${searchData.length} pages for search`);
            return searchData;
        } catch (error) {
            console.error('Failed to load search index:', error);
            return [];
        }
    }
    
    // Hugo-powered content search function
    async function searchContent(query) {
        await loadSearchData();
        
        if (!searchData || searchData.length === 0) {
            return [];
        }
        
        const results = [];
        const lowercaseQuery = query.toLowerCase();
        const queryWords = lowercaseQuery.split(' ').filter(word => word.length > 1);
        
        searchData.forEach(page => {
            let score = 0;
            const title = page.title.toLowerCase();
            const content = page.content.toLowerCase();
            const summary = page.summary.toLowerCase();
            
            // Score calculation
            queryWords.forEach(word => {
                // Title matches get high priority
                if (title.includes(word)) {
                    score += 100;
                }
                
                // Summary matches get medium priority
                if (summary.includes(word)) {
                    score += 50;
                }
                
                // Content matches get lower priority
                const contentMatches = (content.match(new RegExp(word, 'g')) || []).length;
                score += contentMatches * 5;
            });
            
            if (score > 0) {
                const preview = getHugoTextPreview(page, query, 100);
                results.push({
                    title: page.title,
                    preview: preview,
                    url: page.url,
                    section: page.section,
                    type: page.type,
                    score: score
                });
            }
        });
        
        // Sort by relevance and return top 5
        results.sort((a, b) => b.score - a.score);
        return results.slice(0, 5);
    }
    
    // Get a preview of text from Hugo page data
    function getHugoTextPreview(page, query, maxLength) {
        const text = page.summary || page.content;
        const lowercaseText = text.toLowerCase();
        const lowercaseQuery = query.toLowerCase();
        
        const index = lowercaseText.indexOf(lowercaseQuery);
        if (index === -1) {
            // No exact match, return summary or truncated content
            return text.length > maxLength ? text.substring(0, maxLength) + '...' : text;
        }
        
        const start = Math.max(0, index - 30);
        const end = Math.min(text.length, index + query.length + 50);
        
        let preview = text.substring(start, end);
        if (start > 0) preview = '...' + preview;
        if (end < text.length) preview = preview + '...';
        
        // Highlight the search term (case-insensitive)
        const regex = new RegExp(`(${query})`, 'gi');
        preview = preview.replace(regex, '<mark>$1</mark>');
        
        return preview;
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
                <a href="/search/?q=${encodeURIComponent(query)}" class="view-all">View all</a>
            </div>
            <div class="search-dropdown-results">
                ${results.map(result => `
                    <div class="search-result-item" data-url="${result.url}">
                        <div class="search-result-title">${result.title}</div>
                        <div class="search-result-meta">${result.section.replace('_', ' ')} • ${result.type}</div>
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
                const url = item.getAttribute('data-url');
                if (url) {
                    window.location.href = url;
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