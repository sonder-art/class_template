---
title: "Authentication Setup Guide"
type: documentation
date: 2025-08-12
author: "Framework Team"
summary: "Complete authentication setup with profiles, RLS, and Edge Functions"
difficulty: medium
estimated_time: 45
tags:
- authentication
- setup
- supabase
- implementation-complete
---

# Authentication Setup Guide

**Status: IMPLEMENTATION COMPLETE ✅**

This guide walks through setting up authentication for your class instance using Supabase, including database schema, RLS policies, and Edge Functions.

## Prerequisites

- GitHub account with OAuth App creation permissions
- Supabase account (free tier works)
- Access to update `config.yml` in your repository

## Step 1: Create Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Choose a project name (e.g., "class-template-auth")
3. Set a strong database password (save this securely)
4. Select a region close to your users
5. Wait for project provisioning (takes 2-3 minutes)

## Step 2: Configure GitHub OAuth

### In GitHub:

1. Go to Settings → Developer settings → OAuth Apps
2. Click "New OAuth App"
3. Fill in the application details:
   - **Application name**: Your Class Name
   - **Homepage URL**: `https://yourdomain.com/class_template/`
   - **Authorization callback URL**: `https://YOUR_PROJECT.supabase.co/auth/v1/callback`
4. Click "Register application"
5. Copy the **Client ID**
6. Generate and copy a new **Client Secret**

### In Supabase:

1. Go to Authentication → Providers → GitHub
2. Enable the GitHub provider
3. Paste your GitHub OAuth App credentials:
   - **Client ID**: From GitHub
   - **Client Secret**: From GitHub
4. Click "Save"

## Step 3: Configure Callback URLs

In Supabase Dashboard → Authentication → URL Configuration:

Add these Redirect URLs:
```
http://localhost:1313/auth/callback/
http://localhost:1314/auth/callback/
http://127.0.0.1:1313/auth/callback/
http://127.0.0.1:1314/auth/callback/
https://yourdomain.com/auth/callback/
https://yourdomain.com/class_template/auth/callback/
```

## Step 4: Get API Keys

In Supabase Dashboard → Settings → API:

1. Copy the **Project URL** (e.g., `https://abc123.supabase.co`)
2. Copy the **Anon/Public Key** (safe for frontend)
3. Copy the **Service Role Key** (keep secret, for admin only)

## Step 5: Update Framework Configuration

Edit `professor/config.yml`:

```yaml
authentication:
  enabled: true
  provider: "supabase"
  supabase:
    url: "https://YOUR_PROJECT.supabase.co"
    anon_key: "YOUR_ANON_KEY"
  flows:
    login_redirect: "/auth/callback/"
    logout_redirect: "/"
    protected_redirect: "/dashboard/"
  ui:
    show_in_sidebar: true
    login_icon: "🔐"
    logout_icon: "🚪"
```

## Step 6: Deploy Database Schema

### Required: Run SQL Files in Order

1. Go to SQL Editor in Supabase Dashboard
2. Copy and run `framework_code/sql/001_basic_auth.sql`:
   - Creates profiles, classes, class_members, enrollment_tokens tables
   - Sets up automatic profile creation trigger
   - Enables Row Level Security (RLS)
   
3. Copy and run `framework_code/sql/002_auth_policies.sql`:
   - Creates RLS policies for all tables
   - Enables profile creation for authenticated users
   - Sets up proper access controls

4. Verify tables created in Table Editor:
   - `public.profiles`
   - `public.classes` 
   - `public.class_members`
   - `public.enrollment_tokens`

## Step 7: Deploy Edge Functions

1. Install Supabase CLI:
```bash
npm install -g supabase
```

2. Login to Supabase:
```bash
supabase login
```

3. Link your project:
```bash
supabase link --project-ref YOUR_PROJECT_REF
```

4. Deploy functions from the professor/framework_code/supabase directory:
```bash
cd professor/framework_code
supabase functions deploy me --project-ref YOUR_PROJECT_REF
# Future: supabase functions deploy enroll --project-ref YOUR_PROJECT_REF
```

## Step 8: Test Authentication

1. Start development server:
```bash
./manage.sh --dev
```

2. Visit http://localhost:1313
3. Click login button
4. Authenticate with GitHub
5. Verify return to same page
6. Check dashboard shows user info

## Troubleshooting

### "Invalid callback URL" error
- Ensure exact URL is in Supabase Redirect URLs list
- Check for trailing slashes
- Verify protocol (http vs https)

### User not persisting across refreshes
- Check browser cookies enabled
- Verify localStorage not blocked
- Check Supabase session settings

### Edge Functions not responding
- Verify functions deployed successfully
- Check CORS configuration
- Review function logs in Supabase Dashboard

## Next Steps

- Generate enrollment tokens for students
- Customize dashboard for your class
- Set up grading system (if needed)
- Configure email notifications