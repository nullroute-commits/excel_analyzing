#!/usr/bin/env python3
"""
Simple linting checks that don't require external tools.
Provides basic code quality validation.
"""

import ast
import os
import re
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple


class SimpleLinter:
    """A minimal linter for basic code quality checks."""
    
    def __init__(self):
        self.issues = []
        self.files_checked = 0
        
    def check_line_length(self, content: str, filepath: str, max_length: int = 88) -> List[str]:
        """Check for lines that are too long."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if len(line) > max_length:
                issues.append(f"{filepath}:{i}: Line too long ({len(line)} > {max_length})")
                
        return issues
    
    def check_imports(self, content: str, filepath: str) -> List[str]:
        """Check import organization and style."""
        issues = []
        lines = content.split('\n')
        
        # Check for unused imports (simple heuristic)
        import_lines = []
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped.startswith(('import ', 'from ')) and not stripped.startswith('#'):
                import_lines.append((i, stripped))
        
        # Check for imports after non-import statements
        found_non_import = False
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            if stripped and not stripped.startswith('#'):
                if stripped.startswith(('import ', 'from ')):
                    if found_non_import:
                        issues.append(f"{filepath}:{i}: Import should be at top of file")
                elif not stripped.startswith(('"""', "'''", '#')):
                    # Skip docstrings and comments
                    if not (i <= 5 and any(x in stripped for x in ['"""', "'''", '#', '__'])):
                        found_non_import = True
        
        return issues
    
    def check_indentation(self, content: str, filepath: str) -> List[str]:
        """Check for consistent indentation."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            if line.strip():  # Skip empty lines
                # Count leading spaces
                leading_spaces = len(line) - len(line.lstrip(' '))
                if leading_spaces > 0 and leading_spaces % 4 != 0:
                    # Check if it's a continuation line (simple heuristic)
                    if i > 1:
                        prev_line = lines[i-2].rstrip()
                        if not prev_line.endswith(('\\', ',', '(', '[', '{')):
                            issues.append(f"{filepath}:{i}: Indentation not multiple of 4")
        
        return issues
    
    def check_naming_conventions(self, content: str, filepath: str) -> List[str]:
        """Check basic naming conventions."""
        issues = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Function names should be snake_case
                    if not re.match(r'^[a-z_][a-z0-9_]*$', node.name) and not node.name.startswith('_'):
                        issues.append(f"{filepath}:{node.lineno}: Function name '{node.name}' should be snake_case")
                
                elif isinstance(node, ast.ClassDef):
                    # Class names should be PascalCase
                    if not re.match(r'^[A-Z][a-zA-Z0-9]*$', node.name):
                        issues.append(f"{filepath}:{node.lineno}: Class name '{node.name}' should be PascalCase")
                
                elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                    # Variable names should be snake_case (but this is too noisy, skip for now)
                    pass
                    
        except SyntaxError:
            # Skip files with syntax errors (already caught elsewhere)
            pass
        except Exception:
            # Skip other parsing errors
            pass
            
        return issues
    
    def check_whitespace(self, content: str, filepath: str) -> List[str]:
        """Check for whitespace issues."""
        issues = []
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Check for trailing whitespace
            if line.rstrip() != line:
                issues.append(f"{filepath}:{i}: Trailing whitespace")
            
            # Check for tabs (prefer spaces)
            if '\t' in line:
                issues.append(f"{filepath}:{i}: Use spaces instead of tabs")
        
        return issues
    
    def check_file(self, filepath: Path) -> List[str]:
        """Check a single Python file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            return [f"{filepath}: File encoding error"]
        except Exception as e:
            return [f"{filepath}: Error reading file: {e}"]
        
        issues = []
        filepath_str = str(filepath)
        
        # Run all checks
        issues.extend(self.check_line_length(content, filepath_str))
        issues.extend(self.check_imports(content, filepath_str))
        issues.extend(self.check_indentation(content, filepath_str))
        issues.extend(self.check_naming_conventions(content, filepath_str))
        issues.extend(self.check_whitespace(content, filepath_str))
        
        self.files_checked += 1
        return issues
    
    def lint_directory(self, directory: Path = Path(".")) -> bool:
        """Lint all Python files in a directory."""
        print("=" * 60)
        print("RUNNING SIMPLE LINTING CHECKS")
        print("=" * 60)
        
        python_files = list(directory.rglob("*.py"))
        
        # Filter out certain directories
        python_files = [
            f for f in python_files 
            if not any(part in str(f) for part in ['.git', '__pycache__', '.venv', 'venv', 'migrations'])
        ]
        
        all_issues = []
        
        for file_path in python_files:
            issues = self.check_file(file_path)
            all_issues.extend(issues)
            
            if issues:
                print(f"❌ {file_path}: {len(issues)} issues")
                for issue in issues[:3]:  # Show first 3 issues per file
                    print(f"    {issue}")
                if len(issues) > 3:
                    print(f"    ... and {len(issues) - 3} more issues")
            else:
                print(f"✅ {file_path}")
        
        print(f"\n📊 Linting Summary:")
        print(f"Files checked: {self.files_checked}")
        print(f"Total issues: {len(all_issues)}")
        
        if len(all_issues) > 20:
            print(f"\n⚠️  Only showing first 20 issues:")
            for issue in all_issues[:20]:
                print(f"  {issue}")
            print(f"  ... and {len(all_issues) - 20} more issues")
        elif all_issues:
            print(f"\n🔍 All issues:")
            for issue in all_issues:
                print(f"  {issue}")
        
        return len(all_issues) == 0


def main():
    """Main function for the simple linter."""
    linter = SimpleLinter()
    success = linter.lint_directory()
    
    if success:
        print("\n✅ No linting issues found!")
        sys.exit(0)
    else:
        print(f"\n❌ Found linting issues!")
        sys.exit(1)


if __name__ == "__main__":
    main()