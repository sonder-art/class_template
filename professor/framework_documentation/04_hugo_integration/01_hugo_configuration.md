---
title: "Hugo Configuration System"
type: "note"
date: 2025-01-21
author: "Framework Team"
summary: "Technical documentation for Hugo static site generator integration and configuration"
difficulty: "medium"
tags: ["hugo", "static-site", "configuration", "integration"]
---

# Hugo Configuration System

The Hugo configuration system (`professor/framework_code/hugo_config/`) integrates Hugo static site generator with the framework's educational content structure.

## Overview

Hugo integration provides:
- **Evangelion-themed** dark styling with excellent readability
- **Markdown and notebook** content processing
- **Automatic navigation** generation from directory structure
- **Math rendering** with MathJax/KaTeX support
- **Search functionality** with client-side indexing

## Configuration Files

### hugo.toml

Main Hugo configuration with framework-specific settings:

```toml
title = "GitHub Class Template Repository"
baseURL = "https://example.github.io/class_template"

[params]
  theme_name = "default"  # References our Evangelion theme
  enable_search = true
  enable_homework_nav = true
  enable_chapter_nav = true
```

### Content Processing

#### Markdown Configuration
```toml
[markup.goldmark]
  [markup.goldmark.renderer]
    unsafe = true  # Allow HTML in Markdown
  [markup.goldmark.extensions]
    linkify = true
    table = true
    taskList = true
```

#### Syntax Highlighting
```toml
[markup.highlight]
  style = "github-dark"  # Fits our Evangelion theme
  lineNos = true
  codeFences = true
```

### Output Formats

Hugo generates multiple formats:
- **HTML** - Main website pages
- **RSS** - Content feeds
- **JSON** - Search index data

```toml
[outputs]
  home = ["HTML", "RSS", "JSON"]  # JSON for search index
```

## Archetype Templates

### default.md Archetype

Template for standard content files:

```yaml
---
title: "{{ replace .Name "-" " " | title }}"
type: "note"
date: {{ .Date }}
author: "{{ .Site.Params.professor_name }}"
summary: "Brief summary of this content"
difficulty: "medium"
tags: []
---
```

### homework.md Archetype

Template for homework assignments:

```yaml
---
title: "Homework {{ .Name | replaceRE `hw_(\d+).*` `$1` }}"
type: "homework"
difficulty: "medium"
estimated_time: 60
due_date: ""
points: 100
---
```

## Theme Integration

### Theme Selection

Hugo reads theme configuration from framework:
1. **dna.yml** - `theme: default` parameter
2. **Hugo params** - `theme_name = "default"`
3. **CSS loading** - `themes/default/css/main.css`

### Evangelion Theme Features

- **Dark color scheme** - Pure black (#0a0a0a) background
- **Neon accents** - Eva green (#00ff41), orange (#ff6600)
- **Typography** - Inter font stack for readability
- **Responsive layout** - 280px sidebar with mobile support

## Navigation Generation

Hugo automatically generates navigation from:
- **Directory structure** - Chapters and sections
- **File metadata** - Titles and summaries
- **Naming conventions** - Ordered by number/letter

### Homework Navigation

Special handling for homework files:
- **Detection** - Files with `hw_` prefix
- **Grouping** - Separate homework navigation section
- **Ordering** - By homework number

## Content Types

### Supported Formats

- **Markdown** (`.md`) - Standard content
- **Quarto** (`.qmd`) - Extended markdown with code execution
- **Notebooks** (`.ipynb`) - Jupyter notebooks (future integration)

### Content Organization

Hugo maps framework structure:
```
class_notes/01_introduction/01_introduction.md
→ /notes/01_introduction/01_introduction/
```

## Math Rendering

### MathJax Configuration

```toml
[params]
  enable_mathjax = true
  enable_katex = false
```

Supports LaTeX syntax in markdown:
- Inline math: `$equation$`
- Block math: `$$equation$$`

## Search System

### Index Generation

Hugo generates JSON search index:
```toml
[outputs]
  home = ["HTML", "RSS", "JSON"]
```

### Search Data

Index includes:
- **Content metadata** - Title, summary, tags
- **Content preview** - First characters
- **Navigation data** - URLs and relationships

## Build Process

### Development

```bash
npm run dev
# hugo server --bind 0.0.0.0 --disableFastRender
```

### Production

```bash
npm run build
# hugo --minify --gc
```

### Dependencies

package.json includes:
- **Math libraries** - KaTeX, MathJax
- **CSS tools** - PostCSS, Autoprefixer
- **Quality tools** - Stylelint, HTMLHint

## Security

### Content Security Policy

```toml
[server.headers.values]
  Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline'"
```

### Allowed Executables

```toml
[security.exec]
  allow = ["^dart-sass-embedded$", "^go$", "^npx$", "^postcss$"]
```

## Performance

### Caching

```toml
[caches.images]
  dir = ":resourceDir/_gen"
  maxAge = "1440h"
```

### Minification

```toml
[minify]
  disableCSS = false
  disableHTML = false
  disableJS = false
```

## Integration Points

### Framework Components

Hugo integrates with:
- **DNA parser** - Site configuration
- **Course parser** - Content metadata
- **Naming validator** - Content structure
- **Theme system** - Visual styling

### GitHub Pages

Optimized for GitHub Pages deployment:
- **Relative URLs** - Works with subdirectories
- **Static output** - No server-side processing
- **Asset optimization** - Minified CSS/JS

## Troubleshooting

### Common Issues

**Theme not loading:**
- Check `theme_name` in hugo.toml
- Verify theme files in `themes/default/`

**Math not rendering:**
- Enable MathJax in params
- Check LaTeX syntax in content

**Search not working:**
- Verify JSON output format enabled
- Check search index generation

## Testing

Test Hugo configuration:
```bash
cd professor/framework_code/hugo_config
npm install
hugo new site test_site --config hugo.toml
cd test_site
hugo server
``` 