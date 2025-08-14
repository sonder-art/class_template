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

# Import item parsing system (optional, handle different execution contexts)
try:
    from parse_items import ItemParser
    ITEM_PARSING_AVAILABLE = True
except ImportError:
    try:
        # Try relative import for different execution contexts
        import sys
        from pathlib import Path
        script_dir = Path(__file__).parent
        if str(script_dir) not in sys.path:
            sys.path.insert(0, str(script_dir))
        from parse_items import ItemParser
        ITEM_PARSING_AVAILABLE = True
    except ImportError:
        ITEM_PARSING_AVAILABLE = False

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
    # NEW: course.yml is now in class_template directory
    repo_root = Path(__file__).parent.parent.parent  # framework/scripts/ -> repo root
    course_path = repo_root / "class_template" / "course.yml"
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
    
    # NEW: Generate to root-level hugo_generated/ directory
    repo_root = Path(__file__).parent.parent.parent  # framework/scripts/ -> repo root
    template_path = repo_root / "framework" / "hugo_config" / "hugo.toml.j2"
    
    # Output to root-level hugo_generated directory (single build target)
    hugo_generated_dir = repo_root / "hugo_generated"
    hugo_generated_dir.mkdir(exist_ok=True)
    output_path = hugo_generated_dir / "hugo.toml"
    
    # Load template
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file {template_path} not found")
        return False
    
    # Merge configuration data (self-contained)
    config_data = merge_config_data(base_dir)
    
    # Add computed values for framework structure - NEW: Use correct root-level paths
    # These values provide defaults for the template variables to ensure consistent paths
    if 'hugo' not in config_data:
        config_data['hugo'] = {}
    if 'theme' not in config_data:
        config_data['theme'] = {}
    
    # Ensure template defaults point to new framework location
    config_data['hugo']['assets_path'] = '../framework/assets'
    config_data['theme']['path'] = '../framework/themes'
    
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

def run_item_parsing(base_dir):
    """Run graded item parsing from class_notes markdown files."""
    
    if not ITEM_PARSING_AVAILABLE:
        print("📝 Item parsing system not available")
        return True
    
    # Check if homework parsing is enabled in dna.yml
    dna_paths = [
        base_dir / 'dna.yml',  # Same directory
        base_dir / '../dna.yml',  # Parent directory (for student directories)
        base_dir / '../../dna.yml'  # Repository root (for nested student directories)
    ]
    
    config = {'homework_parsing': True}  # Default enabled for grading system
    
    for dna_path in dna_paths:
        if dna_path.exists():
            try:
                with open(dna_path, 'r') as f:
                    dna_config = yaml.safe_load(f) or {}
                if 'homework_parsing' in dna_config:
                    config['homework_parsing'] = bool(dna_config['homework_parsing'])
                break  # Use the first found dna.yml
            except Exception as e:
                print(f"⚠️  Could not read {dna_path}: {e}")
                continue
    
    if not config.get('homework_parsing', True):
        print("📝 Homework parsing disabled in configuration")
        return True
    
    # Check if class_notes directory exists
    class_notes_dir = base_dir / "class_notes"
    if not class_notes_dir.exists():
        print("📝 No class_notes directory found, skipping homework parsing")
        return True
    
    print("📝 Parsing graded items from class_notes...")
    
    try:
        parser = ItemParser(str(class_notes_dir))
        parsed_files = parser.parse_all_content()
        
        if parsed_files:
            # Generate configuration file to root-level hugo_generated directory
            repo_root = Path(__file__).parent.parent.parent  # framework/scripts/ -> repo root
            hugo_generated_dir = repo_root / "hugo_generated"
            output_dir = hugo_generated_dir / "data"
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / "items.json"
            parser.generate_items_config(str(output_file))
            
            # Items.json is already in the correct location for Hugo access
            print(f"📋 Generated {len(parsed_files)} item files to hugo_generated/data/")
            
            total_items = sum(len(pf.items) for pf in parsed_files)
            print(f"✅ Item parsing completed: {total_items} items from {len(parsed_files)} files")
            
            # Copy constituents and modules YAML files for Hugo data access
            # NEW: These are now in class_template/ directory
            repo_root = Path(__file__).parent.parent.parent  # framework/scripts/ -> repo root
            constituents_source = repo_root / "class_template" / "constituents.yml"
            modules_source = repo_root / "class_template" / "modules.yml"
            
            if constituents_source.exists():
                constituents_dest = output_dir / "constituents.yml"
                shutil.copy2(str(constituents_source), str(constituents_dest))
                print(f"📋 Copied constituents data for Hugo access")
            
            if modules_source.exists():
                modules_dest = output_dir / "modules.yml"
                shutil.copy2(str(modules_source), str(modules_dest))
                print(f"📚 Copied modules data for Hugo access")
        else:
            print("📝 No graded items found in class_notes")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Item parsing error: {e}")
        # Don't fail build on item parsing errors (graceful degradation)
        return True

def run_homework_processing(base_dir: Path) -> bool:
    """Run homework content processing to generate beautiful UI from simple YAML"""
    print("🎨 Processing homework content with automatic UI generation...")
    
    try:
        # Import the homework processing module
        import sys
        # NEW: Scripts are now in framework directory
        repo_root = Path(__file__).parent.parent.parent  # framework/scripts/ -> repo root  
        scripts_dir = repo_root / "framework" / "scripts"
        sys.path.insert(0, str(scripts_dir))
        
        from process_homework_content import HomeworkContentProcessor
        
        processor = HomeworkContentProcessor(str(base_dir))
        processed_count = processor.process_all_homework_files()
        
        if processed_count > 0:
            print(f"✅ Processed {processed_count} homework files with beautiful UI")
        else:
            print("📝 No homework files needed processing")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Homework processing error: {e}")
        # Don't fail build on processing errors (graceful degradation)
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
    # NEW: Template is now in framework directory
    repo_root = Path.cwd().parent if Path.cwd().name in ['professor', 'students'] else Path.cwd()
    template_file = repo_root / "framework" / "hugo_config" / "hugo.toml.j2"
    
    if not template_file.exists():
        print(f"Error: Not in a valid project directory. Missing {template_file}")
        print("This script must be run from a directory with access to framework/")
        sys.exit(1)
    
    print(f"🔧 Generating self-contained Hugo configuration from {base_dir}")
    
    # Run automatic index generation first
    if not run_index_generation(base_dir):
        print("❌ Build aborted due to index generation failures")
        sys.exit(1)
    
    # Run homework parsing after index generation
    if not run_item_parsing(base_dir):
        print("❌ Build aborted due to homework parsing failures")
        sys.exit(1)
    
    # Skip homework content processing - keep source files clean
    # Beautiful UI is generated by CSS and Hugo templates at render time
    # run_homework_processing(base_dir)
    
    # Run content validation after homework parsing
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