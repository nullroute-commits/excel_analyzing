# Testing Infrastructure

Excel Analyzing includes a comprehensive testing infrastructure designed to ensure code quality, functionality, and performance across all components.

## Testing Overview

The testing strategy follows a pyramid approach with multiple layers:

- **Unit Tests**: Fast, isolated component testing
- **Integration Tests**: Component interaction and database testing  
- **End-to-End Tests**: Complete workflow validation through web interface
- **Performance Tests**: Performance benchmarking and monitoring
- **Security Tests**: Security validation and vulnerability detection
- **Regression Tests**: Baseline comparison to prevent functionality regression

## Test Structure

```
tests/
├── unit/                           # Unit tests for individual components
│   ├── test_models.py             # Pydantic model validation tests
│   └── test_processor.py          # Data processing logic tests
├── integration/                    # Integration tests
│   ├── test_pipeline_integration.py   # Pipeline integration tests
│   └── test_web_integration.py    # Web interface integration tests
├── e2e/                           # End-to-end tests
│   └── test_complete_workflow.py  # Complete user workflow tests
├── performance/                    # Performance tests
│   └── test_performance_suite.py  # Performance benchmarking
├── security/                      # Security tests
│   └── test_security_suite.py     # Security validation tests
├── regression/                     # Regression tests
│   ├── test_regression_suite.py   # Regression test suite
│   └── baselines/                 # Baseline data for comparison
└── conftest.py                    # Shared test configuration and fixtures
```

## Running Tests

### Quick Start

**Run all tests**:
```bash
# Using pytest directly
pytest

# With coverage reporting
pytest --cov=excel_analyzing --cov-report=html

# Using the test runner script
python run_tests.py --all
```

**Run specific test categories**:
```bash
# Unit tests only
pytest tests/unit/

# Integration tests only  
pytest tests/integration/

# Performance tests only
pytest tests/performance/ -m performance

# End-to-end tests only
pytest tests/e2e/
```

### Docker Testing (Recommended)

**Using Docker Compose**:
```bash
# Run tests in isolated containers
docker-compose -f docker-compose.test.yml up

# Run specific test services
docker-compose -f docker-compose.test.yml up web-service
docker-compose -f docker-compose.test.yml up e2e-service
```

### Test Configuration

Tests are configured through `pytest.ini_options` in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "excel_analyzing.web.settings.test"
python_files = ["tests.py", "test_*.py", "*_tests.py"]
testpaths = ["tests"]
addopts = "--cov=excel_analyzing --cov-report=term-missing --cov-report=html"
markers = [
    "unit: Unit tests",
    "integration: Integration tests", 
    "regression: Regression tests",
    "security: Security tests",
    "performance: Performance tests",
    "e2e: End-to-end tests",
    "slow: Slow running tests"
]
```

## Test Categories

### Unit Tests (`tests/unit/`)

Fast, isolated tests for individual components:

- **Model Tests**: Pydantic schema validation and SQLAlchemy model tests
- **Processor Tests**: Data processing logic and transformation tests
- **Core Logic Tests**: Configuration, type inference, and cleaning function tests

**Example Unit Test**:
```python
import pytest
from excel_analyzing.models.schemas import WorkbookInfo
from pathlib import Path

def test_workbook_info_validation():
    """Test WorkbookInfo model validation."""
    # Test valid workbook info
    workbook = WorkbookInfo(
        file_path=Path("test.xlsx"),
        file_name="test.xlsx",
        file_size_bytes=1024,
        sheet_count=2
    )
    assert workbook.file_name == "test.xlsx"
    assert workbook.sheet_count == 2
```

### Integration Tests (`tests/integration/`)

Tests for component interactions and database operations:

- **Pipeline Integration**: Complete processing pipeline tests
- **Database Integration**: SQLAlchemy model and query tests
- **Web Integration**: Django view and API endpoint tests

**Example Integration Test**:
```python
import pytest
from excel_analyzing.pipeline.orchestrator import ExcelPipeline

@pytest.mark.integration
def test_pipeline_processing(sample_excel_file):
    """Test complete pipeline processing."""
    pipeline = ExcelPipeline()
    result = pipeline.process_workbook(sample_excel_file)
    
    assert result.success
    assert result.workbook.sheet_count > 0
    assert len(result.workbook.sheets) > 0
```

### End-to-End Tests (`tests/e2e/`)

Complete workflow tests using Playwright for web interface testing:

- **File Upload Workflows**: Test file upload through web interface
- **Processing Workflows**: Test complete processing through UI
- **API Workflows**: Test API endpoints with real data

**Example E2E Test**:
```python
import pytest
from playwright.sync_api import Page

@pytest.mark.e2e
def test_workbook_upload_workflow(page: Page, live_server):
    """Test complete workbook upload workflow."""
    page.goto(f"{live_server.url}/upload/")
    
    # Upload file
    page.set_input_files('[data-testid="file-input"]', "test_data/sample.xlsx")
    page.click('[data-testid="upload-button"]')
    
    # Verify processing
    expect(page.locator('[data-testid="success-message"]')).to_be_visible()
