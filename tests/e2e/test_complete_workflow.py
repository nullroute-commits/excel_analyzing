"""End-to-end tests for the complete Excel analysis workflow."""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from playwright.sync_api import Playwright, Page, BrowserContext
import time
import json


@pytest.fixture(scope="session")
def browser_context(playwright: Playwright):
    """Create a browser context for E2E tests."""
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context(
        viewport={'width': 1280, 'height': 720},
        record_video_dir="test-results/videos/"
    )
    yield context
    context.close()
    browser.close()


@pytest.fixture
def page(browser_context: BrowserContext):
    """Create a new page for each test."""
    page = browser_context.new_page()
    yield page
    page.close()


class TestCompleteWorkflow:
    """Test the complete Excel analysis workflow end-to-end."""
    
    @pytest.fixture
    def test_excel_file(self):
        """Create a test Excel file for E2E testing."""
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            # Create sample data
            data = {
                'Employees': pd.DataFrame({
                    'ID': [1, 2, 3, 4, 5],
                    'Name': ['Alice Johnson', 'Bob Smith', 'Charlie Brown', 'Diana Prince', 'Eve Wilson'],
                    'Department': ['Engineering', 'Sales', 'Engineering', 'Marketing', 'HR'],
                    'Salary': [75000, 65000, 80000, 70000, 60000],
                    'Start_Date': pd.to_datetime(['2020-01-15', '2019-03-20', '2018-07-10', '2021-02-01', '2022-05-15'])
                }),
                'Sales': pd.DataFrame({
                    'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
                    'Product': ['Widget A', 'Widget B', 'Widget A', 'Widget C', 'Widget B'],
                    'Quantity': [10, 5, 8, 3, 12],
                    'Revenue': [1000.00, 750.00, 800.00, 450.00, 1800.00]
                })
            }
            
            with pd.ExcelWriter(tmp.name) as writer:
                for sheet_name, df in data.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return tmp.name
    
    def test_user_registration_and_login(self, page: Page):
        """Test user registration and login flow."""
        base_url = "http://localhost:8000"
        
        # Navigate to registration page
        page.goto(f"{base_url}/register/")
        
        # Fill registration form
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="email"]', 'test@example.com')
        page.fill('input[name="password1"]', 'SecurePass123!')
        page.fill('input[name="password2"]', 'SecurePass123!')
        
        # Submit registration
        page.click('button[type="submit"]')
        
        # Should be redirected to login or dashboard
        page.wait_for_url(f"{base_url}/login/")
        
        # Login with new credentials
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="password"]', 'SecurePass123!')
        page.click('button[type="submit"]')
        
        # Should be logged in and see dashboard
        page.wait_for_url(f"{base_url}/dashboard/")
        assert "Dashboard" in page.title()
    
    def test_excel_upload_and_processing(self, page: Page, test_excel_file):
        """Test the complete Excel upload and processing workflow."""
        base_url = "http://localhost:8000"
        
        # Login first (assuming login functionality works)
        page.goto(f"{base_url}/login/")
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="password"]', 'SecurePass123!')
        page.click('button[type="submit"]')
        
        # Navigate to upload page
        page.goto(f"{base_url}/upload/")
        
        # Upload Excel file
        page.set_input_files('input[type="file"]', test_excel_file)
        page.fill('input[name="workbook_name"]', 'Test Workbook E2E')
        page.fill('textarea[name="description"]', 'End-to-end test workbook')
        
        # Submit upload
        page.click('button[type="submit"]')
        
        # Wait for processing to complete
        page.wait_for_selector('.processing-complete', timeout=30000)
        
        # Verify upload success
        assert "Upload successful" in page.text_content('body')
        
        # Navigate to workbooks list
        page.goto(f"{base_url}/workbooks/")
        
        # Verify workbook appears in list
        assert "Test Workbook E2E" in page.text_content('body')
    
    def test_data_exploration_workflow(self, page: Page):
        """Test data exploration and analysis workflow."""
        base_url = "http://localhost:8000"
        
        # Assume we're logged in and have uploaded data
        page.goto(f"{base_url}/workbooks/")
        
        # Click on a workbook
        page.click('a:has-text("Test Workbook E2E")')
        
        # Should see workbook details page
        page.wait_for_selector('.workbook-details')
        
        # Navigate to different sheets
        page.click('a:has-text("Employees")')
        page.wait_for_selector('.sheet-data')
        
        # Verify data is displayed
        assert "Alice Johnson" in page.text_content('body')
        assert "Engineering" in page.text_content('body')
        
        # Switch to Sales sheet
        page.click('a:has-text("Sales")')
        page.wait_for_selector('.sheet-data')
        
        # Verify sales data is displayed
        assert "Widget A" in page.text_content('body')
        assert "1000.00" in page.text_content('body')
    
    def test_data_filtering_and_search(self, page: Page):
        """Test data filtering and search functionality."""
        base_url = "http://localhost:8000"
        
        # Navigate to employees sheet
        page.goto(f"{base_url}/workbooks/1/sheets/employees/")
        
        # Test search functionality
        page.fill('input[name="search"]', 'Alice')
        page.click('button:has-text("Search")')
        
        # Wait for results
        page.wait_for_selector('.search-results')
        
        # Verify search results
        assert "Alice Johnson" in page.text_content('.search-results')
        assert "Bob Smith" not in page.text_content('.search-results')
        
        # Test filtering
        page.select_option('select[name="department_filter"]', 'Engineering')
        page.click('button:has-text("Apply Filter")')
        
        # Verify filter results
        page.wait_for_selector('.filtered-results')
        assert "Alice Johnson" in page.text_content('.filtered-results')
        assert "Charlie Brown" in page.text_content('.filtered-results')
        assert "Bob Smith" not in page.text_content('.filtered-results')
    
    def test_data_export_workflow(self, page: Page):
        """Test data export functionality."""
        base_url = "http://localhost:8000"
        
        # Navigate to workbook
        page.goto(f"{base_url}/workbooks/1/")
        
        # Click export button
        page.click('button:has-text("Export")')
        
        # Select export format
        page.select_option('select[name="export_format"]', 'csv')
        page.select_option('select[name="export_sheets"]', 'all')
        
        # Start export
        with page.expect_download() as download_info:
            page.click('button:has-text("Download")')
        
        download = download_info.value
        
        # Verify download
        assert download.suggested_filename.endswith('.zip')
        
        # Save and verify file content
        download_path = Path("test-results") / download.suggested_filename
        download.save_as(download_path)
        assert download_path.exists()
        assert download_path.stat().st_size > 0
    
    def test_api_integration_workflow(self, page: Page):
        """Test API integration through web interface."""
        base_url = "http://localhost:8000"
        
        # Navigate to API explorer/documentation
        page.goto(f"{base_url}/api/docs/")
        
        # Test API endpoint
        page.click('button:has-text("Try it out")')
        
        # Make API request
        page.fill('textarea[name="request_body"]', '{"query": "SELECT * FROM employees WHERE department = \'Engineering\'"}')
        page.click('button:has-text("Execute")')
        
        # Wait for response
        page.wait_for_selector('.api-response')
        
        # Verify API response
        response_text = page.text_content('.api-response')
        assert "Alice Johnson" in response_text
        assert "Charlie Brown" in response_text
    
    def test_error_handling_workflow(self, page: Page):
        """Test error handling in the user interface."""
        base_url = "http://localhost:8000"
        
        # Test with invalid file upload
        page.goto(f"{base_url}/upload/")
        
        # Create a fake non-Excel file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp:
            tmp.write(b"This is not an Excel file")
            tmp.flush()
            
            # Try to upload invalid file
            page.set_input_files('input[type="file"]', tmp.name)
            page.click('button[type="submit"]')
            
            # Should see error message
            page.wait_for_selector('.error-message')
            assert "Invalid file format" in page.text_content('.error-message')
        
        # Test with network error simulation
        # This would require mocking or service interruption
    
    def test_performance_user_experience(self, page: Page):
        """Test performance aspects of user experience."""
        base_url = "http://localhost:8000"
        
        # Measure page load times
        start_time = time.time()
        page.goto(f"{base_url}/")
        page.wait_for_load_state('networkidle')
        load_time = time.time() - start_time
        
        # Homepage should load quickly
        assert load_time < 3.0, f"Homepage took {load_time:.2f}s to load"
        
        # Test large dataset handling
        page.goto(f"{base_url}/workbooks/")
        
        # Navigate to a sheet with large dataset
        start_time = time.time()
        page.click('a:has-text("Large Dataset")')
        page.wait_for_selector('.sheet-data')
        render_time = time.time() - start_time
        
        # Data rendering should be reasonable
        assert render_time < 5.0, f"Data rendering took {render_time:.2f}s"
    
    def test_mobile_responsiveness(self, browser_context: BrowserContext):
        """Test mobile responsiveness."""
        # Create mobile context
        mobile_page = browser_context.new_page()
        mobile_page.set_viewport_size({"width": 375, "height": 667})  # iPhone size
        
        base_url = "http://localhost:8000"
        mobile_page.goto(base_url)
        
        # Check that mobile navigation works
        mobile_page.click('.mobile-menu-toggle')
        mobile_page.wait_for_selector('.mobile-menu', state='visible')
        
        # Test that content is accessible on mobile
        mobile_page.click('a:has-text("Workbooks")')
        mobile_page.wait_for_selector('.workbook-list')
        
        # Verify responsive layout
        content_width = mobile_page.evaluate('document.querySelector(".main-content").offsetWidth')
        assert content_width <= 375, f"Content too wide for mobile: {content_width}px"
        
        mobile_page.close()
    
    def test_accessibility_compliance(self, page: Page):
        """Test accessibility compliance."""
        base_url = "http://localhost:8000"
        page.goto(base_url)
        
        # Check for proper heading structure
        h1_count = len(page.query_selector_all('h1'))
        assert h1_count == 1, f"Should have exactly one h1 tag, found {h1_count}"
        
        # Check for alt text on images
        images = page.query_selector_all('img')
        for img in images:
            alt_text = img.get_attribute('alt')
            assert alt_text is not None and alt_text.strip() != "", "Images should have alt text"
        
        # Check for proper form labels
        inputs = page.query_selector_all('input[type="text"], input[type="email"], input[type="password"]')
        for input_elem in inputs:
            label_id = input_elem.get_attribute('id')
            if label_id:
                label = page.query_selector(f'label[for="{label_id}"]')
                assert label is not None, f"Input {label_id} should have associated label"
    
    def test_cross_browser_compatibility(self, playwright: Playwright):
        """Test cross-browser compatibility."""
        browsers = ['chromium', 'firefox', 'webkit']
        base_url = "http://localhost:8000"
        
        for browser_name in browsers:
            browser = getattr(playwright, browser_name).launch()
            context = browser.new_context()
            page = context.new_page()
            
            try:
                # Test basic functionality in each browser
                page.goto(base_url)
                page.wait_for_load_state('networkidle')
                
                # Verify page loads correctly
                assert "Excel Analyzing" in page.title()
                
                # Test navigation
                page.click('a:has-text("Workbooks")')
                page.wait_for_selector('.workbook-list')
                
                # Browser-specific tests could go here
                
            finally:
                context.close()
                browser.close()


