/**
 * Floating Copy Button System - Framework Module
 * Provides page-wide content copying with formatting preservation
 * Extracted from baseof.html for better modularity and maintainability
 */

// Initialize floating copy button when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    const floatingCopyBtn = document.getElementById('floatingCopyBtn');
    if (floatingCopyBtn) {
        floatingCopyBtn.addEventListener('click', copyEntirePageContent);
    }
});

// === PAGE CONTENT COPYING SYSTEM ===
function copyEntirePageContent() {
    const button = document.getElementById('floatingCopyBtn');
    
    try {
        // Get the main content area
        const mainContent = document.querySelector('main.site-main') || 
                           document.querySelector('.content') || 
                           document.querySelector('main') ||
                           document.querySelector('#content');
        
        if (!mainContent) {
            console.error('Main content area not found');
            return;
        }
        
        // Convert content to formatted text
        const formattedText = htmlToFormattedText(mainContent);
        
        // Copy to clipboard
        navigator.clipboard.writeText(formattedText).then(() => {
            console.log('✅ Page content copied to clipboard');
            
            // Visual feedback
            button.classList.add('copied');
            button.innerHTML = '✅';
            
            setTimeout(() => {
                button.classList.remove('copied');
                button.innerHTML = '📝';
            }, 2000);
            
        }).catch(err => {
            console.error('Failed to copy page content:', err);
            button.innerHTML = '❌';
            setTimeout(() => {
                button.innerHTML = '📝';
            }, 2000);
        });
        
    } catch (error) {
        console.error('Error copying page content:', error);
    }
}

