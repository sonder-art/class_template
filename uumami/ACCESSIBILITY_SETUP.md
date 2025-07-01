# OpenDyslexic Accessibility Setup Guide

## What's Been Added

✅ **OpenDyslexic Font**: Automatically loaded from CDN via Fontsource  
✅ **CSS System**: Dyslexic mode overrides all fonts when activated  
✅ **JavaScript Toggle**: Remembers user preference across pages  
✅ **Navbar Integration**: Toggle appears directly in navbar next to GitHub icon  
✅ **Responsive Design**: Shows full text on desktop, icon-only on mobile  

## Automatic Site-Wide Integration (RECOMMENDED)

### Option 1: Add to Quarto Configuration

Add this to your `_quarto.yml` file:

```yaml
format:
  html:
    include-after-body: components/accessibility-auto.html
```

This automatically adds the accessibility toggle to the navbar on **every page** of your site.

### Option 2: Manual Page Integration

If you prefer to add it to individual pages only:

```html
```{=html}
<!-- Include accessibility-auto.html content manually -->
```

(Not recommended - use Option 1 for site-wide coverage)

## How It Works

**User Experience:**

**All Screen Sizes:**
1. **Navbar Integration**: "🔤 Dyslexic" toggle appears in the navbar next to GitHub icon
2. **Desktop**: Shows "🔤 Dyslexic" with text
3. **Mobile**: Shows just "🔤" icon to save space
4. **Instant Toggle**: Checking box immediately switches ALL text to OpenDyslexic font
5. **Persistent**: Preference is remembered across all pages and sessions

**Technical Details:**
- ✅ **Auto-Injection**: Toggle appears automatically in navbar on all pages
- ✅ **Font Override**: When enabled, replaces ALL fonts with OpenDyslexic
- ✅ **Theme Compatible**: Works with Evangelion, Cyberpunk, and all themes
- ✅ **Persistent**: Saves preference in browser localStorage
- ✅ **Fast Loading**: Font loads from reliable Fontsource CDN
- ✅ **Smart Fallbacks**: Comic Sans MS → Trebuchet MS → sans-serif
- ✅ **Responsive**: Shows text label on desktop, icon-only on mobile

## What Gets Changed

**When Dyslexic Mode is ON:**
- ✅ All body text → OpenDyslexic
- ✅ All headings → OpenDyslexic  
- ✅ All callouts → OpenDyslexic
- ✅ Code blocks → OpenDyslexic
- ✅ Navigation → OpenDyslexic
- ✅ Everything uses dyslexia-friendly font

**What Stays the Same:**
- ✅ All colors and themes remain unchanged
- ✅ All spacing and layout preserved
- ✅ All functionality works normally
- ✅ All icons and visual elements unchanged

## Files Created/Modified

- ✅ `styles/main.css` - Added OpenDyslexic font, navbar CSS, and override system
- ✅ `components/accessibility-auto.html` - Contains inlined JavaScript and auto-includes on all pages  
- ✅ `_quarto.yml` - Updated to include accessibility system site-wide
- ✅ `components/accessibility-bar.html` - Legacy HTML template (optional)
- ✅ `components/accessibility-test.qmd` - Demo page for testing

## Testing

### All Screen Sizes:
1. **Find the toggle** → Look in the navbar next to the GitHub icon
2. **Desktop view** → Should see "🔤 Dyslexic" with text label
3. **Mobile view** → Should see just "🔤" icon to save space
4. **Click checkbox** → All text changes to OpenDyslexic instantly
5. **Refresh page** → Setting should be remembered
6. **Navigate to other pages** → Setting persists across entire site
7. **Uncheck box** → Should return to original theme fonts

### Visual Verification:
- **OpenDyslexic ON**: Letters have distinctive weighted bottoms and unique shapes
- **OpenDyslexic OFF**: Returns to your selected theme fonts (Evangelion, etc.)

### If Toggle Doesn't Appear:
- Check browser console for JavaScript errors
- Verify `components/accessibility-auto.html` is being included via `_quarto.yml`
- Fallback: A simple floating button should appear in top-right corner if navbar isn't found

## Quick Setup

**For immediate site-wide activation:**

1. Add this line to your `_quarto.yml`:
   ```yaml
   format:
     html:
       include-after-body: components/accessibility-auto.html
   ```

2. The accessibility toggle will automatically appear in the navbar on all pages!

The system is now ready and will work across your entire website automatically. 