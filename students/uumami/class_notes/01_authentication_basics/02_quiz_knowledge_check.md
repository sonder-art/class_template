---
title: "Authentication Knowledge Quiz"
type: "quiz"
date: "2025-08-13"
author: "Professor"
summary: "Quick knowledge verification on authentication concepts and implementation"
tags: ["authentication", "quiz", "theory"]
---

# Authentication Knowledge Quiz

Test your understanding of authentication concepts, OAuth flows, and security principles covered in the authentication basics module.

## Quiz Items

<!-- Items now display in-place where defined -->

### Quiz 1: OAuth Flow Understanding


{{< item "framework-concepts" "oauth_flow_quiz" >}}


Draw and explain the complete OAuth 2.0 authorization code flow:

**Instructions:**
1. Create a sequence diagram showing all steps from user click to token exchange
2. Explain each step in 1-2 sentences
3. Identify potential security vulnerabilities at each stage
4. Suggest mitigation strategies for identified risks

**Submit your response as:**
- Hand-drawn diagram (photo) or digital diagram
- Written explanations for each step
- Security analysis document

### Quiz 2: JWT Token Analysis


{{< item "auth-setup" "jwt_analysis_exercise" >}}


Given these JWT tokens, analyze their structure and security implications:

```
Token A: eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

Token B: eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJhZG1pbiIsImV4cCI6OTk5OTk5OTk5OX0.
```

**Deliverables:**
1. Decode both tokens and explain their payload contents
2. Identify security issues with each token
3. Write code to properly validate JWT tokens
4. Demonstrate secure vs insecure token handling

### Quiz 3: Supabase RLS Policy Design


{{< item "auth-testing" "rls_policy_design" >}}


Design comprehensive RLS policies for our class enrollment system:

**Scenario:** Students can only see their own grades, professors can see all grades for their classes, admins can see everything.

**Requirements:**
1. Write SQL RLS policies for `students`, `enrollments`, and `grades` tables
2. Test policies with different user roles
3. Document edge cases and how policies handle them
4. Create a security audit checklist

**Upload Format:** PDF document with SQL code, test cases, and security analysis

---

## Study Resources

- [OAuth 2.0 RFC 6749](https://tools.ietf.org/html/rfc6749)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)
- [Supabase RLS Documentation](https://supabase.com/docs/guides/auth/row-level-security)

## Grading Rubric

**Knowledge Demonstration (40%)**
- Accuracy of technical concepts
- Understanding of security implications
- Proper use of terminology

**Implementation Quality (35%)**
- Working code examples
- Proper error handling
- Security best practices

**Communication (25%)**
- Clear explanations
- Well-organized documentation
- Professional presentation

Remember: These quizzes test both theoretical understanding and practical application. Focus on demonstrating deep comprehension rather than memorization!