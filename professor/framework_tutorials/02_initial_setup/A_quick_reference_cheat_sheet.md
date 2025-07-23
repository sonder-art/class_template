---
title: "Quick Reference Cheat Sheet"
type: "reference"
date: "2025-01-20"
author: "Framework Team"
summary: "Quick reference for common commands and workflows - perfect for daily use"
difficulty: "easy"
estimated_time: 2
tags: ["reference", "cheat-sheet", "commands", "quick-lookup"]
---

# 📋 Quick Reference Cheat Sheet

**Perfect for bookmarking!** The most common commands and workflows you'll use daily.

---

## 🚀 Essential Daily Commands

### Students (Most Common)
```bash
# 1. Get updates from instructor
cd /path/to/class_template
git fetch upstream && git merge upstream/main

# 2. Go to your directory and sync
cd students/YOUR-USERNAME
python3 professor/framework_code/scripts/manage.py --sync

# 3. Build and preview your work
python3 professor/framework_code/scripts/manage.py --build --dev
# Opens: http://localhost:1314

# 4. Save your work
cd ../../
git add students/YOUR-USERNAME/
git commit -m "Your message here"
git push origin main
```

### Professors (Most Common)
```bash
# 1. Work in professor directory
cd professor

# 2. Build and preview
python3 framework_code/scripts/manage.py --build --dev
# Opens: http://localhost:1313

# 3. Deploy updates (NEW OPTIONS!)
python3 framework_code/scripts/manage.py --publish         # Complete build + deploy
python3 framework_code/scripts/manage.py --build --deploy  # Same as above
python3 framework_code/scripts/manage.py --deploy          # Deploy only
```

---

## 🛠️ Management Script Quick Reference

### Single Actions
| Command | What It Does | Use When |
|---------|--------------|----------|
| `--status` | Show current state | Check before building |
| `--build` | Build website | After editing content |
| `--dev` | Start local server | Preview your work |
| `--sync` | Get professor updates | Students: get latest framework |
| `--clean` | Remove build files | Fix build problems |
| `--validate` | Check content format | Before committing |
| `--deploy` | Build and deploy to production | Professors: publish updates |
| `--publish` | **NEW!** Complete build + deploy | Professors: one-step publishing |

### Common Combinations
| Commands | What It Does | Perfect For |
|----------|--------------|-------------|
| `--build --dev` | Build and preview | Daily content work |
| `--build --deploy` | **NEW!** Build and publish | One-step deployment |
| `--sync --build` | Update and build | Students: get updates + build |
| `--sync --dev` | Update and preview | Students: quick preview |
| `--sync --build --dev` | Update, build, preview | Students: complete workflow |

---

## 📁 Directory Quick Navigation

### Know Where You Are
```bash
pwd                    # Show current directory
ls                     # List files here
ls students/           # List all student directories
```

### Quick Directory Jumps
```bash
# From anywhere in repository:
cd professor                           # Professor workspace
cd students/YOUR-USERNAME              # Your student workspace
cd professor/framework_code/scripts    # Scripts location

# From student directory:
cd ../../                              # Back to repository root
cd professor/framework_code/scripts    # Access management script
```

---

## 🔧 Git Workflow Cheat Sheet

### Initial Setup (One Time)
```bash
# After forking and cloning:
git remote add upstream https://github.com/INSTRUCTOR-USERNAME/class_template.git
git remote -v  # Verify (should see origin + upstream)
```

### Daily Git Workflow
```bash
# 1. Get instructor updates
git fetch upstream
git merge upstream/main

# 2. Work on your content...

# 3. Save and upload your work
git add students/YOUR-USERNAME/     # Add your changes
git status                          # Check what will be committed
git commit -m "Describe your work" # Save with message
git push origin main               # Upload to your GitHub
```

### Check Status
```bash
git status              # What changed?
git log --oneline -5    # Recent commits
git remote -v           # What remotes are set up?
```

---

## 🌐 Server Management