```

### Performance Tests (`tests/performance/`)

Performance benchmarking and monitoring tests:

- **Processing Performance**: Benchmark file processing speed
- **Memory Usage**: Monitor memory consumption during processing
- **Database Performance**: Test query performance and optimization

**Example Performance Test**:
```python
import pytest
from excel_analyzing.pipeline.orchestrator import ExcelPipeline

@pytest.mark.performance
def test_processing_performance(benchmark, large_excel_file):
    """Benchmark processing performance."""
    pipeline = ExcelPipeline()
    
    result = benchmark(pipeline.process_workbook, large_excel_file)
    
    assert result.success
    assert result.processing_time_seconds < 30  # Performance threshold
```

### Security Tests (`tests/security/`)

Security validation and vulnerability detection tests:

- **Input Validation**: Test malicious file handling
- **Authentication**: Test access control and permissions
- **Data Sanitization**: Test XSS and injection prevention

**Example Security Test**:
```python
import pytest
from excel_analyzing.core.security import validate_file_upload

@pytest.mark.security  
def test_malicious_file_rejection():
    """Test rejection of malicious files."""
    malicious_file = "tests/security/malicious.exe"
    
    with pytest.raises(SecurityError):
        validate_file_upload(malicious_file)
```

### Regression Tests (`tests/regression/`)

Baseline comparison tests to prevent functionality regression:

- **Output Validation**: Compare processing results against baselines
- **API Compatibility**: Ensure API responses remain consistent
- **Configuration Changes**: Test configuration backward compatibility

**Example Regression Test**:
```python
import pytest
from excel_analyzing.pipeline.orchestrator import ExcelPipeline

@pytest.mark.regression
def test_processing_output_regression(baseline_data):
    """Test processing output against baseline."""
    pipeline = ExcelPipeline()
    result = pipeline.process_workbook("tests/data/baseline.xlsx")
    
    # Compare against stored baseline
    assert_baseline_match(result.workbook, baseline_data)
```
```

### Local Development Testing

```bash
# Using the test runner script
python run_tests.py --all

# Using tox
tox -e all-tests

# Using pytest directly
pytest tests/ -v
```

### Run Specific Test Categories
```bash
# Unit tests only
python run_tests.py --unit --lint

# Integration and security
python run_tests.py --integration --security

# Performance benchmarking
python run_tests.py --performance --benchmark

# End-to-end with video recording
python run_tests.py --e2e --video
```

## 🔧 Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Speed**: Very fast (< 1s per test)
- **Coverage**: 90%+ code coverage target
- **Dependencies**: Mock external dependencies

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and complete workflows
- **Features**:
  - Excel pipeline processing tests
  - Django web interface testing
  - API endpoint validation
  - Database integration testing
- **Database**: Uses PostgreSQL test database

### Regression Tests (`tests/regression/`)
- **Purpose**: Prevent functionality regressions
- **Features**:
  - Baseline comparison system
  - Data processing consistency validation
  - API response structure verification
  - Performance regression detection
- **Baselines**: Stored in `tests/regression/baselines/`

### Security Tests (`tests/security/`)
- **Purpose**: Identify and prevent security vulnerabilities
- **Coverage**:
  - Input sanitization testing
  - Authentication/authorization validation
  - SQL injection prevention
  - XSS protection testing
  - File upload security
  - Configuration security
- **Tools**: Integrates with Bandit, Safety, Semgrep

### Performance Tests (`tests/performance/`)
- **Purpose**: Monitor and maintain performance characteristics
- **Metrics**:
  - Execution time benchmarking
  - Memory usage monitoring
  - CPU utilization tracking
  - Throughput measurement
- **Categories**:
  - Data processing performance
  - Database operation benchmarks
  - API response time validation
  - Memory leak detection

### End-to-End Tests (`tests/e2e/`)
- **Purpose**: Test complete user workflows
- **Technology**: Playwright browser automation
- **Scenarios**:
  - User registration and authentication
  - Excel file upload and processing
  - Data exploration and filtering
  - Export functionality
  - Error handling workflows
  - Cross-browser compatibility

## 🔄 CI/CD Integration

### GitHub Actions Workflows

#### Comprehensive Testing Pipeline (`.github/workflows/comprehensive-testing.yml`)
- **Triggers**: Push to main/develop, PRs, nightly schedule
- **Matrix**: Python 3.9-3.12 across multiple test categories
- **Services**: PostgreSQL, Redis for integration testing
- **Features**:
  - Parallel test execution
  - Coverage reporting
  - Artifact collection
  - Comprehensive reporting

#### Security Testing Pipeline (`.github/workflows/security-testing.yml`)
- **Triggers**: Push, PRs, daily schedule, manual dispatch
- **Features**:
  - Dependency vulnerability scanning
  - Static application security testing (SAST)
  - Secret scanning
  - Dynamic application security testing (DAST)
  - Container security scanning
  - Automated security alerting

