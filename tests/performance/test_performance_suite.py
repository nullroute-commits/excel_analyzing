"""Performance tests for excel_analyzing."""

import pytest
import time
import psutil
import os
import pandas as pd
from pathlib import Path
import tempfile
from typing import Dict, List
import statistics
from dataclasses import dataclass


@dataclass
class PerformanceMetrics:
    """Container for performance metrics."""
    execution_time: float
    memory_usage_mb: float
    cpu_usage_percent: float
    rows_processed: int
    throughput_rows_per_second: float


class PerformanceTestBase:
    """Base class for performance tests."""
    
    def setup_method(self):
        """Set up performance testing environment."""
        self.process = psutil.Process(os.getpid())
        self.baseline_memory = self.process.memory_info().rss
    
    def measure_performance(self, func, *args, **kwargs) -> PerformanceMetrics:
        """Measure performance of a function call."""
        # Get initial state
        initial_memory = self.process.memory_info().rss
        initial_cpu_times = self.process.cpu_times()
        
        # Execute function with timing
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        
        # Get final state
        final_memory = self.process.memory_info().rss
        final_cpu_times = self.process.cpu_times()
        
        # Calculate metrics
        execution_time = end_time - start_time
        memory_usage = (final_memory - initial_memory) / (1024 * 1024)  # MB
        cpu_time = (final_cpu_times.user - initial_cpu_times.user + 
                   final_cpu_times.system - initial_cpu_times.system)
        cpu_usage = (cpu_time / execution_time * 100) if execution_time > 0 else 0
        
        # Estimate rows processed (this would need to be customized per function)
        rows_processed = getattr(result, 'shape', (0,))[0] if hasattr(result, 'shape') else 0
        throughput = rows_processed / execution_time if execution_time > 0 else 0
        
        return PerformanceMetrics(
            execution_time=execution_time,
            memory_usage_mb=memory_usage,
            cpu_usage_percent=cpu_usage,
            rows_processed=rows_processed,
            throughput_rows_per_second=throughput
        )
    
    def create_test_dataframe(self, rows: int, cols: int) -> pd.DataFrame:
        """Create a test DataFrame with specified dimensions."""
        data = {}
        for i in range(cols):
            if i % 3 == 0:  # Integer column
                data[f'int_col_{i}'] = list(range(rows))
            elif i % 3 == 1:  # Float column
                data[f'float_col_{i}'] = [j * 1.1 for j in range(rows)]
            else:  # Boolean column (converted to int for math operations)
                data[f'bool_col_{i}'] = [int(j % 2 == 0) for j in range(rows)]
        
        return pd.DataFrame(data)
    
    def create_mixed_dataframe(self, rows: int, cols: int) -> pd.DataFrame:
        """Create a test DataFrame with mixed data types."""
        data = {}
        for i in range(cols):
            if i % 4 == 0:  # Integer column
                data[f'int_col_{i}'] = list(range(rows))
            elif i % 4 == 1:  # Float column
                data[f'float_col_{i}'] = [j * 1.1 for j in range(rows)]
            elif i % 4 == 2:  # String column
                data[f'str_col_{i}'] = [f'value_{j}' for j in range(rows)]
            else:  # Boolean column
                data[f'bool_col_{i}'] = [j % 2 == 0 for j in range(rows)]
        
        return pd.DataFrame(data)
    
    def create_test_excel_file(self, filepath: Path, sheets: Dict[str, pd.DataFrame]):
        """Create a test Excel file with multiple sheets."""
        with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)