class TestSecurityE2E:
    """End-to-end security tests."""
    
    def test_xss_protection(self, page: Page):
        """Test XSS protection in the web interface."""
        base_url = "http://localhost:8000"
        
        # Try to inject XSS in workbook name
        page.goto(f"{base_url}/upload/")
        
        xss_payload = '<script>alert("xss")</script>'
        page.fill('input[name="workbook_name"]', xss_payload)
        page.click('button[type="submit"]')
        
        # Check that script is not executed
        page.wait_for_timeout(1000)  # Wait to see if alert appears
        
        # XSS should be escaped/sanitized
        page.goto(f"{base_url}/workbooks/")
        page_content = page.text_content('body')
        assert '<script>' not in page_content
        assert '&lt;script&gt;' in page_content or xss_payload not in page_content
    
    def test_csrf_protection(self, page: Page):
        """Test CSRF protection."""
        base_url = "http://localhost:8000"
        
        # Login first
        page.goto(f"{base_url}/login/")
        page.fill('input[name="username"]', 'testuser')
        page.fill('input[name="password"]', 'SecurePass123!')
        page.click('button[type="submit"]')
        
        # Try to make request without CSRF token
        response = page.evaluate('''
            fetch('/api/workbooks/', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: 'test'})
            }).then(r => r.status)
        ''')
        
        # Should be rejected due to missing CSRF token
        assert response == 403
    
    def test_authentication_required(self, page: Page):
        """Test that authentication is required for protected resources."""
        base_url = "http://localhost:8000"
        
        # Try to access protected resource without login
        page.goto(f"{base_url}/workbooks/")
        
        # Should be redirected to login
        page.wait_for_url(f"{base_url}/login/?next=/workbooks/")
        assert "login" in page.url.lower()


