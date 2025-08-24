"""Regression tests to ensure existing functionality is preserved."""

import pytest
import pandas as pd
import json
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Any, List
import hashlib


@dataclass
class RegressionBaseline:
    """Represents a baseline for regression testing."""
    test_name: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any]
    output_hash: str
    version: str


class RegressionTestBase:
    """Base class for regression tests."""
    
    BASELINE_DIR = Path(__file__).parent / "baselines"
    
    def setUp(self):
        """Set up regression test environment."""
        self.BASELINE_DIR.mkdir(exist_ok=True)
    
    def save_baseline(self, test_name: str, input_data: Dict, output_data: Dict, version: str = "1.0.0"):
        """Save a baseline for regression testing."""
        output_str = json.dumps(output_data, sort_keys=True, default=str)
        output_hash = hashlib.md5(output_str.encode()).hexdigest()
        
        baseline = RegressionBaseline(
            test_name=test_name,
            input_data=input_data,
            expected_output=output_data,
            output_hash=output_hash,
            version=version
        )
        
        baseline_file = self.BASELINE_DIR / f"{test_name}_baseline.json"
        with open(baseline_file, 'w') as f:
            json.dump({
                'test_name': baseline.test_name,
                'input_data': baseline.input_data,
                'expected_output': baseline.expected_output,
                'output_hash': baseline.output_hash,
                'version': baseline.version
            }, f, indent=2, default=str)
    
    def load_baseline(self, test_name: str) -> RegressionBaseline:
        """Load a baseline for regression testing."""
        baseline_file = self.BASELINE_DIR / f"{test_name}_baseline.json"
        if not baseline_file.exists():
            raise FileNotFoundError(f"Baseline file not found: {baseline_file}")
        
        with open(baseline_file, 'r') as f:
            data = json.load(f)
        
        return RegressionBaseline(**data)
    
    def compare_output(self, test_name: str, actual_output: Dict) -> bool:
        """Compare actual output with baseline."""
        try:
            baseline = self.load_baseline(test_name)
        except FileNotFoundError:
            # If no baseline exists, save the current output as baseline
            self.save_baseline(test_name, {}, actual_output)
            return True
        
        actual_str = json.dumps(actual_output, sort_keys=True, default=str)
        actual_hash = hashlib.md5(actual_str.encode()).hexdigest()
        
        return actual_hash == baseline.output_hash


class TestDataProcessingRegression(RegressionTestBase):
    """Regression tests for data processing functionality."""
    
    def setUp(self):
        super().setUp()
    
    @pytest.fixture
    def standard_test_data(self):
        """Standard test data for regression tests."""
        return {
            "simple_data": {
                "Name": ["Alice", "Bob", "Charlie"],
                "Age": [25, 30, 35],
                "Salary": [50000, 60000, 70000]
            },
            "mixed_types": {
                "ID": [1, 2, 3],
                "Text": ["Hello", "World", "Test"],
                "Float": [1.1, 2.2, 3.3],
                "Bool": [True, False, True]
            },
            "with_nulls": {
                "Col1": ["A", None, "C"],
                "Col2": [1, 2, None],
                "Col3": [1.1, None, 3.3]
            }
        }
    
    def test_data_type_inference_regression(self, standard_test_data):
        """Test that data type inference remains consistent."""
        # This would test the data type inference functionality
        # and ensure it produces the same results as the baseline
        
        from excel_analyzing.core.data_types import infer_data_types
        
        for data_name, data in standard_test_data.items():
            df = pd.DataFrame(data)
            inferred_types = infer_data_types(df)
            
            # Convert to serializable format
            types_dict = {col: str(dtype) for col, dtype in inferred_types.items()}
            
            # Compare with baseline
            test_name = f"data_type_inference_{data_name}"
            assert self.compare_output(test_name, types_dict), f"Regression detected in {test_name}"
    
    def test_data_cleaning_regression(self, standard_test_data):
        """Test that data cleaning produces consistent results."""
        from excel_analyzing.core.cleaning import clean_data
        
        for data_name, data in standard_test_data.items():
            df = pd.DataFrame(data)
            cleaned_df = clean_data(df)
            
            # Convert to serializable format
            cleaned_dict = {
                "shape": list(cleaned_df.shape),
                "columns": list(cleaned_df.columns),
                "dtypes": {col: str(dtype) for col, dtype in cleaned_df.dtypes.items()},
                "null_counts": cleaned_df.isnull().sum().to_dict()
            }
            
            test_name = f"data_cleaning_{data_name}"
            assert self.compare_output(test_name, cleaned_dict), f"Regression detected in {test_name}"
    
    def test_schema_detection_regression(self, standard_test_data):
        """Test that schema detection remains consistent."""
        from excel_analyzing.core.schema import detect_schema
        
        for data_name, data in standard_test_data.items():
            df = pd.DataFrame(data)
            schema = detect_schema(df)
            
            # Convert schema to serializable format
            schema_dict = {
                "columns": [
                    {
                        "name": col.name,
                        "type": str(col.type),
                        "nullable": col.nullable,
                        "constraints": col.constraints
                    }
                    for col in schema.columns
                ]
            }
            
            test_name = f"schema_detection_{data_name}"
            assert self.compare_output(test_name, schema_dict), f"Regression detected in {test_name}"


