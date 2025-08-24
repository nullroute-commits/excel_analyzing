"""Pandas wrapper for Excel data processing."""

import json
import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import pandas as pd
from openpyxl import load_workbook

from ..models.schemas import (
    ColumnInfo,
    DataType,
    ProcessingOptions,
    SheetInfo,
    WorkbookInfo,
)

logger = logging.getLogger(__name__)


class ExcelDataProcessor:
    """Pandas wrapper class for processing Excel data with filters and transformations."""
    
    def __init__(self, processing_options: Optional[ProcessingOptions] = None):
        """Initialize Excel data processor."""
        self.options = processing_options or ProcessingOptions()
        self._dataframes: Dict[str, pd.DataFrame] = {}
        self._original_dataframes: Dict[str, pd.DataFrame] = {}
    
    def load_workbook(self, file_path: Union[str, Path]) -> WorkbookInfo:
        """Load an Excel workbook and extract metadata."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        logger.info(f"Loading workbook: {file_path}")
        
        # Get file metadata
        file_size = file_path.stat().st_size
        file_name = file_path.name
        
        # Load workbook to get sheet names
        try:
            # Try openpyxl first for .xlsx files
            if file_path.suffix.lower() in ['.xlsx', '.xlsm']:
                wb = load_workbook(file_path, read_only=True, data_only=True)
                sheet_names = wb.sheetnames
                wb.close()
            else:
                # Fall back to pandas for older formats
                excel_file = pd.ExcelFile(file_path)
                sheet_names = excel_file.sheet_names
                excel_file.close()
        except Exception as e:
            logger.error(f"Failed to load workbook {file_path}: {e}")
            raise
        
        # Create workbook info
        workbook_info = WorkbookInfo(
            file_path=file_path,
            file_name=file_name,
            file_size_bytes=file_size,
            sheet_count=len(sheet_names),
        )
        
        # Process each sheet
        for sheet_name in sheet_names:
            try:
                sheet_info = self._process_sheet(file_path, sheet_name)
                workbook_info.sheets.append(sheet_info)
            except Exception as e:
                logger.warning(f"Failed to process sheet '{sheet_name}' in {file_path}: {e}")
                continue
        
        return workbook_info
    
    def _process_sheet(self, file_path: Path, sheet_name: str) -> SheetInfo:
        """Process a single Excel sheet."""
        logger.debug(f"Processing sheet '{sheet_name}' from {file_path}")
        
        # Load the sheet data
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
        except Exception as e:
            logger.error(f"Failed to read sheet '{sheet_name}': {e}")
            raise
        
        # Store original dataframe
        self._original_dataframes[f"{file_path.stem}_{sheet_name}"] = df.copy()
        
        # Find header row (assume first non-empty row)
        header_row = self._find_header_row(df)
        
        # Extract headers
        if header_row is not None:
            headers = df.iloc[header_row].fillna('').astype(str).tolist()
            data_start_row = header_row + 1
            has_header = True
        else:
            # Generate default headers if no header found
            headers = [f"Column_{i}" for i in range(len(df.columns))]
            data_start_row = 0
            has_header = False
        
        # Clean column names if requested
        if self.options.clean_column_names:
            cleaned_headers = [self._clean_column_name(header) for header in headers]
        else:
            cleaned_headers = headers
        
        # Set up dataframe with proper headers
        if has_header:
            df_data = df.iloc[data_start_row:].copy()
        else:
            df_data = df.copy()
        
        df_data.columns = cleaned_headers
        
        # Drop empty rows and columns if requested
        if self.options.drop_empty_rows:
            df_data = df_data.dropna(how='all')
        
        if self.options.drop_empty_columns:
            df_data = df_data.dropna(axis=1, how='all')
        
        # Drop columns with too many nulls
        if self.options.null_threshold < 1.0:
            null_percentages = df_data.isnull().sum() / len(df_data)
            columns_to_keep = null_percentages[null_percentages <= self.options.null_threshold].index
            df_data = df_data[columns_to_keep]
        
        # Store processed dataframe
        self._dataframes[f"{file_path.stem}_{sheet_name}"] = df_data
        
        # Analyze columns
        columns_info = []
        for i, col_name in enumerate(df_data.columns):
            original_name = headers[i] if i < len(headers) else col_name
            col_info = self._analyze_column(df_data[col_name], col_name, original_name, i)
            columns_info.append(col_info)
        
        # Create sheet info
        sheet_info = SheetInfo(
            name=self._clean_sheet_name(sheet_name),
            original_name=sheet_name,
            row_count=len(df_data),
            column_count=len(df_data.columns),
            has_header=has_header,
            header_row=header_row or 0,
            data_start_row=data_start_row,
            columns=columns_info,
        )
        
        return sheet_info
    
    def _find_header_row(self, df: pd.DataFrame) -> Optional[int]:
        """Find the row containing headers."""
        for i in range(min(5, len(df))):  # Check first 5 rows
            row = df.iloc[i]
            non_null_count = row.notna().sum()
            if non_null_count >= len(df.columns) * 0.5:  # At least 50% non-null
                return i
        return None
    
    def _clean_column_name(self, name: str) -> str:
        """Clean and normalize column names."""
        if not name or pd.isna(name):
            return "unnamed_column"
        
        # Convert to string and strip whitespace
        name = str(name).strip()
        
        # Replace spaces and special characters with underscores
        name = re.sub(r'[^\w\s]', '_', name)
        name = re.sub(r'\s+', '_', name)
        
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name)
        
        # Remove leading/trailing underscores
        name = name.strip('_')
        
        # Ensure it starts with a letter or underscore
        if name and not name[0].isalpha() and name[0] != '_':
            name = f"col_{name}"
        
        # Handle empty names
        if not name:
            return "unnamed_column"
        
        # Convert to lowercase for consistency
        return name.lower()
    
    def _clean_sheet_name(self, name: str) -> str:
        """Clean and normalize sheet names."""
        if not name:
            return "unnamed_sheet"
        
        # Replace problematic characters
        name = re.sub(r'[^\w\s-]', '_', name)
        name = re.sub(r'\s+', '_', name)
        name = re.sub(r'_+', '_', name)
        name = name.strip('_')
        
        return name.lower() if name else "unnamed_sheet"
    
    def _analyze_column(self, series: pd.Series, name: str, original_name: str, position: int) -> ColumnInfo:
        """Analyze a column and infer its data type and properties."""
        # Basic statistics
        total_count = len(series)
        null_count = series.isnull().sum()
        non_null_series = series.dropna()
        unique_count = non_null_series.nunique() if not non_null_series.empty else 0
        
        # Infer data type
        data_type = self._infer_data_type(non_null_series) if self.options.infer_data_types else DataType.STRING
        
        # Get sample values
        sample_size = min(self.options.max_sample_size, len(non_null_series))
        sample_values = non_null_series.head(sample_size).tolist() if not non_null_series.empty else []
        
        return ColumnInfo(
            name=name,
            original_name=original_name,
            position=position,
            data_type=data_type,
            is_nullable=null_count > 0,
            sample_values=sample_values,
            unique_count=unique_count,
            null_count=int(null_count),
        )
    
    def _infer_data_type(self, series: pd.Series) -> DataType:
        """Infer the data type of a pandas series."""
        if series.empty:
            return DataType.STRING
        
        # Check for boolean first (before numeric)
        if series.dtype == 'bool' or series.isin([True, False, 'True', 'False', 'true', 'false']).all():
            return DataType.BOOLEAN
        
        # Try to infer numeric types
        try:
            # Check if all values can be converted to integers
            pd.to_numeric(series, errors='raise')
            if series.apply(lambda x: float(x).is_integer()).all():
                return DataType.INTEGER
            else:
                return DataType.FLOAT
        except (ValueError, TypeError):
            pass
        
        # Check for datetime
        try:
            pd.to_datetime(series, errors='raise')
            # Check if it's just date (no time component)
            dt_series = pd.to_datetime(series)
            if dt_series.dt.time.apply(lambda x: x == pd.Timestamp('00:00:00').time()).all():
                return DataType.DATE
            else:
                return DataType.DATETIME
        except (ValueError, TypeError):
            pass
        
        # Default to string
        return DataType.STRING
    
    def get_dataframe(self, workbook_name: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """Get processed dataframe for a specific sheet."""
        key = f"{workbook_name}_{sheet_name}"
        return self._dataframes.get(key)
    
    def get_original_dataframe(self, workbook_name: str, sheet_name: str) -> Optional[pd.DataFrame]:
        """Get original dataframe for a specific sheet."""
        key = f"{workbook_name}_{sheet_name}"
        return self._original_dataframes.get(key)
    
    def apply_filter(self, workbook_name: str, sheet_name: str, filter_condition: str) -> Optional[pd.DataFrame]:
        """Apply a filter to a dataframe using pandas query syntax."""
        df = self.get_dataframe(workbook_name, sheet_name)
        if df is None:
            return None
        
        try:
            return df.query(filter_condition)
        except Exception as e:
            logger.error(f"Failed to apply filter '{filter_condition}': {e}")
            return None
    
    def apply_transformation(self, workbook_name: str, sheet_name: str, transformation: Dict[str, Any]) -> Optional[pd.DataFrame]:
        """Apply a transformation to a dataframe."""
        df = self.get_dataframe(workbook_name, sheet_name)
        if df is None:
            return None
        
        try:
            # Example transformations
            if transformation.get('operation') == 'group_by':
                columns = transformation.get('columns', [])
                agg_func = transformation.get('agg_func', 'count')
                return df.groupby(columns).agg(agg_func)
            
            elif transformation.get('operation') == 'sort':
                columns = transformation.get('columns', [])
                ascending = transformation.get('ascending', True)
                return df.sort_values(columns, ascending=ascending)
            
            elif transformation.get('operation') == 'select':
                columns = transformation.get('columns', [])
                return df[columns]
            
            else:
                logger.warning(f"Unknown transformation operation: {transformation.get('operation')}")
                return df
                
        except Exception as e:
            logger.error(f"Failed to apply transformation {transformation}: {e}")
            return None
    
    def get_summary_statistics(self, workbook_name: str, sheet_name: str) -> Optional[Dict[str, Any]]:
        """Get summary statistics for a dataframe."""
        df = self.get_dataframe(workbook_name, sheet_name)
        if df is None:
            return None
        
        numeric_df = df.select_dtypes(include=['number'])
        
        summary = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'numeric_columns': len(numeric_df.columns),
            'memory_usage_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
        
        if not numeric_df.empty:
            summary['numeric_summary'] = numeric_df.describe().to_dict()
        
        return summary