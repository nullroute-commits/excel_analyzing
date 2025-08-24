"""Unit tests for data models."""

import pytest
from pathlib import Path
from datetime import datetime

from excel_analyzing.models.schemas import (
    ColumnInfo,
    DataType,
    ProcessingOptions,
    SheetInfo,
    WorkbookInfo,
)


class TestColumnInfo:
    """Test ColumnInfo model."""
    
    def test_column_info_creation(self):
        """Test creating a ColumnInfo instance."""
        column = ColumnInfo(
            name="test_column",
            original_name="Test Column",
            position=0,
            data_type=DataType.STRING,
            sample_values=["value1", "value2"],
            unique_count=2,
            null_count=0,
        )
        
        assert column.name == "test_column"
        assert column.original_name == "Test Column"
        assert column.position == 0
        assert column.data_type == DataType.STRING
        assert column.sample_values == ["value1", "value2"]
        assert column.unique_count == 2
        assert column.null_count == 0
        assert column.is_nullable is True
    
    def test_column_name_validation(self):
        """Test column name validation."""
        with pytest.raises(ValueError, match="Column name cannot be empty"):
            ColumnInfo(
                name="",
                original_name="Test",
                position=0,
                data_type=DataType.STRING,
            )
    
    def test_column_name_strip(self):
        """Test column name is stripped of whitespace."""
        column = ColumnInfo(
            name="  test_column  ",
            original_name="Test Column",
            position=0,
            data_type=DataType.STRING,
        )
        
        assert column.name == "test_column"


class TestSheetInfo:
    """Test SheetInfo model."""
    
    def test_sheet_info_creation(self):
        """Test creating a SheetInfo instance."""
        columns = [
            ColumnInfo(
                name="col1",
                original_name="Column 1",
                position=0,
                data_type=DataType.STRING,
            )
        ]
        
        sheet = SheetInfo(
            name="test_sheet",
            original_name="Test Sheet",
            row_count=100,
            column_count=1,
            columns=columns,
        )
        
        assert sheet.name == "test_sheet"
        assert sheet.original_name == "Test Sheet"
        assert sheet.row_count == 100
        assert sheet.column_count == 1
        assert len(sheet.columns) == 1
        assert sheet.has_header is True
        assert sheet.header_row == 0
        assert sheet.data_start_row == 1
    
    def test_sheet_name_validation(self):
        """Test sheet name validation."""
        with pytest.raises(ValueError, match="Sheet name cannot be empty"):
            SheetInfo(
                name="",
                original_name="Test",
                row_count=100,
                column_count=1,
            )
    
    def test_data_start_row_validation(self):
        """Test data start row validation."""
        with pytest.raises(ValueError, match="Data start row must be after header row"):
            SheetInfo(
                name="test_sheet",
                original_name="Test Sheet",
                row_count=100,
                column_count=1,
                header_row=1,
                data_start_row=1,
            )


class TestWorkbookInfo:
    """Test WorkbookInfo model."""
    
    def test_workbook_info_creation(self, tmp_path):
        """Test creating a WorkbookInfo instance."""
        # Create a temporary file
        test_file = tmp_path / "test.xlsx"
        test_file.write_text("test content")
        
        workbook = WorkbookInfo(
            file_path=test_file,
            file_name="test.xlsx",
            file_size_bytes=1024,
            sheet_count=2,
        )
        
        assert workbook.file_path == test_file
        assert workbook.file_name == "test.xlsx"
        assert workbook.file_size_bytes == 1024
        assert workbook.sheet_count == 2
        assert len(workbook.sheets) == 0
        assert workbook.processed_at is None
    
    def test_file_path_validation_nonexistent(self):
        """Test file path validation for non-existent file."""
        with pytest.raises(ValueError, match="File does not exist"):
            WorkbookInfo(
                file_path=Path("/nonexistent/file.xlsx"),
                file_name="file.xlsx",
                file_size_bytes=1024,
                sheet_count=1,
            )
    
    def test_file_path_validation_directory(self, tmp_path):
        """Test file path validation for directory."""
        with pytest.raises(ValueError, match="Path is not a file"):
            WorkbookInfo(
                file_path=tmp_path,
                file_name="directory",
                file_size_bytes=1024,
                sheet_count=1,
            )
    
    def test_file_name_validation(self, tmp_path):
        """Test file name validation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with pytest.raises(ValueError, match="Invalid Excel file extension"):
            WorkbookInfo(
                file_path=test_file,
                file_name="test.txt",
                file_size_bytes=1024,
                sheet_count=1,
            )


class TestProcessingOptions:
    """Test ProcessingOptions model."""
    
    def test_processing_options_defaults(self):
        """Test ProcessingOptions default values."""
        options = ProcessingOptions()
        
        assert options.drop_empty_rows is True
        assert options.drop_empty_columns is True
        assert options.infer_data_types is True
        assert options.clean_column_names is True
        assert options.max_sample_size == 100
        assert options.null_threshold == 0.9
    
    def test_null_threshold_validation(self):
        """Test null threshold validation."""
        with pytest.raises((ValueError, Exception)):  # Pydantic ValidationError
            ProcessingOptions(null_threshold=1.5)
        
        with pytest.raises((ValueError, Exception)):  # Pydantic ValidationError
            ProcessingOptions(null_threshold=-0.1)
    
    def test_valid_null_threshold(self):
        """Test valid null threshold values."""
        options1 = ProcessingOptions(null_threshold=0.0)
        assert options1.null_threshold == 0.0
        
        options2 = ProcessingOptions(null_threshold=1.0)
        assert options2.null_threshold == 1.0
        
        options3 = ProcessingOptions(null_threshold=0.5)
        assert options3.null_threshold == 0.5


class TestDataType:
    """Test DataType enum."""
    
    def test_data_type_values(self):
        """Test DataType enum values."""
        assert DataType.STRING == "string"
        assert DataType.INTEGER == "integer"
        assert DataType.FLOAT == "float"
        assert DataType.BOOLEAN == "boolean"
        assert DataType.DATETIME == "datetime"
        assert DataType.DATE == "date"
        assert DataType.TIME == "time"