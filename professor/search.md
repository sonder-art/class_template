---
title: "Search"
type: "search"
---

# Search

<div id="search-container">
  <input type="search" id="search-input" placeholder="Search content..." aria-label="Search">
  <div id="search-results"></div>
</div>

<script>
(function() {
  let searchData = null;
  let searchInput = document.getElementById('search-input');
  let searchResults = document.getElementById('search-results');
  
  // Load search data when first needed
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
  
  // Parse section numbering from page data
  function getSectionNumber(page) {
    const chapterMatch = page.chapter ? page.chapter.match(/^(\d+|[A-Z])\d*_/) : null;
    const filenameMatch = page.filename ? page.filename.match(/^(\d+|[A-Z])\d*_/) : null;
    
    const chapterNum = chapterMatch ? chapterMatch[1] : '';
    const fileNum = filenameMatch ? filenameMatch[1] : '';
    
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
    
    if (chapterNum && fileNum) {
      return `${sectionName} ${chapterNum}.${fileNum}`;
    } else if (chapterNum) {
      return `${sectionName} ${chapterNum}`;
    } else {
      return sectionName;
    }
  }
  
  // Get chapter title from path
  function getChapterTitle(page) {
    if (page.chapter) {
      return page.chapter.replace(/^\d+[A-Z]?_/, '').replace(/_/g, ' ');
    }
    return '';
  }
  
  // Enhanced search function with scoring
  function performSearch(query) {
    if (!query || query.length < 2) {
      searchResults.innerHTML = '';
      return;
    }
    
    const results = [];
    const lowercaseQuery = query.toLowerCase();
    const queryWords = lowercaseQuery.split(' ').filter(word => word.length > 1);
    
    searchData.forEach(page => {
      let score = 0;
      const title = page.title.toLowerCase();
      const content = page.content.toLowerCase();
      const summary = page.summary.toLowerCase();
      
      queryWords.forEach(word => {
        if (title.includes(word)) {
          score += 100;
        }
        if (summary.includes(word)) {
          score += 50;
        }
        const contentMatches = (content.match(new RegExp(word, 'g')) || []).length;
        score += contentMatches * 5;
      });
      
      if (score > 0) {
        results.push({
          ...page,
          score: score,
          sectionNumber: getSectionNumber(page),
          chapterTitle: getChapterTitle(page)
        });
      }
    });
    
    // Sort by relevance
    results.sort((a, b) => b.score - a.score);
    
    displayResults(results, query);
  }
  
  // Display search results
  function displayResults(results, query) {
    if (results.length === 0) {
      searchResults.innerHTML = '<p>No results found.</p>';
      return;
    }
    
    const html = results.slice(0, 10).map(page => `
      <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 8px; background: #f9f9f9;">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; gap: 12px;">
          <h3 style="margin: 0; flex: 1;"><a href="${page.url}" style="color: #007cba; text-decoration: none;">${page.title}</a></h3>
          <span style="background: #e6f3ff; color: #007cba; padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: 600; white-space: nowrap; font-family: monospace;">${page.sectionNumber}</span>
        </div>
        <p style="margin: 0 0 8px 0; font-size: 13px; color: #666; font-style: italic;">
          ${page.chapterTitle ? `${page.chapterTitle} • ` : ''}${page.type} • ${page.date}
        </p>
        <p style="margin: 0; color: #555; font-size: 14px; line-height: 1.4;">
          ${page.summary || page.content.substring(0, 200) + '...'}
        </p>
      </div>
    `).join('');
    
    searchResults.innerHTML = `<h3>Found ${results.length} results:</h3>` + html;
  }
  
  // Check for URL query parameter
  const urlParams = new URLSearchParams(window.location.search);
  const initialQuery = urlParams.get('q');
  
  if (initialQuery) {
    searchInput.value = initialQuery;
    loadSearchData().then(() => performSearch(initialQuery));
  }
  
  // Search on input
  searchInput.addEventListener('input', async (e) => {
    await loadSearchData();
    performSearch(e.target.value);
  });
  
  // Load data on first focus for better performance
  searchInput.addEventListener('focus', loadSearchData, { once: true });
})();
</script>

<style>
#search-container {
  max-width: 800px;
  margin: 0 auto;
}

#search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #ddd;
  border-radius: 8px;
  margin-bottom: 20px;
}

#search-input:focus {
  outline: none;
  border-color: #007cba;
}

#search-results h3 a {
  color: #007cba;
  text-decoration: none;
}

#search-results h3 a:hover {
  text-decoration: underline;
}
</style>