class TestDataProcessingPerformance(PerformanceTestBase):
    """Performance tests for data processing operations."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_small_dataset_performance(self):
        """Test performance with small datasets (< 1K rows)."""
        df = self.create_test_dataframe(1000, 10)
        
        # Test data type inference performance
        def infer_types():
            return df.dtypes
        
        metrics = self.measure_performance(infer_types)
        
        # Performance assertions
        assert metrics.execution_time < 1.0, f"Small dataset processing too slow: {metrics.execution_time:.2f}s"
        assert metrics.memory_usage_mb < 50, f"Small dataset uses too much memory: {metrics.memory_usage_mb:.2f}MB"
    
    @pytest.mark.performance
    def test_medium_dataset_performance(self):
        """Test performance with medium datasets (1K-10K rows)."""
        df = self.create_test_dataframe(10000, 20)
        
        def process_medium_dataset():
            # Simulate typical processing operations
            cleaned = df.dropna()
            grouped = cleaned.groupby(cleaned.columns[0]).mean(numeric_only=True)
            return grouped
        
        metrics = self.measure_performance(process_medium_dataset)
        
        # Performance assertions
        assert metrics.execution_time < 5.0, f"Medium dataset processing too slow: {metrics.execution_time:.2f}s"
        assert metrics.memory_usage_mb < 200, f"Medium dataset uses too much memory: {metrics.memory_usage_mb:.2f}MB"
        assert metrics.throughput_rows_per_second > 1000, f"Throughput too low: {metrics.throughput_rows_per_second:.2f} rows/s"
    
    @pytest.mark.performance
    def test_large_dataset_performance(self):
        """Test performance with large datasets (10K+ rows)."""
        df = self.create_test_dataframe(100000, 25)
        
        def process_large_dataset():
            # Simulate memory-intensive operations
            result = df.copy()
            result['computed'] = result.iloc[:, 0] * result.iloc[:, 1]
            return result
        
        metrics = self.measure_performance(process_large_dataset)
        
        # Performance assertions for large datasets
        assert metrics.execution_time < 30.0, f"Large dataset processing too slow: {metrics.execution_time:.2f}s"
        assert metrics.memory_usage_mb < 1000, f"Large dataset uses too much memory: {metrics.memory_usage_mb:.2f}MB"
        assert metrics.throughput_rows_per_second > 3000, f"Throughput too low: {metrics.throughput_rows_per_second:.2f} rows/s"
    
    @pytest.mark.performance
    def test_wide_dataset_performance(self):
        """Test performance with wide datasets (many columns)."""
        df = self.create_test_dataframe(5000, 100)
        
        def process_wide_dataset():
            # Operations that scale with column count
            correlations = df.corr(numeric_only=True)
            return correlations
        
        metrics = self.measure_performance(process_wide_dataset)
        
        # Performance assertions for wide datasets
        assert metrics.execution_time < 15.0, f"Wide dataset processing too slow: {metrics.execution_time:.2f}s"
        assert metrics.memory_usage_mb < 500, f"Wide dataset uses too much memory: {metrics.memory_usage_mb:.2f}MB"


class TestExcelFilePerformance(PerformanceTestBase):
    """Performance tests for Excel file operations."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_excel_reading_performance(self):
        """Test Excel file reading performance."""
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "test.xlsx"
            
            # Create test file with multiple sheets
            sheets = {
                'Sheet1': self.create_test_dataframe(5000, 10),
                'Sheet2': self.create_test_dataframe(3000, 15),
                'Sheet3': self.create_test_dataframe(2000, 8)
            }
            self.create_test_excel_file(filepath, sheets)
            
            def read_excel_file():
                return pd.read_excel(filepath, sheet_name=None)
            
            metrics = self.measure_performance(read_excel_file)
            
            # Performance assertions
            assert metrics.execution_time < 10.0, f"Excel reading too slow: {metrics.execution_time:.2f}s"
            assert metrics.memory_usage_mb < 300, f"Excel reading uses too much memory: {metrics.memory_usage_mb:.2f}MB"
    
    @pytest.mark.performance
    def test_excel_writing_performance(self):
        """Test Excel file writing performance."""
        df = self.create_test_dataframe(10000, 15)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            filepath = Path(temp_dir) / "output.xlsx"
            
            def write_excel_file():
                df.to_excel(filepath, index=False)
                return df
            
            metrics = self.measure_performance(write_excel_file)
            
            # Performance assertions
            assert metrics.execution_time < 15.0, f"Excel writing too slow: {metrics.execution_time:.2f}s"
            assert metrics.memory_usage_mb < 200, f"Excel writing uses too much memory: {metrics.memory_usage_mb:.2f}MB"
    
    @pytest.mark.performance
    def test_multiple_file_processing(self):
        """Test performance when processing multiple Excel files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple test files
            filepaths = []
            for i in range(5):
                filepath = Path(temp_dir) / f"test_{i}.xlsx"
                sheets = {
                    'Sheet1': self.create_test_dataframe(2000, 8)
                }
                self.create_test_excel_file(filepath, sheets)
                filepaths.append(filepath)
            
            def process_multiple_files():
                results = []
                for filepath in filepaths:
                    df = pd.read_excel(filepath)
                    # Simulate processing
                    processed = df.describe()
                    results.append(processed)
                return results
            
            metrics = self.measure_performance(process_multiple_files)
            
            # Performance assertions
            assert metrics.execution_time < 20.0, f"Multiple file processing too slow: {metrics.execution_time:.2f}s"
            assert metrics.memory_usage_mb < 400, f"Multiple file processing uses too much memory: {metrics.memory_usage_mb:.2f}MB"


class TestDatabasePerformance(PerformanceTestBase):
    """Performance tests for database operations."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_bulk_insert_performance(self):
        """Test bulk database insert performance."""
        # This would test actual database operations
        # For now, we'll simulate with DataFrame operations
        
        data = self.create_test_dataframe(10000, 10)
        
        def simulate_bulk_insert():
            # Simulate bulk insert operations
            total_rows = 0
            batch_size = 1000
            for i in range(0, len(data), batch_size):
                batch = data.iloc[i:i+batch_size]
                # In real implementation: batch.to_sql(...)
                total_rows += len(batch)
            # Return a simple object with shape attribute for metric calculation
            class Result:
                def __init__(self, rows):
                    self.shape = (rows,)
            return Result(total_rows)
        
        metrics = self.measure_performance(simulate_bulk_insert)
        
        # Performance assertions
        assert metrics.execution_time < 5.0, f"Bulk insert too slow: {metrics.execution_time:.2f}s"
        assert metrics.throughput_rows_per_second > 2000, f"Insert throughput too low: {metrics.throughput_rows_per_second:.2f} rows/s"
    
    @pytest.mark.performance
    def test_query_performance(self):
        """Test database query performance."""
        # Simulate query operations
        data = self.create_test_dataframe(50000, 15)
        
        def simulate_complex_query():
            # Simulate complex query operations
            filtered = data[data.iloc[:, 0] > 1000]
            grouped = filtered.groupby(filtered.columns[1]).agg({
                filtered.columns[0]: ['count', 'mean', 'std'],
                filtered.columns[2]: ['sum', 'max', 'min']
            })
            return grouped
        
        metrics = self.measure_performance(simulate_complex_query)
        
        # Performance assertions
        assert metrics.execution_time < 10.0, f"Query too slow: {metrics.execution_time:.2f}s"


