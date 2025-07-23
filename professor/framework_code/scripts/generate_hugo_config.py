#!/usr/bin/env python3
"""
Hugo Configuration Generator - Self-Contained
Merges values from course.yml and config.yml to generate hugo.toml
NO dependency on root dna.yml for rendering - fully self-contained per directory
"""

import os
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, BaseLoader

def load_yaml_file(file_path):
    """Load and parse a YAML file, return empty dict if file doesn't exist."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    except FileNotFoundError:
        print(f"Warning: {file_path} not found, using defaults")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing {file_path}: {e}")
        return {}

def merge_config_data(base_dir):
    """Merge configuration data from rendering-related YAML files only."""
    
    # Load only rendering configuration files - NO dna.yml dependency
    course_path = base_dir / "course.yml"
    config_path = base_dir / "config.yml"
    
    course_data = load_yaml_file(course_path)
    config_data = load_yaml_file(config_path)
    
    # Merge configuration data (config.yml takes precedence for conflicts)
    merged_data = {}
    merged_data.update(course_data)
    merged_data.update(config_data)
    
    return merged_data

def default_filter(value, default_value):
    """Default filter for missing values."""
    return value if value is not None else default_value

def bool_to_toml(value):
    """Convert Python boolean to TOML boolean string."""
    if isinstance(value, bool):
        return str(value).lower()
    elif isinstance(value, str):
        if value.lower() in ['true', 'false']:
            return value.lower()
        else:
            # Try to parse as boolean
            if value.lower() in ['yes', '1', 'on']:
                return 'true'
            elif value.lower() in ['no', '0', 'off']:
                return 'false'
            else:
                return value.lower()
    else:
        return str(value).lower()

def generate_hugo_config(base_dir):
    """Generate hugo.toml from template and configuration data."""
    
    # Paths - all relative to the current directory (self-contained)
    template_path = base_dir / "framework_code" / "hugo_config" / "hugo.toml.j2"
    output_path = base_dir / "hugo.toml"
    
    # Load template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file {template_path} not found")
        return False
    
    # Merge configuration data (self-contained)
    config_data = merge_config_data(base_dir)
    
    # Add computed values for framework structure
    if 'framework_code' not in config_data:
        config_data['framework_code'] = {}
    config_data['framework_code']['hugo_generated'] = 'framework_code/hugo_generated'
    
    # Create Jinja2 environment with custom filters
    env = Environment(loader=BaseLoader())
    
    # Add custom filters to environment
    env.filters['default'] = default_filter
    env.filters['toml_bool'] = bool_to_toml
    
    # Create template from string
    template = env.from_string(template_content)
    
    try:
        rendered_content = template.render(**config_data)
    except Exception as e:
        print(f"Error rendering template: {e}")
        return False
    
    # Write the generated hugo.toml
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(rendered_content)
        print(f"✅ Generated hugo.toml at {output_path}")
        return True
    except Exception as e:
        print(f"Error writing hugo.toml: {e}")
        return False

def main():
    """Main entry point - works from any self-contained directory."""
    # Work from current directory (self-contained approach)
    if len(sys.argv) > 1:
        base_dir = Path(sys.argv[1])
    else:
        base_dir = Path.cwd()
    
    # Verify we have the required files for self-contained operation
    course_file = base_dir / "course.yml"
    config_file = base_dir / "config.yml"
    template_file = base_dir / "framework_code" / "hugo_config" / "hugo.toml.j2"
    
    if not template_file.exists():
        print(f"Error: Not in a valid project directory. Missing {template_file}")
        print("This script must be run from a directory with framework_code/")
        sys.exit(1)
    
    print(f"🔧 Generating self-contained Hugo configuration from {base_dir}")
    
    if generate_hugo_config(base_dir):
        print("✅ Hugo configuration generated successfully")
    else:
        print("❌ Failed to generate Hugo configuration")
        sys.exit(1)

if __name__ == "__main__":
    main() 