### Local Development Servers
| URL | Who Uses | Port | Command |
|-----|----------|------|---------|
| `http://localhost:1313` | Professors | 1313 | `manage.py --dev` from professor/ |
| `http://localhost:1314` | Students | 1314 | `manage.py --dev` from students/username/ |

### Server Problems
```bash
# Port busy? Kill existing servers:
pkill hugo

# Or use different port:
python3 professor/framework_code/scripts/manage.py --dev --port 8080
```

---

## 📝 Content Creation Quick Guide

### File Naming Rules
| Type | Example | Location |
|------|---------|----------|
| Class note | `01_intro_to_python.md` | `class_notes/` |
| Homework | `hw_01_variables.md` | anywhere |
| Code file | `01_a_intro_examples.py` | next to related .md |
| Appendix | `A_advanced_topics.md` | any chapter |

### Required Front Matter (Copy & Edit)
```yaml
---
title: "Your Title Here"
type: "note"  # note, homework, tutorial, reference
date: "2025-01-20"  # Today's date
author: "Your Name"
summary: "One sentence description"
---
```

---

## 🚨 Emergency Troubleshooting

### "Permission denied"
```bash
chmod +x students/start.sh
chmod +x professor/framework_code/scripts/manage.sh
```

### "Command not found: python3"
```bash
# Try just 'python' instead:
python professor/framework_code/scripts/manage.py --build
```

### "Hugo not found"
```bash
# Check if Hugo is installed:
hugo version

# If not installed, see: https://gohugo.io/installation/
```

### "Nothing to commit"
```bash
# Check you're adding the right files:
git status
git add students/YOUR-USERNAME/  # Add your specific directory
```

### Git Merge Conflicts
```bash
# If you get conflicts during merge:
git status  # Shows conflicted files
# Edit files to resolve conflicts (look for <<<< and >>>>)
git add .
git commit -m "Resolve merge conflicts"
```

### Start Over (Nuclear Option)
```bash
# Delete your changes and get clean copy:
git fetch upstream
git reset --hard upstream/main
git push origin main --force  # BE CAREFUL! This erases your work!
```

---

## 📱 One-Line Workflows

### Students: Complete Daily Workflow
```bash
cd class_template && git fetch upstream && git merge upstream/main && cd students/YOUR-USERNAME && python3 professor/framework_code/scripts/manage.py --sync --build --dev
```

### Professors: Quick Update & Deploy
```bash
cd professor && python3 framework_code/scripts/manage.py --publish
# OR (equivalent):
cd professor && python3 framework_code/scripts/manage.py --build --deploy
```

### Emergency Clean Build
```bash
python3 professor/framework_code/scripts/manage.py --clean --build --dev
```

---

## 📚 File Organization Rules

### ✅ Safe to Edit
- `students/YOUR-USERNAME/class_notes/` - Your notes
- `students/YOUR-USERNAME/homework/` - Your homework
- `students/YOUR-USERNAME/home.md` - Your homepage
- `professor/class_notes/` - Course content (professors)
- `professor/course.yml` - Course info (professors)

### ❌ Never Touch
- `framework_code/hugo_generated/` - Auto-built files
- Files starting with `00_` - Auto-generated
- `hugo.toml` - Auto-generated config
- `students/YOUR-USERNAME/framework_code/` - Gets overwritten

---

## 🔍 Quick Diagnostics

### Is Everything Working?
```bash
# Check basics:
pwd                                    # Where am I?
ls                                     # What's here?
git remote -v                          # Git setup OK?
python3 --version                      # Python works?
hugo version                           # Hugo installed?

# Check framework:
python3 professor/framework_code/scripts/manage.py --status

# Test build:
python3 professor/framework_code/scripts/manage.py --build
```

### Common Status Messages
- ✅ `Build complete` = Everything working
- ⚠️ `Hugo config missing` = Run setup script
- ❌ `Validation failed` = Fix front matter in content files
- 🔄 `Sync available` = Updates from instructor

---

**📌 Bookmark this page!** Most problems can be solved with these commands.

**Need more help?** See the [Complete Workflow Guide](01_complete_workflow_guide.md) for detailed explanations. 