#!/usr/bin/env python3
"""
Item Parser - Framework Pre-Build Processor
This script parses markdown files to extract graded items and generates
the items configuration for the framework's grading system.

Architecture: Items → Constituents → Modules
"""

import os
import re
import yaml
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Item:
    """Represents a graded item parsed from markdown content"""
    
    def __init__(self, constituent_slug: str, item_id: str, points: float, 
                 due_date: Optional[str] = None, title: Optional[str] = None,
                 delivery_type: Optional[str] = None, important: bool = False,
                 instructions: Optional[str] = None):
        self.constituent_slug = constituent_slug
        self.item_id = item_id
        self.points = points
        self.due_date = due_date  # ISO 8601 format with timezone
        self.title = title
        self.delivery_type = delivery_type  # text|upload|url|code|presentation|video
        self.important = important
        self.instructions = instructions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'constituent_slug': self.constituent_slug,
            'item_id': self.item_id,
            'points': self.points,
            'due_date': self.due_date,
            'title': self.title,
            'delivery_type': self.delivery_type,
            'important': self.important,
            'instructions': self.instructions
        }

class ParsedItemFile:
    """Represents a markdown file containing parsed items"""
    
    def __init__(self, file_path: str, title: str, items: List[Item]):
        self.file_path = file_path
        self.title = title
        self.items = items
        self.parsed_at = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'file_path': self.file_path,
            'title': self.title,
            'parsed_at': self.parsed_at,
            'items': [item.to_dict() for item in self.items]
        }

