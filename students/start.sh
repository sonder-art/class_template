#!/bin/bash
# Student Directory Initialization Script
# Creates a new self-contained student workspace following framework principles
# This is the ONLY manual setup - everything else goes through sync system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🎓 Student Directory Initialization${NC}"
echo "======================================"

# Check if we're in the students directory
if [ "$(basename "$PWD")" != "students" ]; then
    echo -e "${RED}❌ Error: This script must be run from the 'students/' directory${NC}"
    echo "Current directory: $PWD"
    exit 1
fi

# Check if professor directory exists
if [ ! -d "../professor" ]; then
    echo -e "${RED}❌ Error: Professor directory not found${NC}"
    echo "This script must be run from a class template repository"
    exit 1
fi

# Get student username
if [ $# -eq 1 ]; then
    STUDENT_NAME="$1"
else
    echo -e "${YELLOW}📝 Enter your GitHub username (this will be your directory name):${NC}"
    read -p "Username: " STUDENT_NAME
fi

# Validate username
if [ -z "$STUDENT_NAME" ]; then
    echo -e "${RED}❌ Error: Username cannot be empty${NC}"
    exit 1
fi

# Check if directory already exists
if [ -d "$STUDENT_NAME" ]; then
    echo -e "${RED}❌ Error: Directory '$STUDENT_NAME' already exists${NC}"
    echo "Use the sync script to update an existing directory"
    exit 1
fi

echo -e "${BLUE}📁 Creating student directory: ${NC}$STUDENT_NAME"

# Create student directory
mkdir -p "$STUDENT_NAME"
cd "$STUDENT_NAME"

echo -e "${YELLOW}📋 Setting up self-contained workspace...${NC}"

# Copy all files needed for self-contained operation
cp "../../professor/course.yml" .
cp "../../professor/config.yml" .
cp "../../professor/home.md" .
cp "../../professor/manage.sh" .

# Make manage.sh executable
chmod +x manage.sh

# Create student-specific directories
mkdir -p "class_notes"
mkdir -p "personal_projects"
mkdir -p "homework"

# Create student-specific README
cat > README.md << 'EOF'
# Student Workspace

This is your personal workspace within the class template framework.

## 🚀 Getting Started

1. **Keep synchronized**: Run the sync script regularly to get updates
   ```bash
   python3 framework_code/scripts/sync_student.py
   ```

2. **Generate your site**: Build your personal website
   ```bash
   ./manage.sh --build
   ```
   
   Or manually:
   ```bash
   python3 framework_code/scripts/generate_hugo_config.py
   hugo
   ```

3. **View your site**: Open `framework_code/hugo_generated/index.html`

## 📁 Directory Structure

- `class_notes/` - Your personal notes and solutions
- `homework/` - Homework assignments and solutions  
- `personal_projects/` - Your own projects and experiments
- `framework_code/` - Framework tools (synced from instructor)
- `manage.sh` - Main build tool (same as instructor)
- `course.yml` - Class metadata (customize for your workspace)
- `config.yml` - Your personal rendering preferences

## 📝 Customization

You can:
- Modify `config.yml` for personal preferences (theme, colors, etc.)
- Modify `course.yml` to customize course metadata for your workspace
- Add your own content in any directory
- Create your own themes by copying from `framework_code/themes/`

## 🔄 Staying Updated

The sync script will:
- ✅ Add new content from the instructor
- ✅ Update unchanged files you haven't modified
- ❌ **Never overwrite** your personal work
- ✅ Preserve content in `<!-- KEEP -->` blocks

## 🚫 Important Rules

- **Never modify** files in `framework_code/` directly
- **Only work** within your student directory
- **Use the sync script** for all updates

Happy learning! 🎉
EOF

echo -e "${YELLOW}🔄 Running initial sync...${NC}"

# Run initial sync from repository root with automatic confirmation
cd ../../
echo -e "$STUDENT_NAME\ny" | python3 professor/framework_code/scripts/sync_student.py

# Go back to student directory
cd "students/$STUDENT_NAME"

echo -e "${YELLOW}🔧 Running initial build...${NC}"

# Run initial build using the framework's build system
./manage.sh --validate --force

echo -e "${GREEN}✅ Student workspace initialized successfully!${NC}"
echo ""
echo -e "${BLUE}📋 What was created:${NC}"
echo "• Self-contained directory: students/$STUDENT_NAME/"
echo "• Complete framework tools (manage.sh, framework_code/)"
echo "• Personal configuration files (course.yml, config.yml)"
echo "• Basic directory structure for your work"
echo "• Initial framework validation completed"
echo ""
echo -e "${PURPLE}🚀 Next steps:${NC}"
echo "1. Customize your config.yml and course.yml preferences"
echo "2. Start adding content to class_notes/ and homework/"
echo "3. Run './manage.sh --build' to build your personal website"
echo "4. Run './manage.sh --dev' to start development server"
echo "5. Use the sync script regularly to get instructor updates"
echo ""
echo -e "${GREEN}🎉 Happy learning!${NC}" 