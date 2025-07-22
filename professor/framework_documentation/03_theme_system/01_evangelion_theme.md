---
title: "Evangelion Theme Architecture"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Technical documentation for the Evangelion-inspired dark theme system and customization"
difficulty: "medium"
tags: ["theme", "css", "evangelion", "customization"]
---

# Evangelion Theme Architecture

The Evangelion theme (`professor/framework_code/themes/default/`) provides a dark, high-contrast design inspired by the Evangelion anime with excellent readability.

## Overview

The theme system provides:
- **Dark color scheme** with Evangelion signature colors
- **Responsive design** optimized for educational content
- **Typography** focused on readability and accessibility
- **Component system** for consistent UI elements

## Color Palette

### Core Colors

```css
:root {
  /* Dark backgrounds */
  --color-bg-primary: #0a0a0a;        /* Pure black background */
  --color-bg-secondary: #1a1a1a;      /* Cards/sections */
  --color-bg-tertiary: #2a2a2a;       /* Hover states */
  
  /* Evangelion signature colors */
  --color-eva-green: #00ff41;         /* Bright neon green */
  --color-eva-orange: #ff6600;        /* Eva Unit-01 orange */
  --color-eva-purple: #660099;        /* Eva Unit-01 purple */
  --color-eva-red: #ff0033;           /* Emergency/warning red */
  --color-eva-blue: #0099ff;          /* Interface blue */
  
  /* Text colors for maximum readability */
  --color-text-primary: #ffffff;      /* Pure white */
  --color-text-secondary: #cccccc;    /* Light gray */
  --color-text-muted: #888888;        /* Muted gray */
}
```

### Color Usage

- **Headers**: H1 uses Eva green with glow effect, H2 uses orange, H3 uses blue
- **Links**: Eva green with orange hover state
- **Code**: Eva green syntax highlighting on dark background
- **Interactive elements**: Eva green primary buttons, blue secondary

## Typography

### Font Stack

```css
--font-primary: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
--font-mono: 'SF Mono', 'Monaco', 'Inconsolata', 'Roboto Mono', monospace;
```

### Typography Features

- **Inter font** for maximum readability
- **System font fallbacks** for performance
- **Optimal line height** (1.6) for reading
- **Reading width** limited to 70ch for paragraphs
- **Smooth rendering** with antialiasing

## Layout System

### Desktop Layout

```css
.layout-main {
  display: grid;
  grid-template-columns: 280px 1fr;
  min-height: 100vh;
  gap: var(--spacing-lg);
}
```

- **280px sidebar** for navigation tree
- **Main content area** with responsive width
- **Sticky sidebar** for persistent navigation
- **Grid layout** for clean structure

### Mobile Layout

```css
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: -280px;
    transition: left 0.3s ease;
  }
  
  .sidebar.open {
    left: 0;
  }
}
```

- **Collapsible sidebar** with hamburger menu
- **Fixed positioning** for mobile overlay
- **Smooth transitions** for better UX

## Component System

### Navigation Components

```css
.nav-tree {
  list-style: none;
}

.nav-tree a.active {
  background-color: var(--color-eva-green);
  color: var(--color-bg-primary);
}
```

- **Tree structure** for hierarchical navigation
- **Active state** highlighting with Eva green
- **Hover effects** with subtle background changes

### Button Components

```css
.btn-primary {
  background-color: var(--color-eva-green);
  color: var(--color-bg-primary);
}

.btn-primary:hover {
  background-color: var(--color-eva-orange);
  box-shadow: var(--shadow-md);
}
```

- **Primary buttons** in Eva green
- **Secondary buttons** with blue borders
- **Hover effects** with color transitions and shadows

### Card Components

```css
.card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-bg-tertiary);
  border-radius: var(--radius-lg);
}

.card:hover {
  border-color: var(--color-eva-green);
  box-shadow: var(--shadow-md);
}
```

- **Content cards** with subtle borders
- **Hover effects** with Eva green accent
- **Rounded corners** for modern appearance

## Theme Configuration

### Hugo Integration

```toml
# hugo.toml
[params]
  theme_name = "default"  # Maps to themes/default/
```

### CSS Loading

Theme CSS is loaded via Hugo's asset pipeline:
```html
{{ $style := resources.Get "css/main.css" }}
<link rel="stylesheet" href="{{ $style.RelPermalink }}">
```

### Theme Switching

Future theme switching mechanism:
```yaml
# dna.yml
theme: evangelion  # Maps to themes/evangelion/
```

## Accessibility Features

### High Contrast Support

```css
@media (prefers-contrast: high) {
  :root {
    --color-bg-primary: #000000;
    --color-text-primary: #ffffff;
    --color-eva-green: #00ff00;
  }
}
```

### Reduced Motion Support

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

### Focus Management

```css
a:focus {
  outline: 2px solid var(--color-eva-green);
  outline-offset: 2px;
}
```

## Customization

### Creating New Themes

1. **Copy default theme**:
   ```bash
   cp -r professor/framework_code/themes/default/ professor/framework_code/themes/my_theme/
   ```

2. **Update theme.yml**:
   ```yaml
   name: "my_theme"
   display_name: "My Custom Theme"
   primary_color: "#custom_color"
   ```

3. **Modify CSS variables**:
   ```css
   :root {
     --color-eva-green: #your_primary_color;
     --color-eva-orange: #your_secondary_color;
   }
   ```

### Theme Inheritance

Themes can inherit from the default theme:
```css
/* Import base theme */
@import "../../default/css/main.css";

/* Override specific colors */
:root {
  --color-eva-green: #ff0080;  /* Custom pink */
}
```

## Performance

### CSS Optimization

- **CSS custom properties** for consistent theming
- **Minimal specificity** for better performance
- **Efficient selectors** avoiding complex nesting
- **Modern CSS features** with fallbacks

### Asset Management

- **Hugo processing** for minification
- **Critical CSS** inlined for fast loading
- **Progressive enhancement** for advanced features

## Integration Points

### Framework Components

The theme integrates with:
- **Hugo templates** for consistent rendering
- **Navigation generator** for sidebar styling
- **Search components** for styled results
- **Content types** for specialized formatting

### Content Styling

- **Markdown rendering** with syntax highlighting
- **Math expressions** with proper contrast
- **Code blocks** with Eva green highlighting
- **Tables** with alternating row colors

## Browser Support

### Modern Browsers
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Fallbacks
- CSS Grid with Flexbox fallback
- CSS custom properties with static fallbacks
- Modern font-display with system fonts

The Evangelion theme provides a distinctive, readable, and performant foundation for educational content while maintaining the characteristic aesthetic of the source material. 