// Enhanced HTML to formatted text converter for entire pages
function htmlToFormattedText(element) {
    let result = '';
    
    function processNode(node, indent = '') {
        if (node.nodeType === Node.TEXT_NODE) {
            const text = node.textContent.trim();
            if (text) {
                result += text;
            }
            return;
        }
        
        if (node.nodeType !== Node.ELEMENT_NODE) return;
        
        const tagName = node.tagName.toLowerCase();
        
        // Skip navigation, headers, footers, and ALL UI elements
        if (tagName === 'nav' || tagName === 'header' || tagName === 'footer' || tagName === 'button' ||
            node.classList.contains('nav-toggle-btn') ||
            node.classList.contains('site-header') ||
            node.classList.contains('site-sidebar') ||
            node.classList.contains('site-footer') ||
            node.classList.contains('floating-copy-button') ||
            node.classList.contains('copy-code-button') ||
            node.classList.contains('copy-output-button') ||
            node.classList.contains('copy-explanation-button') ||
            node.classList.contains('copy-output-button') ||
            node.classList.contains('run-button') ||
            node.classList.contains('clear-button') ||
            node.classList.contains('python-editor-header') ||
            node.classList.contains('editor-controls') ||
            node.classList.contains('editor-title') ||
            node.classList.contains('editor-badge') ||
            node.classList.contains('explanation-header') ||
            node.classList.contains('output-placeholder')) {
            return;
        }
        
        switch (tagName) {
            case 'h1':
                result += '\n# ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'h2':
                result += '\n## ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'h3':
                result += '\n### ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'h4':
                result += '\n#### ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'h5':
                result += '\n##### ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'h6':
                result += '\n###### ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'p':
                result += '\n';
                processChildren(node);
                result += '\n';
                break;
            case 'strong':
            case 'b':
                result += '**';
                processChildren(node);
                result += '**';
                break;
            case 'em':
            case 'i':
                result += '*';
                processChildren(node);
                result += '*';
                break;
            case 'code':
                if (node.parentNode && node.parentNode.tagName.toLowerCase() === 'pre') {
                    // Block code
                    result += '\n```\n';
                    processChildren(node);
                    result += '\n```\n';
                } else {
                    // Inline code
                    result += '`';
                    processChildren(node);
                    result += '`';
                }
                break;
            case 'pre':
                result += '\n';
                processChildren(node);
                result += '\n';
                break;
            case 'ul':
                result += '\n';
                processChildren(node, indent);
                result += '\n';
                break;
            case 'ol':
                result += '\n';
                let counter = 1;
                for (const child of node.children) {
                    if (child.tagName.toLowerCase() === 'li') {
                        result += `${indent}${counter}. `;
                        processChildren(child, indent + '   ');
                        result += '\n';
                        counter++;
                    }
                }
                result += '\n';
                break;
            case 'li':
                if (node.parentNode.tagName.toLowerCase() === 'ul') {
                    result += `${indent}- `;
                    processChildren(node, indent + '  ');
                    result += '\n';
                }
                break;
            case 'br':
                result += '\n';
                break;
            case 'hr':
                result += '\n---\n\n';
                break;
            case 'blockquote':
                result += '\n> ';
                processChildren(node);
                result += '\n\n';
                break;
            case 'div':
                // Handle special components for pure markdown extraction
                if (node.classList.contains('katex-display')) {
                    result += '\n$$' + extractMathFromKaTeX(node) + '$$\n';
                } else if (node.classList.contains('python-lesson-container')) {
                    // Extract lesson content without UI wrappers
                    processChildren(node, indent);
                } else if (node.classList.contains('python-editor-wrapper')) {
                    // Extract code as it would appear in markdown
                    const codeEditor = node.querySelector('.code-editor');
                    if (codeEditor) {
                        const code = codeEditor.innerText || codeEditor.textContent;
                        if (code && code.trim()) {
                            result += '\n```python\n';
                            result += code.trim();
                            result += '\n```\n\n';
                        }
                    }
                    
                    // Add output if present (as a simple code block)
                    const output = node.querySelector('.python-editor-output .success, .python-editor-output .error');
                    if (output && output.textContent.trim() && 
                        !output.textContent.includes('Output will appear') &&
                        !output.textContent.includes('Copy Output')) {
                        result += '```\n';
                        result += output.textContent.trim();
                        result += '\n```\n\n';
                    }
                } else if (node.classList.contains('lesson-explanation')) {
                    // Extract explanation content directly
                    const explanationContent = node.querySelector('.explanation-content');
                    if (explanationContent) {
                        processChildren(explanationContent, indent);
                    } else {
                        processChildren(node, indent);
                    }
                } else if (node.classList.contains('explanation-header')) {
                    // Skip the copy button header entirely
                    return;
                } else if (node.classList.contains('python-editor-output') && 
                           node.querySelector('.output-placeholder')) {
                    // Skip placeholder output messages
                    return;
                } else {
                    processChildren(node, indent);
                }
                break;
            case 'span':
                if (node.classList.contains('katex')) {
                    result += '$' + extractMathFromKaTeX(node) + '$';
                } else {
                    processChildren(node, indent);
                }
                break;
            default:
                processChildren(node, indent);
                break;
        }
    }
    
    function processChildren(node, indent = '') {
        for (const child of node.childNodes) {
            processNode(child, indent);
        }
    }
    
    function extractMathFromKaTeX(katexElement) {
        // Try to get original LaTeX from data attribute or annotation
        const annotation = katexElement.querySelector('annotation[encoding="application/x-tex"]');
        if (annotation) {
            return annotation.textContent;
        }
        
        // Fallback: try to get from title attribute or data-original
        if (katexElement.title) {
            return katexElement.title;
        }
        
        // Last resort: return the text content but clean it up
        let mathText = katexElement.textContent.trim();
        mathText = mathText.replace(/\s+/g, ' ');
        return mathText;
    }
    
    processNode(element);
    
    // Clean up extra newlines and spaces
    result = result
        .replace(/\n\s*\n\s*\n/g, '\n\n')  // Remove triple+ newlines
        .replace(/^\s+|\s+$/g, '')          // Trim start/end
        .replace(/[ \t]+/g, ' ');           // Normalize spaces
    
    return result;
} 