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
  
  // Simple search function
  function performSearch(query) {
    if (!query || query.length < 2) {
      searchResults.innerHTML = '';
      return;
    }
    
    const results = searchData.filter(page => {
      const searchText = (page.title + ' ' + page.content + ' ' + page.summary).toLowerCase();
      return searchText.includes(query.toLowerCase());
    });
    
    displayResults(results, query);
  }
  
  // Display search results
  function displayResults(results, query) {
    if (results.length === 0) {
      searchResults.innerHTML = '<p>No results found.</p>';
      return;
    }
    
    const html = results.slice(0, 10).map(page => `
      <div style="margin-bottom: 20px; padding: 15px; border: 1px solid #ddd; border-radius: 5px;">
        <h3><a href="${page.url}">${page.title}</a></h3>
        <p><strong>${page.section}</strong> • ${page.date}</p>
        <p>${page.summary || page.content.substring(0, 200) + '...'}</p>
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