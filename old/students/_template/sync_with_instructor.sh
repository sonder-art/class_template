#!/bin/bash
# ==============================================================================
#  sync_with_instructor.sh
#
#  Safely syncs course materials from the instructor's project ('uumami/')
#  and the shared `styles` directory into the student's project.
#
#  Features:
#  - Path-independent: Can be run from anywhere in the project.
#  - Safe: Asks for confirmation before making any changes.
#  - Non-destructive: Updates changed files and adds new ones, but never
#    deletes student's existing files or custom styles.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- ANSI Color Codes for better readability ---
COLOR_BLUE='\033[0;34m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_RED='\033[0;31m'
COLOR_NC='\033[0m' # No Color

echo -e "${COLOR_BLUE}--- STAGE 1: Verifying Paths ---${COLOR_NC}"

# 1. Determine the absolute paths, regardless of where the script is run from.
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
DEST_DIR="${SCRIPT_DIR}"
ROOT_DIR=$( cd -- "${SCRIPT_DIR}/../.." &> /dev/null && pwd )
INSTRUCTOR_CONTENT_DIR="${ROOT_DIR}/uumami"
SHARED_STYLES_DIR="${ROOT_DIR}/styles"

# 2. Confirm the determined paths with the user.
echo "This script will sync new files from the instructor's project to yours."
echo -e "  ${COLOR_GREEN}SOURCE (Content):${COLOR_NC} ${INSTRUCTOR_CONTENT_DIR}"
echo -e "  ${COLOR_GREEN}SOURCE (Styles):${COLOR_NC}  ${SHARED_STYLES_DIR}"
echo -e "  ${COLOR_YELLOW}DESTINATION (You):${COLOR_NC}  ${DEST_DIR}"
echo ""
read -p "Is this correct? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${COLOR_RED}Aborted.${COLOR_NC}"
    exit 1
fi

echo -e "\n${COLOR_BLUE}--- STAGE 2: Syncing Shared 'styles' Directory ---${COLOR_NC}"

# 3. Use rsync to safely update the styles directory.
# -a: archive mode (preserves permissions, etc.)
# -v: verbose (shows what's being copied)
# --ignore-existing: won't overwrite a file if the student has modified it.
#    Use --update if you want to overwrite student's file if yours is newer.
echo "Updating styles... (This will not overwrite your changes to existing files)"
rsync -av --ignore-existing "${SHARED_STYLES_DIR}/" "${DEST_DIR}/styles/"
echo "Styles sync complete."


echo -e "\n${COLOR_BLUE}--- STAGE 3: Analyzing for New Content Files (Dry Run) ---${COLOR_NC}"

# 4. Define exclusion patterns for files that should never be copied.
EXCLUDE_PATTERNS=(
    -path '*/_site/*'
    -path '*/.quarto/*'
    -path '*/__pycache__/*'
    -path '*/styles/*' # Exclude styles dir as it's handled by rsync now
    -name '*.pyc'
)

# 5. Find all files in the source directory, applying the exclusions.
SOURCE_FILES=()
while IFS= read -r -d $'\0' file; do
    SOURCE_FILES+=("$file")
done < <(find "$INSTRUCTOR_CONTENT_DIR" -type f \( "${EXCLUDE_PATTERNS[@]}" \) -prune -o -type f -print0)


# 6. Identify which of the source files are new and need to be copied.
FILES_TO_COPY=()
for src_file in "${SOURCE_FILES[@]}"; do
    # Calculate the corresponding path in the destination directory.
    relative_path="${src_file#"$INSTRUCTOR_CONTENT_DIR"/}"
    dest_file="${DEST_DIR}/${relative_path}"

    if [ ! -f "$dest_file" ]; then
        # If the file does not exist in the destination, add it to our list.
        FILES_TO_COPY+=("$relative_path")
    fi
done

# 7. Report the findings and ask for final confirmation before copying.
if [ ${#FILES_TO_COPY[@]} -eq 0 ]; then
    echo -e "${COLOR_GREEN}Your project is already up-to-date. No new content files to copy.${COLOR_NC}"
    exit 0
else
    echo "The following new content files will be copied into your project directory:"
    for rel_path in "${FILES_TO_COPY[@]}"; do
        echo -e "  - ${COLOR_GREEN}${rel_path}${COLOR_NC}"
    done
    echo ""
    echo -e "${COLOR_YELLOW}No existing files will be overwritten.${COLOR_NC}"
    read -p "Proceed with copy? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${COLOR_RED}Aborted.${COLOR_NC}"
        exit 1
    fi
fi


echo -e "\n${COLOR_BLUE}--- STAGE 4: Copying New Content Files ---${COLOR_NC}"

# 8. Execute the copy operation for each file identified in the dry run.
for rel_path in "${FILES_TO_COPY[@]}"; do
    src_file="${INSTRUCTOR_CONTENT_DIR}/${rel_path}"
    dest_file="${DEST_DIR}/${rel_path}"

    # Ensure the destination subdirectory exists before copying.
    mkdir -p "$(dirname "$dest_file")"

    # Copy the file.
    cp "$src_file" "$dest_file"
    echo "  Copied: ${rel_path}"
done

echo -e "\n${COLOR_GREEN}Sync complete. All new files have been copied.${COLOR_NC}"
exit 0 