# Student Workspace

This is your personal workspace within the class template framework.

## 🚀 Getting Started

**All commands are run from the repository root (../../ from this directory):**

1. **Navigate to repository root**:
   ```bash
   cd ../../
   ```

2. **Keep synchronized**: Run sync regularly to get class content updates
   ```bash
   ./manage.sh --sync
   ```

3. **Generate your site**: Build your personal website
   ```bash
   ./manage.sh --build
   ```

4. **View your site**: Open `hugo_generated/public/index.html` in repository root

5. **Development server**: Start live development server
   ```bash
   ./manage.sh --dev
   ```

## 📁 Directory Structure

- `class_notes/` - Your personal notes and solutions (synced from professor)
- `personal_projects/` - Your own projects and experiments
- `config.yml` - Your personal rendering preferences (copied for customization)
- `home.md` - Your homepage content
- `README.md` - This file with instructions

## 📝 Customization

You can:
- Modify `config.yml` for personal preferences (theme, colors, etc.)
- Edit `home.md` to customize your homepage
- Add your own content in `class_notes/` and `personal_projects/`
- Framework themes are shared at `../../framework/themes/`
- All builds use the shared framework at `../../framework/`

## 🔄 Staying Updated

**Important**: Always run commands from the repository root (../../)

```bash
cd ../../
./manage.sh --sync
```

The sync script will:
- ✅ Add new class content from the instructor  
- ✅ Update class_notes that haven't been modified
- ❌ **Never overwrite** your personal work (config.yml, home.md, personal content)
- ✅ Preserve content in `<!-- KEEP -->` blocks
- 🎯 **Only syncs class content** (not framework - that's shared)

## 🏗️ Framework Architecture

- **Build Configuration**: Root-level `build.yml` (configured for your workspace)
- **Framework**: Shared at repository root (`../../framework/`)
- **Build Output**: Shared at repository root (`../../hugo_generated/`)
- **Your Content**: Lives in this directory
- **Command Execution**: All commands run from repository root

## 🚨 Important Notes

- **Never run commands from this directory** - always use the repository root
- Your `build.yml` is at the repository root and configured for your workspace
- Personal files (`config.yml`, `home.md`) stay in your directory for customization

Happy learning! 🎉
