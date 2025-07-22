# Hugo Configuration for GitHub Class Template Repository

This directory contains the Hugo static site generator configuration for the GitHub Class Template Repository framework.

## Overview

Hugo is configured to work with:
- **Evangelion-inspired dark theme** with excellent readability
- **Markdown and Jupyter notebook content**
- **Automatic navigation generation** based on directory structure
- **Math rendering** with MathJax/KaTeX support
- **Search functionality** with client-side indexing
- **JupyterLite integration** for browser-based code execution

## Configuration Files

### `hugo.toml`
Main Hugo configuration file with:
- Site metadata and parameters
- Content processing settings (Goldmark, syntax highlighting)
- Theme configuration referencing our Evangelion theme
- Menu structure for navigation
- Output formats (HTML, RSS, JSON for search)
- Security and optimization settings

### `archetypes/`
Content templates for new files:
- `default.md` - Standard content template with metadata fields
- `homework.md` - Homework assignment template with grading rubric

### `package.json`
Node.js dependencies for:
- Math rendering libraries (KaTeX, MathJax)
- CSS processing tools (PostCSS, Autoprefixer)
- Code quality tools (Stylelint, HTMLHint)
- Build and development scripts

## Quick Start

### Prerequisites
- Hugo Extended v0.120.0 or later
- Node.js 16+ and npm 8+ (for dependencies)
- Git (for last modified dates)

### Development Setup

1. **Install Hugo dependencies:**
   ```bash
   cd professor/framework_code/hugo_config
   npm install
   ```

2. **Set up Hugo site structure:**
   ```bash
   # From repository root
   hugo new site hugo_site --config professor/framework_code/hugo_config/hugo.toml
   ```

3. **Copy theme files:**
   ```bash
   # Copy our Evangelion theme
   cp -r professor/framework_code/themes/default hugo_site/themes/
   ```

4. **Start development server:**
   ```bash
   cd hugo_site
   npm run dev
   ```

### Content Creation

**Create a new class note:**
```bash
hugo new class_notes/01_introduction/01_introduction.md
```

**Create homework assignment:**
```bash
hugo new class_notes/01_introduction/hw_01.md --kind homework
```

**Create appendix chapter:**
```bash
hugo new class_notes/A_advanced_topics/1_advanced_topics.md
```

## Framework Integration

### Automatic Features

The Hugo configuration automatically:
- **Generates navigation** from directory structure
- **Creates search index** from content metadata
- **Processes homework files** into separate navigation
- **Applies theme styling** from our Evangelion CSS
- **Renders math expressions** with MathJax
- **Shows last modified dates** from Git history

### Metadata Usage

Content files use YAML front matter that integrates with:
- **Navigation generation** (title, type, summary)
- **Search indexing** (tags, difficulty, prerequisites)
- **Course information** (author, estimated_time)
- **Theme features** (difficulty badges, reading time)

### Course Configuration

Site parameters can be overridden by:
1. **dna.yml** - Framework-level settings
2. **course.yml** - Course-specific metadata
3. **Environment variables** - Deployment settings

## Customization

### Theme Customization
- Modify `professor/framework_code/themes/default/` files
- Create new themes by copying the default theme folder
- Update `hugo.toml` `theme_name` parameter

### Content Structure
- Follow naming conventions from `naming_conventions.py`
- Use chapter structure validation from `chapter_structure.py`
- Maintain directory hierarchy for automatic navigation

### Search Configuration
- Customize search index in `hugo.toml` outputs
- Modify search parameters in `[params]` section
- Extend with additional metadata fields

## Production Deployment

### GitHub Pages
```bash
# Build optimized site
npm run build

# Deploy to GitHub Pages
# (Automated via GitHub Actions)
```

### Manual Deployment
```bash
# Build for production
hugo --minify --gc --config professor/framework_code/hugo_config/hugo.toml

# Upload public/ directory to web server
```

## Troubleshooting

### Common Issues

**Hugo version too old:**
```bash
hugo version
# Upgrade to Hugo Extended v0.120.0+
```

**Theme not found:**
```bash
# Ensure theme files are in themes/default/
# Check theme_name in hugo.toml
```

**Math not rendering:**
```bash
# Check MathJax configuration in hugo.toml
# Verify math syntax in content files
```

**Search not working:**
```bash
# Ensure JSON output format is enabled
# Check search index generation
```

## Development Scripts

- `npm run dev` - Development server with live reload
- `npm run build` - Production build with minification
- `npm run build:dev` - Development build with drafts
- `npm run clean` - Clean generated files
- `npm run test` - Run linting and validation
- `npm run preview` - Preview production build

## Integration with Framework

This Hugo configuration integrates with:
- **Naming convention validator** for content structure
- **Chapter structure validator** for navigation
- **Theme system** for visual customization
- **Course metadata parser** for dynamic content
- **Synchronization system** for professor ↔ student updates

For more information, see the main framework documentation in `professor/framework_documentation/`. 