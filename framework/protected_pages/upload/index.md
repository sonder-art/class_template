---
title: "Upload Files"
protected: true
---

# 📤 Upload Files

This is a protected upload area. You must be authenticated to access this section.

## File Upload Interface

<div id="uploadInterface">
    <div class="upload-area">
        <h3>📁 Drag & Drop Files Here</h3>
        <p>Or click to browse files</p>
        <input type="file" id="fileInput" multiple style="display: none;">
        <button onclick="document.getElementById('fileInput').click()">Choose Files</button>
    </div>
    
    <div id="uploadStatus" style="margin-top: 20px;"></div>
</div>

<script>
// Authentication protection
document.addEventListener('DOMContentLoaded', function() {
    // Check authentication status
    setTimeout(() => {
        if (!window.authState || !window.authState.isAuthenticated) {
            console.warn('🚫 Unauthorized access to protected page - redirecting to login');
            window.location.href = window.authConfig?.logout_redirect || '/';
            return;
        }
        
        // Set up file upload interface if authenticated
        const fileInput = document.getElementById('fileInput');
        const uploadStatus = document.getElementById('uploadStatus');
        
        fileInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            
            if (files.length > 0) {
                uploadStatus.innerHTML = `
                    <div class="upload-preview">
                        <h4>📋 Selected Files:</h4>
                        <ul>
                            ${files.map(file => `<li>${file.name} (${(file.size / 1024).toFixed(1)} KB)</li>`).join('')}
                        </ul>
                        <p><em>Note: This is a demo interface. Actual upload functionality would be implemented based on your backend requirements.</em></p>
                    </div>
                `;
            }
        });
    }, 500);
});
</script>

<style>
.upload-area {
    border: 2px dashed #ccc;
    border-radius: 10px;
    padding: 40px;
    text-align: center;
    background: #f9f9f9;
    margin: 20px 0;
    transition: border-color 0.3s;
}

.upload-area:hover {
    border-color: #007bff;
    background: #f0f8ff;
}

.upload-area button {
    background: #007bff;
    color: white;
    border: none;
    padding: 10px 20px;
    border-radius: 5px;
    cursor: pointer;
    margin-top: 10px;
}

.upload-preview {
    background: #e9ecef;
    padding: 15px;
    border-radius: 5px;
    border-left: 4px solid #28a745;
}

.upload-preview ul {
    text-align: left;
    max-width: 400px;
    margin: 10px auto;
}
</style>