# Authentication Setup Guide

**Status: IMPLEMENTATION COMPLETE ✅**

## Overview
This framework uses Supabase for authentication with GitHub OAuth. The implementation supports:
- Multiple repository deployments (e.g., /class_template/, /another_class/)
- Development and production environments  
- User profiles and class membership management
- Row Level Security (RLS) with automatic profile creation
- Edge Functions for authentication API
- PKCE flow for enhanced security

## Supabase Configuration

### 1. Create a Supabase Project
1. Go to [supabase.com](https://supabase.com) and create a new project
2. Note your project URL and anon key

### 2. Configure GitHub OAuth
1. In Supabase Dashboard → Authentication → Providers → GitHub
2. Enable GitHub provider
3. Add your GitHub OAuth App credentials:
   - **Client ID**: From your GitHub OAuth App
   - **Client Secret**: From your GitHub OAuth App

### 3. Configure Callback URLs
Add ALL of these callback URLs in Supabase (Authentication → URL Configuration):

#### For Development:
```
http://localhost:1313/auth/callback/
http://localhost:1314/auth/callback/
http://127.0.0.1:1313/auth/callback/
http://127.0.0.1:1314/auth/callback/
```

#### For Production (adjust domain):
```
https://yourdomain.com/auth/callback/
https://yourdomain.com/class_template/auth/callback/
https://yourdomain.com/[repo-name]/auth/callback/
```

### 4. GitHub OAuth App Setup
1. Go to GitHub → Settings → Developer settings → OAuth Apps
2. Create a new OAuth App with:
   - **Application name**: Your Class Name
   - **Homepage URL**: https://yourdomain.com/class_template/
   - **Authorization callback URL**: https://yourdomain.com/class_template/auth/callback/
3. Copy the Client ID and Client Secret to Supabase

## Database Setup

### 1. Deploy Database Schema
Run these SQL files in Supabase SQL Editor (in order):

```sql
-- File: professor/framework_code/sql/001_basic_auth.sql
-- Creates profiles, classes, class_members, enrollment_tokens tables
-- Includes automatic profile creation trigger
```

```sql  
-- File: professor/framework_code/sql/002_auth_policies.sql
-- Sets up Row Level Security policies for all tables
-- Enables profile creation and proper access controls
```

### 2. Deploy Edge Functions
```bash
# Deploy the /me endpoint
npx supabase functions deploy me --project-ref YOUR_PROJECT_ID
```

## Framework Configuration

### 1. Update config.yml
Edit `professor/config.yml` (and student directories after sync):

```yaml
authentication:
  enabled: true
  provider: "supabase"
  supabase:
    url: "https://YOUR_PROJECT.supabase.co"
    anon_key: "YOUR_ANON_KEY"
  flows:
    login_redirect: "/auth/callback/"
    logout_redirect: "/"  # Not used - stays on same page
    protected_redirect: "/dashboard/"
  ui:
    show_in_sidebar: true
    login_icon: "🔐"
    logout_icon: "🚪"
```

### 2. Update course.yml
Ensure the base URL is correct:

```yaml
site:
  baseurl: "https://yourdomain.com/class_template/"
```

## Authentication Flow

### Login Process:
1. User clicks login button on any page
2. Current page URL is stored in redirect parameter
3. User is redirected to GitHub for authentication
4. After GitHub auth, returns to `/auth/callback/`
5. Callback page processes auth and redirects back to original page

### Logout Process:
1. User clicks logout button
2. Session is cleared
3. Page reloads to update UI (stays on same page)

## Security Features

### Implemented:
- **PKCE Flow**: Enhanced OAuth security
- **Path Validation**: Prevents open redirect vulnerabilities
- **Session Management**: Automatic token refresh
- **Environment Detection**: Different behavior for dev/prod

### Best Practices:
1. Never commit real API keys - use environment variables in production
2. Regularly rotate your Supabase service role key
3. Configure Row Level Security (RLS) in Supabase
4. Use the anon key in frontend, never the service key

## Troubleshooting

### Issue: Redirects to wrong page after login
**Solution**: Check that the callback.md file has been updated with the latest version that properly handles the redirect parameter.

### Issue: Authentication works locally but not in production
**Solution**: 
1. Verify all callback URLs are added in Supabase
2. Check that course.yml has the correct production baseurl
3. Ensure GitHub OAuth app has production URLs

### Issue: "Invalid callback URL" error
**Solution**: The exact callback URL must be whitelisted in both:
1. Supabase Dashboard → Authentication → URL Configuration
2. GitHub OAuth App settings

### Issue: User stays logged in across different class repositories
**Solution**: This is expected behavior. Sessions are stored per-domain. Users can manually logout if needed.

## Testing Authentication

### Local Development:
1. Run `./manage.sh --dev`
2. Navigate to http://localhost:1313
3. Click login button
4. After GitHub auth, should return to the same page

### Production:
1. Deploy with `./manage.sh --professor/framework_documentationdeploy`
2. Navigate to your production URL
3. Test login/logout on different pages
4. Verify you return to the same page after auth

## Advanced Configuration

### Multiple Classes on Same Domain:
If hosting multiple classes on the same domain (e.g., /class1/, /class2/):
1. Each class needs its own Supabase project OR
2. Use a single project with RLS policies based on repository

### Custom Authentication Providers:
To add additional providers (Google, Azure, etc.):
1. Enable in Supabase Dashboard
2. Update the provider setting in supabase-auth.js
3. Add provider-specific configuration

## Support

For framework-specific auth issues, check:
- Browser console for JavaScript errors
- Network tab for failed requests
- Supabase Dashboard logs

For Supabase issues, refer to:
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [Supabase GitHub OAuth Guide](https://supabase.com/docs/guides/auth/social-login/auth-github)