class TestPerformanceE2E:
    """End-to-end performance tests."""
    
    def test_large_file_upload_performance(self, page: Page):
        """Test performance with large file uploads."""
        # Create a large test file
        large_data = pd.DataFrame({
            f'col_{i}': range(10000) for i in range(20)
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            large_data.to_excel(tmp.name, index=False)
            
            base_url = "http://localhost:8000"
            page.goto(f"{base_url}/upload/")
            
            # Measure upload time
            start_time = time.time()
            page.set_input_files('input[type="file"]', tmp.name)
            page.click('button[type="submit"]')
            page.wait_for_selector('.processing-complete', timeout=120000)  # 2 minutes
            upload_time = time.time() - start_time
            
            # Large file should process within reasonable time
            assert upload_time < 120, f"Large file upload took {upload_time:.2f}s"
    
    def test_concurrent_user_performance(self, playwright: Playwright):
        """Test performance with concurrent users."""
        base_url = "http://localhost:8000"
        concurrent_users = 5
        
        # Create multiple browser contexts to simulate concurrent users
        contexts = []
        pages = []
        
        try:
            for i in range(concurrent_users):
                browser = playwright.chromium.launch()
                context = browser.new_context()
                page = context.new_page()
                contexts.append(context)
                pages.append(page)
            
            # All users navigate to the site simultaneously
            start_time = time.time()
            for page in pages:
                page.goto(base_url)
            
            # Wait for all pages to load
            for page in pages:
                page.wait_for_load_state('networkidle')
            
            total_time = time.time() - start_time
            
            # Should handle concurrent users reasonably
            assert total_time < 10, f"Concurrent user load took {total_time:.2f}s"
            
        finally:
            for context in contexts:
                context.close()