---
title: "Dashboard"
protected: true
---

# 📊 Dashboard

Welcome to your protected dashboard! This area requires authentication.

## User Information

<div id="userInfo">
    <p>Loading user information...</p>
</div>

## Quick Actions

- **Upload Files**: [Go to Upload Section](/upload/)
- **View Analytics**: Coming soon...
- **Manage Settings**: Coming soon...

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
        
        // Display user information if authenticated
        const userInfoEl = document.getElementById('userInfo');
        const user = window.authState.user;
        
        userInfoEl.innerHTML = `
            <div class="user-card">
                <h3>👤 ${user.email}</h3>
                <p><strong>Provider:</strong> ${user.app_metadata?.provider || 'Unknown'}</p>
                <p><strong>Last Sign In:</strong> ${new Date(user.last_sign_in_at).toLocaleString()}</p>
                <p><strong>User ID:</strong> ${user.id}</p>
            </div>
        `;
    }, 500);
});
</script>

<style>
.user-card {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 8px;
    padding: 20px;
    margin: 20px 0;
}

.user-card h3 {
    margin-top: 0;
    color: #495057;
}
</style>