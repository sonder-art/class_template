---
title: "Running the Setup Script"
type: "tutorial"
date: "2025-01-20"
author: "Framework Team"
summary: "Focused guide on using the start.sh script for initial student directory setup"
difficulty: "easy"
estimated_time: 3
tags: ["setup", "initialization", "getting-started"]
---


> **📋 For the Complete Workflow:** See [Complete Workflow Guide](01_complete_workflow_guide.md) for the full step-by-step process from fork to first site.

The framework includes an automated setup script that creates your personal student directory with all necessary files. This tutorial focuses specifically on the setup script itself.

## What the Script Does

The `students/start.sh` script automatically:

1. **Creates your directory** at `students/<your-username>/`
2. **Copies essential files** from professor (config.yml, course.yml, home.md)
3. **Creates your content directories** (class_notes/, personal_projects/, homework/)
4. **Runs initial sync** to get current framework code
5. **Generates your Hugo config** for immediate site building

## Prerequisites

Before running the setup script, make sure you have:
- ✅ Forked the repository 
- ✅ Cloned your fork to your computer
- ✅ Set up upstream remote (connection to instructor's repository)
- ✅ Fetched latest updates from instructor

> **Need help with prerequisites?** See [Complete Workflow Guide](01_complete_workflow_guide.md) for detailed instructions.

## Running the Script

From the repository root directory (where you can see the `students/` folder):

```bash
# Check you're in the right place
ls
# You should see: professor/ students/ dna.yml README.md etc.

# Run the setup script with YOUR GitHub username
./students/start.sh YOUR-USERNAME
```

**⚠️ Important:** Use your exact GitHub username as the parameter.

### Example

If your GitHub username is `alice`:

```bash
./students/start.sh alice
```

## What You'll See

The script provides clear output showing each step:

```
🚀 Setting up student directory for: alice
📁 Creating directory structure...
   ✓ Created students/alice/
   ✓ Created students/alice/class_notes/
   ✓ Created students/alice/homework/
   ✓ Created students/alice/personal_projects/

📋 Copying configuration files...
   ✓ Copied professor/config.yml → students/alice/config.yml
   ✓ Copied professor/course.yml → students/alice/course.yml
   ✓ Copied professor/home.md → students/alice/home.md

📚 Creating content directories...
   ✓ Content structure ready

🔄 Running initial sync...
   ✓ Framework code synced from professor
   ✓ Themes and components updated

⚙️ Generating Hugo configuration...
   ✓ hugo.toml created and configured

✅ Setup complete! Your directory is ready at students/alice/

Next steps:
1. Navigate to your directory: cd students/alice/
2. Build your site: python3 professor/framework_code/scripts/manage.py --build
3. Preview your site: python3 professor/framework_code/scripts/manage.py --dev
```

## After Setup: Your Directory Structure

Once the script completes, you'll have:

```
students/alice/
├── class_notes/              # Your class notes and assignments
├── homework/                 # Your homework submissions
├── personal_projects/        # Your side projects
├── framework_code/           # Framework tools (synced from professor)
│   ├── themes/
│   ├── components/
│   ├── scripts/
│   └── ...
├── config.yml               # Your rendering preferences (copied from professor)
├── course.yml               # Course information (copied from professor)
├── home.md                  # Your personal homepage (copied from professor)
└── hugo.toml                # Auto-generated Hugo configuration
```

## Script Options and Behavior

### Basic Usage
```bash
./students/start.sh USERNAME
```

### What If Directory Already Exists?
The script will check if the directory already exists:

```bash
./students/start.sh alice
# Output: ⚠️ Directory students/alice/ already exists!
#         Use --force to overwrite or choose a different username.
```

### Force Overwrite (Use Carefully)
```bash
./students/start.sh alice --force
# This will DELETE existing directory and create fresh one
```

**⚠️ Warning:** `--force` will completely remove your existing directory and all your work. Only use if you want to start completely over.

## Troubleshooting

### "Permission denied" Error
```bash
chmod +x students/start.sh
./students/start.sh YOUR-USERNAME
```

### "No such file or directory" 
Make sure you're in the repository root:
```bash
# Check current location
pwd
# Should end with: .../class_template

# List files to verify
ls
# Should see: professor/ students/ dna.yml etc.
```

### Script Fails During Sync
If the sync step fails:
```bash
# Try manual sync after setup
cd students/YOUR-USERNAME
python3 professor/framework_code/scripts/manage.py --sync
```

### Hugo Config Generation Fails
```bash
# Manually generate Hugo config
cd students/YOUR-USERNAME
python3 professor/framework_code/scripts/generate_hugo_config.py
```

## Next Steps After Running Setup

1. **Navigate to your directory:**
   ```bash
   cd students/YOUR-USERNAME
   ```

2. **Build your first site:**
   ```bash
   python3 professor/framework_code/scripts/manage.py --build --dev
   ```

3. **View your site:** Open `http://localhost:1314` in your browser

4. **Start creating content:** Add files to `class_notes/` directory

5. **Learn the daily workflow:** See [Complete Workflow Guide](01_complete_workflow_guide.md)

## What the Setup Script Does NOT Do

The setup script only handles initial directory creation. It does NOT:
- ❌ Fork the repository for you
- ❌ Clone repositories 
- ❌ Set up Git remotes
- ❌ Install Hugo or Python
- ❌ Manage Git commits/pushes

For complete setup including these steps, see [Complete Workflow Guide](01_complete_workflow_guide.md).

---

The setup script handles all the complex initialization automatically, so you can focus on learning and creating content rather than configuration management.

**Ready for the full workflow?** Continue with [Complete Workflow Guide](01_complete_workflow_guide.md) to learn the complete process from fork to deployment. 