---
title: "Terminal Flags Quick Reference"
type: "reference"
date: "2025-01-16"
author: "Framework Team"
summary: "Quick reference for common GitHub and Hugo command-line flags and options"
difficulty: "easy"
estimated_time: 5
---


*A simple reference for the most useful command-line flags when working with GitHub and Hugo.*

## 🐙 GitHub CLI Commands

### Basic Repository Operations
```bash
# Clone with specific branch
git clone -b branch-name https://github.com/user/repo.git

# Force push (use with caution!)
git push --force-with-lease

# Show commit history in one line
git log --oneline --graph --decorate

# Check status with short format
git status -s
```

### Useful Git Flags
- `--dry-run` - Preview what would happen without making changes
- `--verbose` - Show detailed output
- `--quiet` - Suppress most output
- `--force-with-lease` - Safer alternative to `--force`

## 🏗️ Hugo Command Flags

### Development Server
```bash
# Start development server
hugo server

# Start with drafts included
hugo server -D

# Start on specific port
hugo server --port 1314

# Start with fast rebuild
hugo server --disableFastRender=false
```

### Building Sites
```bash
# Build for production
hugo --minify

# Build to specific directory
hugo --destination docs/

# Build with base URL
hugo --baseURL https://mysite.com/

# Show build statistics
hugo --templateMetrics
```

### Useful Hugo Flags
- `-D, --buildDrafts` - Include draft content
- `--minify` - Minify HTML, CSS, JS
- `--verbose` - Detailed logging
- `--quiet` - Minimal output
- `--cleanDestinationDir` - Remove files from destination not found in static dirs

## 💡 Pro Tips

1. **Use `--help`** - Every command has help: `git --help`, `hugo server --help`
2. **Combine flags** - Many flags can be used together: `hugo server -D --port 1314`
3. **Check versions** - Use `git --version` and `hugo version` for troubleshooting

## 🔗 Quick Links

- [Git Documentation](https://git-scm.com/docs)
- [Hugo CLI Reference](https://gohugo.io/commands/)
- [GitHub CLI Handbook](https://cli.github.com/manual/) 