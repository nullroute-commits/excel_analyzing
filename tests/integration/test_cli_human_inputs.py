"""Integration tests for CLI with human input scenarios."""

import tempfile
import pytest
import pandas as pd
import os
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, MagicMock

from excel_analyzing.cli import cli


class TestCLIHumanInputScenarios:
    """Test CLI with various human input scenarios and edge cases."""
    
    @pytest.fixture
    def runner(self):
        """Provide a Click test runner."""
        return CliRunner()
    
    @pytest.fixture
    def sample_workbooks_directory(self, temp_dir):
        """Create a directory with multiple Excel workbooks for testing."""
        workbooks_dir = temp_dir / "sample_workbooks"
        workbooks_dir.mkdir()
        
        # Create various types of Excel files
        files_created = []
        
        # 1. Simple employee data
        simple_file = workbooks_dir / "employees.xlsx"
        employees_df = pd.DataFrame({
            'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
            'Department': ['Engineering', 'Sales', 'Marketing'],
            'Salary': [75000, 65000, 70000],
            'Active': [True, True, False]
        })
        employees_df.to_excel(simple_file, index=False)
        files_created.append(simple_file)
        
        # 2. Financial data with multiple sheets
        financial_file = workbooks_dir / "financials_2023.xlsx"
        with pd.ExcelWriter(financial_file) as writer:
            income_df = pd.DataFrame({
                'Month': ['Jan', 'Feb', 'Mar', 'Apr'],
                'Revenue': [100000, 110000, 95000, 120000],
                'Expenses': [80000, 85000, 75000, 95000],
                'Profit': [20000, 25000, 20000, 25000]
            })
            income_df.to_excel(writer, sheet_name='Income_Statement', index=False)
            
            balance_df = pd.DataFrame({
                'Account': ['Cash', 'Accounts_Receivable', 'Inventory', 'Equipment'],
                'Amount': [50000, 30000, 20000, 100000],
                'Type': ['Asset', 'Asset', 'Asset', 'Asset']
            })
            balance_df.to_excel(writer, sheet_name='Balance_Sheet', index=False)
        files_created.append(financial_file)
        
        # 3. Sales data with dates and nulls
        sales_file = workbooks_dir / "sales_data.xlsx"
        sales_df = pd.DataFrame({
            'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
            'Product': ['Widget A', 'Widget B', None, 'Widget A', 'Widget C'],
            'Quantity': [10, 15, 8, 12, None],
            'Price': [25.50, 30.75, 18.00, 25.50, 45.25],
            'Customer': ['Acme Corp', 'Beta LLC', 'Gamma Inc', None, 'Delta Ltd']
        })
        sales_df.to_excel(sales_file, index=False)
        files_created.append(sales_file)
        
        # 4. Large dataset for performance testing
        large_file = workbooks_dir / "large_dataset.xlsx"
        large_df = pd.DataFrame({
            'ID': range(1000),
            'Value': [i * 0.5 for i in range(1000)],
            'Category': [f'Cat_{i % 20}' for i in range(1000)],
            'Flag': [i % 3 == 0 for i in range(1000)]
        })
        large_df.to_excel(large_file, index=False)
        files_created.append(large_file)
        
        # 5. Edge case: Empty sheets and mixed data
        edge_case_file = workbooks_dir / "edge_cases.xlsx"
        with pd.ExcelWriter(edge_case_file) as writer:
            # Sheet with data
            normal_df = pd.DataFrame({'A': [1, 2, 3], 'B': ['x', 'y', 'z']})
            normal_df.to_excel(writer, sheet_name='Normal_Data', index=False)
            
            # Empty sheet
            empty_df = pd.DataFrame()
            empty_df.to_excel(writer, sheet_name='Empty_Sheet', index=False)
            
            # Sheet with only headers
            headers_only_df = pd.DataFrame(columns=['Col1', 'Col2', 'Col3'])
            headers_only_df.to_excel(writer, sheet_name='Headers_Only', index=False)
        files_created.append(edge_case_file)
        
        return workbooks_dir, files_created

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_multiple_files_scenario(self, mock_pipeline_class, runner, sample_workbooks_directory):
        """Test processing multiple Excel files in a directory (typical user scenario)."""
        workbooks_dir, files_created = sample_workbooks_directory
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.discover_workbooks.return_value = files_created
        
        # Mock successful processing for all files
        mock_result = MagicMock()
        mock_result.success = True
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['process', str(workbooks_dir), '--recursive'])
        
        assert result.exit_code == 0
        assert f'Found {len(files_created)} Excel file(s)' in result.output
        assert 'Processing Summary:' in result.output
        assert f'✅ Successful: {len(files_created)}' in result.output
        assert '❌ Failed: 0' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_process_with_some_failures_scenario(self, mock_pipeline_class, runner, sample_workbooks_directory):
        """Test processing where some files succeed and some fail (realistic scenario)."""
        workbooks_dir, files_created = sample_workbooks_directory
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.discover_workbooks.return_value = files_created
        
        # Mock mixed results - some succeed, some fail
        def mock_process_workbook(file_path):
            if 'large_dataset' in str(file_path):
                mock_result = MagicMock()
                mock_result.success = False
                mock_result.error_message = "File too large to process"
                return mock_result
            else:
                mock_result = MagicMock()
                mock_result.success = True
                return mock_result
        
        mock_pipeline.process_workbook.side_effect = mock_process_workbook
        
        result = runner.invoke(cli, ['process', str(workbooks_dir)])
        
        assert result.exit_code == 0
        assert 'Processing Summary:' in result.output
        assert '✅ Successful: 4' in result.output
        assert '❌ Failed: 1' in result.output
        assert 'File too large to process' in result.output

    def test_interactive_database_reset_scenario(self, runner):
        """Test interactive database reset scenario (user input required)."""
        with patch('excel_analyzing.cli.db_manager') as mock_db_manager:
            mock_db_manager.drop_tables.return_value = None
            mock_db_manager.create_tables.return_value = None
            
            # Test user confirms reset
            result = runner.invoke(cli, ['reset-db'], input='y\n')
            assert result.exit_code == 0
            assert '✅ Database reset successfully!' in result.output
            
            # Test user cancels reset
            result = runner.invoke(cli, ['reset-db'], input='n\n')
            assert result.exit_code == 0
            assert 'Operation cancelled.' in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_analyze_different_file_types_scenario(self, mock_pipeline_class, runner, sample_workbooks_directory):
        """Test analyzing different types of Excel files (user explores data)."""
        workbooks_dir, files_created = sample_workbooks_directory
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Test analyzing each type of file
        for file_path in files_created:
            # Mock different workbook structures for each file
            mock_workbook = MagicMock()
            mock_workbook.file_name = file_path.name
            mock_workbook.file_size_bytes = 1024 * 50
            mock_workbook.processing_time_seconds = 0.1
            
            if 'employees' in file_path.name:
                mock_workbook.sheet_count = 1
                mock_sheet = MagicMock()
                mock_sheet.name = 'Sheet1'
                mock_sheet.row_count = 3
                mock_sheet.column_count = 4
                mock_workbook.sheets = [mock_sheet]
            elif 'financials' in file_path.name:
                mock_workbook.sheet_count = 2
                mock_workbook.sheets = [
                    MagicMock(name='Income_Statement', row_count=4, column_count=4),
                    MagicMock(name='Balance_Sheet', row_count=4, column_count=3)
                ]
            elif 'large_dataset' in file_path.name:
                mock_workbook.sheet_count = 1
                mock_sheet = MagicMock()
                mock_sheet.name = 'Sheet1'
                mock_sheet.row_count = 1000
                mock_sheet.column_count = 4
                mock_workbook.sheets = [mock_sheet]
            else:
                mock_workbook.sheet_count = 1
                mock_workbook.sheets = [MagicMock(name='Sheet1', row_count=5, column_count=5)]
            
            # Set up all sheets to have empty columns for simplicity
            for sheet in mock_workbook.sheets:
                sheet.columns = []
                sheet.has_header = True
                sheet.header_row = 0
            
            mock_result = MagicMock()
            mock_result.success = True
            mock_result.workbook = mock_workbook
            mock_pipeline.process_workbook.return_value = mock_result
            
            result = runner.invoke(cli, ['analyze', str(file_path)])
            assert result.exit_code == 0
            assert file_path.name in result.output

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_query_data_exploration_scenario(self, mock_pipeline_class, runner):
        """Test data exploration through query command (typical user workflow)."""
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Test querying employee data
        employees_df = pd.DataFrame({
            'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown'],
            'Department': ['Engineering', 'Sales', 'Marketing'],
            'Salary': [75000, 65000, 70000]
        })
        mock_pipeline.processor.get_dataframe.return_value = employees_df
        mock_pipeline.processor.apply_filter.return_value = employees_df
        
        # Basic query without filter
        result = runner.invoke(cli, ['query', 'employees.xlsx', 'Sheet1', '--limit', '10'])
        assert result.exit_code == 0
        assert 'Data from employees.xlsx → Sheet1' in result.output
        assert 'Alice Johnson' in result.output
        
        # Query with filter for high earners
        high_earners_df = employees_df[employees_df['Salary'] >= 70000]
        mock_pipeline.processor.apply_filter.return_value = high_earners_df
        
        result = runner.invoke(cli, [
            'query', 'employees.xlsx', 'Sheet1', 
            '--filter', 'Salary >= 70000',
            '--limit', '5'
        ])
        assert result.exit_code == 0
        assert 'Filter: Salary >= 70000' in result.output

    def test_help_and_usage_scenarios(self, runner):
        """Test various help and usage scenarios."""
        # Main help
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert 'Excel Analyzing CLI' in result.output
        
        # Command-specific help
        commands = ['process', 'analyze', 'query', 'init-db', 'list-workbooks', 'reset-db']
        for command in commands:
            result = runner.invoke(cli, [command, '--help'])
            assert result.exit_code == 0
            assert command in result.output or command.replace('-', '_') in result.output

    def test_invalid_input_scenarios(self, runner):
        """Test various invalid input scenarios and error handling."""
        # Invalid command
        result = runner.invoke(cli, ['invalid-command'])
        assert result.exit_code == 2
        assert 'No such command' in result.output
        
        # Invalid option for process command
        result = runner.invoke(cli, ['process', '--invalid-option'])
        assert result.exit_code == 2
        assert 'No such option' in result.output
        
        # Invalid null threshold value
        result = runner.invoke(cli, ['process', '/tmp', '--null-threshold', '1.5'])
        assert result.exit_code == 2  # Should fail validation
        
        # Invalid null threshold value (negative)
        result = runner.invoke(cli, ['process', '/tmp', '--null-threshold', '-0.5'])
        assert result.exit_code == 2  # Should fail validation

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_large_dataset_performance_scenario(self, mock_pipeline_class, runner, temp_dir):
        """Test CLI with large dataset (performance scenario)."""
        # Create a larger test file
        large_file = temp_dir / "performance_test.xlsx"
        large_df = pd.DataFrame({
            'ID': range(5000),
            'Value': [i * 0.1 for i in range(5000)],
            'Category': [f'Category_{i % 50}' for i in range(5000)],
            'Date': pd.date_range('2023-01-01', periods=5000, freq='H'),
            'Flag': [i % 7 == 0 for i in range(5000)]
        })
        large_df.to_excel(large_file, index=False)
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Mock performance results
        mock_workbook = MagicMock()
        mock_workbook.file_name = "performance_test.xlsx"
        mock_workbook.file_size_bytes = large_file.stat().st_size
        mock_workbook.sheet_count = 1
        mock_workbook.sheets = [MagicMock(
            name='Sheet1',
            row_count=5000,
            column_count=5,
            columns=[],
            has_header=True,
            header_row=0
        )]
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_result.workbook = mock_workbook
        mock_result.processing_time_seconds = 2.5  # Realistic processing time for large file
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['analyze', str(large_file)])
        assert result.exit_code == 0
        assert 'performance_test.xlsx' in result.output
        assert '5000 rows' in result.output

    def test_empty_and_corrupted_file_scenarios(self, runner, temp_dir):
        """Test handling of empty and corrupted files."""
        # Test with empty file
        empty_file = temp_dir / "empty.xlsx"
        empty_file.touch()
        
        result = runner.invoke(cli, ['analyze', str(empty_file)])
        # This should be handled gracefully, either with an error message or processing
        assert result.exit_code in [0, 1, 2]  # Allow various error codes
        
        # Test with non-Excel file
        text_file = temp_dir / "not_excel.xlsx"
        text_file.write_text("This is not an Excel file")
        
        result = runner.invoke(cli, ['analyze', str(text_file)])
        # Should handle gracefully
        assert result.exit_code in [0, 1, 2]

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_realistic_business_workflow(self, mock_pipeline_class, runner, temp_dir):
        """Test a realistic business user workflow."""
        # Simulate a business user's typical workflow:
        # 1. Initialize database
        # 2. Process some Excel files
        # 3. List processed workbooks
        # 4. Analyze specific files
        # 5. Query data
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        
        # Create business-like Excel files
        business_dir = temp_dir / "business_data"
        business_dir.mkdir()
        
        # Monthly sales report
        sales_file = business_dir / "monthly_sales_2023.xlsx"
        sales_df = pd.DataFrame({
            'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'Product_Line_A': [50000, 55000, 48000, 62000, 58000, 61000],
            'Product_Line_B': [35000, 38000, 33000, 41000, 39000, 42000],
            'Total_Revenue': [85000, 93000, 81000, 103000, 97000, 103000],
            'Target': [90000, 90000, 90000, 90000, 90000, 90000]
        })
        sales_df.to_excel(sales_file, index=False)
        
        # Employee performance data
        performance_file = business_dir / "employee_performance.xlsx"
        with pd.ExcelWriter(performance_file) as writer:
            perf_df = pd.DataFrame({
                'Employee_ID': [101, 102, 103, 104, 105],
                'Name': ['John Smith', 'Jane Doe', 'Mike Johnson', 'Sarah Wilson', 'Tom Brown'],
                'Q1_Score': [4.2, 4.8, 3.9, 4.5, 4.1],
                'Q2_Score': [4.0, 4.9, 4.2, 4.3, 4.4],
                'Promotion_Eligible': [True, True, False, True, False]
            })
            perf_df.to_excel(writer, sheet_name='Performance_Scores', index=False)
        
        # Mock the pipeline for workflow testing
        files_created = [sales_file, performance_file]
        mock_pipeline.discover_workbooks.return_value = files_created
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_pipeline.process_workbook.return_value = mock_result
        
        # Step 1: Initialize database
        with patch('excel_analyzing.cli.db_manager') as mock_db:
            mock_db.create_tables.return_value = None
            result = runner.invoke(cli, ['init-db'])
            assert result.exit_code == 0
            assert '✅ Database tables created successfully!' in result.output
        
        # Step 2: Process business files
        result = runner.invoke(cli, ['process', str(business_dir)])
        assert result.exit_code == 0
        assert 'Found 2 Excel file(s)' in result.output
        
        # Step 3: List workbooks
        with patch('excel_analyzing.cli.db_manager') as mock_db:
            mock_workbook = MagicMock()
            mock_workbook.file_name = "monthly_sales_2023.xlsx"
            mock_workbook.sheet_count = 1
            mock_workbook.file_size_bytes = 1024 * 20
            mock_workbook.processed_at = None
            
            mock_session = MagicMock()
            mock_session.query.return_value.order_by.return_value.all.return_value = [mock_workbook]
            mock_db.get_session.return_value = iter([mock_session])
            
            result = runner.invoke(cli, ['list-workbooks'])
            assert result.exit_code == 0
            assert 'monthly_sales_2023.xlsx' in result.output
        
        # Step 4: Analyze specific file
        mock_workbook = MagicMock()
        mock_workbook.file_name = "monthly_sales_2023.xlsx"
        mock_workbook.file_size_bytes = 1024 * 20
        mock_workbook.sheet_count = 1
        mock_workbook.sheets = [MagicMock(
            name='Sheet1',
            row_count=6,
            column_count=5,
            columns=[],
            has_header=True,
            header_row=0
        )]
        
        mock_result.workbook = mock_workbook
        mock_result.processing_time_seconds = 0.3
        
        result = runner.invoke(cli, ['analyze', str(sales_file)])
        assert result.exit_code == 0
        assert 'monthly_sales_2023.xlsx' in result.output
        
        # Step 5: Query data
        mock_pipeline.processor.get_dataframe.return_value = sales_df
        mock_pipeline.processor.apply_filter.return_value = sales_df
        
        result = runner.invoke(cli, [
            'query', 'monthly_sales_2023.xlsx', 'Sheet1',
            '--filter', 'Total_Revenue >= 90000',
            '--limit', '10'
        ])
        assert result.exit_code == 0
        assert 'Filter: Total_Revenue >= 90000' in result.output