class TestAPIPerformance(PerformanceTestBase):
    """Performance tests for API endpoints."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_api_response_time(self):
        """Test API response time performance."""
        # This would test actual API endpoints
        # For now, we'll simulate API operations
        
        def simulate_api_call():
            # Simulate data serialization (common API bottleneck)
            data = self.create_test_dataframe(1000, 10)
            serialized = data.to_dict('records')
            return serialized
        
        # Test multiple API calls
        response_times = []
        for _ in range(10):
            metrics = self.measure_performance(simulate_api_call)
            response_times.append(metrics.execution_time)
        
        # Calculate statistics
        avg_response_time = statistics.mean(response_times)
        p95_response_time = statistics.quantiles(response_times, n=20)[18]  # 95th percentile
        
        # Performance assertions
        assert avg_response_time < 1.0, f"Average API response time too slow: {avg_response_time:.2f}s"
        assert p95_response_time < 2.0, f"95th percentile response time too slow: {p95_response_time:.2f}s"
    
    @pytest.mark.performance
    def test_concurrent_api_performance(self):
        """Test API performance under concurrent load."""
        import concurrent.futures
        import threading
        
        def simulate_concurrent_api_call():
            data = self.create_test_dataframe(500, 8)
            return data.describe()
        
        # Simulate concurrent requests
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(simulate_concurrent_api_call) for _ in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        end_time = time.time()
        
        total_time = end_time - start_time
        requests_per_second = 20 / total_time
        
        # Performance assertions
        assert total_time < 10.0, f"Concurrent requests took too long: {total_time:.2f}s"
        assert requests_per_second > 2.0, f"Request throughput too low: {requests_per_second:.2f} req/s"


class TestMemoryPerformance(PerformanceTestBase):
    """Memory-specific performance tests."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_memory_leak_detection(self):
        """Test for memory leaks in repeated operations."""
        initial_memory = self.process.memory_info().rss
        
        # Perform the same operation multiple times
        for i in range(100):
            df = self.create_test_dataframe(1000, 10)
            processed = df.groupby(df.columns[0]).mean(numeric_only=True)
            del df, processed  # Explicit cleanup
        
        final_memory = self.process.memory_info().rss
        memory_increase = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        # Should not have significant memory increase
        assert memory_increase < 100, f"Potential memory leak detected: {memory_increase:.2f}MB increase"
    
    @pytest.mark.performance
    def test_memory_efficiency(self):
        """Test memory efficiency of operations."""
        # Test memory usage for different data sizes
        sizes = [1000, 5000, 10000, 20000]
        memory_per_row = []
        
        for size in sizes:
            initial_memory = self.process.memory_info().rss
            df = self.create_test_dataframe(size, 10)
            peak_memory = self.process.memory_info().rss
            
            memory_used = (peak_memory - initial_memory) / (1024 * 1024)  # MB
            memory_per_row.append(memory_used / size)
            
            del df
        
        # Memory usage per row should be relatively consistent
        avg_memory_per_row = statistics.mean(memory_per_row)
        assert avg_memory_per_row < 0.01, f"Memory usage per row too high: {avg_memory_per_row:.6f}MB/row"


class TestScalabilityPerformance(PerformanceTestBase):
    """Scalability performance tests."""
    
    def setup_method(self):
        super().setup_method()
    
    @pytest.mark.performance
    def test_linear_scalability(self):
        """Test that performance scales linearly with data size."""
        sizes = [1000, 2000, 4000, 8000]
        execution_times = []
        
        for size in sizes:
            df = self.create_test_dataframe(size, 10)
            
            def process_data():
                return df.groupby(df.columns[0]).agg({
                    df.columns[1]: 'mean',
                    df.columns[2]: 'sum'
                })
            
            metrics = self.measure_performance(process_data)
            execution_times.append(metrics.execution_time)
        
        # Check that execution time increases roughly linearly
        # (allowing for some variance due to overhead)
        time_ratios = [execution_times[i] / execution_times[0] for i in range(1, len(execution_times))]
        size_ratios = [sizes[i] / sizes[0] for i in range(1, len(sizes))]
        
        for i, (time_ratio, size_ratio) in enumerate(zip(time_ratios, size_ratios)):
            # Allow for some non-linearity, but should be roughly proportional
            assert time_ratio < size_ratio * 2, f"Performance doesn't scale linearly at size {sizes[i+1]}"