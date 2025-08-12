# Authentication Implementation Plan

Status: MODULES 1-5 COMPLETE ✅ - AUTHENTICATION SYSTEM FULLY OPERATIONAL
Last Updated: 2025-08-12

## Overview

This document tracks the modular implementation of authentication for the Class Template Framework, following the design specification in DESIGN.md but adapted to the framework's static site architecture.

## Module 0: MCP Configuration (PREREQUISITE) ✅

**Goal:** Enable direct Supabase interaction via MCP

**Steps:**
1. Install MCP server: `npm install -g @modelcontextprotocol/server-supabase`
2. Get Service Role Key from Supabase Dashboard (Settings → API)
3. Configure `~/.config/claude/mcp_servers.json`:
```json
{
  "supabase": {
    "command": "npx",
    "args": ["@modelcontextprotocol/server-supabase"],
    "env": {
      "SUPABASE_URL": "https://levybxqsltedfjtnkntm.supabase.co",
      "SUPABASE_SERVICE_ROLE_KEY": "YOUR_KEY_HERE"
    }
  }
}
```
4. Restart Claude Desktop
5. Test with: "Can you query the Supabase database?"

**Status:** Ready to implement

---

## Module 1: Basic Database Schema ✅ COMPLETE

**Goal:** Create minimal authentication tables without grading complexity

**Status:** ✅ Completed - SQL files created and deployed
- Created `professor/framework_code/sql/001_basic_auth.sql`
- Created `professor/framework_code/sql/002_auth_policies.sql` 
- Schema deployed to Supabase successfully
- RLS policies applied and working
- Profile creation trigger tested and functional

**Files to create:**
- `professor/framework_code/sql/001_basic_auth.sql`

**Schema:**
```sql
-- Simplified from DESIGN.md Section 1.1
CREATE TABLE profiles (
  user_id UUID PRIMARY KEY REFERENCES auth.users(id),
  github_username TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE classes (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  slug TEXT UNIQUE NOT NULL,
  title TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE class_members (
  class_id UUID REFERENCES classes(id),
  user_id UUID REFERENCES auth.users(id),
  role TEXT CHECK (role IN ('professor', 'student')),
  enrolled_at TIMESTAMPTZ DEFAULT NOW(),
  PRIMARY KEY (class_id, user_id)
);

CREATE TABLE enrollment_tokens (
  id BIGSERIAL PRIMARY KEY,
  class_id UUID REFERENCES classes(id),
  token_hash TEXT NOT NULL,
  expires_at TIMESTAMPTZ NOT NULL,
  max_uses INT DEFAULT 0,
  uses INT DEFAULT 0
);
```

**Test Checklist:**
- [ ] Tables created in Supabase
- [ ] Test class inserted: `INSERT INTO classes (slug, title) VALUES ('class_template', 'Class Template Framework')`
- [ ] RLS policies not yet enabled (do after testing)

---

## Module 2: Frontend Auth State Enhancement ✅ COMPLETE

**Goal:** Call /me endpoint after login to get user context

**Status:** ✅ Completed - JavaScript files enhanced
- Created `professor/framework_code/assets/js/auth-client.js`
- Enhanced `professor/framework_code/assets/js/supabase-auth.js`
- Added fetchUserContext() function with debug logging
- Updated Hugo baseof.html to include auth-client.js
- API client ready for backend communication

**Files to modify:**
- `professor/framework_code/assets/js/supabase-auth.js`
- `professor/framework_code/assets/js/auth-client.js` (NEW)