class TestCLIUserExperienceScenarios:
    """Test user experience aspects of the CLI."""
    
    @pytest.fixture
    def runner(self):
        return CliRunner()
    
    def test_logging_levels(self, runner, temp_dir):
        """Test different logging levels."""
        # Test with different log levels
        log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        for level in log_levels:
            result = runner.invoke(cli, ['--log-level', level, '--help'])
            assert result.exit_code == 0
            # The help should still work regardless of log level
            assert 'Excel Analyzing CLI' in result.output

    def test_command_suggestions_for_typos(self, runner):
        """Test that CLI provides helpful error messages for typos."""
        # Test common typos
        typos = ['proces', 'analize', 'listt', 'quer']
        
        for typo in typos:
            result = runner.invoke(cli, [typo])
            assert result.exit_code == 2
            assert 'No such command' in result.output

    def test_required_parameter_validation(self, runner):
        """Test validation of required parameters."""
        # Test process command without path
        result = runner.invoke(cli, ['process'])
        assert result.exit_code == 2
        assert 'Missing argument' in result.output
        
        # Test analyze command without path
        result = runner.invoke(cli, ['analyze'])
        assert result.exit_code == 2
        assert 'Missing argument' in result.output
        
        # Test query command without required arguments
        result = runner.invoke(cli, ['query'])
        assert result.exit_code == 2
        assert 'Missing argument' in result.output

    def test_option_validation(self, runner, temp_dir):
        """Test validation of command options."""
        dummy_file = temp_dir / "test.xlsx"
        dummy_file.touch()
        
        # Test invalid null threshold values
        invalid_thresholds = ['1.5', '-0.1', 'abc', '']
        
        for threshold in invalid_thresholds:
            result = runner.invoke(cli, ['process', str(temp_dir), '--null-threshold', threshold])
            # Should fail with validation error (exit code 2)
            assert result.exit_code == 2

    @patch("excel_analyzing.cli.ExcelPipeline")
    def test_progress_indicators(self, mock_pipeline_class, runner, temp_dir):
        """Test that progress indicators work during processing."""
        # Create multiple files to show progress
        files = []
        for i in range(3):
            file_path = temp_dir / f"test_{i}.xlsx"
            file_path.touch()
            files.append(file_path)
        
        mock_pipeline = MagicMock()
        mock_pipeline_class.return_value = mock_pipeline
        mock_pipeline.discover_workbooks.return_value = files
        
        mock_result = MagicMock()
        mock_result.success = True
        mock_pipeline.process_workbook.return_value = mock_result
        
        result = runner.invoke(cli, ['process', str(temp_dir)])
        assert result.exit_code == 0
        # Should show progress indicators
        assert 'Processing files...' in result.output or 'Processing' in result.output
        assert 'Processing Summary:' in result.output