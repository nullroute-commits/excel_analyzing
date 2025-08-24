#!/usr/bin/env python3
"""
Simple test runner that doesn't require external dependencies.
Used when pytest and other tools are not available.
"""

import os
import sys
import traceback
import importlib.util
from pathlib import Path
from typing import List, Dict, Any
import time


class SimpleTestRunner:
    """A minimal test runner for basic validation without pytest."""
    
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        
    def run_import_tests(self) -> bool:
        """Test that all modules can be imported."""
        print("=" * 60)
        print("RUNNING IMPORT TESTS")
        print("=" * 60)
        
        modules_to_test = [
            'excel_analyzing',
            'excel_analyzing.models.schemas',
            'excel_analyzing.core',
            'excel_analyzing.pipeline',
            'excel_analyzing.utils',
            'excel_analyzing.web',
            'excel_analyzing.cli',
        ]
        
        all_passed = True
        for module_name in modules_to_test:
            try:
                __import__(module_name)
                print(f"✅ {module_name}")
                self.passed += 1
            except ImportError as e:
                print(f"❌ {module_name}: {e}")
                self.failed += 1
                self.errors.append(f"Import error in {module_name}: {e}")
                all_passed = False
            except Exception as e:
                print(f"❌ {module_name}: {e}")
                self.failed += 1
                self.errors.append(f"Error in {module_name}: {e}")
                all_passed = False
                
        return all_passed
    
    def run_syntax_checks(self) -> bool:
        """Check Python syntax of all .py files."""
        print("\n" + "=" * 60)
        print("RUNNING SYNTAX CHECKS")
        print("=" * 60)
        
        all_passed = True
        python_files = list(Path(".").rglob("*.py"))
        
        for file_path in python_files:
            # Skip certain directories
            if any(part in str(file_path) for part in ['.git', '__pycache__', '.venv', 'venv']):
                continue
                
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                compile(content, str(file_path), 'exec')
                print(f"✅ {file_path}")
                self.passed += 1
            except SyntaxError as e:
                print(f"❌ {file_path}: Syntax Error - {e}")
                self.failed += 1
                self.errors.append(f"Syntax error in {file_path}: {e}")
                all_passed = False
            except Exception as e:
                print(f"❌ {file_path}: {e}")
                self.failed += 1
                self.errors.append(f"Error checking {file_path}: {e}")
                all_passed = False
                
        return all_passed
    
    def run_basic_model_tests(self) -> bool:
        """Run basic tests on data models."""
        print("\n" + "=" * 60)
        print("RUNNING BASIC MODEL TESTS")
        print("=" * 60)
        
        all_passed = True
        
        try:
            from excel_analyzing.models.schemas import DataType, ColumnInfo, ProcessingOptions
            
            # Test DataType enum
            assert DataType.STRING == "string"
            assert DataType.INTEGER == "integer"
            print("✅ DataType enum works correctly")
            self.passed += 1
            
            # Test ProcessingOptions defaults
            options = ProcessingOptions()
            assert options.drop_empty_rows is True
            assert options.drop_empty_columns is True
            assert options.max_sample_size == 100
            print("✅ ProcessingOptions defaults work correctly")
            self.passed += 1
            
            # Test ColumnInfo creation
            column = ColumnInfo(
                name="test_column",
                original_name="Test Column", 
                position=0,
                data_type=DataType.STRING,
            )
            assert column.name == "test_column"
            assert column.data_type == DataType.STRING
            print("✅ ColumnInfo creation works correctly")
            self.passed += 1
            
        except Exception as e:
            print(f"❌ Model tests failed: {e}")
            traceback.print_exc()
            self.failed += 1
            self.errors.append(f"Model test error: {e}")
            all_passed = False
            
        return all_passed
        
    def run_test_file_validation(self) -> bool:
        """Validate that test files have proper structure."""
        print("\n" + "=" * 60)
        print("RUNNING TEST FILE VALIDATION")
        print("=" * 60)
        
        all_passed = True
        test_dirs = ['tests/unit', 'tests/integration', 'tests/security', 
                    'tests/performance', 'tests/regression', 'tests/e2e']
        
        for test_dir in test_dirs:
            test_path = Path(test_dir)
            if test_path.exists():
                test_files = list(test_path.glob("test_*.py"))
                if test_files:
                    print(f"✅ {test_dir}: Found {len(test_files)} test files")
                    self.passed += 1
                else:
                    print(f"❌ {test_dir}: No test files found")
                    self.failed += 1
                    self.errors.append(f"No test files in {test_dir}")
                    all_passed = False
            else:
                print(f"❌ {test_dir}: Directory does not exist")
                self.failed += 1
                self.errors.append(f"Missing test directory: {test_dir}")
                all_passed = False
                
        return all_passed
    
    def run_all_tests(self) -> bool:
        """Run all available tests."""
        print("🚀 Starting Simple Test Runner...")
        print(f"Working directory: {os.getcwd()}")
        
        start_time = time.time()
        
        results = [
            self.run_import_tests(),
            self.run_syntax_checks(),
            self.run_basic_model_tests(),
            self.run_test_file_validation(),
        ]
        
        duration = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.passed + self.failed}")
        print(f"Passed: {self.passed} ✅")
        print(f"Failed: {self.failed} ❌")
        print(f"Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        print(f"Total Duration: {duration:.2f}s")
        
        if self.errors:
            print("\n" + "=" * 60)
            print("ERRORS")
            print("=" * 60)
            for error in self.errors:
                print(f"❌ {error}")
        
        return all(results)


if __name__ == "__main__":
    runner = SimpleTestRunner()
    success = runner.run_all_tests()
    
    if success:
        print("\n✅ All tests passed!")
        sys.exit(0)
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)