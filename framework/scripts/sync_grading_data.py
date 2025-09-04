#!/usr/bin/env python3
"""
Grading Data Synchronization with Supabase

This script synchronizes parsed grading data (modules, constituents, grading policies)
with the Supabase database. It handles creation, updates, and maintains referential integrity.

Uses the grading system database schema defined in framework/sql/003_grading_system.sql
"""

import json
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False


@dataclass
class SyncResult:
    """Result of synchronization operation"""
    success: bool
    created_count: int = 0
    updated_count: int = 0
    skipped_count: int = 0
    error_count: int = 0
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class GradingDataSynchronizer:
    """Synchronizes grading data with Supabase database"""
    
    def __init__(self, supabase_url: str, supabase_key: str, console: Console = None):
        if not SUPABASE_AVAILABLE:
            raise ImportError("supabase-py package not installed. Install with: pip install supabase")
        
        self.console = console or Console()
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Track sync statistics
        self.sync_stats = {
            'modules': SyncResult(success=True),
            'constituents': SyncResult(success=True), 
            'grading_policies': SyncResult(success=True)
        }
    
    async def sync_all(self, grading_data: Dict[str, Any]) -> Tuple[bool, Dict[str, SyncResult]]:
        """Synchronize all grading data with Supabase using ground truth pattern
        
        Ground Truth Pattern:
        1. Deactivate all existing items (is_current = false)
        2. Create/update from ground truth (is_current = true)
        3. Result: Only ground truth items are active
        
        Args:
            grading_data: Parsed grading data from parse_grading_data.py
            
        Returns:
            tuple: (overall_success, sync_results_by_type)
        """
        
        self.console.print("🔄 [bold]Starting Ground Truth Synchronization[/bold]")
        
        overall_success = True
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console
        ) as progress:
            
            # Get class_id from first module or validation summary
            class_id = None
            if grading_data.get('modules') and len(grading_data['modules']) > 0:
                class_id = grading_data['modules'][0].get('class_id')
            
            # Fallback: try to get from validation summary or constituents
            if not class_id and grading_data.get('constituents') and len(grading_data['constituents']) > 0:
                class_id = grading_data['constituents'][0].get('class_id')
            
            # Final fallback: use hardcoded class_id (should be fixed in parse scripts)
            if not class_id:
                class_id = 'df6b6665-d793-445d-8514-f1680ff77369'  # Current class ID
            
            if not class_id:
                self.console.print("❌ No class_id found in grading data")
                return False, self.sync_stats
            
            # Step 1: Deactivate all existing items first
            deactivate_task = progress.add_task("Deactivating existing items...", total=None)
            deactivate_result = await self._deactivate_all_items(class_id)
            if not deactivate_result:
                overall_success = False
                self.console.print("❌ Failed to deactivate existing items")
                return overall_success, self.sync_stats
            progress.update(deactivate_task, description="All existing items deactivated")
            
            # Step 2: Sync modules first (constituents reference them)
            modules_task = progress.add_task("Syncing modules...", total=None)
            modules_result = await self._sync_modules(grading_data.get('modules', []), class_id)
            self.sync_stats['modules'] = modules_result
            progress.update(modules_task, description=f"Modules: {modules_result.created_count} created, {modules_result.updated_count} updated")
            
            if not modules_result.success:
                overall_success = False
            
            # Step 3: Sync constituents (reference modules)
            constituents_task = progress.add_task("Syncing constituents...", total=None)
            constituents_result = await self._sync_constituents(grading_data.get('constituents', []), class_id)
            self.sync_stats['constituents'] = constituents_result
            progress.update(constituents_task, description=f"Constituents: {constituents_result.created_count} created, {constituents_result.updated_count} updated")
            
            if not constituents_result.success:
                overall_success = False
                
            # Step 4: Sync grading policies (reference modules)
            policies_task = progress.add_task("Syncing grading policies...", total=None)
            policies_result = await self._sync_grading_policies(grading_data.get('grading_policies', []), class_id)
            self.sync_stats['grading_policies'] = policies_result
            progress.update(policies_task, description=f"Policies: {policies_result.created_count} created, {policies_result.updated_count} updated")
            
            if not policies_result.success:
                overall_success = False
        
        self.console.print("✅ [bold green]Ground Truth Synchronization Complete[/bold green]")
        return overall_success, self.sync_stats
    
    async def _deactivate_all_items(self, class_id: str) -> bool:
        """Deactivate all existing grading items for this class (ground truth pattern step 1)"""
        
        try:
            self.console.print("   🔄 Deactivating all modules, constituents, and policies...")
            
            # Deactivate all existing records (but don't delete)
            results = await asyncio.gather(
                self.supabase.table('modules').update({'is_current': False}).eq('class_id', class_id).execute(),
                self.supabase.table('constituents').update({'is_current': False}).eq('class_id', class_id).execute(),
                self.supabase.table('grading_policies').update({'is_active': False}).eq('class_id', class_id).execute(),
                return_exceptions=True
            )
            
            # Check for errors
            for i, result in enumerate(results):
                table_names = ['modules', 'constituents', 'grading_policies']
                if isinstance(result, Exception):
                    self.console.print(f"   ❌ Failed to deactivate {table_names[i]}: {result}")
                    return False
                elif hasattr(result, 'error') and result.error:
                    self.console.print(f"   ❌ Failed to deactivate {table_names[i]}: {result.error}")
                    return False
            
            self.console.print("   ✅ All existing items deactivated")
            return True
            
        except Exception as e:
            self.console.print(f"   ❌ Critical error deactivating items: {e}")
            return False
    
    async def _sync_modules(self, modules_data: List[Dict[str, Any]], class_id: str) -> SyncResult:
        """Synchronize modules with database (ground truth pattern step 2)"""
        
        result = SyncResult(success=True)
        
        try:
            for module_data in modules_data:
                try:
                    # Prepare data for database including ground truth flags
                    db_data = {
                        'id': module_data['id'],
                        'class_id': class_id,
                        'name': module_data['name'],
                        'description': module_data.get('description', ''),
                        'weight': float(module_data['weight']),
                        'order_index': int(module_data['order']),
                        'color': module_data.get('color', '#4a90e2'),
                        'icon': module_data.get('icon', '📚'),
                        'is_current': True  # CRITICAL: Mark as current (ground truth)
                    }
                    
                    # Use upsert to handle both create and update
                    upsert_result = self.supabase.table('modules').upsert(db_data).execute()
                    
                    if upsert_result.error:
                        raise Exception(upsert_result.error.message)
                    
                    # Determine if this was create or update
                    existing_check = self.supabase.table('modules').select('*').eq('id', module_data['id']).eq('class_id', class_id).execute()
                    if existing_check.data and len(existing_check.data) > 0:
                        result.updated_count += 1
                        self.console.print(f"   📝 Activated/Updated module: {module_data['name']}")
                    else:
                        result.created_count += 1
                        self.console.print(f"   ➕ Created module: {module_data['name']}")
                        
                except Exception as e:
                    result.error_count += 1
                    error_msg = f"Error syncing module {module_data.get('id', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    self.console.print(f"   ❌ {error_msg}")
                    
        except Exception as e:
            result.success = False
            result.errors.append(f"Critical error syncing modules: {e}")
            self.console.print(f"❌ Critical error syncing modules: {e}")
        
        return result
    
    async def _sync_constituents(self, constituents_data: List[Dict[str, Any]], class_id: str) -> SyncResult:
        """Synchronize constituents with database (ground truth pattern step 3)"""
        
        result = SyncResult(success=True)
        
        try:
            for constituent_data in constituents_data:
                try:
                    # Prepare data for database including ground truth flags
                    db_data = {
                        'id': constituent_data['id'],
                        'class_id': class_id,
                        'slug': constituent_data['slug'],
                        'name': constituent_data['name'],
                        'description': constituent_data.get('description', ''),
                        'module_id': constituent_data['module_id'],
                        'weight': float(constituent_data['weight']),
                        'type': constituent_data.get('type', 'implementation'),
                        'max_attempts': int(constituent_data.get('max_attempts', 3)),
                        'is_current': True  # CRITICAL: Mark as current (ground truth)
                    }
                    
                    # Use upsert to handle both create and update
                    upsert_result = self.supabase.table('constituents').upsert(db_data).execute()
                    
                    if upsert_result.error:
                        raise Exception(upsert_result.error.message)
                    
                    result.updated_count += 1
                    self.console.print(f"   📝 Activated/Updated constituent: {constituent_data['name']}")
                        
                except Exception as e:
                    result.error_count += 1
                    error_msg = f"Error syncing constituent {constituent_data.get('id', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    self.console.print(f"   ❌ {error_msg}")
                    
        except Exception as e:
            result.success = False
            result.errors.append(f"Critical error syncing constituents: {e}")
            self.console.print(f"❌ Critical error syncing constituents: {e}")
        
        return result
    
    async def _sync_grading_policies(self, policies_data: List[Dict[str, Any]], class_id: str) -> SyncResult:
        """Synchronize grading policies with database (ground truth pattern step 4)"""
        
        result = SyncResult(success=True)
        
        try:
            for policy_data in policies_data:
                try:
                    module_id = policy_data.get('module_id')  # None for universal policies
                    version = policy_data['version']
                    policy_name = policy_data['policy_name']
                    
                    # Prepare policy_rules as JSONB (just the rules, not full YAML)
                    policy_rules = {
                        'grading_rules': policy_data['policy_data'].get('grading_rules', []),
                        'policy_settings': policy_data['policy_data'].get('policy_settings', {}),
                        'metadata': policy_data['policy_data'].get('policy_metadata', {})
                    }
                    
                    # Prepare data for database including ground truth flags
                    db_data = {
                        'module_id': module_id,
                        'class_id': class_id,
                        'policy_name': policy_name,
                        'version': version,
                        'policy_rules': policy_rules,  # Store as JSONB for SQL function
                        'description': policy_data['policy_data'].get('policy_metadata', {}).get('description'),
                        'is_active': True  # CRITICAL: Mark as active (ground truth)
                    }
                    
                    # Use upsert to handle both create and update
                    upsert_result = self.supabase.table('grading_policies').upsert(db_data).execute()
                    
                    if upsert_result.error:
                        raise Exception(upsert_result.error.message)
                    
                    result.updated_count += 1
                    policy_type = "Universal" if module_id is None else f"Module-specific ({module_id})"
                    self.console.print(f"   📝 Activated/Updated {policy_type} policy: {policy_name}")
                        
                except Exception as e:
                    result.error_count += 1
                    error_msg = f"Error syncing grading policy {policy_data.get('policy_name', 'unknown')}: {e}"
                    result.errors.append(error_msg)
                    self.console.print(f"   ❌ {error_msg}")
                    
        except Exception as e:
            result.success = False
            result.errors.append(f"Critical error syncing grading policies: {e}")
            self.console.print(f"❌ Critical error syncing grading policies: {e}")
        
        return result
    
    def show_sync_summary(self):
        """Display summary of synchronization results"""
        
        self.console.print("\n📊 [bold]Synchronization Summary[/bold]")
        
        for data_type, result in self.sync_stats.items():
            status = "✅ Success" if result.success else "❌ Failed"
            
            self.console.print(f"\n{data_type.title()}:")
            self.console.print(f"   Status: {status}")
            self.console.print(f"   Created: {result.created_count}")
            self.console.print(f"   Updated: {result.updated_count}")
            self.console.print(f"   Errors: {result.error_count}")
            
            if result.errors:
                self.console.print("   Error Details:")
                for error in result.errors:
                    self.console.print(f"      • {error}")


