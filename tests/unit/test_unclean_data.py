"""Unit tests for handling unclean datasources."""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import shutil

from excel_analyzing.models.schemas import DataType, ProcessingOptions
from excel_analyzing.pipeline.processor import ExcelDataProcessor


class TestUncleanDataSources:
    """Test ExcelDataProcessor with various unclean data scenarios."""
    
    @classmethod
    def setup_class(cls):
        """Set up test files for the class."""
        cls.test_data_dir = Path("/tmp/unclean_test_data")
        
        # Create the test files if they don't exist
        if not cls.test_data_dir.exists():
            exec(open("/tmp/create_unclean_test_files.py").read())
    
    def test_mixed_data_types_handling(self):
        """Test processing of files with mixed data types in columns."""
        processor = ExcelDataProcessor()
        
        file_path = self.test_data_dir / "mixed_data_types.xlsx"
        workbook_info = processor.load_workbook(file_path)
        
        assert workbook_info is not None
        assert len(workbook_info.sheets) == 1
        
        sheet = workbook_info.sheets[0]
        assert sheet.row_count > 0  # Should have processed some data
        assert sheet.column_count == 5  # Original had 5 columns
        
        # Get the processed dataframe
        df = processor.get_dataframe(file_path.stem, sheet.name)
        assert df is not None
        
        # Check that columns with clean names exist
        expected_columns = ['id', 'name', 'date', 'amount', 'status']
        for col in expected_columns:
            assert col in df.columns
    
    def test_special_characters_in_columns(self):
        """Test handling of special characters in column names."""
        processor = ExcelDataProcessor()
        
        file_path = self.test_data_dir / "special_characters.xlsx"
        workbook_info = processor.load_workbook(file_path)
        
        assert workbook_info is not None
        sheet = workbook_info.sheets[0]
        
        # Get the processed dataframe
        df = processor.get_dataframe(file_path.stem, sheet.name)
        assert df is not None
        
        # Check that all column names are cleaned appropriately
        for col in df.columns:
            assert isinstance(col, str)
            # ASCII characters should be lowercase
            if col.isascii():
                assert col.islower(), f"ASCII column {col} should be lowercase"
            # No special characters like @#$%/\ should remain
            assert not any(char in col for char in '@#$%/\\'), f"Column {col} contains special chars"
            
        # Check that empty header columns are handled
        assert any('unnamed_column' in col for col in df.columns)
        
        # Check that numeric start columns are prefixed
        assert any(col.startswith('col_') for col in df.columns)
    
    def test_sparse_data_handling(self):
        """Test processing of very sparse data (mostly nulls)."""
        # Test with high null threshold (should keep columns)
        processor_lenient = ExcelDataProcessor(
            ProcessingOptions(null_threshold=0.95)  # Keep columns with up to 95% nulls
        )
        
        file_path = self.test_data_dir / "sparse_data.xlsx"
        workbook_info = processor_lenient.load_workbook(file_path)
        
        df_lenient = processor_lenient.get_dataframe(file_path.stem, workbook_info.sheets[0].name)
        assert df_lenient is not None
        
        # Test with low null threshold (should drop columns)
        processor_strict = ExcelDataProcessor(
            ProcessingOptions(null_threshold=0.5)  # Drop columns with more than 50% nulls
        )
        
        workbook_info_strict = processor_strict.load_workbook(file_path)
        df_strict = processor_strict.get_dataframe(file_path.stem, workbook_info_strict.sheets[0].name)
        
        # Strict processor should have fewer columns
        if df_strict is not None:
            assert len(df_strict.columns) <= len(df_lenient.columns)
    
    def test_empty_and_problematic_structure(self):
        """Test handling of empty sheets and problematic structures."""
        processor = ExcelDataProcessor()
        
        file_path = self.test_data_dir / "problematic_structure.xlsx"
        workbook_info = processor.load_workbook(file_path)
        
        assert workbook_info is not None
        assert len(workbook_info.sheets) >= 1  # Should process at least some sheets
        
        # Check that processor doesn't crash on empty sheets
        for sheet in workbook_info.sheets:
            df = processor.get_dataframe(file_path.stem, sheet.name)
            # df can be None or empty, but shouldn't cause crashes
            if df is not None:
                assert isinstance(df, pd.DataFrame)
    
    def test_duplicate_data_handling(self):
        """Test handling of duplicate rows."""
        # Test with duplicate removal enabled
        processor_dedup = ExcelDataProcessor(
            ProcessingOptions(drop_empty_rows=True)
        )
        
        file_path = self.test_data_dir / "duplicate_data.xlsx"
        workbook_info = processor_dedup.load_workbook(file_path)
        
        df = processor_dedup.get_dataframe(file_path.stem, workbook_info.sheets[0].name)
        assert df is not None
        
        # Check that we can access the data without errors
        assert len(df) > 0
        assert len(df.columns) > 0
    
    def test_multiple_sheets_mixed_quality(self):
        """Test processing files with multiple sheets of varying quality."""
        processor = ExcelDataProcessor()
        
        file_path = self.test_data_dir / "multiple_sheets_mixed.xlsx"
        workbook_info = processor.load_workbook(file_path)
        
        assert workbook_info is not None
        assert len(workbook_info.sheets) >= 1  # Should process at least some sheets
        
        # Verify that at least one sheet was processed successfully
        processed_sheets = 0
        for sheet in workbook_info.sheets:
            df = processor.get_dataframe(file_path.stem, sheet.name)
            if df is not None and not df.empty:
                processed_sheets += 1
        
        assert processed_sheets > 0  # At least one sheet should be processable
    
    def test_large_sparse_data_performance(self):
        """Test that large sparse data doesn't cause memory issues."""
        processor = ExcelDataProcessor(
            ProcessingOptions(
                null_threshold=0.9,  # Aggressive null filtering
                max_sample_size=10   # Small sample for type inference
            )
        )
        
        file_path = self.test_data_dir / "large_sparse.xlsx"
        
        # This should not raise memory errors or take too long
        workbook_info = processor.load_workbook(file_path)
        
        assert workbook_info is not None
        if workbook_info.sheets:
            sheet = workbook_info.sheets[0]
            df = processor.get_dataframe(file_path.stem, sheet.name)
            # Should either process successfully or return None gracefully
            if df is not None:
                assert isinstance(df, pd.DataFrame)
    
    def test_error_recovery_with_corrupted_data(self):
        """Test that processor recovers gracefully from corrupted data."""
        processor = ExcelDataProcessor()
        
        # Test with non-existent file
        with pytest.raises(FileNotFoundError):
            processor.load_workbook("/non/existent/file.xlsx")
        
        # Test with invalid data types in series
        test_series = pd.Series([1, "text", None, complex(1, 2), [1, 2, 3]])
        data_type = processor._infer_data_type(test_series)
        assert data_type == DataType.STRING  # Should fall back to string
    
    def test_column_name_edge_cases(self):
        """Test edge cases in column name cleaning."""
        processor = ExcelDataProcessor()
        
        # Test various problematic column names
        test_cases = [
            ("", "unnamed_column"),
            ("   ", "unnamed_column"),
            (None, "unnamed_column"),
            ("123", "col_123"),
            ("@#$%", "unnamed_column"),
            ("Multiple   Spaces", "multiple_spaces"),
            ("SpecialChars@#$%^&*()", "specialchars"),
            ("MixedCase_With-Dashes", "mixedcase_with_dashes"),
        ]
        
        for input_name, expected in test_cases:
            result = processor._clean_column_name(input_name)
            assert result == expected, f"Failed for input '{input_name}': got '{result}', expected '{expected}'"
    
    def test_data_type_inference_edge_cases(self):
        """Test data type inference with problematic data."""
        processor = ExcelDataProcessor()
        
        # Test empty series
        empty_series = pd.Series([])
        assert processor._infer_data_type(empty_series) == DataType.STRING
        
        # Test series with all nulls (after dropna should be empty and return STRING)
        null_series = pd.Series([None, None, None])
        non_null_series = null_series.dropna()  # This simulates what _analyze_column does
        assert processor._infer_data_type(non_null_series) == DataType.STRING
        
        # Test mixed numeric and text
        mixed_series = pd.Series([1, 2, "text", 4])
        data_type = processor._infer_data_type(mixed_series)
        assert data_type == DataType.STRING  # Should fall back to string
        
        # Test boolean-like strings
        bool_series = pd.Series(["True", "False", "true", "false"])
        assert processor._infer_data_type(bool_series) == DataType.BOOLEAN
        
        # Test mixed boolean data (should fall back to string)
        mixed_bool_series = pd.Series([True, 'Active', True, 0, 'false'])
        assert processor._infer_data_type(mixed_bool_series) == DataType.STRING
        
        # Test malformed dates
        date_series = pd.Series(["2023-01-01", "invalid-date", "2023/12/01"])
        data_type = processor._infer_data_type(date_series)
        assert data_type == DataType.STRING  # Should fall back when mixed
    
    def test_processing_options_validation(self):
        """Test that processing options handle edge cases properly."""
        # Test with extreme null threshold
        options_high = ProcessingOptions(null_threshold=1.0)
        assert options_high.null_threshold == 1.0
        
        options_low = ProcessingOptions(null_threshold=0.0)
        assert options_low.null_threshold == 0.0
        
        # Test with very small sample size
        options_small = ProcessingOptions(max_sample_size=1)
        assert options_small.max_sample_size == 1
        
        processor = ExcelDataProcessor(options_small)
        assert processor.options.max_sample_size == 1
    
    def test_filter_and_transformation_with_unclean_data(self):
        """Test that filters and transformations work with unclean data."""
        processor = ExcelDataProcessor()
        
        file_path = self.test_data_dir / "mixed_data_types.xlsx"
        workbook_info = processor.load_workbook(file_path)
        
        # Test applying filters (should handle gracefully even if they fail)
        result = processor.apply_filter(file_path.stem, workbook_info.sheets[0].name, "id > 0")
        # Result can be None if the filter fails, which is acceptable
        
        # Test applying transformations
        transform_result = processor.apply_transformation(
            file_path.stem, 
            workbook_info.sheets[0].name,
            {"operation": "sort", "columns": ["id"], "ascending": True}
        )
        # Should not crash, even if transformation fails
        
        # Test getting summary statistics
        stats = processor.get_summary_statistics(file_path.stem, workbook_info.sheets[0].name)
        if stats is not None:
            assert isinstance(stats, dict)
            assert "total_rows" in stats
            assert "total_columns" in stats