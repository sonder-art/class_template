#!/usr/bin/env python3
"""
Class Context Injection Script
This script injects class-specific identifiers and security context into Hugo templates
during the build process, enabling secure frontend operations
"""

import os
import yaml
import json
import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console


class ClassContextInjector:
    """Injects class context into Hugo configuration and templates"""
    
    def __init__(self, project_root: Path, console: Console = None):
        self.project_root = Path(project_root)
        self.console = console or Console()
        
        # Class context data
        self.class_context = {}
        self.supabase_config = {}
        
    def inject_class_context(self, target_directory: str = "professor") -> bool:
        """Main method to inject class context into build
        
        Args:
            target_directory: Directory being built (professor, students/username)
            
        Returns:
            bool: True if successful, False otherwise
        """
        
        self.console.print(f"🔧 Injecting class context for: {target_directory}")
        
        # Step 1: Extract class context from configuration files
        if not self._extract_class_context(target_directory):
            return False
        
        # Step 2: Get Supabase configuration
        if not self._get_supabase_config():
            return False
        
        # Step 3: Inject into Hugo configuration
        if not self._inject_hugo_config():
            return False
        
        # Step 4: Generate Hugo data files
        if not self._generate_hugo_data_files():
            return False
        
        # Step 5: Create JavaScript configuration
        if not self._create_js_config_file():
            return False
        
        self.console.print("✅ Class context injection completed")
        return True
    
    def _extract_class_context(self, target_directory: str) -> bool:
        """Extract class context from dna.yml and course.yml"""
        
        try:
            # Read dna.yml for repository and professor information
            dna_file = self.project_root / "dna.yml"
            if not dna_file.exists():
                self.console.print("❌ dna.yml not found")
                return False
            
            with open(dna_file, 'r') as f:
                dna_config = yaml.safe_load(f)
            
            # Read course.yml for class-specific information
            course_files = [
                self.project_root / target_directory / "course.yml",
                self.project_root / "class_template" / "course.yml",
                self.project_root / "course.yml"
            ]
            
            course_config = {}
            for course_file in course_files:
                if course_file.exists():
                    with open(course_file, 'r') as f:
                        course_config = yaml.safe_load(f)
                    break
            
            # Extract class information
            repo_name = self._get_repo_name()
            professor_github_id = dna_config.get('professor_profile', 'unknown')
            professor_github_username = professor_github_id  # Same for now
            
            # Generate or get class_id (could be deterministic hash of repo + professor)
            import hashlib
            class_id_source = f"{repo_name}:{professor_github_id}"
            class_id = hashlib.sha256(class_id_source.encode()).hexdigest()[:16]
            
            self.class_context = {
                'class_id': class_id,
                'repo_name': repo_name,
                'class_name': course_config.get('course', {}).get('name', repo_name),
                'professor_github_id': professor_github_id,
                'professor_github_username': professor_github_username,
                'target_directory': target_directory,
                'build_mode': 'professor' if target_directory == 'professor' else 'student',
                'semester': course_config.get('course', {}).get('semester', 'Unknown'),
                'year': course_config.get('course', {}).get('year', 'Unknown')
            }
            
            self.console.print(f"📋 Class context extracted:")
            self.console.print(f"   Repository: {repo_name}")
            self.console.print(f"   Class ID: {class_id}")
            self.console.print(f"   Professor: {professor_github_username}")
            self.console.print(f"   Build mode: {self.class_context['build_mode']}")
            
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error extracting class context: {e}")
            return False
    
    def _get_repo_name(self) -> str:
        """Get repository name from git or directory name"""
        
        # Try to get from git
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'], 
                cwd=self.project_root, 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                url = result.stdout.strip()
                # Extract repo name from URL
                if url.endswith('.git'):
                    url = url[:-4]
                repo_name = url.split('/')[-1]
                return repo_name
        except:
            pass
        
        # Fall back to directory name
        return self.project_root.name
    
    def _get_supabase_config(self) -> bool:
        """Get Supabase configuration from environment or config files"""
        
        # Check environment variables first
        supabase_url = os.environ.get('SUPABASE_URL')
        supabase_anon_key = os.environ.get('SUPABASE_ANON_KEY')
        
        # Try to read from .env file if environment variables not set
        if not supabase_url or not supabase_anon_key:
            env_files = [
                self.project_root / ".env",
                self.project_root / ".env.local",
                self.project_root / "supabase" / ".env"
            ]
            
            for env_file in env_files:
                if env_file.exists():
                    try:
                        with open(env_file, 'r') as f:
                            for line in f:
                                line = line.strip()
                                if line.startswith('SUPABASE_URL='):
                                    supabase_url = line.split('=', 1)[1].strip('"\'')
                                elif line.startswith('SUPABASE_ANON_KEY='):
                                    supabase_anon_key = line.split('=', 1)[1].strip('"\'')
                    except Exception as e:
                        self.console.print(f"Warning: Could not read {env_file}: {e}")
        
        if not supabase_url:
            self.console.print("⚠️  SUPABASE_URL not found - frontend features will be limited")
            supabase_url = "https://your-project.supabase.co"
        
        if not supabase_anon_key:
            self.console.print("⚠️  SUPABASE_ANON_KEY not found - authentication will not work")
            supabase_anon_key = "your-anon-key"
        
        self.supabase_config = {
            'supabase_url': supabase_url,
            'supabase_anon_key': supabase_anon_key
        }
        
        self.console.print(f"🔗 Supabase URL: {supabase_url}")
        return True
    
    def _inject_hugo_config(self) -> bool:
        """Inject class context into Hugo configuration"""
        
        try:
            # Read the current Hugo config
            hugo_config_file = self.project_root / "hugo_generated" / "hugo.toml"
            
            if not hugo_config_file.exists():
                self.console.print("⚠️  Hugo config not found, will be created")
                hugo_config_file.parent.mkdir(parents=True, exist_ok=True)
                config_content = ""
            else:
                with open(hugo_config_file, 'r') as f:
                    config_content = f.read()
            
            # Add class context section to Hugo config
            class_context_toml = f"""

# ============================================================================
# CLASS CONTEXT (Auto-generated by inject_class_context.py)
# ============================================================================

[params.class_context]
class_id = "{self.class_context['class_id']}"
repo_name = "{self.class_context['repo_name']}"
class_name = "{self.class_context['class_name']}"
professor_github = "{self.class_context['professor_github_username']}"
build_mode = "{self.class_context['build_mode']}"
target_directory = "{self.class_context['target_directory']}"
semester = "{self.class_context['semester']}"
year = "{self.class_context['year']}"

[params.supabase]
url = "{self.supabase_config['supabase_url']}"
anon_key = "{self.supabase_config['supabase_anon_key']}"

[params.security]
enable_submissions = true
enable_grading = {str(self.class_context['build_mode'] == 'professor').lower()}
require_class_membership = true
"""
            
            # Remove any existing class_context section
            import re
            config_content = re.sub(
                r'# ============================================================================\n# CLASS CONTEXT.*?# ============================================================================\n',
                '',
                config_content,
                flags=re.DOTALL
            )
            
            # Add new class context
            config_content += class_context_toml
            
            # Write updated config
            with open(hugo_config_file, 'w') as f:
                f.write(config_content)
            
            self.console.print(f"✅ Hugo config updated: {hugo_config_file}")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error injecting Hugo config: {e}")
            return False
    
    def _generate_hugo_data_files(self) -> bool:
        """Generate Hugo data files for templates"""
        
        try:
            data_dir = self.project_root / "hugo_generated" / "data"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Create class_context.json
            class_context_file = data_dir / "class_context.json"
            with open(class_context_file, 'w') as f:
                json.dump(self.class_context, f, indent=2)
            
            # Create supabase_config.json (only non-sensitive data)
            supabase_public_config = {
                'url': self.supabase_config['supabase_url'],
                'has_config': bool(self.supabase_config['supabase_anon_key']),
                'features_enabled': {
                    'authentication': bool(self.supabase_config['supabase_anon_key']),
                    'submissions': bool(self.supabase_config['supabase_anon_key']),
                    'grading': self.class_context['build_mode'] == 'professor'
                }
            }
            
            supabase_config_file = data_dir / "supabase_config.json"
            with open(supabase_config_file, 'w') as f:
                json.dump(supabase_public_config, f, indent=2)
            
            self.console.print(f"✅ Hugo data files generated in: {data_dir}")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error generating Hugo data files: {e}")
            return False
    
    def _create_js_config_file(self) -> bool:
        """Create JavaScript configuration file for runtime use"""
        
        try:
            # Create JavaScript config in the static directory
            static_dir = self.project_root / "hugo_generated" / "static" / "js"
            static_dir.mkdir(parents=True, exist_ok=True)
            
            js_config_file = static_dir / "framework-config.js"
            
            js_content = f"""// Framework Configuration (Auto-generated)
// This file contains configuration for the frontend JavaScript
window.FrameworkConfig = {{
    classContext: {{
        classId: "{self.class_context['class_id']}",
        repoName: "{self.class_context['repo_name']}",
        className: "{self.class_context['class_name']}",
        professorGithub: "{self.class_context['professor_github_username']}",
        buildMode: "{self.class_context['build_mode']}",
        targetDirectory: "{self.class_context['target_directory']}"
    }},
    supabase: {{
        url: "{self.supabase_config['supabase_url']}",
        anonKey: "{self.supabase_config['supabase_anon_key']}",
        featuresEnabled: {{
            authentication: {str(bool(self.supabase_config['supabase_anon_key'])).lower()},
            submissions: {str(bool(self.supabase_config['supabase_anon_key'])).lower()},
            grading: {str(self.class_context['build_mode'] == 'professor').lower()}
        }}
    }},
    security: {{
        enableSubmissions: true,
        enableGrading: {str(self.class_context['build_mode'] == 'professor').lower()},
        requireClassMembership: true
    }},
    debug: {{
        generatedAt: "{datetime.datetime.now().isoformat()}",
        buildMode: "{self.class_context['build_mode']}",
        targetDirectory: "{self.class_context['target_directory']}"
    }}
}};

// Auto-inject meta tags for backward compatibility
document.addEventListener('DOMContentLoaded', function() {{
    const head = document.head;
    
    // Only inject if not already present
    if (!document.querySelector('meta[name="class-id"]')) {{
        const metaTags = [
            ['class-id', window.FrameworkConfig.classContext.classId],
            ['repo-name', window.FrameworkConfig.classContext.repoName], 
            ['professor-github', window.FrameworkConfig.classContext.professorGithub],
            ['supabase-url', window.FrameworkConfig.supabase.url],
            ['supabase-anon-key', window.FrameworkConfig.supabase.anonKey]
        ];
        
        metaTags.forEach(([name, content]) => {{
            const meta = document.createElement('meta');
            meta.name = name;
            meta.content = content;
            head.appendChild(meta);
        }});
    }}
}});
"""
            
            with open(js_config_file, 'w') as f:
                f.write(js_content)
            
            self.console.print(f"✅ JavaScript config created: {js_config_file}")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error creating JavaScript config: {e}")
            return False


def main():
    """Main function for standalone execution"""
    import sys
    
    console = Console()
    
    # Get target directory from command line or default to professor
    target_directory = sys.argv[1] if len(sys.argv) > 1 else "professor"
    
    # Determine project root
    project_root = Path.cwd()
    if project_root.name in ['professor', 'students']:
        project_root = project_root.parent
    
    console.print(f"🚀 [bold]Class Context Injection[/bold]")
    console.print(f"Project root: {project_root}")
    console.print(f"Target directory: {target_directory}")
    
    # Create injector and run
    injector = ClassContextInjector(project_root, console)
    success = injector.inject_class_context(target_directory)
    
    if success:
        console.print("\n✅ [bold green]Class context injection completed successfully[/bold green]")
        return 0
    else:
        console.print("\n❌ [bold red]Class context injection failed[/bold red]")
        return 1


if __name__ == "__main__":
    exit(main())