class ItemParser:
    """Main parser class for extracting items from markdown files"""
    
    def __init__(self, class_notes_dir: str):
        self.class_notes_dir = Path(class_notes_dir)
        self.parsed_files: List[ParsedItemFile] = []
        
    def parse_all_content(self) -> List[ParsedItemFile]:
        """Parse all markdown files for graded items"""
        logger.info(f"Parsing items from {self.class_notes_dir}")
        
        # Find all markdown files recursively
        markdown_files = list(self.class_notes_dir.rglob("*.md"))
        
        for file_path in markdown_files:
            # Skip auto-generated index files
            if file_path.name.startswith("00_"):
                continue
                
            try:
                parsed_file = self._parse_file(file_path)
                if parsed_file.items:  # Only include files with graded items
                    self.parsed_files.append(parsed_file)
                    logger.info(f"Parsed {len(parsed_file.items)} items from {file_path}")
                
            except Exception as e:
                logger.error(f"Error parsing {file_path}: {e}")
                
        logger.info(f"Total files parsed: {len(self.parsed_files)}")
        return self.parsed_files
    
    def _parse_file(self, file_path: Path) -> ParsedItemFile:
        """Parse a single markdown file for graded items"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Extract title from frontmatter
        title = self._extract_title_from_frontmatter(content)
        
        # Parse graded items
        items = self._parse_items(content)
        
        # Convert file path to relative path from professor directory
        relative_path = str(file_path.relative_to(self.class_notes_dir.parent))
        
        return ParsedItemFile(relative_path, title, items)
    
    def _extract_title_from_frontmatter(self, content: str) -> str:
        """Extract title from YAML frontmatter"""
        frontmatter_match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
        
        if not frontmatter_match:
            return "Untitled Content"
            
        try:
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            return frontmatter.get('title', 'Untitled Content')
        except yaml.YAMLError:
            return "Untitled Content"
    
    def _parse_items(self, content: str) -> List[Item]:
        """Parse all item blocks from markdown content"""
        items = []
        
        # Generic item parsing: <!-- ITEM_START ... ITEM_END -->
        pattern = r'<!-- ITEM_START\s*\n(.*?)\nITEM_END -->'
        matches = re.finditer(pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in matches:
            item_block = match.group(1).strip()
            try:
                item = self._parse_item_block(item_block)
                if item:
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse item block: {e}")
                continue
        
        # Backward compatibility: HOMEWORK_ITEM_START blocks
        homework_pattern = r'<!-- HOMEWORK_ITEM_START\s*\n(.*?)\nHOMEWORK_ITEM_END -->'
        homework_matches = re.finditer(homework_pattern, content, re.MULTILINE | re.DOTALL)
        
        for match in homework_matches:
            item_block = match.group(1).strip()
            try:
                item = self._parse_item_block(item_block)
                if item:
                    items.append(item)
            except Exception as e:
                logger.warning(f"Failed to parse homework item block: {e}")
                continue
                
        return items
    
    def _parse_item_block(self, block: str) -> Optional[Item]:
        """Parse a single item block"""
        parsed_data = {}
        
        # Parse simple key: value pairs
        lines = [line.strip() for line in block.split('\n') if line.strip() and ':' in line and not line.startswith('#')]
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip().strip('"\'')  # Remove quotes
                
                # Handle boolean values
                if value.lower() in ('true', 'false'):
                    value = value.lower() == 'true'
                # Try to convert numeric values
                elif key == 'points':
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                        
                parsed_data[key] = value
        
        # Validate required fields
        required_fields = ['constituent_slug', 'item_id', 'points']
        for field in required_fields:
            if field not in parsed_data:
                logger.warning(f"Missing required field '{field}' in item")
                return None
        
        try:
            # Create Item object
            return Item(
                constituent_slug=parsed_data['constituent_slug'],
                item_id=parsed_data['item_id'], 
                points=float(parsed_data['points']),
                due_date=parsed_data.get('due_date'),
                title=parsed_data.get('title'),
                delivery_type=parsed_data.get('delivery_type'),
                important=parsed_data.get('important', False),
                instructions=parsed_data.get('instructions')
            )
        except (ValueError, KeyError) as e:
            logger.warning(f"Error creating Item: {e}")
            return None
    
    def generate_items_config(self, output_path: str) -> None:
        """Generate items configuration file for framework"""
        all_items = []
        
        for parsed_file in self.parsed_files:
            for item in parsed_file.items:
                item_dict = item.to_dict()
                item_dict['file_path'] = parsed_file.file_path
                item_dict['file_title'] = parsed_file.title
                all_items.append(item_dict)
        
        config = {
            'generated_at': datetime.now().isoformat(),
            'total_items': len(all_items),
            'total_files': len(self.parsed_files),
            'items': all_items,
            'files': [pf.to_dict() for pf in self.parsed_files]
        }
        
        # Write to output file
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
            
        logger.info(f"Generated items config: {output_path}")
        logger.info(f"Total items: {len(all_items)} from {len(self.parsed_files)} files")
        
        # Also copy config files to Hugo data directory
        self._copy_config_files_to_hugo_data(output_file.parent)
    
    def _copy_config_files_to_hugo_data(self, data_dir: Path) -> None:
        """Copy configuration files to Hugo data directory"""
        base_dir = self.class_notes_dir.parent
        
        config_files = [
            ('modules.yml', 'modules.yml'),
            ('constituents.yml', 'constituents.yml')
        ]
        
        for source_name, target_name in config_files:
            source_file = base_dir / source_name
            target_file = data_dir / target_name
            
            if source_file.exists():
                try:
                    import shutil
                    shutil.copy2(source_file, target_file)
                    logger.info(f"Copied {source_name} to Hugo data directory")
                except Exception as e:
                    logger.warning(f"Failed to copy {source_name}: {e}")
            else:
                logger.warning(f"Config file {source_name} not found")

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Parse graded items from markdown files')
    parser.add_argument('--class-notes-dir', default='class_notes', 
                       help='Directory containing class notes (default: class_notes)')
    parser.add_argument('--output-dir', default='framework_code/hugo_generated/data',
                       help='Output directory for generated config (default: framework_code/hugo_generated/data)')
    parser.add_argument('--output-file', default='items.json',
                       help='Output filename (default: items.json)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize parser
    parser_instance = ItemParser(args.class_notes_dir)
    
    # Parse all files
    parsed_files = parser_instance.parse_all_content()
    
    if not parsed_files:
        logger.warning("No items found in class_notes directory")
        return
    
    # Generate configuration
    output_path = os.path.join(args.output_dir, args.output_file)
    parser_instance.generate_items_config(output_path)
    
    print(f"✅ Successfully parsed items:")
    print(f"   📁 Files processed: {len(parsed_files)}")
    print(f"   📝 Items found: {sum(len(pf.items) for pf in parsed_files)}")
    print(f"   💾 Config saved: {output_path}")

if __name__ == '__main__':
    main()