#!/usr/bin/env python3
"""
Hugo Configuration Generator - Self-Contained
Merges values from course.yml and config.yml to generate hugo.toml
NO dependency on root dna.yml for rendering - fully self-contained per directory

Now includes optional content validation before Hugo config generation.
"""

import os
import sys
import yaml
from pathlib import Path
from jinja2 import Environment, BaseLoader

# Import validation system (optional, handle different execution contexts)
try:
    from validate_content import ContentValidator, load_validation_config
    VALIDATION_AVAILABLE = True
except ImportError:
    try:
        # Try relative import for different execution contexts
        import sys
        from pathlib import Path
        script_dir = Path(__file__).parent
        sys.path.insert(0, str(script_dir))
        from validate_content import ContentValidator, load_validation_config
        VALIDATION_AVAILABLE = True
    except ImportError:
        VALIDATION_AVAILABLE = False

# Import index generation system (optional, handle different execution contexts)
try:
    from generate_indices import IndexGenerator
    INDEX_GENERATION_AVAILABLE = True
except ImportError:
    try:
        # Try relative import for different execution contexts
        import sys
        from pathlib import Path
        script_dir = Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        from generate_indices import IndexGenerator
        INDEX_GENERATION_AVAILABLE = True
    except ImportError:
        INDEX_GENERATION_AVAILABLE = False

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

def run_content_validation(base_dir: Path) -> bool:
    """
    Run content validation if available and enabled.
    
    Args:
        base_dir: Base directory to validate
        
    Returns:
        bool: True if validation passed or was skipped, False if validation failed
    """
    if not VALIDATION_AVAILABLE:
        return True  # Skip validation if not available
    
    # Load validation configuration
    config = load_validation_config(base_dir)
    
    if not config.get('content_validation', True):
        print("📝 Content validation disabled in configuration")
        return True
    
    print("📝 Running content validation...")
    
    try:
        validator = ContentValidator(base_dir, config.get('strict_validation', False))
        success = validator.validate_all_content()
        
        if success:
            print("✅ Content validation passed")
        else:
            print("❌ Content validation failed")
        
        return success
        
    except Exception as e:
        print(f"⚠️  Content validation error: {e}")
        # Don't fail build on validation errors unless in strict mode
        return not config.get('strict_validation', False)

def run_index_generation(base_dir: Path) -> bool:
    """
    Run automatic index generation if available and enabled.
    
    Args:
        base_dir: Base directory to generate indices for
        
    Returns:
        bool: True if generation succeeded or was skipped, False if generation failed
    """
    if not INDEX_GENERATION_AVAILABLE:
        return True  # Skip index generation if not available
    
    # Load index generation configuration from dna.yml (try multiple locations)
    dna_paths = [
        base_dir / 'dna.yml',  # Same directory
        base_dir / '../dna.yml',  # Parent directory (for student directories)
        base_dir / '../../dna.yml'  # Repository root (for nested student directories)
    ]
    
    config = {'index_generation': True}
    
    for dna_path in dna_paths:
        if dna_path.exists():
            try:
                with open(dna_path, 'r') as f:
                    dna_config = yaml.safe_load(f) or {}
                if 'index_generation' in dna_config:
                    config['index_generation'] = bool(dna_config['index_generation'])
                break  # Use the first found dna.yml
            except Exception as e:
                print(f"⚠️  Could not read {dna_path}: {e}")
                continue
    
    if not config.get('index_generation', True):
        print("📚 Index generation disabled in configuration")
        return True
    
    print("📚 Running automatic index generation...")
    
    try:
        generator = IndexGenerator(base_dir)
        success = generator.generate_all_indices()
        
        if success:
            print("✅ Index generation completed")
        else:
            print("⚠️  Index generation completed with warnings")
        
        return success
        
    except Exception as e:
        print(f"⚠️  Index generation error: {e}")
        # Don't fail build on index generation errors (graceful degradation)
        return True

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
    
    # Run automatic index generation first
    if not run_index_generation(base_dir):
        print("❌ Build aborted due to index generation failures")
        sys.exit(1)
    
    # Run content validation after index generation
    if not run_content_validation(base_dir):
        print("❌ Build aborted due to content validation failures")
        sys.exit(1)
    
    if generate_hugo_config(base_dir):
        print("✅ Hugo configuration generated successfully")
    else:
        print("❌ Failed to generate Hugo configuration")
        sys.exit(1)

if __name__ == "__main__":
    main() 