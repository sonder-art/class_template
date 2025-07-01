# Theme System Documentation

## Overview

This system enables unlimited theme creation while maintaining **universal callout readability** and **consistent educational structure**.

## Architecture

```
styles/
├── main.css (structure + responsive layout)
├── THEME_SYSTEM.md (this file)
└── themes/
    ├── _template.css (evangelion-based default)
    ├── evangelion.css (enhanced evangelion)
    ├── cyberpunk.css (example alternative)
    └── [18 more themes...]
```

## Universal Standards (🔒 LOCKED)

These **NEVER change** across themes to ensure readability and optimal presentation:

- **Callout contrast ratio**: 6:1 minimum (WCAG AA+)
- **Callout icons**: Universal symbols (⚠️ warning, 💡 tip, etc.)
- **Callout prominence**: Same visual weight across all themes
- **Callout structure**: Padding, borders, spacing locked
- **Responsive layout**: Presentation-optimized widths for all screen sizes
- **Typography scale**: Font sizes optimized for classroom visibility

## Theme Personality Elements (✅ CUSTOMIZABLE)

Each theme can freely customize:

- **Color palette**: Primary, accent, background colors
- **Typography**: Font families and styles  
- **Visual effects**: Glows, shadows, animations
- **Background patterns**: Textures, gradients, images
- **Hover effects**: Interactive elements
- **TOC colors**: Tab, panel, text, borders
- **Callout colors**: Background, text, borders per callout type

## Responsive Layout System

The theme system includes automatic responsive layout optimized for presentations:

### Screen Size Breakpoints
- **Large screens (1600px+)**: 80% width - optimal for projectors
- **Desktop/Laptop (1200px+)**: 85% width - maximum screen utilization
- **Tablet (768-1199px)**: 90% width - balanced approach
- **Mobile (<768px)**: 95% width - maintains readability

### Benefits
- ✅ **Presentation-ready**: Content uses full screen real estate
- ✅ **Automatic**: No manual adjustments needed
- ✅ **Universal**: Works with all themes
- ✅ **Mobile-friendly**: Still readable on phones

## Color Override System

The system provides smart defaults with optional override capability for maximum flexibility.

### Available Color Variables

#### **TOC Colors** (Optional Overrides)
```css
:root {
  --toc-tab-bg: var(--accent-color);         /* Default: theme accent */
  --toc-tab-text: var(--bg-color);          /* Default: theme bg */
  --toc-panel-bg: var(--bg-color-offset);   /* Default: theme offset */
  --toc-panel-border: var(--accent-color);  /* Default: theme accent */
  --toc-text: var(--text-color);            /* Default: theme text */
  --toc-link-hover: var(--accent-color);    /* Default: theme accent */
}
```

#### **Callout Colors** (Optional Overrides) 
```css
:root {
  /* Note/Definition callouts */
  --callout-note-bg: var(--bg-color-offset);
  --callout-note-text: var(--text-color);
  --callout-note-border: var(--primary-color);
  
  /* Tip callouts */
  --callout-tip-bg: var(--bg-color-offset);
  --callout-tip-text: var(--text-color);
  --callout-tip-border: var(--accent-color);
  
  /* Warning callouts */
  --callout-warning-bg: var(--bg-color-offset);
  --callout-warning-text: var(--text-color);
  --callout-warning-border: #E74C3C;    /* Universal red */
  
  /* Important callouts */
  --callout-important-bg: var(--bg-color-offset);
  --callout-important-text: var(--text-color);
  --callout-important-border: var(--accent-color);
  
  /* Exercise callouts */
  --callout-exercise-bg: var(--bg-color-offset);
  --callout-exercise-text: var(--text-color);
  --callout-exercise-border: #F39C12;   /* Universal amber */
  
  /* Objective callouts */
  --callout-objective-bg: var(--bg-color-offset);
  --callout-objective-text: var(--text-color);
  --callout-objective-border: #4A90E2;  /* Universal blue */
}
```

### How It Works

1. **Smart Defaults**: All colors automatically inherit from your theme's base colors
2. **Selective Overrides**: Only customize the specific colors you want to change
3. **Zero Setup**: Most themes work perfectly without any color overrides
4. **Maximum Control**: Granular control when you need theme-specific callout styling

## Creating New Themes

### Step 1: Copy Template
```bash
cp _template.css your-theme-name.css
```

### Step 2: Define Personality
1. **Choose theme concept** (e.g., forest, ocean, retro, academic)
2. **Find color palette** (use [coolors.co](https://coolors.co))
3. **Select fonts** from [Google Fonts](https://fonts.google.com)

### Step 3: Update Variables
```css
:root {
  /* Theme personality colors */
  --primary-color: #your-primary;
  --accent-color: #your-accent;
  --bg-color: #your-background;
  
  /* Typography */
  --font-family-heading: 'Your Font', sans-serif;
  
  /* Optional: Override specific callout colors */
  --callout-note-border: #your-special-color;
  --toc-tab-bg: #your-special-color;
}
```

### Step 4: Add Personality Elements
```css
/* Theme-specific visual flair */
h1, h2, h3 {
  /* Your heading effects */
}

body::before {
  /* Your background pattern */
}
```

## Quality Checklist

✅ **Contrast**: All callouts have 6:1+ contrast ratio  
✅ **Icons**: Universal callout icons unchanged  
✅ **Readability**: Text clearly visible in all contexts  
✅ **Personality**: Theme has distinct visual character  
✅ **Consistency**: Callouts have same visual weight  

## Example Themes

- **Evangelion** (default): Purple/green, sci-fi, terminal aesthetic
- **Cyberpunk**: Pink/cyan, neon glows, digital grid
- **Forest**: Green/brown, natural textures, organic shapes
- **Ocean**: Blue/teal, wave patterns, fluid design
- **Academic**: Traditional colors, serif fonts, clean lines

## Current Status

✅ **Universal callout system** implemented  
✅ **Template** converted to evangelion-based default  
✅ **Cyberpunk theme** created as example  
✅ **Responsive layout system** optimized for presentations  
✅ **Typography scaling** for classroom visibility  
✅ **Color override system** for TOC and callouts  
✅ **Hover-based TOC** with theme-aware styling  
🚀 **Ready for 18+ more themes**

## Implementation Priority

1. ✅ Convert evangelion to template *(complete)*
2. ✅ Establish universal callout system *(complete)*
3. ✅ Create example alternative theme *(complete)*
4. ✅ Implement responsive layout system *(complete)*
5. ✅ Optimize typography for presentations *(complete)*
6. ✅ Implement color override system *(complete)*
7. ✅ Create hover-based TOC system *(complete)*
8. 🔄 **Next**: Build 2-3 more themes to test system
9. 📋 **Future**: Scale to 20+ themes 