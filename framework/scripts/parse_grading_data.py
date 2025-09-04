#!/usr/bin/env python3
"""
Grading Data Parser for Framework Manager

This script parses modules.yml, constituents.yml, and grading policy files
to create structured data for Supabase synchronization.

Validates the grading system configuration and extracts data for database insertion.
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from rich.console import Console
from rich.table import Table


@dataclass
class Module:
    """Represents a grading module"""
    id: str
    name: str
    description: str
    weight: float
    order: int
    color: str
    icon: str


@dataclass  
class Constituent:
    """Represents a grading constituent within a module"""
    id: str
    slug: str
    name: str
    description: str
    module_id: str
    weight: float
    type: str
    max_attempts: int


@dataclass
class GradingPolicy:
    """Represents a grading policy for a module"""
    module_id: str
    policy_name: str
    version: str
    policy_data: Dict[str, Any]
    sql_function_name: Optional[str] = None


class GradingDataParser:
    """Parses and validates grading configuration files"""
    
    def __init__(self, content_directory: Path, console: Console = None):
        self.content_directory = Path(content_directory)
        self.console = console or Console()
        
        # Data containers
        self.modules: Dict[str, Module] = {}
        self.constituents: Dict[str, Constituent] = {}
        self.grading_policies: Dict[str, GradingPolicy] = {}
        
        # Validation errors
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def parse_all(self) -> Tuple[bool, Dict[str, Any]]:
        """Parse all grading data files
        
        Returns:
            tuple: (success, parsed_data_dict)
        """
        
        success = True
        
        # Parse modules.yml
        if not self._parse_modules():
            success = False
            
        # Parse constituents.yml  
        if not self._parse_constituents():
            success = False
            
        # Parse grading policies
        if not self._parse_grading_policies():
            success = False
            
        # Validate cross-references
        if not self._validate_cross_references():
            success = False
            
        # Enhanced validation (non-blocking warnings)
        self._validate_enhanced_relationships()
        self._validate_weight_sums()
        
        # Load class_id from course.yml
        class_id = self._load_class_id()
        
        # Build result data structure with class_id injected
        modules_with_class_id = []
        for module in self.modules.values():
            module_dict = asdict(module)
            module_dict['class_id'] = class_id
            modules_with_class_id.append(module_dict)
        
        constituents_with_class_id = []
        for constituent in self.constituents.values():
            constituent_dict = asdict(constituent)
            constituent_dict['class_id'] = class_id
            constituents_with_class_id.append(constituent_dict)
        
        result_data = {
            'modules': modules_with_class_id,
            'constituents': constituents_with_class_id,
            'grading_policies': [asdict(policy) for policy in self.grading_policies.values()],
            'class_id': class_id,
            'validation_summary': {
                'total_modules': len(self.modules),
                'total_constituents': len(self.constituents),
                'total_policies': len(self.grading_policies),
                'errors': self.errors,
                'warnings': self.warnings
            }
        }
        
        return success, result_data
    
    def _parse_modules(self) -> bool:
        """Parse modules.yml file"""
        
        modules_file = self.content_directory / "modules.yml"
        
        if not modules_file.exists():
            self.errors.append(f"modules.yml not found at {modules_file}")
            return False
            
        try:
            with open(modules_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            modules_config = data.get('modules', {})
            
            for module_id, module_data in modules_config.items():
                try:
                    module = Module(
                        id=module_data.get('id', module_id),
                        name=module_data['name'],
                        description=module_data.get('description', ''),
                        weight=float(module_data['weight']),
                        order=int(module_data.get('order', 999)),
                        color=module_data.get('color', '#4a90e2'),
                        icon=module_data.get('icon', '📚')
                    )
                    
                    # Validate weight
                    if not (0 <= module.weight <= 100):
                        self.errors.append(f"Module {module_id} weight {module.weight} is not between 0-100")
                        continue
                        
                    self.modules[module_id] = module
                    
                except KeyError as e:
                    self.errors.append(f"Module {module_id} missing required field: {e}")
                except ValueError as e:
                    self.errors.append(f"Module {module_id} invalid value: {e}")
                    
        except yaml.YAMLError as e:
            self.errors.append(f"YAML error in modules.yml: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error parsing modules.yml: {e}")
            return False
            
        # Validate total module weights
        total_weight = sum(module.weight for module in self.modules.values())
        if abs(total_weight - 100.0) > 0.1:
            self.warnings.append(f"Module weights sum to {total_weight}, not 100.0")
            
        self.console.print(f"✅ Parsed {len(self.modules)} modules from modules.yml")
        return True
    
    def _parse_constituents(self) -> bool:
        """Parse constituents.yml file"""
        
        constituents_file = self.content_directory / "constituents.yml"
        
        if not constituents_file.exists():
            self.errors.append(f"constituents.yml not found at {constituents_file}")
            return False
            
        try:
            with open(constituents_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            constituents_config = data.get('constituents', {})
            
            for constituent_id, constituent_data in constituents_config.items():
                try:
                    constituent = Constituent(
                        id=constituent_data.get('id', constituent_id),
                        slug=constituent_data['slug'],
                        name=constituent_data['name'],
                        description=constituent_data.get('description', ''),
                        module_id=constituent_data['module_id'],
                        weight=float(constituent_data['weight']),
                        type=constituent_data.get('type', 'implementation'),
                        max_attempts=int(constituent_data.get('max_attempts', 3))
                    )
                    
                    # Validate weight
                    if not (0 <= constituent.weight <= 100):
                        self.errors.append(f"Constituent {constituent_id} weight {constituent.weight} is not between 0-100")
                        continue
                        
                    # Validate max_attempts
                    if constituent.max_attempts < 1:
                        self.errors.append(f"Constituent {constituent_id} max_attempts must be >= 1")
                        continue
                        
                    self.constituents[constituent_id] = constituent
                    
                except KeyError as e:
                    self.errors.append(f"Constituent {constituent_id} missing required field: {e}")
                except ValueError as e:
                    self.errors.append(f"Constituent {constituent_id} invalid value: {e}")
                    
        except yaml.YAMLError as e:
            self.errors.append(f"YAML error in constituents.yml: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Error parsing constituents.yml: {e}")
            return False
            
        self.console.print(f"✅ Parsed {len(self.constituents)} constituents from constituents.yml")
        return True
    
    def _parse_grading_policies(self) -> bool:
        """Parse grading policy files from grading_policies/ directory"""
        
        policies_dir = self.content_directory / "grading_policies"
        
        if not policies_dir.exists():
            self.warnings.append(f"grading_policies directory not found at {policies_dir}")
            return True  # Not required
            
        policy_files = list(policies_dir.glob("*.yml"))
        
        if not policy_files:
            self.warnings.append("No grading policy files found in grading_policies/")
            return True
            
        for policy_file in policy_files:
            try:
                with open(policy_file, 'r', encoding='utf-8') as f:
                    policy_data = yaml.safe_load(f)
                    
                metadata = policy_data.get('policy_metadata', {})
                
                # Handle universal policies (applies_to: "all_modules")
                applies_to = metadata.get('applies_to', '')
                if applies_to == 'all_modules':
                    # Universal policy - use None as module_id
                    module_id = None
                    policy_key = 'universal'
                else:
                    # Module-specific policy
                    module_id = metadata.get('module_id')
                    if not module_id:
                        self.errors.append(f"Policy file {policy_file.name} missing module_id in policy_metadata (or use applies_to: 'all_modules')")
                        continue
                    policy_key = module_id
                
                # Validate required grading_rules structure
                if 'grading_rules' not in policy_data:
                    self.errors.append(f"Policy file {policy_file.name} missing required 'grading_rules' section")
                    continue
                    
                grading_rules = policy_data.get('grading_rules', [])
                if not isinstance(grading_rules, list) or len(grading_rules) == 0:
                    self.errors.append(f"Policy file {policy_file.name} 'grading_rules' must be a non-empty array")
                    continue
                
                policy = GradingPolicy(
                    module_id=module_id,
                    policy_name=metadata.get('name', policy_file.stem),
                    version=metadata.get('version', '1.0'),
                    policy_data=policy_data,
                    sql_function_name=None  # We use universal apply_grading_policy function
                )
                
                self.grading_policies[policy_key] = policy
                
            except yaml.YAMLError as e:
                self.errors.append(f"YAML error in {policy_file.name}: {e}")
            except Exception as e:
                self.errors.append(f"Error parsing {policy_file.name}: {e}")
                
        self.console.print(f"✅ Parsed {len(self.grading_policies)} grading policies")
        return True
    
    def _validate_cross_references(self) -> bool:
        """Validate cross-references between modules, constituents, and policies"""
        
        success = True
        
        # Check that all constituents reference valid modules
        for constituent_id, constituent in self.constituents.items():
            if constituent.module_id not in self.modules:
                self.errors.append(f"Constituent {constituent_id} references unknown module: {constituent.module_id}")
                success = False
        
        # Check that all grading policies reference valid modules (or are universal)
        for policy_module_id, policy in self.grading_policies.items():
            # Universal policies (module_id = None) are valid
            if policy.module_id is not None and policy.module_id not in self.modules:
                self.errors.append(f"Grading policy for {policy_module_id} references unknown module: {policy.module_id}")
                success = False
        
        # Validate constituent weights within each module
        module_constituent_weights = {}
        for constituent in self.constituents.values():
            module_id = constituent.module_id
            if module_id not in module_constituent_weights:
                module_constituent_weights[module_id] = []
            module_constituent_weights[module_id].append(constituent.weight)
        
        for module_id, weights in module_constituent_weights.items():
            total_weight = sum(weights)
            if abs(total_weight - 100.0) > 0.1:
                self.warnings.append(f"Module {module_id} constituent weights sum to {total_weight}, not 100.0")
        
        return success
    
    def _load_class_id(self) -> str:
        """Load class_id from course.yml file"""
        
        # Look for course.yml in the parent directory (class_template/course.yml)
        course_file = self.content_directory / "course.yml"
        
        try:
            if course_file.exists():
                with open(course_file, 'r', encoding='utf-8') as f:
                    course_data = yaml.safe_load(f)
                    class_id = course_data.get('class_id')
                    if class_id:
                        return class_id
                        
        except Exception as e:
            self.warnings.append(f"Could not load class_id from {course_file}: {e}")
        
        # Default class_id if not found
        default_class_id = 'df6b6665-d793-445d-8514-f1680ff77369'
        self.warnings.append(f"Using default class_id: {default_class_id}")
        return default_class_id
    
    def _validate_enhanced_relationships(self):
        """Enhanced validation for relationships (warnings only)"""
        
        # Check for orphaned constituents (referencing non-existent modules)
        for constituent_id, constituent in self.constituents.items():
            if constituent.module_id not in self.modules:
                self.warnings.append(f"Orphaned constituent: '{constituent_id}' references missing module: '{constituent.module_id}'")
        
        # Check for modules without constituents
        for module_id, module in self.modules.items():
            has_constituents = any(c.module_id == module_id for c in self.constituents.values())
            if not has_constituents:
                self.warnings.append(f"Empty module: '{module_id}' has no constituents defined")
    
    def _validate_weight_sums(self):
        """Validate weight sums (warnings only)"""
        
        # Check module weights (flexible - can be != 100)
        total_module_weight = sum(module.weight for module in self.modules.values())
        if abs(total_module_weight - 100.0) > 0.1:
            self.warnings.append(f"Module weights sum to {total_module_weight}%, not 100%. This is allowed but may indicate an issue.")
        
        # Check constituent weights per module (should = 100)
        module_constituent_weights = {}
        for constituent in self.constituents.values():
            module_id = constituent.module_id
            if module_id in self.modules:  # Only check valid modules
                if module_id not in module_constituent_weights:
                    module_constituent_weights[module_id] = []
                module_constituent_weights[module_id].append(constituent.weight)
        
        for module_id, weights in module_constituent_weights.items():
            total_weight = sum(weights)
            if abs(total_weight - 100.0) > 0.1:
                self.warnings.append(f"Module '{module_id}' constituent weights sum to {total_weight}%, not 100%")
    
    def show_summary(self):
        """Display a summary table of parsed grading data"""
        
        # Modules table
        modules_table = Table(title="📚 Parsed Modules")
        modules_table.add_column("ID", style="cyan")
        modules_table.add_column("Name", style="green")
        modules_table.add_column("Weight", justify="right")
        modules_table.add_column("Order", justify="right")
        modules_table.add_column("Constituents", justify="right")
        
        for module in sorted(self.modules.values(), key=lambda m: m.order):
            constituent_count = len([c for c in self.constituents.values() if c.module_id == module.id])
            modules_table.add_row(
                module.id,
                module.name,
                f"{module.weight}%",
                str(module.order),
                str(constituent_count)
            )
        
        self.console.print(modules_table)
        
        # Constituents table
        constituents_table = Table(title="🔧 Parsed Constituents")
        constituents_table.add_column("ID", style="cyan")
        constituents_table.add_column("Name", style="green")
        constituents_table.add_column("Module", style="yellow")
        constituents_table.add_column("Weight", justify="right")
        constituents_table.add_column("Type", style="magenta")
        
        for constituent in sorted(self.constituents.values(), key=lambda c: (c.module_id, c.weight)):
            constituents_table.add_row(
                constituent.id,
                constituent.name,
                constituent.module_id,
                f"{constituent.weight}%",
                constituent.type
            )
        
        self.console.print(constituents_table)
        
        # Policies table
        if self.grading_policies:
            policies_table = Table(title="📋 Parsed Grading Policies")
            policies_table.add_column("Module", style="cyan")
            policies_table.add_column("Policy Name", style="green")
            policies_table.add_column("Version", style="yellow")
            policies_table.add_column("SQL Function", style="magenta")
            
            for policy in self.grading_policies.values():
                policies_table.add_row(
                    policy.module_id,
                    policy.policy_name,
                    policy.version,
                    policy.sql_function_name or "None"
                )
            
            self.console.print(policies_table)
        
        # Validation summary
        if self.errors or self.warnings:
            self.console.print("\n🚨 [bold red]Validation Issues[/bold red]")
            
            if self.errors:
                self.console.print(f"❌ {len(self.errors)} Errors:")
                for error in self.errors:
                    self.console.print(f"   • {error}")
            
            if self.warnings:
                self.console.print(f"⚠️  {len(self.warnings)} Warnings:")
                for warning in self.warnings:
                    self.console.print(f"   • {warning}")
        else:
            self.console.print("\n✅ [bold green]All validation checks passed[/bold green]")


def main():
    """Main function for standalone execution"""
    import sys
    
    console = Console()
    
    # Determine content directory
    content_dir = Path.cwd()
    
    # Look for grading files in common locations
    search_paths = [
        content_dir,
        content_dir / "professor",
        content_dir / "class_template",
        content_dir.parent / "class_template"
    ]
    
    grading_dir = None
    for search_path in search_paths:
        if (search_path / "modules.yml").exists():
            grading_dir = search_path
            break
    
    if not grading_dir:
        console.print("❌ Could not find modules.yml in any expected location")
        console.print("Searched paths:")
        for path in search_paths:
            console.print(f"   • {path}")
        sys.exit(1)
    
    console.print(f"📁 Using grading data from: {grading_dir}")
    
    # Parse grading data
    parser = GradingDataParser(grading_dir, console)
    success, data = parser.parse_all()
    
    # Show summary
    parser.show_summary()
    
    # Write JSON output for other tools
    output_file = grading_dir / "grading_data_parsed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    
    console.print(f"\n💾 Parsed data written to: {output_file}")
    
    if not success:
        console.print("\n❌ Parsing completed with errors")
        sys.exit(1)
    else:
        console.print("\n✅ Parsing completed successfully")


if __name__ == "__main__":
    main()