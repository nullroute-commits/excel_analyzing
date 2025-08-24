"""Test configuration and utilities for the comprehensive testing suite."""

import os
import pytest
import tempfile
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import logging
from unittest.mock import Mock, patch

# Configure logging for tests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestConfig:
    """Configuration for test environments."""
    
    # Test database settings
    database_url: str = "sqlite:///test.db"
    
    # Test data directories
    test_data_dir: Path = Path(__file__).parent / "test_data"
    fixtures_dir: Path = Path(__file__).parent / "fixtures"
    
    # Performance test settings
    performance_timeout: int = 300  # 5 minutes
    benchmark_iterations: int = 5
    
    # Security test settings
    security_timeout: int = 600  # 10 minutes
    
    # Integration test settings
    integration_timeout: int = 900  # 15 minutes
    
    def __post_init__(self):
        """Ensure test directories exist."""
        self.test_data_dir.mkdir(exist_ok=True)
        self.fixtures_dir.mkdir(exist_ok=True)


# Global test configuration
TEST_CONFIG = TestConfig()


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "regression: mark test as a regression test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically mark tests based on their location."""
    for item in items:
        # Add markers based on test file location
        if "performance" in str(item.fspath):
            item.add_marker(pytest.mark.performance)
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        if "security" in str(item.fspath):
            item.add_marker(pytest.mark.security)
        if "regression" in str(item.fspath):
            item.add_marker(pytest.mark.regression)


# Common fixtures
@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration."""
    return TEST_CONFIG


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def sample_dataframe():
    """Provide a standard sample DataFrame for testing."""
    return pd.DataFrame({
        'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
        'Age': [25, 30, 35, 28],
        'Salary': [50000, 60000, 70000, 55000],
        'Department': ['Engineering', 'Sales', 'Engineering', 'Marketing'],
        'Start_Date': pd.to_datetime(['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-01'])
    })


@pytest.fixture
def large_dataframe():
    """Provide a large DataFrame for performance testing."""
    size = 10000
    return pd.DataFrame({
        'id': range(size),
        'value': [i * 1.1 for i in range(size)],
        'category': [f'cat_{i % 10}' for i in range(size)],
        'flag': [i % 2 == 0 for i in range(size)]
    })


@pytest.fixture
def complex_dataframe():
    """Provide a complex DataFrame with various data types and edge cases."""
    return pd.DataFrame({
        'integers': [1, 2, None, 4, 5],
        'floats': [1.1, 2.2, 3.3, None, 5.5],
        'strings': ['hello', '', None, 'world', 'test'],
        'booleans': [True, False, None, True, False],
        'dates': pd.to_datetime(['2023-01-01', '2023-02-01', None, '2023-04-01', '2023-05-01']),
        'mixed': [1, 'two', 3.0, None, True]
    })


@pytest.fixture
def sample_excel_file(temp_dir, sample_dataframe):
    """Provide a sample Excel file for testing."""
    file_path = temp_dir / "sample.xlsx"
    with pd.ExcelWriter(file_path) as writer:
        sample_dataframe.to_excel(writer, sheet_name='Sheet1', index=False)
        # Add a second sheet
        pd.DataFrame({'Col1': [1, 2, 3], 'Col2': ['A', 'B', 'C']}).to_excel(
            writer, sheet_name='Sheet2', index=False
        )
    return file_path


@pytest.fixture
def multi_sheet_excel_file(temp_dir):
    """Provide an Excel file with multiple sheets and various data types."""
    file_path = temp_dir / "multi_sheet.xlsx"
    
    sheets = {
        'Employees': pd.DataFrame({
            'ID': [1, 2, 3, 4],
            'Name': ['Alice', 'Bob', 'Charlie', 'Diana'],
            'Salary': [50000, 60000, 70000, 55000]
        }),
        'Products': pd.DataFrame({
            'ProductID': ['P001', 'P002', 'P003'],
            'Name': ['Widget A', 'Widget B', 'Widget C'],
            'Price': [19.99, 29.99, 39.99]
        }),
        'Sales': pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'ProductID': ['P001', 'P002', 'P001'],
            'Quantity': [10, 5, 8],
            'Revenue': [199.90, 149.95, 159.92]
        })
    }
    
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    return file_path


# Test data generators
class TestDataGenerator:
    """Generate test data for various testing scenarios."""
    
    @staticmethod
    def create_performance_dataset(rows: int, cols: int) -> pd.DataFrame:
        """Create a dataset for performance testing."""
        data = {}
        for i in range(cols):
            if i % 3 == 0:
                data[f'num_col_{i}'] = range(rows)
            elif i % 3 == 1:
                data[f'str_col_{i}'] = [f'value_{j % 100}' for j in range(rows)]
            else:
                data[f'float_col_{i}'] = [j * 0.1 for j in range(rows)]
        return pd.DataFrame(data)
    
    @staticmethod
    def create_security_test_data() -> Dict[str, Any]:
        """Create data with potential security issues for testing."""
        return {
            'malicious_filenames': [
                '../../../etc/passwd',
                'file<script>alert("xss")</script>.xlsx',
                'file; rm -rf /.xlsx',
                'file`whoami`.xlsx'
            ],
            'sql_injection_attempts': [
                "'; DROP TABLE users; --",
                "1' OR '1'='1",
                "UNION SELECT * FROM sensitive_data"
            ],
            'xss_payloads': [
                '<script>alert("xss")</script>',
                'javascript:alert("xss")',
                '<img src=x onerror=alert("xss")>'
            ],
            'formula_injection': [
                '=cmd|"/c calc"!A1',
                '=HYPERLINK("http://evil.com","Click me")',
                '@SUM(1+1)*cmd|"/c calc"!A0'
            ]
        }
    
    @staticmethod
    def create_regression_baseline() -> Dict[str, Any]:
        """Create baseline data for regression testing."""
        return {
            'data_types': {
                'int64': ['id', 'count'],
                'float64': ['value', 'rate'],
                'object': ['name', 'category'],
                'bool': ['active', 'verified'],
                'datetime64[ns]': ['created_at', 'updated_at']
            },
            'expected_shapes': {
                'small_dataset': (100, 5),
                'medium_dataset': (1000, 10),
                'large_dataset': (10000, 15)
            },
            'processing_times': {
                'small_dataset': 0.1,
                'medium_dataset': 1.0,
                'large_dataset': 10.0
            }
        }


# Test utilities
class TestUtils:
    """Utility functions for testing."""
    
    @staticmethod
    def assert_dataframe_equal(df1: pd.DataFrame, df2: pd.DataFrame, 
                             check_dtype: bool = True, check_names: bool = True):
        """Enhanced DataFrame comparison for testing."""
        try:
            pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype, check_names=check_names)
        except AssertionError as e:
            logger.error(f"DataFrames are not equal: {e}")
            logger.info(f"DataFrame 1 shape: {df1.shape}")
            logger.info(f"DataFrame 2 shape: {df2.shape}")
            logger.info(f"DataFrame 1 columns: {list(df1.columns)}")
            logger.info(f"DataFrame 2 columns: {list(df2.columns)}")
            raise
    
    @staticmethod
    def measure_execution_time(func, *args, **kwargs):
        """Measure execution time of a function."""
        import time
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    
    @staticmethod
    def check_memory_usage(func, *args, **kwargs):
        """Measure memory usage of a function."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        result = func(*args, **kwargs)
        
        final_memory = process.memory_info().rss
        memory_used = (final_memory - initial_memory) / (1024 * 1024)  # MB
        
        return result, memory_used
    
    @staticmethod
    def create_mock_objects():
        """Create common mock objects for testing."""
        mocks = {
            'database': Mock(),
            'file_system': Mock(),
            'api_client': Mock(),
            'email_service': Mock(),
            'cache': Mock()
        }
        return mocks
    
    @staticmethod
    def skip_if_no_database():
        """Skip test if no database is available."""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url or 'sqlite:///:memory:' in database_url:
            pytest.skip("Database not available for integration testing")
    
    @staticmethod
    def skip_if_no_network():
        """Skip test if no network is available."""
        import socket
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=3)
        except OSError:
            pytest.skip("Network not available for integration testing")


