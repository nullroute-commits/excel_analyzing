#!/usr/bin/env python3
"""
Simple test to validate Excel Analyzer functionality
"""

import pandas as pd
import tempfile
import os
from excel_analyzer import ExcelAnalyzer


def create_test_excel():
    """Create a test Excel file for demonstration"""
    # Create sample data
    data1 = {
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 75000, 55000],
        'Department': ['IT', 'HR', 'IT', 'Finance']
    }
    
    data2 = {
        'Product': ['Widget A', 'Widget B', 'Widget C'],
        'Price': [10.99, 15.50, 8.75],
        'Stock': [100, 75, 200]
    }
    
    # Create temporary Excel file
    with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
        temp_path = tmp.name
    
    # Write to Excel with multiple sheets
    with pd.ExcelWriter(temp_path, engine='openpyxl') as writer:
        pd.DataFrame(data1).to_excel(writer, sheet_name='Employees', index=False)
        pd.DataFrame(data2).to_excel(writer, sheet_name='Products', index=False)
    
    return temp_path


def test_excel_analyzer():
    """Test the ExcelAnalyzer functionality"""
    print("Creating test Excel file...")
    test_file = create_test_excel()
    
    try:
        print(f"Test file created: {test_file}")
        
        # Initialize analyzer
        print("\nInitializing ExcelAnalyzer...")
        analyzer = ExcelAnalyzer(test_file)
        
        # Test basic functionality
        print(f"Sheets found: {analyzer.list_sheets()}")
        
        # Analyze Employees sheet
        print("\nAnalyzing 'Employees' sheet:")
        employees_analysis = analyzer.analyze_sheet('Employees')
        print(f"Shape: {employees_analysis['shape']}")
        print(f"Columns: {employees_analysis['columns']}")
        print(f"Data types: {employees_analysis['data_types']}")
        
        # Test query functionality
        print("\nTesting query functionality:")
        high_earners = analyzer.query_sheet('Employees', 'Salary > 55000')
        print(f"Employees with salary > 55000:")
        print(high_earners.to_string())
        
        # Get workbook summary
        print("\nGetting workbook summary...")
        summary = analyzer.get_workbook_summary()
        print(f"Total sheets: {summary['total_sheets']}")
        print(f"Total rows: {summary['total_rows']}")
        print(f"Total columns: {summary['total_columns']}")
        
        print("\n✅ All tests passed! Excel Analyzer is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"Cleaned up test file: {test_file}")
    
    return True


if __name__ == "__main__":
    success = test_excel_analyzer()
    exit(0 if success else 1)