/**
 * Python Environment System - Framework Module
 * Handles Pyodide loading, Python execution, and JupyterLite integration
 * Extracted from baseof.html for better modularity and maintainability
 */

// Initialize Python environment when DOM is ready
document.addEventListener("DOMContentLoaded", function() {
    // Initialize Python environment if needed
    initializePythonEnvironment();
});

// Global Python Execution System
let pyodideReady = false;
let pyodide = null;

async function initializePythonEnvironment() {
    const pythonContainers = document.querySelectorAll('.python-exec-container');
    console.log(`🔍 Found ${pythonContainers.length} Python execution containers`);

    // Setup each container with clean single-textarea approach
    pythonContainers.forEach(container => {
        const textarea = container.querySelector('.python-code-input');
        
        if (textarea) {
            console.log('📝 Initializing Python container with simplified approach');
            
            // Setup keyboard shortcuts and behavior
            setupPythonEditor(container, textarea);
        }
    });

    if (pythonContainers.length > 0 && !pyodideReady) {
        console.log('🐍 Starting Pyodide initialization...');

        if (typeof loadPyodide === 'undefined') {
            console.error('❌ loadPyodide function not found - Pyodide script failed to load');
            updateAllButtons('❌ Python Failed', true);
            return;
        }

        try {
            console.log('🔄 Loading Pyodide runtime...');
            pyodide = await loadPyodide();
            pyodideReady = true;
            console.log('✅ Pyodide loaded successfully!');

            updateAllButtons('▶️ Run Python', false);
            console.log('🎉 Python execution environment ready!');
            
        } catch (error) {
            console.error('❌ Failed to load Pyodide:', error);
            updateAllButtons('❌ Python Error', true);
        }
    }
}

function updateAllButtons(text, disabled) {
    document.querySelectorAll('.python-exec-button').forEach(btn => {
        const buttonText = btn.querySelector('.button-text');
        const buttonIcon = btn.querySelector('.button-icon');
        
        if (buttonText) buttonText.textContent = text.replace(/^.*?\s/, ''); // Remove emoji for text
        if (buttonIcon) buttonIcon.textContent = text.match(/^.*?(?=\s)/)?.[0] || '▶️'; // Extract emoji
        btn.disabled = disabled;
    });
}

function setupPythonEditor(container, textarea) {
    // Keyboard shortcuts
    textarea.addEventListener('keydown', function(e) {
        // Ctrl+Enter or Cmd+Enter: Execute code
        if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
            e.preventDefault();
            const button = container.querySelector('.python-exec-button');
            if (button && !button.disabled) {
                executePythonCode(button);
            }
        }
        
        // Tab: Insert 4 spaces for indentation
        if (e.key === 'Tab') {
            e.preventDefault();
            const start = this.selectionStart;
            const end = this.selectionEnd;
            
            // Insert 4 spaces
            this.value = this.value.substring(0, start) + '    ' + this.value.substring(end);
            this.selectionStart = this.selectionEnd = start + 4;
        }
        
        // Ctrl+/ or Cmd+/: Toggle line comment
        if ((e.ctrlKey || e.metaKey) && e.key === '/') {
            e.preventDefault();
            toggleLineComment(this);
        }
    });

    // Auto-resize textarea based on content
    textarea.addEventListener('input', function() {
        autoResizeTextarea(this);
    });

    // Initial resize
    autoResizeTextarea(textarea);
}

function autoResizeTextarea(textarea) {
    // Reset height to recalculate
    textarea.style.height = 'auto';
    
    // Calculate required height (minimum 8 lines, maximum 60vh)
    const lineHeight = parseInt(window.getComputedStyle(textarea).lineHeight);
    const minHeight = lineHeight * 8; // 8 lines minimum
    const maxHeight = Math.min(window.innerHeight * 0.6, 600); // 60vh or 600px max
    
    const scrollHeight = Math.max(textarea.scrollHeight, minHeight);
    const finalHeight = Math.min(scrollHeight, maxHeight);
    
    textarea.style.height = finalHeight + 'px';
    
    // Update the parent editor container height
    const editor = textarea.closest('.python-exec-editor');
    if (editor) {
        editor.style.minHeight = finalHeight + 'px';
    }
}

function toggleLineComment(textarea) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const lines = textarea.value.split('\n');
    
    // Find which lines are selected
    let startLine = 0;
    let endLine = 0;
    let currentPos = 0;
    
    for (let i = 0; i < lines.length; i++) {
        if (currentPos <= start && start <= currentPos + lines[i].length) {
            startLine = i;
        }
        if (currentPos <= end && end <= currentPos + lines[i].length) {
            endLine = i;
            break;
        }
        currentPos += lines[i].length + 1; // +1 for newline
    }
    
    // Check if all selected lines are commented
    let allCommented = true;
    for (let i = startLine; i <= endLine; i++) {
        if (!lines[i].trim().startsWith('#')) {
            allCommented = false;
            break;
        }
    }
    
    // Toggle comments
    for (let i = startLine; i <= endLine; i++) {
        if (allCommented) {
            // Remove comment
            lines[i] = lines[i].replace(/^\s*#\s?/, '');
        } else {
            // Add comment
            const indentMatch = lines[i].match(/^(\s*)/);
            const indent = indentMatch ? indentMatch[1] : '';
            const content = lines[i].slice(indent.length);
            lines[i] = indent + '# ' + content;
        }
    }
    
    textarea.value = lines.join('\n');
    autoResizeTextarea(textarea);
}

