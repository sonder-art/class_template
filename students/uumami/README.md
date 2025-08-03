# Student Workspace

This is your personal workspace within the class template framework.

## 🚀 Getting Started

1. **Keep synchronized**: Run the sync script regularly to get updates
   ```bash
   python3 framework_code/scripts/sync_student.py
   ```

2. **Generate your site**: Build your personal website
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
- `course.yml` - Class metadata (synced from instructor)
- `config.yml` - Your personal rendering preferences

## 📝 Customization

You can:
- Modify `config.yml` for personal preferences (theme, colors, etc.)
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
