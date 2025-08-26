"""Unit tests for the CLI module."""

import tempfile
import pytest
import pandas as pd
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from excel_analyzing.cli import cli, main
from excel_analyzing.models.schemas import ProcessingOptions


class TestCLI:
    """Test the CLI commands and functionality."""
    
    @pytest.fixture
    def runner(self):
        """Provide a Click test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_excel_workbook(self, temp_dir):
        """Create a sample Excel workbook for testing."""
        file_path = temp_dir / "test_workbook.xlsx"
        
        # Create multiple sheets with different data types
        with pd.ExcelWriter(file_path) as writer:
            # Sheet 1: Employee data
            employees_df = pd.DataFrame({
                'ID': [1, 2, 3, 4, 5],
                'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Eve Wilson'],
                'Department': ['Engineering', 'Sales', 'Engineering', 'Marketing', 'HR'],
                'Salary': [75000, 65000, 80000, 70000, 60000],
                'Active': [True, True, False, True, True],
                'Start_Date': pd.to_datetime(['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-01', '2022-05-15'])
            })
            employees_df.to_excel(writer, sheet_name='Employees', index=False)
            
            # Sheet 2: Sales data  
            sales_df = pd.DataFrame({
                'Product': ['Widget A', 'Widget B', 'Widget C', 'Widget A', 'Widget B'],
                'Quantity': [100, 150, 75, 200, 120],
                'Price': [10.50, 15.75, 22.00, 10.50, 15.75],
                'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05'])
            })
            sales_df.to_excel(writer, sheet_name='Sales', index=False)
            
            # Sheet 3: Mixed data types and edge cases
            mixed_df = pd.DataFrame({
                'String_Col': ['Hello', 'World', None, '', 'Test'],
                'Int_Col': [1, 2, None, 4, 5],
                'Float_Col': [1.1, 2.2, 3.3, None, 5.5],
                'Bool_Col': [True, False, None, True, False],
                'Empty_Col': [None, None, None, None, None]
            })
            mixed_df.to_excel(writer, sheet_name='Mixed_Data', index=False)
        
        return file_path
    
    @pytest.fixture 
    def complex_excel_workbook(self, temp_dir):
        """Create a complex Excel workbook with multiple sheets and large data."""
        file_path = temp_dir / "complex_workbook.xlsx"
        
        with pd.ExcelWriter(file_path) as writer:
            # Large dataset for performance testing
            large_df = pd.DataFrame({
                'id': range(1000),
                'value': [i * 0.1 for i in range(1000)],
                'category': [f'cat_{i % 10}' for i in range(1000)],
                'flag': [i % 2 == 0 for i in range(1000)]
            })
            large_df.to_excel(writer, sheet_name='Large_Dataset', index=False)
            
            # Financial data
            financial_df = pd.DataFrame({
                'Account': ['Assets', 'Liabilities', 'Equity', 'Revenue', 'Expenses'],
                'Q1': [100000, 50000, 50000, 80000, 70000],
                'Q2': [110000, 55000, 55000, 85000, 75000],
                'Q3': [120000, 60000, 60000, 90000, 80000],
                'Q4': [130000, 65000, 65000, 95000, 85000]
            })
            financial_df.to_excel(writer, sheet_name='Financial_Data', index=False)
        
        return file_path

    def test_cli_help(self, runner):
        """Test CLI help command."""
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Excel Analyzing CLI' in result.output
        assert 'Commands:' in result.output
        assert 'analyze' in result.output
        assert 'process' in result.output
        assert 'init-db' in result.output

    def test_cli_version_and_basic_functionality(self, runner):
        """Test that CLI can be imported and basic commands work."""
        # Test that the main CLI group works with help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Commands:' in result.output

    @patch('excel_analyzing.cli.db_manager')
    def test_init_db_command(self, mock_db_manager, runner):
        """Test database initialization command."""
        mock_db_manager.create_tables.return_value = None
        
        result = runner.invoke(cli, ['init-db'])
        assert result.exit_code == 0
        assert '✅ Database tables created successfully!' in result.output
        mock_db_manager.create_tables.assert_called_once()

    @patch('excel_analyzing.cli.db_manager')
    def test_init_db_command_failure(self, mock_db_manager, runner):
        """Test database initialization command failure."""
        mock_db_manager.create_tables.side_effect = Exception("Database error")
        
        result = runner.invoke(cli, ['init-db'])
        assert result.exit_code == 1  # click.Abort() returns exit code 1
        assert '❌ Failed to create database tables: Database error' in result.output

    @patch('excel_analyzing.cli.db_manager')
    def test_reset_db_command_with_confirm(self, mock_db_manager, runner):
        """Test database reset command with confirmation flag."""
        mock_db_manager.drop_tables.return_value = None
        mock_db_manager.create_tables.return_value = None
        
        result = runner.invoke(cli, ['reset-db', '--confirm'])
        assert result.exit_code == 0
        assert '✅ Database reset successfully!' in result.output
        mock_db_manager.drop_tables.assert_called_once()
        mock_db_manager.create_tables.assert_called_once()

    @patch('excel_analyzing.cli.db_manager')
    def test_reset_db_command_without_confirm(self, mock_db_manager, runner):
        """Test database reset command without confirmation."""
        # Simulate user declining confirmation
        result = runner.invoke(cli, ['reset-db'], input='n\n')
        assert result.exit_code == 0
        assert 'Operation cancelled.' in result.output
        mock_db_manager.drop_tables.assert_not_called()

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_command_basic(self, mock_pipeline_class, runner, sample_excel_workbook):
        """Test the process command with a sample Excel workbook."""
        # Mock the pipeline
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Mock file discovery
        mock_pipeline.discover_workbooks.return_value = [sample_excel_workbook]
        
        # Mock processing result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.error_message = None
        mock_pipeline.process_workbook.return_value = mock_result
        
        # Test the command
        result = runner.invoke(cli, ['process', str(sample_excel_workbook.parent)])
        assert result.exit_code == 0
        assert '🔍 Discovering Excel files' in result.output
        assert '📊 Found 1 Excel file(s)' in result.output
        assert '✅' in result.output  # Success indicator

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_command_no_files(self, mock_pipeline_class, runner, temp_dir):
        """Test process command when no Excel files are found."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.discover_workbooks.return_value = []
        
        result = runner.invoke(cli, ['process', str(temp_dir)])
        assert result.exit_code == 0
        assert 'No Excel files found.' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_command_with_options(self, mock_pipeline_class, runner, sample_excel_workbook):
        """Test process command with custom processing options."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.discover_workbooks.return_value = [sample_excel_workbook]
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_pipeline.process_workbook.return_value = mock_result
        
        # Test with custom options (using only valid options)
        result = runner.invoke(cli, [
            'process', str(sample_excel_workbook.parent),
            '--recursive',
            '--null-threshold', '0.5'
        ])
        assert result.exit_code == 0
        
        # Verify pipeline was created
        mock_pipeline_class.assert_called_once()

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_analyze_command(self, mock_pipeline_class, runner, sample_excel_workbook):
        """Test the analyze command with a sample workbook."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Mock workbook info
        mock_workbook = MagicMock()
        mock_workbook.file_name = "test_workbook.xlsx"
        mock_workbook.file_size_bytes = 1024 * 50  # 50KB
        mock_workbook.sheet_count = 3
        mock_workbook.sheets = []
        
        # Mock processing result
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.workbook = mock_workbook
        mock_result.processing_time_seconds = 0.5
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['analyze', str(sample_excel_workbook)])
        assert result.exit_code == 0
        assert '🔍 Analyzing:' in result.output
        assert '📊 Workbook: test_workbook.xlsx' in result.output

    def test_analyze_command_directory_error(self, runner, temp_dir):
        """Test analyze command with directory instead of file."""
        result = runner.invoke(cli, ['analyze', str(temp_dir)])
        assert result.exit_code == 0
        assert '❌ Please specify a file, not a directory' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_analyze_command_processing_failure(self, mock_pipeline_class, runner, sample_excel_workbook):
        """Test analyze command when processing fails."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error_message = "Invalid Excel format"
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['analyze', str(sample_excel_workbook)])
        assert result.exit_code == 0
        assert '❌ Failed to process: Invalid Excel format' in result.output

    @patch('excel_analyzing.cli.db_manager')
    def test_list_workbooks_command_empty(self, mock_db_manager, runner):
        """Test list-workbooks command when no workbooks exist."""
        # Mock empty session and query
        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.all.return_value = []
        mock_db_manager.get_session.return_value = iter([mock_session])
        
        result = runner.invoke(cli, ['list-workbooks'])
        assert result.exit_code == 0
        assert 'No workbooks found in database.' in result.output

    @patch('excel_analyzing.cli.db_manager')
    def test_list_workbooks_command_with_data(self, mock_db_manager, runner):
        """Test list-workbooks command with existing workbooks."""
        from datetime import datetime
        
        # Mock workbook data
        mock_workbook = MagicMock()
        mock_workbook.file_name = "sample.xlsx"
        mock_workbook.sheet_count = 2
        mock_workbook.file_size_bytes = 1024 * 100  # 100KB
        mock_workbook.processed_at = datetime(2023, 1, 1, 12, 0, 0)
        
        mock_session = MagicMock()
        mock_session.query.return_value.order_by.return_value.all.return_value = [mock_workbook]
        mock_db_manager.get_session.return_value = iter([mock_session])
        
        result = runner.invoke(cli, ['list-workbooks'])
        assert result.exit_code == 0
        assert 'Processed Workbooks' in result.output
        assert 'sample.xlsx' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_query_command(self, mock_pipeline_class, runner):
        """Test the query command."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Mock dataframe result
        mock_df = pd.DataFrame({'Name': ['Alice', 'Bob'], 'Age': [25, 30]})
        mock_pipeline.processor.get_dataframe.return_value = mock_df
        mock_pipeline.processor.apply_filter.return_value = mock_df
        
        result = runner.invoke(cli, ['query', 'test_workbook', 'Employees', '--limit', '5'])
        assert result.exit_code == 0
        assert '📊 Data from test_workbook → Employees' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_query_command_not_found(self, mock_pipeline_class, runner):
        """Test query command when sheet is not found."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.processor.get_dataframe.return_value = None
        
        result = runner.invoke(cli, ['query', 'test_workbook', 'NonexistentSheet'])
        assert result.exit_code == 0
        assert "❌ Sheet 'NonexistentSheet' not found" in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_query_command_with_filter(self, mock_pipeline_class, runner):
        """Test query command with filter condition."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_df = pd.DataFrame({'Name': ['Alice'], 'Age': [25]})
        mock_pipeline.processor.get_dataframe.return_value = mock_df
        mock_pipeline.processor.apply_filter.return_value = mock_df
        
        result = runner.invoke(cli, [
            'query', 'test_workbook', 'Employees', 
            '--filter', 'Age > 24',
            '--limit', '10'
        ])
        assert result.exit_code == 0
        assert '🔍 Filter: Age > 24' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_query_command_invalid_filter(self, mock_pipeline_class, runner):
        """Test query command with invalid filter condition."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        mock_pipeline.processor.get_dataframe.return_value = pd.DataFrame({'Name': ['Alice'], 'Age': [25]})
        mock_pipeline.processor.apply_filter.return_value = None  # Invalid filter returns None
        
        result = runner.invoke(cli, [
            'query', 'test_workbook', 'Employees', 
            '--filter', 'InvalidColumn > 100'
        ])
        assert result.exit_code == 0
        assert '❌ Invalid filter condition' in result.output


class TestCLIErrorHandling:
    """Test CLI error handling and edge cases."""
    
    @pytest.fixture
    def runner(self):
        """Provide a Click test runner."""
        return CliRunner()
    
    def test_process_nonexistent_path(self, runner):
        """Test process command with non-existent path."""
        result = runner.invoke(cli, ['process', '/nonexistent/path'])
        assert result.exit_code == 2  # Click parameter validation error
        assert 'does not exist' in result.output

    def test_analyze_nonexistent_file(self, runner):
        """Test analyze command with non-existent file."""
        result = runner.invoke(cli, ['analyze', '/nonexistent/file.xlsx'])
        assert result.exit_code == 2  # Click parameter validation error
        assert 'does not exist' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_command_with_exception(self, mock_pipeline_class, runner, temp_dir):
        """Test process command when pipeline raises exception."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create a dummy file to discover
        dummy_file = temp_dir / "test.xlsx"
        dummy_file.touch()
        mock_pipeline.discover_workbooks.return_value = [dummy_file]
        
        # Mock processing failure
        mock_result = MagicMock()
        mock_result.success = False
        mock_result.error_message = "Corrupted file"
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['process', str(temp_dir)])
        assert result.exit_code == 0
        assert '❌' in result.output
        assert 'Corrupted file' in result.output

    def test_main_function(self):
        """Test the main function entry point."""
        # This tests that main() can be called without exceptions
        with patch('excel_analyzing.cli.cli') as mock_cli:
            main()
            mock_cli.assert_called_once()