window.executePythonCode = async function(button) {
    const container = button.closest('.python-exec-container');
    const textarea = container.querySelector('.python-code-input');
    const code = textarea.value.trim();
    const outputDiv = container.querySelector('.python-exec-output');
    const resultPre = container.querySelector('.python-exec-result');

    if (!pyodideReady) {
        showOutput(outputDiv, resultPre, '❌ Python environment not ready. Please wait for Pyodide to load.');
        return;
    }

    if (!code) {
        showOutput(outputDiv, resultPre, '⚠️ No code to execute. Write some Python code first!');
        return;
    }

    // Set loading state
    container.classList.add('loading');
    showOutput(outputDiv, resultPre, '⏳ Executing Python code...');
    updateButtonState(button, '⏳', 'Running...', true);

    try {
        // Capture stdout
        pyodide.runPython(`
import sys
from io import StringIO
sys.stdout = StringIO()
        `);
        
        // Execute user code
        pyodide.runPython(code);
        
        // Get output
        const output = pyodide.runPython("sys.stdout.getvalue()");
        
        // Restore stdout
        pyodide.runPython("sys.stdout = sys.__stdout__");

        // Display result
        if (output.trim()) {
            showOutput(outputDiv, resultPre, output);
        } else {
            showOutput(outputDiv, resultPre, '✅ Code executed successfully (no output)');
        }
        
        container.classList.remove('error');

    } catch (error) {
        showOutput(outputDiv, resultPre, `❌ Error: ${error.message}`);
        container.classList.add('error');
        
    } finally {
        container.classList.remove('loading');
        updateButtonState(button, '▶️', 'Run Python', false);
    }
}

function showOutput(outputDiv, resultPre, content) {
    outputDiv.style.display = 'block';
    resultPre.textContent = content;
    
    // Scroll output into view
    outputDiv.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function updateButtonState(button, icon, text, disabled) {
    const buttonIcon = button.querySelector('.button-icon');
    const buttonText = button.querySelector('.button-text');
    
    if (buttonIcon) buttonIcon.textContent = icon;
    if (buttonText) buttonText.textContent = text;
    button.disabled = disabled;
}

window.clearPythonOutput = function(button) {
    const container = button.closest('.python-exec-container');
    const outputDiv = container.querySelector('.python-exec-output');
    outputDiv.style.display = 'none';
    
    // Remove error state
    container.classList.remove('error');
}

window.copyPythonOutput = function(button) {
    const container = button.closest('.python-exec-container');
    const resultPre = container.querySelector('.python-exec-result');
    
    if (resultPre && resultPre.textContent.trim()) {
        navigator.clipboard.writeText(resultPre.textContent).then(() => {
            // Show feedback
            const originalText = button.textContent;
            button.textContent = '✅';
            setTimeout(() => {
                button.textContent = originalText;
            }, 1000);
        }).catch(err => {
            console.error('Failed to copy output:', err);
            button.textContent = '❌';
            setTimeout(() => {
                button.textContent = '📋';
            }, 1000);
        });
    }
}

// Global Lab Environment Functions
window.openJupyterLiteLab = function(root, title) {
    console.log('🧪 Lab button clicked!');
    console.log('📁 Root directory:', root);
    console.log('🏷️ Title:', title);
    
    // Create container ID  
    const containerId = `lab-embed-${(root || 'default').replace(/[^a-zA-Z0-9]/g, '-')}`;
    console.log('🔍 Looking for container:', containerId);
    
    const container = document.getElementById(containerId);
    console.log('📦 Container found:', container);
    
    if (!container) {
        console.error('❌ Container not found:', containerId);
        console.log('🔍 Available containers:', 
            Array.from(document.querySelectorAll('[id*="lab-embed"]')).map(el => el.id));
        alert(`Lab container not found: ${containerId}`);
        return;
    }
    
    // Show loading state
    container.style.display = 'block';
    container.innerHTML = `
        <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100%; background: var(--elevated-color); border-radius: 8px;">
            <div style="font-size: 48px; margin-bottom: 20px;">🧪</div>
            <h3 style="color: var(--eva-cyan-primary); margin: 0 0 10px 0;">Loading JupyterLite Lab...</h3>
            <p style="color: var(--text-secondary); margin: 0;">Setting up Python environment with Pyodide...</p>
            ${root ? `<p style="color: var(--text-muted); margin: 10px 0 0 0; font-size: 14px;">Working Directory: <code>${root}</code></p>` : ''}
        </div>
    `;
    
    // Create iframe for JupyterLite Lab
    const iframe = document.createElement('iframe');
    
    // Build JupyterLite URL
    let jupyterUrl = 'https://jupyterlite.github.io/demo/lab/index.html';
    
    // Add path parameter if root is specified
    if (root) {
        jupyterUrl += `?path=${encodeURIComponent(root)}`;
    }
    
    iframe.src = jupyterUrl;
    iframe.style.width = '100%';
    iframe.style.height = '100%';
    iframe.style.border = 'none';
    iframe.style.borderRadius = '8px';
    iframe.title = `JupyterLite Lab: ${title}`;
    
    // Replace loading content with iframe after a delay
    setTimeout(() => {
        container.innerHTML = '';
        container.appendChild(iframe);
        
        // Add a close button
        const closeButton = document.createElement('button');
        closeButton.innerHTML = '❌ Close Lab';
        closeButton.style.cssText = `
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
            padding: 8px 12px;
            background: var(--eva-red-primary, #BF616A);
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-weight: bold;
        `;
        closeButton.onclick = () => {
            container.style.display = 'none';
            container.innerHTML = '';
        };
        
        container.style.position = 'relative';
        container.appendChild(closeButton);
        
    }, 2000);
} 