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
                // Show more results in current dropdown instead of navigating away
                showExpandedResults(query);
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
    
    // Cache for search results
    let cachedResults = null;
    let cachedQuery = null;
    
    // Perform Hugo-powered content search
    async function performSearch(query) {
        const results = await searchContent(query);
        cachedResults = results;
        cachedQuery = query;
        displaySearchResults(results, query);
    }
    
    // Show expanded results in dropdown
    async function showExpandedResults(query) {
        if (cachedResults && cachedQuery === query) {
            displaySearchResults(cachedResults, query, true);
        } else {
            const results = await searchContent(query);
            cachedResults = results;
            cachedQuery = query;
            displaySearchResults(results, query, true);
        }
    }
    
    // Make showExpandedResults globally available for onclick
    window.showExpandedResults = showExpandedResults;
    
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
                const sectionNumber = getSectionNumber(page);
                const chapterTitle = getChapterTitle(page);
                
                results.push({
                    title: page.title,
                    preview: preview,
                    url: page.url,
                    section: page.section,
                    type: page.type,
                    sectionNumber: sectionNumber,
                    chapterTitle: chapterTitle,
                    score: score
                });
            }
        });
        
        // Sort by relevance 
        results.sort((a, b) => b.score - a.score);
        return results; // Return all results, limit applied in display function
    }
    
    // Parse section numbering from page data
    function getSectionNumber(page) {
        // Extract numbers from chapter and filename
        const chapterMatch = page.chapter ? page.chapter.match(/^(\d+|[A-Z])\d*_/) : null;
        const filenameMatch = page.filename ? page.filename.match(/^(\d+|[A-Z])\d*_/) : null;
        
        const chapterNum = chapterMatch ? chapterMatch[1] : '';
        const fileNum = filenameMatch ? filenameMatch[1] : '';
        
        // Create section reference
        let sectionName = '';
        switch(page.section) {
            case 'framework_tutorials':
                sectionName = 'Tutorials';
                break;
            case 'framework_documentation':
                sectionName = 'Docs';
                break;
            case 'class_notes':
                sectionName = 'Notes';
                break;
            default:
                sectionName = page.section.replace('_', ' ');
        }
        
        // Build the reference string
        if (chapterNum && fileNum) {
            return `${sectionName} ${chapterNum}.${fileNum}`;
        } else if (chapterNum) {
            return `${sectionName} ${chapterNum}`;
        } else {
            return sectionName;
        }
    }
    
    // Get chapter/section title from path
    function getChapterTitle(page) {
        if (page.chapter) {
            // Remove number prefix and convert underscores to spaces
            return page.chapter.replace(/^\d+[A-Z]?_/, '').replace(/_/g, ' ');
        }
        return '';
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
    function displaySearchResults(results, query, showAll = false) {
        clearSearchResults();
        
        if (results.length === 0) {
            return;
        }
        
        const maxResults = showAll ? Math.min(results.length, 15) : 5;
        const displayResults = results.slice(0, maxResults);
        const hasMore = results.length > maxResults;
        
        const dropdown = document.createElement('div');
        dropdown.className = 'search-dropdown';
        dropdown.innerHTML = `
            <div class="search-dropdown-header">
                <span>Search results for "${query}" ${showAll ? `(${results.length} total)` : ''}</span>
                ${!showAll && hasMore ? `<button class="view-all" onclick="showExpandedResults('${query.replace(/'/g, "\\'")}')">Show all ${results.length}</button>` : ''}
            </div>
            <div class="search-dropdown-results">
                ${displayResults.map(result => `
                    <div class="search-result-item" data-url="${result.url}">
                        <div class="search-result-header">
                            <div class="search-result-title">${result.title}</div>
                            <div class="search-result-number">${result.sectionNumber}</div>
                        </div>
                        <div class="search-result-meta">
                            ${result.chapterTitle ? `${result.chapterTitle} • ` : ''}${result.type}
                        </div>
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