/**
 * Math Rendering System - Framework Module
 * Handles LaTeX formula rendering throughout the site using KaTeX
 * Extracted from baseof.html for better modularity
 */

// KaTeX Auto-Render Initialization - Production Version
document.addEventListener("DOMContentLoaded", function() {
    if (typeof renderMathInElement !== 'undefined') {
        renderMathInElement(document.body, {
            delimiters: [
                {left: '$$', right: '$$', display: true},
                {left: '$', right: '$', display: false},
                {left: '\\(', right: '\\)', display: false},
                {left: '\\[', right: '\\]', display: true}
            ],
            throwOnError: false,
            strict: false,
            trust: false,
            macros: {
                "\\f": "#1f(#2)"
            }
        });
    }
}); 