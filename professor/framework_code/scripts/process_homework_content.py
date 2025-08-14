#!/usr/bin/env python3
"""
Homework Content Processor - Simple UI Generation
Processes markdown files to automatically wrap homework items with beautiful UI
This script transforms simple YAML metadata into beautiful HTML cards during build
"""

import os
import re
from pathlib import Path
from datetime import datetime

class HomeworkContentProcessor:
    """Processes homework content to generate beautiful UI from simple YAML metadata"""
    
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        
    def process_all_homework_files(self) -> int:
        """Process all markdown files containing homework items"""
        class_notes_dir = self.base_dir / "class_notes"
        if not class_notes_dir.exists():
            return 0
            
        processed_count = 0
        
        for md_file in class_notes_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Only process files that have HOMEWORK_ITEM blocks and haven't been processed
                if 'HOMEWORK_ITEM_START' in content and not '<div class="homework-item"' in content:
                    if self.process_homework_file(md_file):
                        processed_count += 1
                        print(f"✨ Processed: {md_file.relative_to(self.base_dir)}")
                        
            except Exception as e:
                print(f"⚠️  Error processing {md_file}: {e}")
                continue
                
        return processed_count
    
    def process_homework_file(self, file_path: Path) -> bool:
        """Process a single homework file to generate beautiful UI"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Process each homework item block
            pattern = r'(### Item \d+: [^\n]+\n\n<!-- HOMEWORK_ITEM_START\s*\n(.*?)\nHOMEWORK_ITEM_END -->\n\n)(.*?)(?=### Item \d+:|---|\Z)'
            
            def replace_homework_item(match):
                header_and_metadata = match.group(1)
                yaml_content = match.group(2).strip()
                item_content = match.group(3).strip()
                
                # Parse YAML metadata
                metadata = self.parse_yaml_metadata(yaml_content)
                
                # Generate beautiful HTML card
                html_card = self.generate_homework_card(metadata, item_content)
                
                return html_card
            
            # Replace all homework items with beautiful cards
            processed_content = re.sub(pattern, replace_homework_item, content, flags=re.MULTILINE | re.DOTALL)
            
            # Write processed content back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(processed_content)
                
            return True
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return False
    
    def parse_yaml_metadata(self, yaml_content: str) -> dict:
        """Parse simple YAML metadata into dictionary"""
        metadata = {}
        
        for line in yaml_content.split('\n'):
            line = line.strip()
            if ':' in line and not line.startswith('#'):
                key, value = line.split(':', 1)
                key = key.strip()
                value = value.strip()
                
                # Convert numeric values
                try:
                    if '.' in value:
                        value = float(value)
                    else:
                        value = int(value)
                except ValueError:
                    pass
                    
                metadata[key] = value
                
        return metadata
    
    def generate_homework_card(self, metadata: dict, content: str) -> str:
        """Generate beautiful homework card HTML from metadata and content"""
        
        # Get metadata values
        title = metadata.get('title', metadata.get('item_id', 'Homework Item'))
        points = int(metadata.get('points', 0))
        due_date = metadata.get('due_date', '')
        submission_type = metadata.get('submission_type', 'text')
        item_id = metadata.get('item_id', 'homework_item')
        
        # Get submission type icon
        icons = {
            "url": "🔗",
            "screenshot": "📸", 
            "code_and_demo": "💻",
            "report_and_code": "📝",
            "file": "📎",
            "text": "📝"
        }
        icon = icons.get(submission_type, "📋")
        
        # Calculate due date class
        due_date_class = self.get_due_date_class(due_date)
        due_date_formatted = self.format_due_date(due_date)
        
        # Format submission type label
        submission_label = submission_type.replace('_', ' ').title()
        
        # Generate the HTML card
        html_card = f'''
<!-- HOMEWORK_ITEM_START
constituent_slug: {metadata.get('constituent_slug', '')}
item_id: {item_id}
points: {points}
due_date: {due_date}
submission_type: {submission_type}
title: {title}
HOMEWORK_ITEM_END -->

<div class="homework-item" data-item-id="{item_id}">
<div class="homework-header">
<h3 class="homework-title">{icon} {title}</h3>
<div class="homework-meta">
<div class="meta-item">
<span class="meta-label">Points</span>
<span class="meta-value points-value">{points}</span>
</div>
<div class="meta-item">
<span class="meta-label">Due Date</span>
<span class="meta-value due-date-value {due_date_class}">{due_date_formatted}</span>
</div>
<div class="meta-item">
<span class="meta-label">Submission</span>
<span class="meta-value"><span class="submission-type-badge {submission_type}">{submission_label}</span></span>
</div>
</div>
</div>

<div class="homework-content">
<div class="homework-instructions">
<h4>📋 Instructions</h4>
{content}
</div>
</div>
</div>
'''
        
        return html_card.strip()
    
    def get_due_date_class(self, due_date_str: str) -> str:
        """Calculate CSS class based on due date urgency"""
        try:
            due_date = datetime.strptime(str(due_date_str), '%Y-%m-%d')
            now = datetime.now()
            days_until_due = (due_date - now).days
            
            if days_until_due < 2:
                return "due-urgent"
            elif days_until_due < 7:
                return "due-soon"
            else:
                return "due-ok"
        except:
            return "due-ok"
    
    def format_due_date(self, due_date_str: str) -> str:
        """Format due date for display"""
        try:
            due_date = datetime.strptime(str(due_date_str), '%Y-%m-%d')
            return due_date.strftime('%b %d, %Y')
        except:
            return str(due_date_str)

def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) > 1:
        base_dir = sys.argv[1]
    else:
        base_dir = os.getcwd()
    
    processor = HomeworkContentProcessor(base_dir)
    processed_count = processor.process_all_homework_files()
    
    if processed_count > 0:
        print(f"✅ Processed {processed_count} homework files with automatic UI generation")
    else:
        print("ℹ️  No homework files needed processing")

if __name__ == "__main__":
    main()