# Environment-specific configurations
class TestEnvironments:
    """Configuration for different test environments."""
    
    @staticmethod
    def get_ci_config():
        """Configuration for CI environment."""
        return {
            'database_url': os.environ.get('DATABASE_URL', 'sqlite:///:memory:'),
            'redis_url': os.environ.get('REDIS_URL', 'redis://localhost:6379/0'),
            'timeout_multiplier': 2.0,  # CI is slower
            'parallel_workers': 2
        }
    
    @staticmethod
    def get_local_config():
        """Configuration for local development."""
        return {
            'database_url': 'sqlite:///test_local.db',
            'redis_url': 'redis://localhost:6379/1',
            'timeout_multiplier': 1.0,
            'parallel_workers': 4
        }
    
    @staticmethod
    def get_staging_config():
        """Configuration for staging environment."""
        return {
            'database_url': os.environ.get('STAGING_DATABASE_URL'),
            'redis_url': os.environ.get('STAGING_REDIS_URL'),
            'timeout_multiplier': 1.5,
            'parallel_workers': 3
        }


# Test markers and decorators
def integration_test(func):
    """Decorator to mark a function as an integration test."""
    return pytest.mark.integration(func)


def performance_test(func):
    """Decorator to mark a function as a performance test."""
    return pytest.mark.performance(func)


def security_test(func):
    """Decorator to mark a function as a security test."""
    return pytest.mark.security(func)


def regression_test(func):
    """Decorator to mark a function as a regression test."""
    return pytest.mark.regression(func)


def slow_test(func):
    """Decorator to mark a function as a slow test."""
    return pytest.mark.slow(func)


# Custom assertions
def assert_performance_threshold(execution_time: float, threshold: float, operation: str):
    """Assert that execution time is within performance threshold."""
    assert execution_time <= threshold, \
        f"{operation} took {execution_time:.2f}s, exceeding threshold of {threshold:.2f}s"


def assert_memory_threshold(memory_usage: float, threshold: float, operation: str):
    """Assert that memory usage is within threshold."""
    assert memory_usage <= threshold, \
        f"{operation} used {memory_usage:.2f}MB, exceeding threshold of {threshold:.2f}MB"


def assert_no_security_issues(scan_results: Dict[str, Any]):
    """Assert that security scan results contain no critical issues."""
    critical_issues = scan_results.get('critical', [])
    high_issues = scan_results.get('high', [])
    
    assert len(critical_issues) == 0, f"Critical security issues found: {critical_issues}"
    assert len(high_issues) == 0, f"High severity security issues found: {high_issues}"