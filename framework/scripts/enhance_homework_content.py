#!/usr/bin/env python3
"""
Homework Content Enhancement Script
Automatically enhances markdown files with homework items by wrapping them in beautiful UI components.
This script processes markdown files and replaces simple homework content with styled cards.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

class HomeworkContentEnhancer:
    """Enhances homework markdown files with automatic UI generation"""
    
    def __init__(self, professor_dir: str):
        self.professor_dir = Path(professor_dir)
        self.homework_data_file = self.professor_dir / "framework_code" / "hugo_generated" / "data" / "homework_items.json"
        self.modules_data_file = self.professor_dir / "modules.yml"
        self.constituents_data_file = self.professor_dir / "constituents.yml"
        
    def load_homework_data(self) -> Dict[str, Any]:
        """Load homework data from JSON file"""
        if not self.homework_data_file.exists():
            return {}
            
        with open(self.homework_data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_due_date_class(self, due_date_str: str) -> str:
        """Calculate CSS class based on due date urgency"""
        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
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
    
    def get_submission_icon(self, submission_type: str) -> str:
        """Get emoji icon for submission type"""
        icons = {
            "url": "🔗",
            "screenshot": "📸", 
            "code_and_demo": "💻",
            "report_and_code": "📝",
            "file": "📎",
            "text": "📝"
        }
        return icons.get(submission_type, "📋")
    
    def enhance_homework_file(self, file_path: Path) -> bool:
        """Enhance a single homework file with automatic UI generation"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Load homework data
            homework_data = self.load_homework_data()
            if not homework_data or 'files' not in homework_data:
                return False
            
            # Find homework items for this file
            relative_path = str(file_path.relative_to(self.professor_dir))
            file_items = []
            
            for file_data in homework_data['files']:
                if file_data['file_path'] == relative_path:
                    file_items = file_data['items']
                    break
            
            if not file_items:
                return False
            
            # Process each homework item
            enhanced_content = content
            
            for item in file_items:
                # Find the homework item section
                item_pattern = rf'### Item \d+: ([^\n]+)\s*\n\s*<!-- graded_item:\s*\nconstituent_slug: "{re.escape(item["constituent_slug"])}"\s*\nitem_id: "{re.escape(item["item_id"])}"[^>]*-->\s*\n(.*?)(?=### Item \d+:|---|\Z)'
                
                def replace_homework_section(match):
                    title = match.group(1)
                    content_section = match.group(2).strip()
                    
                    # Get due date info
                    due_date_class = self.get_due_date_class(item.get('due_date', ''))
                    due_date_formatted = item.get('due_date', 'TBD')
                    if due_date_formatted != 'TBD':
                        try:
                            due_date_obj = datetime.strptime(due_date_formatted, '%Y-%m-%d')
                            due_date_formatted = due_date_obj.strftime('%b %d, %Y')
                        except:
                            pass
                    
                    # Get submission type info
                    submission_type = item.get('submission_type', 'text')
                    submission_icon = self.get_submission_icon(submission_type)
                    submission_label = submission_type.replace('_', ' ').title()
                    
                    # Parse content sections
                    instructions = ""
                    requirements = ""
                    grading = ""
                    
                    # Split content by bold headers
                    sections = re.split(r'\*\*(.*?)\*\*', content_section)
                    current_section = "instructions"
                    
                    for i, section in enumerate(sections):
                        if i % 2 == 1:  # This is a header
                            if "submission" in section.lower() or "requirement" in section.lower():
                                current_section = "requirements"
                            elif "grading" in section.lower() or "criteria" in section.lower():
                                current_section = "grading"
                        else:  # This is content
                            section = section.strip()
                            if section:
                                if current_section == "requirements":
                                    requirements += section
                                elif current_section == "grading":
                                    grading += section
                                else:
                                    instructions += section
                    
                    # Build the enhanced HTML
                    enhanced_html = f'''
<!-- graded_item:
constituent_slug: "{item['constituent_slug']}"
item_id: "{item['item_id']}"
points: {item['points']}
due_date: "{item['due_date']}"
submission_type: "{item['submission_type']}"
-->

<div class="homework-item" data-item-id="{item['item_id']}">
<div class="homework-header">
<h3 class="homework-title">{submission_icon} {title}</h3>
<div class="homework-meta">
<div class="meta-item">
<span class="meta-label">Points</span>
<span class="meta-value points-value">{int(item['points'])}</span>
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

<div class="homework-content">'''
                    
                    if instructions:
                        enhanced_html += f'''
<div class="homework-instructions">
<h4>📋 What You Need to Do</h4>
{instructions}
</div>'''
                    
                    if requirements:
                        enhanced_html += f'''
<div class="homework-requirements">
<h4>✅ Submission Requirements</h4>
{requirements}
</div>'''
                    
                    if grading:
                        enhanced_html += f'''
<div class="homework-grading">
<h4>🎯 Grading Criteria ({int(item['points'])} points total)</h4>
{grading}
</div>'''
                    
                    enhanced_html += '''
</div>
</div>
'''
                    
                    return enhanced_html
                
                enhanced_content = re.sub(item_pattern, replace_homework_section, enhanced_content, flags=re.MULTILINE | re.DOTALL)
            
            # Write enhanced content back to file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enhanced_content)
                
            return True
            
        except Exception as e:
            print(f"Error enhancing {file_path}: {e}")
            return False
    
    def enhance_all_homework_files(self) -> int:
        """Enhance all homework files in the class_notes directory"""
        class_notes_dir = self.professor_dir / "class_notes"
        if not class_notes_dir.exists():
            return 0
        
        enhanced_count = 0
        
        # Find all markdown files that contain graded_item comments
        for md_file in class_notes_dir.rglob("*.md"):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'graded_item:' in content and not '<div class="homework-item"' in content:
                    if self.enhance_homework_file(md_file):
                        enhanced_count += 1
                        print(f"Enhanced: {md_file.relative_to(self.professor_dir)}")
                        
            except Exception as e:
                print(f"Error processing {md_file}: {e}")
                continue
        
        return enhanced_count

def main():
    """Main function to enhance homework files"""
    import sys
    
    if len(sys.argv) > 1:
        professor_dir = sys.argv[1]
    else:
        professor_dir = os.getcwd()
    
    enhancer = HomeworkContentEnhancer(professor_dir)
    enhanced_count = enhancer.enhance_all_homework_files()
    
    if enhanced_count > 0:
        print(f"✅ Enhanced {enhanced_count} homework files with beautiful UI")
    else:
        print("ℹ️  No homework files needed enhancement")

if __name__ == "__main__":
    main()