**Implementation for auth-client.js:**
```javascript
window.AuthClient = {
  baseUrl: 'https://levybxqsltedfjtnkntm.supabase.co/functions/v1',
  
  async callEndpoint(endpoint, options = {}) {
    const token = window.authState?.session?.access_token;
    if (!token) throw new Error('Not authenticated');
    
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        ...options.headers
      }
    });
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.status}`);
    }
    
    return response.json();
  },
  
  async getMe(classSlug) {
    return this.callEndpoint(`/me?class_slug=${classSlug}`);
  },
  
  async enroll(classSlug, token) {
    return this.callEndpoint('/enroll', {
      method: 'POST',
      body: JSON.stringify({ class_slug: classSlug, token: token })
    });
  }
};
```

**Update supabase-auth.js (after line 141 in updateAuthState):**
```javascript
// Fetch user context if authenticated
if (user && window.AuthClient) {
  // Get class slug from current path or default
  const pathParts = window.location.pathname.split('/');
  const classSlug = pathParts[1] || 'class_template';
  
  window.AuthClient.getMe(classSlug)
    .then(context => {
      window.authState.userContext = context;
      console.log('User context loaded:', context);
    })
    .catch(err => {
      console.warn('Could not fetch user context:', err);
    });
}
```

**Test Checklist:**
- [ ] Login works
- [ ] Console shows attempt to call /me
- [ ] Error is expected (endpoint doesn't exist yet)

---

## Module 3: First Edge Function (/me) ✅ COMPLETE

**Goal:** Deploy minimal /me endpoint to Supabase

**Status:** ✅ Completed - Edge Function deployed and tested
- Created `professor/framework_code/supabase/functions/me/index.ts`
- Edge Function deployed to Supabase successfully
- /me endpoint responding correctly to requests
- CORS headers configured properly
- JWT authentication working
- Database integration tested and functional

**Deployment Steps:**
1. Install Supabase CLI
2. Create functions directory: `supabase/functions/me/`
3. Create `index.ts`:

```typescript
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const url = new URL(req.url)
    const classSlug = url.searchParams.get('class_slug')
    
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_ANON_KEY') ?? '',
      { global: { headers: { Authorization: req.headers.get('Authorization')! } } }
    )

    const { data: { user }, error } = await supabase.auth.getUser()
    if (error || !user) {
      return new Response(JSON.stringify({ error: 'Unauthorized' }), {
        status: 401,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // Get class
    const { data: classData } = await supabase
      .from('classes')
      .select('id')
      .eq('slug', classSlug)
      .single()

    // Check membership
    const { data: membership } = await supabase
      .from('class_members')
      .select('role')
      .eq('class_id', classData?.id)
      .eq('user_id', user.id)
      .single()

    return new Response(JSON.stringify({
      user_id: user.id,
      class_id: classData?.id,
      role: membership?.role || null,
      is_member: !!membership
    }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})
```

4. Deploy: `supabase functions deploy me`

**Test Checklist:**
- [ ] Function deployed successfully
- [ ] Test with curl: `curl -H "Authorization: Bearer YOUR_TOKEN" https://YOUR_PROJECT.supabase.co/functions/v1/me?class_slug=class_template`
- [ ] Frontend receives response

---

## Module 4: Dashboard Role Display

**Goal:** Show different content based on user role

**Files to modify:**
- `professor/framework_code/protected_pages/dashboard/_index.md`

**Update dashboard script section:**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(() => {
        if (!window.authState || !window.authState.isAuthenticated) {
            window.location.href = '/';
            return;
        }
        
        const userInfoEl = document.getElementById('userInfo');
        const user = window.authState.user;
        const context = window.authState.userContext;
        
        let roleDisplay = 'Not Enrolled';
        let roleClass = 'role-none';
        
        if (context) {
            if (context.role === 'professor') {
                roleDisplay = '👨‍🏫 Professor';
                roleClass = 'role-professor';
            } else if (context.role === 'student') {
                roleDisplay = '👩‍🎓 Student';
                roleClass = 'role-student';
            }
        }
        
        userInfoEl.innerHTML = `
            <div class="user-card">
                <h3>👤 ${user.email}</h3>
                <p class="${roleClass}"><strong>Role:</strong> ${roleDisplay}</p>
                <p><strong>User ID:</strong> ${user.id}</p>
                ${context && !context.is_member ? 
                  '<a href="/enroll/" class="enroll-btn">Join Class</a>' : ''}
            </div>
        `;
    }, 1000);
});
```

**Test Checklist:**
- [ ] Dashboard shows role correctly
- [ ] Non-members see "Join Class" button
- [ ] Styling differentiates roles

---

## Module 5: Enrollment System ✅ COMPLETE

**Goal:** Allow token-based enrollment

**Status:** ✅ Completed - Full enrollment system with dashboard integration
- Created `professor/framework_code/supabase/functions/enroll/index.ts` - Edge Function for enrollment
- Created `professor/framework_code/supabase/functions/generate-token/index.ts` - Edge Function for token generation
- Enhanced dashboard with prominent enrollment section and role-based tools
- Implemented SHA-256 token hashing using crypto.subtle (Deno Edge Functions compatible)
- Added enrollment token management with expiration and usage limits
- Created large orange enrollment button with animations and visual feedback
- Integrated JavaScript enrollment handlers in dashboard
- Professor tools for generating and managing enrollment tokens
- **Technical Note**: Replaced bcrypt with crypto.subtle.digest() for Deno Edge Functions compatibility

**Files Created/Modified:**
- `professor/framework_code/supabase/functions/enroll/index.ts`
- `professor/framework_code/supabase/functions/generate-token/index.ts`  
- `professor/framework_code/protected_pages/dashboard/index.md`
- `professor/framework_code/themes/evangelion/css/components/dashboard.css`
- `professor/framework_code/assets/js/auth-client.js`

**Enrollment page (_index.md):**
```markdown
---
title: "Join Class"
protected: true
---

# Join Class

<div id="enrollmentForm">
    <label for="token">Enrollment Token:</label>
    <input type="text" id="token" placeholder="Enter your enrollment token">
    <button onclick="enrollStudent()">Enroll</button>
    <div id="message"></div>
</div>

<script>
async function enrollStudent() {
    const token = document.getElementById('token').value;
    const messageEl = document.getElementById('message');
    
    try {
        const result = await window.AuthClient.enroll('class_template', token);
        messageEl.innerHTML = '<p class="success">✅ Enrolled successfully!</p>';
        setTimeout(() => window.location.href = '/dashboard/', 2000);
    } catch (error) {
        messageEl.innerHTML = `<p class="error">❌ ${error.message}</p>`;
    }
}
</script>
```

**Test Checklist:**
- [ ] Enrollment page accessible
- [ ] Token submission works
- [ ] Successful enrollment redirects to dashboard
- [ ] Invalid tokens show error

---

## Module 6: Python Database Setup Script

**Goal:** Automate SQL migrations

**Files to create:**
- `professor/framework_code/scripts/init_supabase.py`

```python
#!/usr/bin/env python3
"""Initialize Supabase database with authentication schema"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client

def run_migrations(supabase: Client):
    """Run SQL migrations in order"""
    sql_dir = Path(__file__).parent.parent / 'sql'
    
    # Get all SQL files in order
    sql_files = sorted(sql_dir.glob('*.sql'))
    
    for sql_file in sql_files:
        print(f"Running {sql_file.name}...")
        with open(sql_file, 'r') as f:
            sql = f.read()
            
        try:
            # Execute SQL
            supabase.postgrest.rpc('exec_sql', {'query': sql}).execute()
            print(f"✅ {sql_file.name} completed")
        except Exception as e:
            print(f"❌ {sql_file.name} failed: {e}")
            return False
    
    return True

def main():
    url = os.environ.get('SUPABASE_URL')
    key = os.environ.get('SUPABASE_SERVICE_KEY')
    
    if not url or not key:
        print("Error: Set SUPABASE_URL and SUPABASE_SERVICE_KEY environment variables")
        sys.exit(1)
    
    supabase = create_client(url, key)
    
    if run_migrations(supabase):
        print("✅ All migrations completed successfully")
    else:
        print("❌ Migration failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Test Checklist:**
- [ ] Script connects to Supabase
- [ ] Migrations run in order
- [ ] Can run multiple times safely

---

## Module 7: Framework Documentation

**Goal:** Document the authentication system properly

**Files to create (following framework standards):**
- `professor/framework_documentation/05_authentication_system/00_index.md`
- `professor/framework_documentation/05_authentication_system/01_setup_guide.md`
- `professor/framework_documentation/05_authentication_system/02_edge_functions.md`
- `professor/framework_documentation/05_authentication_system/03_database_schema.md`

**Example: 01_setup_guide.md**
```markdown
---
title: "Authentication Setup Guide"
type: documentation
date: 2025-01-08
author: "Framework Team"
summary: "Step-by-step guide to setting up authentication with Supabase"
difficulty: medium
estimated_time: 30
tags:
- authentication
- setup
- supabase
---

# Authentication Setup Guide

This guide walks through setting up authentication for your class instance...
```

---

## Testing Strategy

### Unit Tests (per module):
1. Functionality works in isolation
2. No breaking changes to existing features
3. Error handling graceful
4. Follows framework conventions

### Integration Tests:
- Module 1 → 3: Database ↔ Edge Function connection
- Module 2 → 3: Frontend ↔ Edge Function communication
- Module 3 → 4: User context affects UI rendering
- Module 4 → 5: Complete enrollment flow
- Module 1 → 6: Automated setup matches manual

### End-to-End Test:
1. New user visits site
2. Clicks login → GitHub OAuth
3. Returns to same page
4. Dashboard shows "Not Enrolled"
5. Uses token to enroll
6. Dashboard shows "Student" role

## Implementation Order

**Week 1:**
- Module 1: Database schema (2 hours)
- Module 2: Frontend state (1 hour)
- Module 3: /me endpoint (2 hours)

**Week 2:**
- Module 4: Dashboard (1 hour)
- Module 5: Enrollment (2 hours)

**Week 3:**
- Module 6: Automation (2 hours)
- Module 7: Documentation (2 hours)

## Success Metrics

- [ ] Authentication preserves page location
- [ ] Role-based UI rendering works
- [ ] Enrollment flow complete
- [ ] Documentation follows framework standards
- [ ] All code in correct framework locations
- [ ] Syncs properly to student directories