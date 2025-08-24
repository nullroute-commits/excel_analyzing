"""
Excel Analyzer - Analyze Excel workbooks like databases and sheets like tables
"""

import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any


class ExcelAnalyzer:
    """Analyze Excel workbooks with database-like operations"""
    
    def __init__(self, file_path: str):
        """Initialize with Excel file path"""
        self.file_path = Path(file_path)
        self.workbook_data: Dict[str, pd.DataFrame] = {}
        self._load_workbook()
    
    def _load_workbook(self) -> None:
        """Load all sheets from the Excel workbook"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {self.file_path}")
        
        try:
            # Read all sheets
            all_sheets = pd.read_excel(self.file_path, sheet_name=None)
            self.workbook_data = all_sheets
            print(f"Loaded {len(all_sheets)} sheets from {self.file_path.name}")
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {e}")
    
    def list_sheets(self) -> List[str]:
        """List all sheet names in the workbook"""
        return list(self.workbook_data.keys())
    
    def get_sheet(self, sheet_name: str) -> pd.DataFrame:
        """Get a specific sheet as DataFrame"""
        if sheet_name not in self.workbook_data:
            raise ValueError(f"Sheet '{sheet_name}' not found. Available sheets: {self.list_sheets()}")
        return self.workbook_data[sheet_name]
    
    def analyze_sheet(self, sheet_name: str) -> Dict[str, Any]:
        """Analyze a sheet and return summary statistics"""
        df = self.get_sheet(sheet_name)
        
        analysis = {
            'name': sheet_name,
            'shape': df.shape,
            'columns': list(df.columns),
            'data_types': df.dtypes.to_dict(),
            'missing_values': df.isnull().sum().to_dict(),
            'memory_usage': df.memory_usage(deep=True).sum(),
            'numeric_columns': df.select_dtypes(include=['number']).columns.tolist(),
            'text_columns': df.select_dtypes(include=['object']).columns.tolist()
        }
        
        # Add summary statistics for numeric columns
        if analysis['numeric_columns']:
            analysis['numeric_summary'] = df[analysis['numeric_columns']].describe().to_dict()
        
        return analysis
    
    def query_sheet(self, sheet_name: str, query: str) -> pd.DataFrame:
        """Query a sheet using pandas query syntax"""
        df = self.get_sheet(sheet_name)
        try:
            return df.query(query)
        except Exception as e:
            raise ValueError(f"Invalid query '{query}': {e}")
    
    def get_workbook_summary(self) -> Dict[str, Any]:
        """Get summary of entire workbook"""
        summary = {
            'file_path': str(self.file_path),
            'total_sheets': len(self.workbook_data),
            'sheet_names': self.list_sheets(),
            'total_rows': sum(df.shape[0] for df in self.workbook_data.values()),
            'total_columns': sum(df.shape[1] for df in self.workbook_data.values()),
            'file_size_mb': self.file_path.stat().st_size / (1024 * 1024)
        }
        
        # Analyze each sheet
        summary['sheet_analyses'] = {}
        for sheet_name in self.list_sheets():
            summary['sheet_analyses'][sheet_name] = self.analyze_sheet(sheet_name)
        
        return summary