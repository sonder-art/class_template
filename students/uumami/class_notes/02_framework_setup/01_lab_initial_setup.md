---
title: "Framework Setup Lab - Hands-On Practice"
type: "lab"
date: "2025-08-13"
author: "Professor"
summary: "Interactive lab for setting up and configuring the GitHub Class Template Framework"
tags: ["framework", "setup", "lab", "hands-on"]
---

# Framework Setup Lab

Hands-on laboratory session to set up your own instance of the GitHub Class Template Framework and understand its architecture through direct experience.

## Lab Exercises

<!-- Items now display in-place where defined -->

### Lab 1: Repository Setup & Configuration


{{< item "initial-setup" "repo_fork_and_config" >}}


Set up your own working instance of the framework:

**Part A: Repository Setup**
1. Fork the class template repository to your GitHub account
2. Clone your fork locally 
3. Create a new branch called `lab-setup`
4. Configure your `course.yml` with your personal course information

**Part B: Content Creation**
1. Create a new class note in `class_notes/00_my_introduction/`
2. Add your introduction with proper frontmatter
3. Include at least one code example with syntax highlighting
4. Test the build process locally

**Part C: Deployment**
1. Set up GitHub Pages deployment
2. Configure custom domain (optional)
3. Ensure all pages render correctly online

**Submission:** Submit the URL to your deployed framework instance

### Lab 2: Theme Customization


{{< item "framework-concepts" "theme_customization_lab" >}}


Create a custom theme variant and present your design decisions:

**Technical Requirements:**
1. Create a new theme called `tokyo-3` in `framework_code/themes/`
2. Design a cohesive color scheme (minimum 8 CSS variables)
3. Customize at least 3 component styles
4. Ensure responsive design on mobile devices
5. Test theme switching functionality

**Design Challenge:**
- Choose a theme inspired by any anime, movie, or artistic movement
- Justify your color and typography choices
- Demonstrate accessibility compliance (contrast ratios)
- Show before/after comparisons

**Presentation Format:** 10-minute live demo of your theme with Q&A

### Lab 3: Advanced Hugo Features


{{< item "build-validation" "hugo_advanced_features" >}}


Build advanced Hugo functionality to extend the framework:

**Challenge 1: Custom Shortcode**
Create a new shortcode called `code-demo` that:
- Accepts parameters for language, title, and GitHub URL
- Displays syntax-highlighted code
- Includes a "Try it" button linking to the repository
- Shows line numbers and copy functionality

**Challenge 2: Data Processing**
Enhance the item parsing system:
- Add support for `prerequisite` field linking items together
- Create a dependency graph visualization
- Generate completion progress tracking
- Build a "suggested next steps" recommendation engine

**Challenge 3: Content Automation**
Build a system that:
- Auto-generates course calendars from item due dates
- Creates summary pages for each module
- Builds a searchable assignment database
- Exports data to multiple formats (JSON, CSV, iCal)

**Deliverables:**
- Complete Hugo shortcode code
- Enhanced Python parsing scripts  
- Demo repository showing all features
- Documentation explaining your implementation

### Lab 4: Integration Testing


{{< item "build-validation" "integration_testing_suite" >}}


Create and demonstrate a comprehensive testing strategy:

**Testing Categories:**
1. **Build Testing:** Automated validation of Hugo builds across different content types
2. **Content Testing:** Verification that all markdown files meet standards
3. **Theme Testing:** Cross-browser compatibility and responsive design validation
4. **Performance Testing:** Page load times and optimization analysis
5. **Accessibility Testing:** WCAG compliance verification

**Video Requirements:**
- 15-20 minute screen recording
- Demonstrate each testing category with live examples
- Show failing tests and how to debug them
- Explain testing philosophy and best practices
- Include automated testing setup instructions

**Bonus Challenge:** Set up GitHub Actions CI/CD pipeline for automated testing

---

## Lab Resources

### Development Environment
- **Hugo Version:** 0.148.2 or newer
- **Python Version:** 3.8+ with rich, pyyaml, jinja2
- **Git:** Latest stable version
- **VS Code Extensions:** Hugo Language and Syntax Support

### Documentation Links
- [Hugo Shortcode Development](https://gohugo.io/content-management/shortcodes/)
- [Framework Architecture Guide](../../framework_documentation/01_core_concepts/01_architecture_overview.md)
- [Theme Development Tutorial](../../framework_tutorials/03_theme_development/01_getting_started.md)

### Testing Tools
- **Browser Testing:** BrowserStack or similar cross-browser platform
- **Performance:** Google PageSpeed Insights, Lighthouse
- **Accessibility:** aXe DevTools, WAVE Web Accessibility Evaluator
- **Build Testing:** Local Hugo server + automated scripts

## Evaluation Criteria

**Technical Implementation (50%)**
- Code quality and organization
- Proper use of Hugo/framework patterns
- Error handling and edge cases
- Performance and optimization

**Innovation & Creativity (25%)**
- Original problem-solving approaches
- Thoughtful design decisions  
- Creative use of framework features
- Going beyond minimum requirements

**Documentation & Communication (25%)**
- Clear code comments and documentation
- Professional presentation/demo skills
- Thorough testing and validation
- Helpful explanations for other students

## Lab Tips

💡 **Start Early:** These labs build on each other - don't wait until the last minute!

🔧 **Experiment Freely:** The framework is designed to be modified - break things and learn!

🤝 **Collaborate:** Share discoveries and help classmates (but submit individual work)

📋 **Document Everything:** Keep notes on what works, what doesn't, and why

🎯 **Focus on Understanding:** The goal is deep framework comprehension, not just completion