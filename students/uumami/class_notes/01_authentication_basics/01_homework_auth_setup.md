---
title: "Authentication System Setup - Homework 1"
type: "homework"
date: "2025-08-13" 
author: "Professor"
summary: "Complete authentication system setup and initial testing"
tags: ["authentication", "setup", "homework"]
---

# Authentication System Setup - Homework 1

This chapter covers the fundamental setup of the authentication system for our GitHub Class Template Framework. You will implement Supabase authentication, configure GitHub OAuth, and test the complete authentication flow.

## Learning Objectives

By the end of this homework, you will be able to:
- Configure Supabase authentication with GitHub OAuth
- Implement JWT-based session management  
- Test authentication flows with error handling
- Deploy authentication Edge Functions

## Background Reading

Before starting this homework, review the following resources:
- [Framework Authentication Documentation](../../framework_documentation/05_authentication_system/00_index.md)
- [Supabase Auth Documentation](https://supabase.com/docs/guides/auth)
- [GitHub OAuth Apps Guide](https://docs.github.com/en/apps/oauth-apps)

---

## Homework Items

<!-- Items now display in-place where defined -->

### Item 1: Supabase Project Setup



{{< item-inline constituent_slug="auth-setup" item_id="supabase_project_setup" points="25" due_date="2025-08-20T23:59:59-05:00" title="Supabase Project Setup" delivery_type="url" important="true" >}}



Set up a new Supabase project for your authentication system:

1. Create a new Supabase project
2. Configure the database schema using the provided SQL files
3. Set up Row Level Security (RLS) policies
4. Configure your environment variables

**Submission Requirements:**
- Submit the URL to your Supabase project dashboard
- Include screenshots of your configured RLS policies
- Provide your `SUPABASE_URL` and `SUPABASE_ANON_KEY` (anon key only!)

**Grading Criteria:**
- Project created and accessible (5 points)
- Database schema correctly applied (10 points)
- RLS policies properly configured (10 points)

### Item 2: GitHub OAuth Configuration



{{< item-inline constituent_slug="auth-setup" item_id="github_oauth_setup" points="20" due_date="2025-08-20T17:00:00-05:00" title="GitHub OAuth Configuration" delivery_type="upload" >}}



Configure GitHub OAuth for your application:

1. Create a new GitHub OAuth App
2. Configure the callback URLs for both development and production
3. Set up the required environment variables
4. Test the OAuth flow with a test user

**Submission Requirements:**
- Screenshot of your GitHub OAuth App settings
- Screenshot showing successful OAuth callback in development
- Brief explanation of your callback URL configuration

**Grading Criteria:**
- OAuth App properly configured (10 points)
- Callback URLs correct for both environments (5 points)
- Successful test authentication (5 points)

### Item 3: Edge Functions Deployment



{{< item-inline constituent_slug="auth-integration" item_id="edge_functions_deployment" points="30" due_date="2025-08-22" title="Edge Functions Deployment" delivery_type="code" >}}



Deploy and test the authentication Edge Functions:

1. Deploy the `/me` endpoint for user profile retrieval
2. Deploy the `/enroll` endpoint for class enrollment
3. Implement proper error handling and CORS configuration
4. Create a simple test page to demonstrate functionality

**Submission Requirements:**
- Links to your deployed Edge Functions
- Test page demonstrating successful authentication flow
- Code showing proper error handling implementation
- Screenshots of successful API responses

**Grading Criteria:**
- Edge Functions successfully deployed (15 points)
- Proper error handling implemented (10 points)
- Successful demonstration of authentication flow (5 points)

### Item 4: Comprehensive Authentication Testing



{{< item-inline constituent_slug="auth-testing" item_id="comprehensive_auth_testing" points="25" due_date="2025-08-25" title="Authentication Testing" delivery_type="text" important="true" >}}



Perform comprehensive testing of your authentication system:

1. Test successful login/logout flows
2. Test error scenarios (invalid tokens, expired sessions)
3. Test protected route access
4. Verify RLS policies work correctly
5. Test cross-browser compatibility

**Submission Requirements:**
- Detailed test report documenting all test cases
- Screenshots of successful and error scenarios
- Code for any automated tests you created
- Summary of any issues found and how they were resolved

**Grading Criteria:**
- Comprehensive test coverage (15 points)
- Proper documentation of test results (5 points)
- Evidence of error scenario testing (5 points)

---

## Additional Resources

- [Authentication Troubleshooting Guide](../../framework_documentation/05_authentication_system/01_setup_guide.md)
- [Supabase Edge Functions Documentation](https://supabase.com/docs/guides/functions)
- [Framework Development Commands](../../framework_tutorials/A_github_hugo_terminal_commands/01_terminal_flags_quick_reference.md)

## Getting Help

If you encounter issues:
1. Check the framework documentation first
2. Review the authentication setup guide
3. Test with the provided debugging tools
4. Ask questions in the class discussion forum

Remember: The authentication system is critical for all other framework features, so take your time to understand and implement it correctly!