class TestCLIIntegrationWithRealData:
    """Integration tests with real Excel data."""
    
    @pytest.fixture
    def runner(self):
        """Provide a Click test runner."""
        return CliRunner()
    
    @patch('excel_analyzing.cli.ExcelPipeline')
    def test_full_workflow_with_real_excel_file(self, mock_pipeline_class, runner, temp_dir):
        """Test a complete workflow with a real Excel file."""
        # Create a real Excel file
        excel_file = temp_dir / "integration_test.xlsx"
        
        # Create realistic test data
        employees_data = {
            'Employee_ID': [1001, 1002, 1003, 1004, 1005],
            'First_Name': ['John', 'Jane', 'Bob', 'Alice', 'Charlie'],
            'Last_Name': ['Doe', 'Smith', 'Johnson', 'Williams', 'Brown'],
            'Department': ['Engineering', 'Sales', 'Marketing', 'HR', 'Engineering'],
            'Hire_Date': pd.to_datetime(['2020-01-15', '2019-05-22', '2021-03-10', '2018-11-30', '2022-07-08']),
            'Salary': [85000, 72000, 68000, 75000, 90000],
            'Is_Manager': [False, True, False, True, False],
            'Performance_Rating': [4.2, 3.8, 4.5, 4.0, 4.7]
        }
        
        sales_data = {
            'Transaction_ID': ['T001', 'T002', 'T003', 'T004', 'T005'],
            'Product_Name': ['Laptop Pro', 'Mouse Wireless', 'Keyboard RGB', 'Monitor 4K', 'Webcam HD'],
            'Category': ['Electronics', 'Accessories', 'Accessories', 'Electronics', 'Electronics'],
            'Sale_Date': pd.to_datetime(['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18', '2023-01-19']),
            'Quantity': [2, 5, 3, 1, 4],
            'Unit_Price': [1299.99, 29.99, 89.99, 599.99, 149.99],
            'Total_Amount': [2599.98, 149.95, 269.97, 599.99, 599.96]
        }
        
        with pd.ExcelWriter(excel_file) as writer:
            pd.DataFrame(employees_data).to_excel(writer, sheet_name='Employees', index=False)
            pd.DataFrame(sales_data).to_excel(writer, sheet_name='Sales_Data', index=False)
        
        # Test that the file was created successfully
        assert excel_file.exists()
        assert excel_file.stat().st_size > 0
        
        # Test analyze command with the real file
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create realistic mock workbook info
        mock_sheet1 = MagicMock()
        mock_sheet1.name = 'Employees'
        mock_sheet1.row_count = 5
        mock_sheet1.column_count = 8
        mock_sheet1.has_header = True
        mock_sheet1.header_row = 0
        mock_sheet1.columns = []
        
        mock_sheet2 = MagicMock()
        mock_sheet2.name = 'Sales_Data'
        mock_sheet2.row_count = 5
        mock_sheet2.column_count = 7
        mock_sheet2.has_header = True
        mock_sheet2.header_row = 0
        mock_sheet2.columns = []
        
        mock_workbook = MagicMock()
        mock_workbook.file_name = "integration_test.xlsx"
        mock_workbook.file_size_bytes = excel_file.stat().st_size
        mock_workbook.sheet_count = 2
        mock_workbook.sheets = [mock_sheet1, mock_sheet2]
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.workbook = mock_workbook
        mock_result.processing_time_seconds = 0.15
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['analyze', str(excel_file)])
        assert result.exit_code == 0
        assert 'integration_test.xlsx' in result.output
        assert 'Employees' in result.output
        assert 'Sales_Data' in result.output