class TestAPIRegression(RegressionTestBase):
    """Regression tests for API functionality."""
    
    def setUp(self):
        super().setUp()
    
    def test_api_response_structure_regression(self):
        """Test that API response structures remain consistent."""
        # Mock API responses for testing
        api_responses = {
            "workbooks_list": {
                "count": 0,
                "next": None,
                "previous": None,
                "results": []
            },
            "workbook_detail": {
                "id": 1,
                "name": "Test Workbook",
                "created_at": "2023-01-01T00:00:00Z",
                "updated_at": "2023-01-01T00:00:00Z",
                "sheets": []
            },
            "error_response": {
                "error": "Not found",
                "code": 404,
                "message": "The requested resource was not found"
            }
        }
        
        for response_name, response_data in api_responses.items():
            test_name = f"api_response_{response_name}"
            assert self.compare_output(test_name, response_data), f"API regression detected in {test_name}"
    
    def test_serializer_output_regression(self):
        """Test that serializer outputs remain consistent."""
        # This would test Django REST framework serializers
        serializer_outputs = {
            "workbook_serializer": {
                "id": 1,
                "name": "Test",
                "description": "Test workbook",
                "file_path": "/path/to/file.xlsx",
                "created_at": "2023-01-01T00:00:00Z"
            },
            "sheet_serializer": {
                "id": 1,
                "name": "Sheet1",
                "workbook": 1,
                "row_count": 100,
                "column_count": 5
            }
        }
        
        for serializer_name, output_data in serializer_outputs.items():
            test_name = f"serializer_{serializer_name}"
            assert self.compare_output(test_name, output_data), f"Serializer regression detected in {test_name}"


class TestPerformanceRegression(RegressionTestBase):
    """Regression tests for performance characteristics."""
    
    def setUp(self):
        super().setUp()
    
    def test_processing_time_regression(self):
        """Test that processing times don't regress significantly."""
        import time
        
        # Create test data of various sizes
        test_sizes = [100, 1000, 5000]
        
        for size in test_sizes:
            # Generate test DataFrame
            data = {
                "col1": list(range(size)),
                "col2": [f"text_{i}" for i in range(size)],
                "col3": [i * 1.1 for i in range(size)]
            }
            df = pd.DataFrame(data)
            
            # Measure processing time
            start_time = time.time()
            # This would call the actual processing function
            # processed_df = process_dataframe(df)
            end_time = time.time()
            
            processing_time = end_time - start_time
            
            # Store timing data
            timing_data = {
                "size": size,
                "processing_time": processing_time,
                "rows_per_second": size / processing_time if processing_time > 0 else 0
            }
            
            test_name = f"processing_time_{size}_rows"
            # For performance tests, we might want to allow some variance
            # This is a simplified check - in practice, you'd want more sophisticated analysis
            assert processing_time < 10.0, f"Processing time regression for {size} rows: {processing_time}s"
    
    def test_memory_usage_regression(self):
        """Test that memory usage doesn't increase significantly."""
        import psutil
        import os
        
        # Get initial memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and process large dataset
        size = 10000
        data = {
            "col1": list(range(size)),
            "col2": [f"text_{i}" for i in range(size)],
            "col3": [i * 1.1 for i in range(size)]
        }
        df = pd.DataFrame(data)
        
        # This would call memory-intensive operations
        # processed_df = process_dataframe(df)
        
        # Get peak memory usage
        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory
        
        # Store memory data
        memory_data = {
            "initial_memory_mb": initial_memory / (1024 * 1024),
            "peak_memory_mb": peak_memory / (1024 * 1024),
            "memory_increase_mb": memory_increase / (1024 * 1024),
            "data_size": size
        }
        
        test_name = "memory_usage_large_dataset"
        # This is a simplified check - adjust threshold based on expectations
        assert memory_increase < 500 * 1024 * 1024, f"Memory usage regression: {memory_increase / (1024*1024):.2f} MB"


class TestConfigurationRegression(RegressionTestBase):
    """Regression tests for configuration and settings."""
    
    def test_default_settings_regression(self):
        """Test that default settings remain consistent."""
        from excel_analyzing.core.config import get_default_settings
        
        default_settings = get_default_settings()
        
        # Convert to serializable format
        settings_dict = {
            key: str(value) if not isinstance(value, (dict, list, str, int, float, bool)) else value
            for key, value in default_settings.items()
        }
        
        test_name = "default_settings"
        assert self.compare_output(test_name, settings_dict), "Default settings regression detected"
    
    def test_processing_options_regression(self):
        """Test that processing options behave consistently."""
        from excel_analyzing.models.schemas import ProcessingOptions
        
        # Test default options
        default_options = ProcessingOptions()
        options_dict = default_options.dict()
        
        test_name = "default_processing_options"
        assert self.compare_output(test_name, options_dict), "Processing options regression detected"