# Complete Theme System Guide

## Overview

This system enables **unlimited theme creation** while maintaining **universal callout readability** and **consistent educational structure**. Whether you want a forest theme, cyberpunk aesthetic, or academic styling, this guide will walk you through creating your own theme from scratch.

## Architecture

```
styles/
├── main.css               # Core structure + responsive layout (NEVER EDIT)
├── THEME_SYSTEM.md        # This comprehensive guide
└── themes/
    ├── _template.css      # Default dark theme (evangelion-based)
    ├── evangelion.css     # Enhanced evangelion theme
    ├── cyberpunk.css      # Neon cyberpunk example
    ├── forest.css         # Your new theme!
    ├── ocean.css          # Another new theme!
    └── [unlimited more themes...]
```

## Universal Standards (🔒 LOCKED - Never Change These)

These elements **NEVER change** across themes to ensure educational content remains readable:

### **Callout System Standards**
- **Contrast ratio**: 6:1 minimum (WCAG AA+ compliance)
- **Font sizes**: `1.3rem` body text, `1.3rem` titles (optimized for classroom presentations)
- **Icons**: Universal symbols (⚠️ warning, 💡 tip, 📖 note, ✏️ exercise, 🎯 objective, ⭐ important)
- **Structure**: Padding, borders, spacing, layout locked for consistency
- **Visual weight**: All callouts have same prominence across themes

### **Typography Standards**
- **Heading scale**: h1-h6 sizes optimized for presentation visibility
- **Base font**: `1.4rem` for all body text
- **Line height**: `1.65` for optimal readability
- **Responsive scaling**: Automatic size adjustments for different screen sizes

### **Layout Standards**
- **Content width**: 95-80% depending on screen size (maximizes presentation space)
- **TOC system**: Hover-based collapsible table of contents
- **Responsive breakpoints**: Mobile, tablet, desktop, large screen optimizations

## Theme Personality Elements (✅ Fully Customizable)

Each theme can freely customize these elements to create unique visual personality:

### **Colors**
- Primary color (headings, major elements)
- Accent color (links, highlights, call-to-action elements)
- Background colors (main, offset/secondary)
- Text colors (main, light/muted)
- Border colors

### **Typography** 
- Font families (Google Fonts recommended)
- Font weights and styles
- Letter spacing and text transforms

### **Visual Effects**
- Shadows and glows
- Hover animations and transitions
- Background patterns and textures
- Gradient overlays

### **Component Styling**
- TOC colors and styling
- Callout color overrides
- Code block styling
- Navigation elements

---

# Step-by-Step Theme Creation Tutorial

## Phase 1: Planning Your Theme

### 1. Choose Your Theme Concept
Pick a clear theme concept with distinct personality:
- **Examples**: Forest, Ocean, Cyberpunk, Academic, Retro, Minimalist, Gothic, Space