## 📊 Test Reporting

### Coverage Reports
- HTML coverage reports generated in `htmlcov/`
- XML reports for CI integration
- Coverage thresholds enforced

### Performance Benchmarks
- JSON benchmark reports
- Historical performance tracking
- Regression detection

### Security Reports
- Bandit static analysis reports
- Safety dependency vulnerability reports
- Semgrep security findings

## 🛠️ Configuration

### Test Configuration Files
- `pyproject.toml`: Main pytest configuration with markers
- `tox.ini`: Multi-environment testing configuration
- `tests/conftest.py`: Shared fixtures and utilities
- Environment-specific settings in test files

### Test Markers
```python
@pytest.mark.unit          # Unit tests
@pytest.mark.integration   # Integration tests  
@pytest.mark.regression    # Regression tests
@pytest.mark.security      # Security tests
@pytest.mark.performance   # Performance tests
@pytest.mark.e2e          # End-to-end tests
@pytest.mark.slow         # Slow running tests
```

### Environment Variables
```bash
ENVIRONMENT=test                    # Test environment
DATABASE_URL=postgresql://...       # Test database URL
REDIS_URL=redis://localhost:6379/0  # Test Redis URL
```

## 🎮 Usage Examples

### Running Tests with Coverage
```bash
pytest tests/unit/ --cov=excel_analyzing --cov-report=html
```

### Security Testing
```bash
# Run security test suite
pytest tests/security/ -v

# Static security analysis
bandit -r excel_analyzing/
safety check

# Using test runner
python run_tests.py --security
```

### Performance Testing with Benchmarks
```bash
# Run performance tests with benchmarking
pytest tests/performance/ --benchmark-json=benchmark.json

# Compare with previous benchmarks
pytest tests/performance/ --benchmark-compare

# Using test runner
python run_tests.py --performance --benchmark
```

### End-to-End Testing
```bash
# Install browser dependencies
playwright install chromium

# Run E2E tests
pytest tests/e2e/ -v

# Run with video recording
pytest tests/e2e/ --video=on

# Run in headed mode for debugging
pytest tests/e2e/ --headed

# Using test runner
python run_tests.py --e2e --video --headed
```

### Regression Testing
```bash
# Run regression tests
pytest tests/regression/ -v

# Update baselines (when needed)
pytest tests/regression/ --update-baselines
```

## 🔍 Test Utilities

### Test Data Generators
```python
from tests.conftest import TestDataGenerator

# Generate performance test data
df = TestDataGenerator.create_performance_dataset(10000, 20)

# Generate security test data
security_data = TestDataGenerator.create_security_test_data()
```

### Custom Assertions
```python
from tests.conftest import assert_performance_threshold, assert_no_security_issues

# Performance assertions
assert_performance_threshold(execution_time, 5.0, "Data processing")

# Security assertions  
assert_no_security_issues(scan_results)
```

## 📚 Documentation

- **Comprehensive Testing Guide**: `docs/testing/comprehensive-testing-guide.md`
- **Developer Guide Updates**: Updated with new testing processes
- **Test Runner Script**: `run_tests.py` with help documentation

## 🚀 Future Enhancements

### Planned Improvements
- Visual regression testing for UI components
- Load testing with realistic user patterns
- Chaos engineering tests
- Mobile app testing capabilities
- API contract testing

### Tool Integrations
- SonarQube for code quality analysis
- OWASP ZAP for web application security testing
- K6 for load and performance testing
- Storybook for component testing

## 🤝 Contributing

### Adding New Tests
1. Choose appropriate test category
2. Follow existing test patterns
3. Use provided fixtures and utilities
4. Add appropriate test markers
5. Update documentation

### Test Best Practices
1. Clear, descriptive test names
2. Single responsibility per test
3. Fast feedback with unit tests
4. Realistic test data
5. Proper cleanup and isolation

## 📈 Metrics and Monitoring

### Test Metrics Tracked
- **Coverage**: Code coverage percentage
- **Performance**: Test execution time trends
- **Quality**: Test failure rates and flakiness
- **Security**: Security finding trends over time

### Success Criteria
- Unit test coverage > 90%
- Integration tests pass across all environments
- No critical or high security vulnerabilities
- Performance regressions < 10%
- E2E tests pass in multiple browsers

## 🔗 Related Files

### Key Files Added/Modified
- `tests/integration/` - New integration test suite
- `tests/regression/` - New regression test suite  
- `tests/security/` - New security test suite
- `tests/performance/` - New performance test suite
- `tests/e2e/` - New end-to-end test suite
- `tests/conftest.py` - Shared test configuration
- `.github/workflows/comprehensive-testing.yml` - Comprehensive CI pipeline
- `.github/workflows/security-testing.yml` - Security-focused CI pipeline
- `run_tests.py` - Convenient test runner script
- `docs/testing/` - Testing documentation
- Updated `pyproject.toml` and `tox.ini` with new test configurations

This comprehensive testing infrastructure ensures robust, secure, and performant code through multiple layers of automated validation.