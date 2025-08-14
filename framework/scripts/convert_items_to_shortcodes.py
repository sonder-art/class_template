#!/usr/bin/env python3
"""
Item Block Converter - Framework Pre-Build Processor
This script converts ITEM_START/ITEM_END blocks into Hugo shortcode calls
for natural in-place rendering of graded items.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
import logging
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ItemBlockConverter:
    """Converts ITEM_START/ITEM_END blocks to Hugo shortcode calls"""
    
    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir)
        self.processed_files: List[str] = []
        
        # Pattern to match ITEM_START/ITEM_END blocks in HTML comments
        self.item_pattern = re.compile(
            r'<!-- ITEM_START\s*\n(.*?)\nITEM_END -->',
            re.DOTALL | re.MULTILINE
        )
        
        # Legacy pattern support
        self.legacy_pattern = re.compile(
            r'<!-- HOMEWORK_ITEM_START\s*\n(.*?)\nHOMEWORK_ITEM_END -->',
            re.DOTALL | re.MULTILINE
        )
    
    def parse_item_metadata(self, metadata_text: str) -> Optional[Dict[str, str]]:
        """Parse the YAML-like metadata from an item block"""
        try:
            metadata = {}
            for line in metadata_text.strip().split('\n'):
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip()
                    value = value.strip()
                    metadata[key] = value
            return metadata
        except Exception as e:
            logger.warning(f"Failed to parse item metadata: {e}")
            return None
    
    def convert_item_block_to_shortcode(self, match) -> str:
        """Convert a single ITEM_START/ITEM_END block to a shortcode call"""
        metadata_text = match.group(1)
        metadata = self.parse_item_metadata(metadata_text)
        
        if not metadata:
            logger.warning("Invalid item metadata, keeping original block")
            return match.group(0)
        
        # Extract required fields
        constituent_slug = metadata.get('constituent_slug')
        item_id = metadata.get('item_id')
        
        if not constituent_slug or not item_id:
            logger.warning(f"Missing required fields (constituent_slug, item_id) in item block")
            return match.group(0)
        
        # Create shortcode call - ensure it's on its own line with proper spacing
        shortcode = f'{{{{< item "{constituent_slug}" "{item_id}" >}}}}'
        
        # No visible comments - metadata is in the JSON data file
        return f"\n{shortcode}\n"
    
    def process_file(self, file_path: Path) -> bool:
        """Process a single markdown file to convert ITEM blocks to shortcodes"""
        try:
            # Read the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            conversions_made = 0
            
            # Convert ITEM_START/ITEM_END blocks
            content = self.item_pattern.sub(self.convert_item_block_to_shortcode, content)
            conversions_made += len(self.item_pattern.findall(original_content))
            
            # Convert legacy HOMEWORK_ITEM blocks 
            content = self.legacy_pattern.sub(self.convert_item_block_to_shortcode, content)
            conversions_made += len(self.legacy_pattern.findall(original_content))
            
            # Remove the old item-display shortcode if it exists (since we're now using individual items)
            content = re.sub(r'\{\{\<\s*item-display\s*\>\}\}', 
                           '<!-- Items now display in-place where defined -->', 
                           content)
            
            if content != original_content:
                # Create backup
                backup_path = file_path.with_suffix(file_path.suffix + '.backup')
                shutil.copy2(file_path, backup_path)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                logger.info(f"Converted {conversions_made} item blocks in {file_path}")
                self.processed_files.append(str(file_path.relative_to(self.base_dir)))
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            return False
    
    def find_markdown_files(self, directory: Path) -> List[Path]:
        """Find all markdown files in directory recursively"""
        markdown_files = []
        for root, dirs, files in os.walk(directory):
            # Skip framework_code and other system directories
            root_path = Path(root)
            if any(part.startswith('.') or part in ['framework_code', 'hugo_generated', 'public'] 
                   for part in root_path.parts):
                continue
                
            for file in files:
                if file.endswith('.md'):
                    file_path = root_path / file
                    markdown_files.append(file_path)
        
        return markdown_files
    
    def process_all(self, target_directories: List[str] = None) -> Dict[str, int]:
        """Process all markdown files in the specified directories"""
        if target_directories is None:
            target_directories = ['class_notes', 'homework', 'framework_documentation', 
                                'framework_tutorials', 'personal_projects']
        
        results = {
            'files_processed': 0,
            'files_modified': 0,
            'total_conversions': 0
        }
        
        for dir_name in target_directories:
            dir_path = self.base_dir / dir_name
            if not dir_path.exists():
                logger.info(f"Directory {dir_name} does not exist, skipping")
                continue
            
            markdown_files = self.find_markdown_files(dir_path)
            logger.info(f"Found {len(markdown_files)} markdown files in {dir_name}")
            
            for file_path in markdown_files:
                results['files_processed'] += 1
                if self.process_file(file_path):
                    results['files_modified'] += 1
        
        logger.info(f"Conversion complete: {results['files_modified']} files modified out of {results['files_processed']} processed")
        return results

def main():
    """Main function"""
    # Get the base directory (should be professor/ or students/username/)
    current_dir = Path.cwd()
    
    # Look for framework_code directory to determine base directory
    if (current_dir / 'framework_code').exists():
        base_dir = current_dir
    elif (current_dir.parent / 'framework_code').exists():
        base_dir = current_dir.parent
    else:
        logger.error("Could not find framework_code directory. Run from professor/ or students/username/ directory.")
        return 1
    
    converter = ItemBlockConverter(base_dir)
    results = converter.process_all()
    
    if results['files_modified'] > 0:
        logger.info("Item block conversion completed successfully!")
        logger.info(f"Modified files: {converter.processed_files}")
        logger.info("Remember to rebuild the site to see the changes.")
    else:
        logger.info("No item blocks found to convert.")
    
    return 0

if __name__ == '__main__':
    exit(main())