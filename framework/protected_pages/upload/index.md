---
title: "Submit Assignments"
protected: true
---

# 📤 Submit Assignments

View all course assignments and submit your work. Track your submission status and manage deadlines.

<!-- Authentication check -->
<div id="authCheck" style="display: none;">
<div class="auth-error">
<h3>🔐 Authentication Required</h3>
<p>Please log in to submit assignments.</p>
<button onclick="window.location.href='{{ .Site.BaseURL }}auth/login/'">Log In with GitHub</button>
</div>
</div>

<!-- Loading state -->
<div id="loadingState">
<div class="loading-message">
<p>🔄 Loading assignments...</p>
</div>
</div>

<!-- Main submissions interface -->
<div id="submissionsInterface" style="display: none;">

<!-- Summary stats -->
<div class="submissions-header">
<div class="stats-summary" id="submissionStats">
<div class="stat-item">
<span class="stat-number" id="totalItems">--</span>
<span class="stat-label">Total Items</span>
</div>
<div class="stat-item">
<span class="stat-number" id="submittedItems">--</span>
<span class="stat-label">Submitted</span>
</div>
<div class="stat-item">
<span class="stat-number" id="pendingItems">--</span>
<span class="stat-label">Pending</span>
</div>
<div class="stat-item">
<span class="stat-number" id="overdueItems">--</span>
<span class="stat-label">Overdue</span>
</div>
</div>
</div>

<!-- Filters and search -->
<div class="submissions-controls">
<div class="control-group">
<label for="moduleFilter">Module:</label>
<select id="moduleFilter">
<option value="all">All Modules</option>
</select>
</div>
<div class="control-group">
<label for="statusFilter">Status:</label>
<select id="statusFilter">
<option value="all">All Status</option>
<option value="not_submitted">Not Submitted</option>
<option value="submitted">Submitted</option>
<option value="graded">Graded</option>
<option value="overdue">Overdue</option>
</select>
</div>
<div class="control-group">
<input type="text" id="searchFilter" placeholder="🔍 Search assignments...">
</div>
</div>

<!-- Items list -->
<div id="itemsList" class="items-list">
<!-- Dynamically populated -->
</div>

</div>

<!-- Error state -->
<div id="errorState" style="display: none;">
<div class="error-message">
<h3>⚠️ Unable to Load Assignments</h3>
<p id="errorMessage"></p>
<button onclick="window.location.reload()">🔄 Retry</button>
</div>
</div>

