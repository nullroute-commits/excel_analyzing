#!/usr/bin/env python3
"""
Main module for Excel Analyzer - demonstrating usage
"""

import argparse
import json
from pathlib import Path
from excel_analyzer import ExcelAnalyzer


def main():
    """Main function to demonstrate Excel analysis capabilities"""
    parser = argparse.ArgumentParser(description='Analyze Excel workbooks like databases')
    parser.add_argument('file_path', help='Path to Excel file (.xlsx or .xls)')
    parser.add_argument('--sheet', help='Specific sheet to analyze')
    parser.add_argument('--query', help='Query to run on the sheet (requires --sheet)')
    parser.add_argument('--summary', action='store_true', help='Show workbook summary')
    parser.add_argument('--output', help='Output file for results (JSON format)')
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer
        analyzer = ExcelAnalyzer(args.file_path)
        
        if args.summary:
            # Show full workbook summary
            summary = analyzer.get_workbook_summary()
            print(json.dumps(summary, indent=2, default=str))
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(summary, f, indent=2, default=str)
                print(f"Summary saved to {args.output}")
        
        elif args.sheet:
            if args.query:
                # Run query on specific sheet
                result = analyzer.query_sheet(args.sheet, args.query)
                print(f"Query results for '{args.query}' on sheet '{args.sheet}':")
                print(result.to_string())
                
                if args.output:
                    result.to_json(args.output, indent=2)
                    print(f"Query results saved to {args.output}")
            else:
                # Analyze specific sheet
                analysis = analyzer.analyze_sheet(args.sheet)
                print(json.dumps(analysis, indent=2, default=str))
                
                if args.output:
                    with open(args.output, 'w') as f:
                        json.dump(analysis, f, indent=2, default=str)
                    print(f"Analysis saved to {args.output}")
        
        else:
            # Show basic info
            print(f"Excel file: {args.file_path}")
            print(f"Sheets available: {analyzer.list_sheets()}")
            print("\nUse --summary for full analysis or --sheet <name> for specific sheet analysis")
            print("Example: python main.py data.xlsx --sheet Sheet1 --query \"column_name > 100\"")
    
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())