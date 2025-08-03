---
title: "Running the Setup Script"
type: "tutorial"
date: "2024-01-15"
author: "Framework Team"
summary: "Step-by-step guide to using start.sh for initial student directory setup"
difficulty: "easy"
estimated_time: 3
tags: ["setup", "initialization", "getting-started"]
---

# Running the Setup Script

The framework includes an automated setup script that creates your personal student directory with all necessary files. This tutorial walks you through the one-time setup process.

## What the Script Does

The `students/start.sh` script automatically:

1. **Creates your directory** at `students/<your-username>/`
2. **Copies essential files** from professor (config.yml, course.yml, home.md)
3. **Creates your content directories** (class_notes/, personal_projects/, homework/)
4. **Runs initial sync** to get current framework code
5. **Generates your Hugo config** for immediate site building

## Running the Script

From the repository root directory, run:

```bash
./students/start.sh <your-username>
```

**Important**: Use your exact GitHub username as the parameter.

### Example

If your GitHub username is `alice`, run:

```bash
./students/start.sh alice
```

## What You'll See

The script provides clear output showing each step:

```
🚀 Setting up student directory for: alice
📁 Creating directory structure...
📋 Copying configuration files...
📚 Creating content directories...
🔄 Running initial sync...
⚙️ Generating Hugo configuration...
✅ Setup complete! Your directory is ready at students/alice/
```

## After Setup

Once the script completes, you'll have:

- **Your own directory**: `students/<username>/`
- **Working configuration**: Ready for Hugo site generation
- **Current framework**: All latest code and themes
- **Content structure**: Organized directories for your work

## Next Steps

After running the setup script:

1. **Navigate to your directory**: `cd students/<username>/`
2. **Build your site**: `hugo`
3. **View your site**: `python3 -m http.server 8080 -d framework_code/hugo_generated/`
4. **Start adding content** to your class_notes/ directory

## Troubleshooting

**Script not executable?**
```bash
chmod +x students/start.sh
```

**Wrong directory?**
Make sure you're in the repository root (where you can see the `students/` folder).

**Permission errors?**
Ensure you have write permissions in the repository directory.

The setup script handles all the complex initialization automatically, so you can focus on learning and creating content rather than configuration management. 