### 2. Define Your Color Palette
Use [Coolors.co](https://coolors.co) or [Adobe Color](https://color.adobe.com) to create a 5-color palette:
- **Primary**: Main color for headings/major elements
- **Accent**: Bright color for links/highlights  
- **Background**: Main page background
- **Background Offset**: Secondary/card backgrounds
- **Text**: Main text color

**Example - Forest Theme:**
- Primary: `#2D5016` (Dark forest green)
- Accent: `#7CB342` (Bright leaf green)  
- Background: `#F1F8E9` (Light cream)
- Background Offset: `#E8F5E8` (Pale green)
- Text: `#1B5E20` (Deep green)

### 3. Select Typography
Choose 2-3 fonts from [Google Fonts](https://fonts.google.com):
- **Heading font**: Distinctive personality font
- **Body font**: Highly readable font
- **Monospace font**: For code (optional)

**Example - Forest Theme:**
- Headings: 'Merriweather' (classic serif)
- Body: 'Open Sans' (clean sans-serif)
- Code: 'Fira Code' (modern monospace)

## Phase 2: Create Your Theme File

### 1. Copy the Template
```bash
# Navigate to themes directory
cd uumami/styles/themes/

# Copy template with your theme name
cp _template.css forest.css
```

### 2. Add Font Imports
Add this at the very top of your new theme file:

```css
/*
============================================
   FOREST THEME: forest.css
   
   A nature-inspired theme with earth tones,
   organic fonts, and subtle woodland patterns.
============================================
*/

/* Import your chosen Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@300;400;700&family=Open+Sans:wght@300;400;500;600&family=Fira+Code:wght@400;500&display=swap');
```

### 3. Define Core Variables
Replace the color variables in the `:root` section:

```css
:root {
  /* ========================================
     FOREST THEME COLORS
     ======================================== */

  /* -- GLOBAL COLORS -- */
  --primary-color: #2D5016;          /* Dark forest green for headings */
  --accent-color: #7CB342;           /* Bright leaf green for accents */
  --text-color: #1B5E20;             /* Deep green for body text */
  --text-color-light: #4E7C31;       /* Muted green for secondary text */
  --bg-color: #F1F8E9;               /* Light cream background */
  --bg-color-offset: #E8F5E8;        /* Pale green for cards/sections */
  --link-color: #7CB342;             /* Bright green for links */
  --link-color-hover: #8BC34A;       /* Lighter green on hover */
  --border-color: #A5D6A7;           /* Soft green for borders */

  /* -- TYPOGRAPHY -- */
  --font-family-body: 'Open Sans', sans-serif;
  --font-family-heading: 'Merriweather', serif;
  --font-family-monospace: 'Fira Code', monospace;

  /* -- COMPONENTS -- */
  --code-bg-color: #E0F2E0;
  --code-text-color: #2E7D32;
  --table-header-bg: #C8E6C9;
  --table-row-even-bg: #E8F5E8;
  --blockquote-border-color: var(--accent-color);
}
```

## Phase 3: Customize TOC Colors (Optional)

If you want custom TOC styling, add these overrides:

```css
:root {
  /* ========================================
     TOC COLOR OVERRIDES (Optional)
     ======================================== */
  
  --toc-tab-bg: #7CB342;                 /* Forest green tab */
  --toc-tab-text: #FFFFFF;               /* White text on green */
  --toc-panel-bg: #F1F8E9;               /* Light background */
  --toc-panel-border: #2D5016;           /* Dark green border */
  --toc-text: #1B5E20;                   /* Dark green text */
  --toc-link-hover: #7CB342;             /* Green hover */
}
```

## Phase 4: Customize Callout Colors (Optional)

For theme-specific callout styling, add these overrides:

```css
:root {
  /* ========================================
     CALLOUT COLOR OVERRIDES (Optional)
     ======================================== */

  /* Note callouts - use theme colors */
  --callout-note-bg: #E8F5E8;            /* Pale green background */
  --callout-note-text: #1B5E20;          /* Dark green text */
  --callout-note-border: #2D5016;        /* Forest green border */

  /* Tip callouts - brighter theme colors */
  --callout-tip-bg: #F1F8E9;             /* Light cream */
  --callout-tip-text: #1B5E20;           /* Dark green text */
  --callout-tip-border: #7CB342;         /* Bright green border */

  /* Keep warning/exercise/objective as universal colors */
  /* No overrides needed - they'll use standard colors */
}
```

## Phase 5: Add Theme Personality Effects

### Basic Heading Effects
```css
/* ========================================
   FOREST THEME PERSONALITY
   ======================================== */

/* Organic heading styling */
h1, h2, h3 {
  text-shadow: 1px 1px 2px rgba(45, 80, 22, 0.1);
}

/* Subtle growth effect on hover */
h1:hover, h2:hover, h3:hover {
  transform: scale(1.02);
  transition: transform 0.3s ease;
}
```

### Background Patterns
```css
/* Subtle woodland pattern overlay */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='%237CB342' fill-opacity='0.05'%3E%3Cpath d='M20 20c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10zm10 0c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10 10-4.5 10-10z'/%3E%3C/g%3E%3C/svg%3E");
  pointer-events: none;
  z-index: -1;
}
```

### Code Block Styling
```css
/* Nature-inspired code blocks */
pre {
  border-left: 4px solid var(--accent-color);
  background: linear-gradient(135deg, #E0F2E0, #F1F8E9);
}

pre:hover {
  box-shadow: 0 4px 12px rgba(124, 179, 66, 0.2);
  transition: box-shadow 0.3s ease;
}
```

## Phase 6: Activate Your Theme

### 1. Update Quarto Configuration
Edit `_quarto.yml` to use your new theme:

```yaml
format:
  html:
    theme: 
      - styles/main.css
      - styles/themes/forest.css  # Your new theme!
```

### 2. Test Your Theme
```bash
# Render your site to see the theme
quarto render

# Or preview with live reload
quarto preview
```

---

# Advanced Theme Techniques

## Complex Color Schemes

### Gradient Backgrounds
```css
body {
  background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E8 50%, #C8E6C9 100%);
}
```

### CSS Custom Properties for Dynamic Colors
```css
:root {
  /* Define color variations */
  --primary-light: color-mix(in srgb, var(--primary-color) 70%, white);
  --primary-dark: color-mix(in srgb, var(--primary-color) 80%, black);
  --accent-light: color-mix(in srgb, var(--accent-color) 60%, white);
}
```

## Advanced Typography

### Custom Font Loading
```css
@font-face {
  font-family: 'CustomFont';
  src: url('fonts/CustomFont.woff2') format('woff2');
  font-display: swap;
}
```

### Responsive Typography
```css
h1 {
  font-size: clamp(2rem, 5vw, 4rem);
}
```

## Animation Systems

### Subtle Page Load Animation
```css
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

main {
  animation: fadeInUp 0.6s ease-out;
}
```

### Interactive Elements
```css
/* Floating action button effect */
.nav-button {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.nav-button:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(0,0,0,0.15);
}
```

## Complex Background Patterns

### SVG Pattern Generator
Use [Hero Patterns](https://heropatterns.com/) to generate custom SVG backgrounds:

```css
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,YOUR_GENERATED_PATTERN");
  opacity: 0.1;
  pointer-events: none;
  z-index: -1;
}
```

---

# Complete Variable Reference

## Core Color Variables
```css
:root {
  /* Global palette */
  --primary-color: #value;           /* Headings, major elements */
  --accent-color: #value;            /* Links, highlights, CTAs */
  --text-color: #value;              /* Main body text */
  --text-color-light: #value;        /* Secondary/muted text */
  --bg-color: #value;                /* Main background */
  --bg-color-offset: #value;         /* Cards, sections, alternates */
  --link-color: #value;              /* Link text */
  --link-color-hover: #value;        /* Link hover state */
  --border-color: #value;            /* General borders */
}
```

## Typography Variables
```css
:root {
  /* Font families */
  --font-family-body: 'Font Name', fallback;
  --font-family-heading: 'Font Name', fallback;
  --font-family-monospace: 'Font Name', fallback;
  
  /* Base sizes (usually don't change these) */
  --font-size-base: 1.4rem;          /* Base body text */
  --line-height-base: 1.65;          /* Base line height */
}
```

## Component Variables
```css
:root {
  /* Code styling */
  --code-bg-color: #value;
  --code-text-color: #value;
  
  /* Table styling */
  --table-header-bg: #value;
  --table-row-even-bg: #value;
  
  /* Blockquote styling */
  --blockquote-border-color: #value;
}
```

## Callout Typography Variables (Usually Don't Change)
```css
:root {
  /* Callout sizing - optimized for presentations */
  --callout-font-size: 1.3rem;       /* Body text size */
  --callout-title-font-size: 1.3rem; /* Title size */
  --callout-line-height: 1.65;       /* Line spacing */
  --callout-padding: 1.5rem;         /* Internal spacing */
}
```

## TOC Color Overrides (Optional)
```css
:root {
  /* TOC customization */
  --toc-tab-bg: #value;              /* Tab background */
  --toc-tab-text: #value;            /* Tab text */
  --toc-panel-bg: #value;            /* Panel background */
  --toc-panel-border: #value;        /* Panel border */
  --toc-text: #value;                /* TOC text */
  --toc-link-hover: #value;          /* Link hover */
}
```

## Callout Color Overrides (Optional)
```css
:root {
  /* Note/Definition callouts */
  --callout-note-bg: #value;
  --callout-note-text: #value;
  --callout-note-border: #value;
  
  /* Tip callouts */
  --callout-tip-bg: #value;
  --callout-tip-text: #value;
  --callout-tip-border: #value;
  
  /* Warning callouts */
  --callout-warning-bg: #value;
  --callout-warning-text: #value;
  --callout-warning-border: #value;  /* Override universal red */
  
  /* Important callouts */
  --callout-important-bg: #value;
  --callout-important-text: #value;
  --callout-important-border: #value;
  
  /* Exercise callouts */
  --callout-exercise-bg: #value;
  --callout-exercise-text: #value;
  --callout-exercise-border: #value; /* Override universal amber */
  
  /* Objective callouts */
  --callout-objective-bg: #value;
  --callout-objective-text: #value;
  --callout-objective-border: #value; /* Override universal blue */
}
```

---

# Theme Examples & Templates

## Example 1: Ocean Theme
```css
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&family=Source+Code+Pro:wght@400;500&display=swap');

:root {
  /* Ocean color palette */
  --primary-color: #0277BD;          /* Deep ocean blue */
  --accent-color: #00BCD4;           /* Cyan accent */
  --text-color: #263238;             /* Dark blue-gray */
  --text-color-light: #607D8B;       /* Muted blue-gray */
  --bg-color: #F0F8FF;               /* Light blue background */
  --bg-color-offset: #E1F5FE;        /* Pale cyan */
  --link-color: #00BCD4;             /* Cyan links */
  --link-color-hover: #26C6DA;       /* Brighter cyan hover */
  --border-color: #B3E5FC;           /* Light blue borders */

  /* Ocean typography */
  --font-family-body: 'Nunito', sans-serif;
  --font-family-heading: 'Nunito', sans-serif;
  --font-family-monospace: 'Source Code Pro', monospace;
}

/* Wave animation background */
body::before {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 320'%3E%3Cpath fill='%2300bcd4' fill-opacity='0.05' d='M0,160L48,149.3C96,139,192,117,288,128C384,139,480,181,576,181.3C672,181,768,139,864,117.3C960,96,1056,96,1152,112C1248,128,1344,160,1392,176L1440,192L1440,320L1392,320C1344,320,1248,320,1152,320C1056,320,960,320,864,320C768,320,672,320,576,320C480,320,384,320,288,320C192,320,96,320,48,320L0,320Z'%3E%3C/path%3E%3C/svg%3E") repeat-x;
  animation: wave 20s linear infinite;
  pointer-events: none;
  z-index: -1;
}

@keyframes wave {
  0% { background-position-x: 0; }
  100% { background-position-x: 1440px; }
}
```

## Example 2: Academic Theme
```css
@import url('https://fonts.googleapis.com/css2?family=Crimson+Text:wght@400;600;700&family=Source+Sans+Pro:wght@300;400;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* Traditional academic colors */
  --primary-color: #1A237E;          /* Deep navy blue */
  --accent-color: #D32F2F;           /* Classic red */
  --text-color: #212121;             /* Near black */
  --text-color-light: #616161;       /* Medium gray */
  --bg-color: #FAFAFA;               /* Off-white */
  --bg-color-offset: #F5F5F5;        /* Light gray */
  --link-color: #1976D2;             /* Professional blue */
  --link-color-hover: #1565C0;       /* Darker blue */
  --border-color: #E0E0E0;           /* Light gray borders */

  /* Academic typography */
  --font-family-body: 'Source Sans Pro', sans-serif;
  --font-family-heading: 'Crimson Text', serif;
  --font-family-monospace: 'JetBrains Mono', monospace;
}

/* Subtle paper texture */
body {
  background-image: 
    radial-gradient(circle at 1px 1px, rgba(0,0,0,0.02) 1px, transparent 0);
  background-size: 20px 20px;
}

/* Traditional underlines for headings */
h1, h2, h3 {
  border-bottom: 2px solid var(--accent-color);
  padding-bottom: 0.5rem;
}
```

## Example 3: Minimalist Theme
```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500&display=swap');

:root {
  /* Ultra-minimal palette */
  --primary-color: #000000;          /* Pure black */
  --accent-color: #6366F1;           /* Single accent color */
  --text-color: #374151;             /* Dark gray */
  --text-color-light: #9CA3AF;       /* Light gray */
  --bg-color: #FFFFFF;               /* Pure white */
  --bg-color-offset: #F9FAFB;        /* Barely gray */
  --link-color: #6366F1;             /* Accent purple */
  --link-color-hover: #4F46E5;       /* Darker purple */
  --border-color: #E5E7EB;           /* Subtle border */

  /* Clean typography */
  --font-family-body: 'Inter', sans-serif;
  --font-family-heading: 'Inter', sans-serif;
  --font-family-monospace: 'JetBrains Mono', monospace;
}

/* No background patterns - pure minimalism */
/* Focus on typography and whitespace */
h1, h2, h3 {
  font-weight: 600;
  letter-spacing: -0.025em;
}
```

---

# Testing & Quality Assurance

## Visual Testing Checklist

### ✅ **Color Contrast**
- [ ] All text meets 6:1 contrast ratio minimum
- [ ] Callouts remain highly readable
- [ ] Links are clearly distinguishable
- [ ] Hover states are visible

### ✅ **Typography Readability**
- [ ] Headings are clearly hierarchical
- [ ] Body text is comfortable to read
- [ ] Code blocks are distinctive
- [ ] Font sizes work at presentation scale

### ✅ **Theme Consistency**
- [ ] Color palette is coherent across all elements
- [ ] Visual style is consistent throughout
- [ ] All components feel unified
- [ ] No jarring color clashes

### ✅ **Responsive Behavior**
- [ ] Theme works on mobile devices
- [ ] TOC remains functional on all screen sizes
- [ ] Content scales properly on large screens
- [ ] No horizontal scrolling issues

## Contrast Testing Tools

Use these tools to verify accessibility:
- **WebAIM Contrast Checker**: https://webaim.org/resources/contrastchecker/
- **Colour Contrast Analyser**: Free desktop app
- **Browser DevTools**: Built-in accessibility audits

## Browser Testing

Test your theme in:
- ✅ Chrome/Chromium
- ✅ Firefox  
- ✅ Safari (if possible)
- ✅ Edge

---

# Troubleshooting Common Issues

## Problem: Colors Not Applying

**Symptoms**: CSS variables defined but colors don't change

**Solutions**:
1. Check CSS syntax - missing semicolons break variable definitions
2. Verify `:root` selector is properly formed
3. Ensure theme file is loaded after main.css in `_quarto.yml`
4. Clear browser cache and hard refresh (Ctrl+Shift+R)

```css
/* ❌ Wrong - missing semicolon */
:root {
  --primary-color: #123456
  --accent-color: #abcdef;
}

/* ✅ Correct */
:root {
  --primary-color: #123456;
  --accent-color: #abcdef;
}
```

## Problem: Fonts Not Loading

**Symptoms**: Google Fonts import not working

**Solutions**:
1. Verify Google Fonts URL is correct and complete
2. Check internet connection during development
3. Add font-display: swap for better loading
4. Include fallback fonts

```css
/* ❌ Wrong - incomplete URL */
@import url('https://fonts.googleapis.com/css2?family=Roboto');

/* ✅ Correct - complete with weights and display */
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

/* ✅ Always include fallbacks */
--font-family-body: 'Roboto', Arial, sans-serif;
```

## Problem: Theme Not Activating

**Symptoms**: Still seeing default theme after changes

**Solutions**:
1. Check `_quarto.yml` theme path is correct
2. Verify theme file exists and has correct name
3. Restart Quarto preview (`quarto preview`)
4. Check for CSS syntax errors preventing file parsing

```yaml
# ❌ Wrong path
format:
  html:
    theme: 
      - styles/main.css
      - themes/forest.css

# ✅ Correct path
format:
  html:
    theme: 
      - styles/main.css
      - styles/themes/forest.css
```

## Problem: Callouts Look Broken

**Symptoms**: Callouts have poor contrast or formatting issues

**Solutions**:
1. Don't override callout structure - only colors
2. Ensure 6:1 contrast ratio for all callout text
3. Test with actual content, not just placeholder text
4. Verify callout color variables are properly formatted

```css
/* ❌ Wrong - trying to change structure */
.callout {
  padding: 0.5rem; /* Don't override padding */
  font-size: 0.8rem; /* Don't override font size */
}

/* ✅ Correct - only override colors */
:root {
  --callout-note-bg: #f0f8ff;
  --callout-note-text: #1a1a1a;
  --callout-note-border: #007acc;
}
```

## Problem: Performance Issues

**Symptoms**: Slow page loading or janky animations

**Solutions**:
1. Optimize background images and SVG patterns
2. Use CSS transforms instead of changing layout properties
3. Limit complex animations to hover states only
4. Avoid huge background images

```css
/* ❌ Performance problem - animating layout properties */
.element {
  transition: width 0.3s, height 0.3s, left 0.3s;
}

/* ✅ Better - animating transforms */
.element {
  transition: transform 0.3s, opacity 0.3s;
}
```

---

# Best Practices

## Design Principles

### **1. Readability First**
- Always prioritize content readability over visual flair
- Test with actual course content, not Lorem ipsum
- Consider classroom projection scenarios

### **2. Consistent Color Story**
- Choose 3-5 core colors maximum
- Use color relationships (complementary, analogous, triadic)
- Maintain consistent color temperature throughout

### **3. Purposeful Animation**
- Use animations to enhance, not distract
- Keep animations subtle and purposeful
- Prefer micro-interactions over flashy effects

### **4. Scalable Approach**
- Design for multiple screen sizes from the start
- Use relative units (rem, em, %) when possible
- Test at different zoom levels

## Code Organization

### **File Structure**
```css
/* 1. Font imports */
@import url('...');

/* 2. Theme comment header */
/*
============================================
   THEME NAME: description
============================================
*/

/* 3. Core variables */
:root {
  /* Color palette */
  /* Typography */
  /* Components */
}

/* 4. Optional color overrides */
:root {
  /* TOC colors */
  /* Callout colors */
}

/* 5. Theme personality effects */
/* Headings */
/* Backgrounds */
/* Animations */
```

### **Variable Naming**
- Use descriptive names: `--forest-green` instead of `--color1`
- Follow existing convention: `--component-property-modifier`
- Group related variables together

### **Comments**
```css
/* ========================================
   SECTION NAME
   ======================================== */

/* Brief description of what this block does */
.selector {
  property: value; /* Inline explanation for complex rules */
}
```

## Performance Guidelines

### **Efficient CSS**
- Use CSS custom properties for repeated values
- Minimize specificity conflicts
- Prefer CSS Grid/Flexbox over floats and positioning
- Optimize SVG patterns for file size

### **Font Loading**
- Limit to 3-4 font weights maximum
- Use `font-display: swap` for better loading
- Include system font fallbacks
- Consider variable fonts for multiple weights

### **Resource Optimization**
- Optimize background images for web
- Use SVG for simple patterns and icons
- Minimize HTTP requests where possible
- Consider critical CSS for above-the-fold content

---

# Advanced Theme Examples

## Example: Cyberpunk Enhancement
```css
/* Advanced neon glow system */
:root {
  --neon-pink: #ff00ff;
  --neon-cyan: #00ffff;
  --glow-intensity: 0.8;
}

/* Multiple glow layers for realistic neon */
h1 {
  color: var(--neon-pink);
  text-shadow: 
    0 0 5px var(--neon-pink),
    0 0 10px var(--neon-pink),
    0 0 15px var(--neon-pink),
    0 0 20px var(--neon-pink);
  animation: flicker 2s infinite alternate;
}

@keyframes flicker {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.8; }
}

/* Scanline effect */
body::after {
  content: '';
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    transparent 50%,
    rgba(0, 255, 255, 0.03) 50%
  );
  background-size: 100% 4px;
  pointer-events: none;
  z-index: 1000;
}
```

## Example: Hand-drawn/Sketch Style
```css
/* Wobbly, hand-drawn borders */
.callout {
  border-radius: 255px 15px 225px 15px / 15px 225px 15px 255px;
  border: 2px solid var(--primary-color);
  position: relative;
}

.callout::before {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  border: 1px solid var(--primary-color);
  border-radius: 235px 15px 255px 15px / 15px 255px 15px 235px;
  opacity: 0.7;
}

/* Sketchy text shadows */
h1, h2, h3 {
  text-shadow: 
    1px 1px 0 var(--primary-color),
    -1px 1px 0 var(--primary-color),
    1px -1px 0 var(--primary-color),
    -1px -1px 0 var(--primary-color);
}
```

---

# Future Enhancements

## Planned Features

### **Theme Variants**
- Light/dark mode toggle within themes
- Seasonal theme variations
- Accessibility-focused theme variants

### **Advanced Customization**
- Theme-specific component libraries
- Custom icon sets per theme
- Advanced animation libraries

### **Developer Tools**
- Theme validation scripts
- Contrast ratio automation
- Live theme editor interface

### **Community Features**
- Theme sharing repository
- Community voting on themes
- Collaborative theme development

---

# Current Theme Status

## ✅ **Completed Themes**
- **evangelion.css**: Dark sci-fi theme (default)
- **cyberpunk.css**: Neon-punk aesthetic
- **_template.css**: Base template for new themes

## 🚀 **Ready for Development**
The system is fully prepared for unlimited theme creation. All infrastructure is in place:
- ✅ Universal callout system (6:1 contrast guaranteed)
- ✅ Responsive layout system (presentation-optimized)
- ✅ Typography scaling (classroom visibility)
- ✅ Color override system (flexible customization)
- ✅ Hover-based TOC (theme-aware styling)
- ✅ Complete development guide (this document)

## 🎯 **Next Steps**
1. Create 2-3 additional themes using this guide
2. Test theme system with diverse visual styles
3. Gather feedback from theme creators
4. Expand to 20+ themes for comprehensive choice

---

*This guide provides everything needed to create unlimited themes while maintaining educational content readability and optimal presentation formatting. Happy theming!*