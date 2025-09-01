---
title: "Grading System Sync"
protected: true
type: "grading-sync"
---

# 📊 Grading System Sync

<div id="sync-app">
<div id="auth-verification" class="loading-card">
<div class="spinner"></div>
<p>🔒 Verifying professor credentials...</p>
</div>

<div id="sync-content" style="display: none;">
<!-- Status card -->
<div id="sync-status-card" class="status-card">
<!-- Dynamically generated status -->
</div>

<!-- Data preview -->
<div id="data-preview" class="preview-section">
<h3>📋 Grading Data Overview</h3>
<div id="data-tree">
<!-- Dynamically generated tree view -->
</div>
</div>

<!-- Sync controls -->
<div id="sync-controls" class="controls-section">
<button id="preview-changes-btn" class="btn btn-secondary">
🔍 Preview Changes
</button>
<button id="sync-now-btn" class="btn btn-primary" disabled>
📤 Sync to Database
</button>
<button id="force-sync-btn" class="btn btn-warning">
⚡ Force Full Resync
</button>
</div>

<!-- Progress area -->
<div id="sync-progress" class="progress-section" style="display: none;">
<div class="progress-bar">
<div id="progress-fill" class="progress-fill"></div>
</div>
<div id="progress-text">Initializing sync...</div>
</div>

<!-- Results area -->
<div id="sync-results" class="results-section" style="display: none;">
<!-- Success/error messages -->
</div>
</div>

<div id="error-display" class="error-card" style="display: none;">
<!-- Error messages -->
</div>
</div>