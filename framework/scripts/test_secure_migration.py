#!/usr/bin/env python3
"""
Test Script for Secure Grading System Migration
This script tests the compatibility of the secure migration with existing data
"""

import os
import tempfile
import subprocess
from pathlib import Path
from rich.console import Console
from rich.table import Table


class MigrationTester:
    """Test the secure grading migration for compatibility"""
    
    def __init__(self):
        self.console = Console()
        self.framework_dir = Path(__file__).parent.parent
        self.sql_dir = self.framework_dir / "sql"
        
    def test_sql_syntax(self) -> bool:
        """Test if the SQL files have valid syntax"""
        
        self.console.print("🔍 [bold]Testing SQL Syntax[/bold]")
        
        # Test both migration files
        migrations = [
            self.sql_dir / "003_grading_system.sql",
            self.sql_dir / "004_secure_grading_system.sql"
        ]
        
        for migration in migrations:
            if not migration.exists():
                self.console.print(f"❌ Missing migration: {migration}")
                return False
                
            # Basic syntax checks
            try:
                with open(migration, 'r') as f:
                    content = f.read()
                    
                # Check for common SQL syntax issues
                issues = []
                
                # Check balanced parentheses
                if content.count('(') != content.count(')'):
                    issues.append("Unbalanced parentheses")
                
                # Check for missing semicolons on complete SQL statements
                # Split by semicolons to get complete statements
                statements = [stmt.strip() for stmt in content.split(';') if stmt.strip()]
                for stmt in statements:
                    # Skip comments and empty lines
                    if stmt.startswith('--') or not stmt.strip():
                        continue
                    # Check if statement looks incomplete (very basic check)
                    if ('CREATE' in stmt or 'ALTER' in stmt or 'DROP' in stmt) and len(stmt) < 20:
                        issues.append(f"Possibly incomplete statement: {stmt[:50]}...")
                
                if issues:
                    self.console.print(f"❌ {migration.name}: {', '.join(issues)}")
                    return False
                else:
                    self.console.print(f"✅ {migration.name}: Syntax OK")
                    
            except Exception as e:
                self.console.print(f"❌ Error reading {migration.name}: {e}")
                return False
        
        return True
    
    def test_table_compatibility(self) -> bool:
        """Test that table modifications are backward compatible"""
        
        self.console.print("🔍 [bold]Testing Table Compatibility[/bold]")
        
        # Read both migrations
        original_file = self.sql_dir / "003_grading_system.sql"
        secure_file = self.sql_dir / "004_secure_grading_system.sql"
        
        with open(original_file) as f:
            original_content = f.read()
        
        with open(secure_file) as f:
            secure_content = f.read()
        
        # Check that all original tables are preserved
        original_tables = self._extract_table_names(original_content)
        
        compatibility_issues = []
        
        for table in original_tables:
            if f"DROP TABLE {table}" in secure_content:
                compatibility_issues.append(f"Table {table} is being dropped")
            
            # Check if table is being recreated differently
            if f"CREATE TABLE {table}" in secure_content and "IF NOT EXISTS" not in secure_content:
                compatibility_issues.append(f"Table {table} is being recreated without IF NOT EXISTS")
        
        # Check ALTER TABLE statements use IF NOT EXISTS for columns
        alter_statements = [line for line in secure_content.split('\n') if 'ALTER TABLE' in line and 'ADD COLUMN' in line]
        for stmt in alter_statements:
            if 'IF NOT EXISTS' not in stmt:
                compatibility_issues.append(f"ALTER TABLE without IF NOT EXISTS: {stmt.strip()}")
        
        if compatibility_issues:
            self.console.print("❌ [red]Compatibility Issues Found:[/red]")
            for issue in compatibility_issues:
                self.console.print(f"   • {issue}")
            return False
        else:
            self.console.print("✅ Table modifications are backward compatible")
            return True
    
    def test_rls_policy_changes(self) -> bool:
        """Test that RLS policy changes are safe"""
        
        self.console.print("🔍 [bold]Testing RLS Policy Changes[/bold]")
        
        secure_file = self.sql_dir / "004_secure_grading_system.sql"
        
        with open(secure_file) as f:
            content = f.read()
        
        # Check that old policies are dropped before new ones are created
        drops = [line for line in content.split('\n') if 'DROP POLICY' in line]
        creates = [line for line in content.split('\n') if 'CREATE POLICY' in line]
        
        if not drops:
            self.console.print("⚠️  No DROP POLICY statements found - old policies may conflict")
            
        if len(creates) == 0:
            self.console.print("❌ No CREATE POLICY statements found")
            return False
        
        # Check that policies handle NULL class_id (legacy data)
        null_checks = content.count('class_id IS NULL')
        if null_checks < 3:  # Should be in modules, constituents, homework_items
            self.console.print("⚠️  May not handle legacy data (NULL class_id) properly")
        else:
            self.console.print("✅ RLS policies handle legacy data properly")
        
        self.console.print(f"✅ Found {len(drops)} DROP and {len(creates)} CREATE policy statements")
        return True
    
    def test_migration_order(self) -> bool:
        """Test that migration operations are in correct order"""
        
        self.console.print("🔍 [bold]Testing Migration Order[/bold]")
        
        secure_file = self.sql_dir / "004_secure_grading_system.sql"
        
        with open(secure_file) as f:
            lines = f.readlines()
        
        # Check that tables are created before they are referenced
        table_creates = {}
        table_references = []
        
        for i, line in enumerate(lines):
            if 'CREATE TABLE' in line and 'IF NOT EXISTS' in line:
                table_name = line.split('CREATE TABLE IF NOT EXISTS ')[1].split(' ')[0]
                table_creates[table_name] = i
            
            if 'REFERENCES' in line:
                ref_table = line.split('REFERENCES ')[1].split('(')[0].strip()
                table_references.append((i, ref_table))
        
        # Check order
        order_issues = []
        for line_num, ref_table in table_references:
            if ref_table in table_creates:
                if table_creates[ref_table] > line_num:
                    order_issues.append(f"Table {ref_table} referenced before creation at line {line_num}")
        
        if order_issues:
            self.console.print("❌ [red]Migration order issues:[/red]")
            for issue in order_issues:
                self.console.print(f"   • {issue}")
            return False
        else:
            self.console.print("✅ Migration operations in correct order")
            return True
    
    def _extract_table_names(self, sql_content: str) -> list:
        """Extract table names from SQL content"""
        tables = []
        for line in sql_content.split('\n'):
            if 'CREATE TABLE' in line and 'IF NOT EXISTS' in line:
                table_name = line.split('CREATE TABLE IF NOT EXISTS ')[1].split(' ')[0]
                tables.append(table_name)
        return tables
    
    def run_all_tests(self) -> bool:
        """Run all compatibility tests"""
        
        self.console.print("🚀 [bold blue]Running Secure Migration Compatibility Tests[/bold blue]\n")
        
        tests = [
            ("SQL Syntax", self.test_sql_syntax),
            ("Table Compatibility", self.test_table_compatibility), 
            ("RLS Policy Changes", self.test_rls_policy_changes),
            ("Migration Order", self.test_migration_order)
        ]
        
        results = []
        
        for test_name, test_func in tests:
            try:
                result = test_func()
                results.append((test_name, result))
                self.console.print()  # Add spacing
            except Exception as e:
                self.console.print(f"❌ {test_name} failed with error: {e}")
                results.append((test_name, False))
        
        # Show summary
        self.show_test_summary(results)
        
        return all(result for _, result in results)
    
    def show_test_summary(self, results):
        """Display test results summary"""
        
        table = Table(title="🧪 Migration Compatibility Test Results")
        table.add_column("Test", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Notes", style="dim")
        
        for test_name, passed in results:
            status = "✅ PASS" if passed else "❌ FAIL"
            notes = "Compatible with existing system" if passed else "Needs attention"
            table.add_row(test_name, status, notes)
        
        self.console.print(table)
        
        # Overall result
        all_passed = all(result for _, result in results)
        if all_passed:
            self.console.print("\n🎉 [bold green]All tests passed! Migration is compatible.[/bold green]")
            self.console.print("✅ Safe to apply secure migration")
        else:
            self.console.print("\n⚠️  [bold yellow]Some tests failed. Review issues before applying migration.[/bold yellow]")
            self.console.print("🔧 Fix the issues above before proceeding")


def main():
    tester = MigrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n✅ Migration compatibility verified!")
        return 0
    else:
        print("\n❌ Migration compatibility issues found!")
        return 1


if __name__ == "__main__":
    exit(main())