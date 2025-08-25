---
title: "Professor Grading Interface"
protected: true
---

# 🎯 Professor Grading Interface

Grade student submissions, provide feedback, and manage class performance.

<!-- Authentication check -->
<div id="authCheck" style="display: none;">
<div class="auth-error">
<h3>🔐 Professor Access Required</h3>
<p>Please log in with professor credentials to access grading.</p>
<button onclick="window.location.href='/class_template/auth/login/'">Log In with GitHub</button>
</div>
</div>

<!-- Loading state -->
<div id="loadingState">
<div class="loading-message">
<p>🔄 Loading grading data...</p>
</div>
</div>

<!-- Main grading interface -->
<div id="gradingInterface" style="display: none;">

<!-- Grading summary -->
<div class="grading-header">
<div class="grading-stats" id="gradingStats">
<div class="stat-item">
<span class="stat-number" id="pendingCount">--</span>
<span class="stat-label">Pending Submissions</span>
</div>
<div class="stat-item">
<span class="stat-number" id="gradedCount">--</span>
<span class="stat-label">Graded Submissions</span>
</div>
<div class="stat-item">
<span class="stat-number" id="studentsCount">--</span>
<span class="stat-label">Enrolled Students</span>
</div>
<div class="stat-item">
<span class="stat-number" id="itemsCount">--</span>
<span class="stat-label">Active Items</span>
</div>
</div>
</div>

<!-- Grading tabs -->
<div class="grading-tabs">
<button class="tab-btn active" data-tab="pending">📋 Pending Submissions</button>
<button class="tab-btn" data-tab="graded">✅ Recently Graded</button>
<button class="tab-btn" data-tab="students">👥 By Student</button>
<button class="tab-btn" data-tab="items">📝 By Assignment</button>
</div>

<!-- Tab content -->
<div class="tab-content active" id="pending-tab">
<div id="pendingSubmissions" class="submissions-container">
<!-- Dynamically populated -->
</div>
</div>

<div class="tab-content" id="graded-tab">
<div id="gradedSubmissions" class="submissions-container">
<!-- Dynamically populated -->
</div>
</div>

<div class="tab-content" id="students-tab">
<div id="studentView" class="students-container">
<!-- Dynamically populated -->
</div>
</div>

<div class="tab-content" id="items-tab">
<div id="itemsView" class="items-container">
<!-- Dynamically populated -->
</div>
</div>

</div>

<!-- Error state -->
<div id="errorState" style="display: none;">
<div class="error-message">
<h3>⚠️ Unable to Load Grading Data</h3>
<p id="errorMessage"></p>
<button onclick="window.location.reload()">🔄 Retry</button>
</div>
</div>

<!-- Grading modal -->
<div id="gradingModal" class="modal" style="display: none;">
<div class="modal-content grading-modal">
<div class="modal-header">
<h3 id="modalTitle">Grade Submission</h3>
<button class="modal-close" onclick="window.professorGrading.closeGradingModal()">&times;</button>
</div>
<div class="modal-body" id="gradingModalBody">
<!-- Dynamically populated with grading form -->
</div>
</div>
</div>

