"""Unit tests for Excel data processor."""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch

from excel_analyzing.models.schemas import DataType, ProcessingOptions
from excel_analyzing.pipeline.processor import ExcelDataProcessor


class TestExcelDataProcessor:
    """Test ExcelDataProcessor class."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ExcelDataProcessor()
        assert processor.options is not None
        assert isinstance(processor.options, ProcessingOptions)
        assert processor._dataframes == {}
        assert processor._original_dataframes == {}
    
    def test_processor_with_custom_options(self):
        """Test processor with custom options."""
        options = ProcessingOptions(
            drop_empty_rows=False,
            clean_column_names=False,
        )
        processor = ExcelDataProcessor(options)
        assert processor.options.drop_empty_rows is False
        assert processor.options.clean_column_names is False
    
    def test_clean_column_name(self):
        """Test column name cleaning."""
        processor = ExcelDataProcessor()
        
        # Test basic cleaning
        assert processor._clean_column_name("Test Column") == "test_column"
        assert processor._clean_column_name("  Spaced  ") == "spaced"
        assert processor._clean_column_name("Special@#$%Characters") == "special_characters"
        assert processor._clean_column_name("Multiple   Spaces") == "multiple_spaces"
        
        # Test edge cases
        assert processor._clean_column_name("") == "unnamed_column"
        assert processor._clean_column_name("   ") == "unnamed_column"
        assert processor._clean_column_name(None) == "unnamed_column"
        assert processor._clean_column_name("123_starts_with_number") == "col_123_starts_with_number"
    
    def test_clean_sheet_name(self):
        """Test sheet name cleaning."""
        processor = ExcelDataProcessor()
        
        assert processor._clean_sheet_name("Test Sheet") == "test_sheet"
        assert processor._clean_sheet_name("Special@Characters") == "special_characters"
        assert processor._clean_sheet_name("") == "unnamed_sheet"
        assert processor._clean_sheet_name("   ") == "unnamed_sheet"
    
    def test_infer_data_type_string(self):
        """Test data type inference for strings."""
        processor = ExcelDataProcessor()
        
        string_series = pd.Series(["hello", "world", "test"])
        assert processor._infer_data_type(string_series) == DataType.STRING
    
    def test_infer_data_type_integer(self):
        """Test data type inference for integers."""
        processor = ExcelDataProcessor()
        
        int_series = pd.Series([1, 2, 3, 4])
        assert processor._infer_data_type(int_series) == DataType.INTEGER
    
    def test_infer_data_type_float(self):
        """Test data type inference for floats."""
        processor = ExcelDataProcessor()
        
        float_series = pd.Series([1.1, 2.2, 3.3])
        assert processor._infer_data_type(float_series) == DataType.FLOAT
    
    def test_infer_data_type_boolean(self):
        """Test data type inference for booleans."""
        processor = ExcelDataProcessor()
        
        bool_series = pd.Series([True, False, True])
        assert processor._infer_data_type(bool_series) == DataType.BOOLEAN
        
        bool_string_series = pd.Series(["True", "False", "true"])
        assert processor._infer_data_type(bool_string_series) == DataType.BOOLEAN
    
    def test_infer_data_type_empty(self):
        """Test data type inference for empty series."""
        processor = ExcelDataProcessor()
        
        empty_series = pd.Series([])
        assert processor._infer_data_type(empty_series) == DataType.STRING
    
    def test_find_header_row(self):
        """Test header row detection."""
        processor = ExcelDataProcessor()
        
        # DataFrame with clear header in first row
        df_with_header = pd.DataFrame([
            ["Name", "Age", "City"],
            ["John", 25, "NYC"],
            ["Jane", 30, "LA"],
        ])
        assert processor._find_header_row(df_with_header) == 0
        
        # DataFrame with empty first row
        df_empty_first = pd.DataFrame([
            [None, None, None],
            ["Name", "Age", "City"],
            ["John", 25, "NYC"],
        ])
        assert processor._find_header_row(df_empty_first) == 1
        
        # DataFrame with no clear header
        df_no_header = pd.DataFrame([
            [None, None, None],
            [None, None, None],
            [None, None, None],
        ])
        assert processor._find_header_row(df_no_header) is None
    
    def test_analyze_column(self):
        """Test column analysis."""
        processor = ExcelDataProcessor()
        
        # Test string column
        string_series = pd.Series(["A", "B", "C", "A"])
        column_info = processor._analyze_column(string_series, "test_col", "Test Col", 0)
        
        assert column_info.name == "test_col"
        assert column_info.original_name == "Test Col"
        assert column_info.position == 0
        assert column_info.data_type == DataType.STRING
        assert column_info.unique_count == 3  # A, B, C
        assert column_info.null_count == 0
        assert len(column_info.sample_values) == 4
    
    def test_analyze_column_with_nulls(self):
        """Test column analysis with null values."""
        processor = ExcelDataProcessor()
        
        series_with_nulls = pd.Series([1, 2, None, 4, None])
        column_info = processor._analyze_column(series_with_nulls, "test_col", "Test Col", 0)
        
        assert column_info.null_count == 2
        assert column_info.is_nullable is True
        assert column_info.unique_count == 3  # 1, 2, 4
    
    @patch('pandas.read_excel')
    def test_load_workbook_file_not_found(self, mock_read_excel):
        """Test loading non-existent workbook."""
        processor = ExcelDataProcessor()
        
        with pytest.raises(FileNotFoundError):
            processor.load_workbook("/nonexistent/file.xlsx")
    
    def test_get_dataframe_nonexistent(self):
        """Test getting non-existent dataframe."""
        processor = ExcelDataProcessor()
        
        df = processor.get_dataframe("nonexistent", "sheet")
        assert df is None
    
    def test_apply_filter_nonexistent(self):
        """Test applying filter to non-existent dataframe."""
        processor = ExcelDataProcessor()
        
        result = processor.apply_filter("nonexistent", "sheet", "column > 0")
        assert result is None
    
    def test_apply_transformation_nonexistent(self):
        """Test applying transformation to non-existent dataframe."""
        processor = ExcelDataProcessor()
        
        result = processor.apply_transformation("nonexistent", "sheet", {"operation": "sort"})
        assert result is None
    
    def test_get_summary_statistics_nonexistent(self):
        """Test getting summary statistics for non-existent dataframe."""
        processor = ExcelDataProcessor()
        
        result = processor.get_summary_statistics("nonexistent", "sheet")
        assert result is None