"""Integration tests for Excel pipeline processing."""

import pytest
import pandas as pd
from pathlib import Path
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions


@pytest.fixture
def sample_excel_file(tmp_path):
    """Create a sample Excel file for integration testing."""
    file_path = tmp_path / "test_workbook.xlsx"
    
    # Create sample data
    data = {
        "Sheet1": {
            "Name": ["Alice", "Bob", "Charlie", "Diana"],
            "Age": [25, 30, 35, 28],
            "Salary": [50000, 60000, 70000, 55000],
            "Department": ["Engineering", "Sales", "Engineering", "Marketing"]
        },
        "Sheet2": {
            "Product": ["Widget A", "Widget B", "Widget C"],
            "Price": [19.99, 29.99, 39.99],
            "Stock": [100, 50, 75]
        }
    }
    
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, sheet_data in data.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return file_path


@pytest.fixture
def complex_excel_file(tmp_path):
    """Create a complex Excel file with edge cases."""
    file_path = tmp_path / "complex_workbook.xlsx"
    
    # Create data with various edge cases
    data = {
        "Mixed_Types": {
            "ID": [1, 2, 3, 4, 5],
            "Text": ["Hello", "", None, "World", "Test"],
            "Numbers": [1.5, 2, None, 4.7, 0],
            "Dates": pd.to_datetime(["2023-01-01", "2023-02-01", None, "2023-04-01", "2023-05-01"]),
            "Boolean": [True, False, None, True, False]
        },
        "Empty_Rows": {
            "Col1": ["Data1", "", None, "Data4"],
            "Col2": [1, None, "", 4],
            "Col3": ["A", "", None, "D"]
        }
    }
    
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, sheet_data in data.items():
            df = pd.DataFrame(sheet_data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return file_path


class TestExcelPipelineIntegration:
    """Integration tests for the Excel processing pipeline."""
    
    def test_end_to_end_workflow(self, sample_excel_file):
        """Test complete workflow with sample Excel file."""
        pipeline = ExcelPipeline()
        result = pipeline.process_workbook(sample_excel_file)
        
        assert result is not None
        # Add more specific assertions based on expected pipeline behavior
    
    def test_pipeline_with_custom_options(self, sample_excel_file):
        """Test pipeline with custom processing options."""
        options = ProcessingOptions(
            drop_empty_rows=True,
            clean_column_names=True,
            null_threshold=0.8
        )
        pipeline = ExcelPipeline(options)
        result = pipeline.process_workbook(sample_excel_file)
        
        assert result is not None
        # Verify that custom options were applied
    
    def test_complex_data_processing(self, complex_excel_file):
        """Test processing of complex Excel data with edge cases."""
        pipeline = ExcelPipeline()
        result = pipeline.process_workbook(complex_excel_file)
        
        assert result is not None
        # Test handling of mixed data types, nulls, etc.
    
    def test_directory_processing(self, tmp_path):
        """Test processing multiple Excel files in a directory."""
        # Create multiple test files
        for i in range(3):
            file_path = tmp_path / f"test_{i}.xlsx"
            data = {"Sheet1": {"Value": [i * 10, i * 20, i * 30]}}
            with pd.ExcelWriter(file_path) as writer:
                df = pd.DataFrame(data["Sheet1"])
                df.to_excel(writer, sheet_name="Sheet1", index=False)
        
        pipeline = ExcelPipeline()
        results = pipeline.process_directory(tmp_path)
        
        assert len(results) == 3
        # Verify all files were processed successfully
    
    def test_error_handling(self, tmp_path):
        """Test pipeline error handling with invalid files."""
        # Create a non-Excel file
        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("This is not an Excel file")
        
        pipeline = ExcelPipeline()
        # Test that pipeline handles invalid files gracefully
        with pytest.raises(Exception):
            pipeline.process_workbook(invalid_file)
    
    def test_database_integration(self, sample_excel_file):
        """Test integration with database storage."""
        pipeline = ExcelPipeline()
        result = pipeline.process_workbook(sample_excel_file)
        
        # Test that data was properly stored in database
        # This would require database setup and verification
        assert result is not None
    
    def test_api_integration(self, sample_excel_file):
        """Test integration with REST API endpoints."""
        # This would test the Django REST API endpoints
        # that consume the processed Excel data
        pipeline = ExcelPipeline()
        result = pipeline.process_workbook(sample_excel_file)
        
        assert result is not None
        # Add API endpoint testing here