async def main():
    """Main function for standalone execution"""
    import os
    import sys
    
    console = Console()
    
    # Check for required environment variables
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_SERVICE_ROLE_KEY') or os.environ.get('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        console.print("❌ Missing required environment variables:")
        console.print("   • SUPABASE_URL")
        console.print("   • SUPABASE_SERVICE_ROLE_KEY (or SUPABASE_KEY)")
        sys.exit(1)
    
    # Find grading data - try YAML files first, then parsed JSON
    current_dir = Path.cwd()
    search_paths = [
        current_dir,
        current_dir / "professor", 
        current_dir / "class_template",
        current_dir.parent / "class_template"
    ]
    
    grading_data = None
    data_source = None
    
    # Try to load directly from YAML files (preferred)
    for search_path in search_paths:
        modules_file = search_path / "modules.yml"
        constituents_file = search_path / "constituents.yml"
        course_file = search_path / "course.yml"
        
        if modules_file.exists() and constituents_file.exists() and course_file.exists():
            console.print(f"📁 Loading from YAML files: {search_path}")
            try:
                import yaml
                
                # Load course info for class_id
                with open(course_file, 'r') as f:
                    course_data = yaml.safe_load(f)
                class_id = course_data['class_id']
                
                # Load modules
                with open(modules_file, 'r') as f:
                    modules_yaml = yaml.safe_load(f)
                
                # Load constituents
                with open(constituents_file, 'r') as f:
                    constituents_yaml = yaml.safe_load(f)
                
                # Convert to expected format
                grading_data = {
                    'modules': [],
                    'constituents': [],
                    'grading_policies': []
                }
                
                # Convert modules
                for module_key, module_info in modules_yaml['modules'].items():
                    grading_data['modules'].append({
                        **module_info,
                        'class_id': class_id
                    })
                
                # Convert constituents
                for const_key, const_info in constituents_yaml['constituents'].items():
                    grading_data['constituents'].append({
                        **const_info,
                        'class_id': class_id
                    })
                
                data_source = f"YAML files in {search_path}"
                break
                
            except Exception as e:
                console.print(f"⚠️  Error loading YAML from {search_path}: {e}")
                continue
    
    # Fallback to parsed JSON if YAML loading failed
    if not grading_data:
        grading_data_file = None
        for search_path in search_paths:
            candidate = search_path / "grading_data_parsed.json"
            if candidate.exists():
                grading_data_file = candidate
                break
        
        if not grading_data_file:
            console.print("❌ Could not find grading data")
            console.print("Missing either:")
            console.print("   • YAML files: modules.yml, constituents.yml, course.yml")
            console.print("   • Or parsed JSON: grading_data_parsed.json")
            sys.exit(1)
        
        console.print(f"📁 Using parsed JSON: {grading_data_file}")
        try:
            with open(grading_data_file, 'r', encoding='utf-8') as f:
                grading_data = json.load(f)
            data_source = f"JSON file {grading_data_file}"
        except Exception as e:
            console.print(f"❌ Error loading grading data: {e}")
            sys.exit(1)
    
    console.print(f"📊 Data source: {data_source}")
    
    # Initialize synchronizer and sync data
    try:
        synchronizer = GradingDataSynchronizer(supabase_url, supabase_key, console)
        success, results = await synchronizer.sync_all(grading_data)
        
        # Show summary
        synchronizer.show_sync_summary()
        
        if success:
            console.print("\n✅ [bold green]Synchronization completed successfully[/bold green]")
        else:
            console.print("\n❌ [bold red]Synchronization completed with errors[/bold red]")
            sys.exit(1)
            
    except Exception as e:
        console.print(f"❌ Critical error during synchronization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    if not SUPABASE_AVAILABLE:
        print("❌ supabase-py package not installed")
        print("Install with: pip install supabase")
        exit(1)
    
    asyncio.run(main())