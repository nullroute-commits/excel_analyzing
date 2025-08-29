# Excel Analyzing: Data Processing & Analysis Framework

## Overview

Excel Analyzing is a Python-based data processing framework for analyzing and transforming Microsoft Excel workbook files. The framework treats Excel workbooks as database entities, where individual worksheets function as database tables with automated schema detection, data type inference, and data validation.

The system provides a clean, modular architecture with separate concerns for data processing, web interface, and command-line operations. Built with modern Python standards and best practices.

## Features

### Core Data Processing
- **Multi-Format Excel Support**: Handles XLSX, XLS, XLSM, and XLSB files using openpyxl and xlrd
- **Database Integration**: SQLAlchemy ORM with PostgreSQL backend for metadata storage  
- **Automatic Data Type Inference**: Intelligent detection of string, integer, float, boolean, and datetime types
- **Data Cleaning Pipeline**: Removes empty rows/columns, normalizes column names, handles null values
- **Workbook-to-Database Mapping**: Treats workbooks as schemas and worksheets as tables

### User Interfaces
- **Command Line Interface**: Click-based CLI with Rich formatting for data processing operations
- **Web Interface**: Django-based web application with REST API endpoints
- **Programmatic API**: Python classes for integration into other applications

### Configuration & Deployment  
- **Environment-Specific Settings**: Support for development, test, and production configurations
- **Docker Support**: Multi-stage containerized deployment with Alpine Linux base images
- **Hostname-Based Service Discovery**: Service communication through hostnames rather than localhost

## Architecture

The Excel Analyzing framework uses a layered architecture with clear separation of concerns:

### Directory Structure
```text
excel_analyzing/
├── cli.py                   # Command line interface (Click)
├── core/                    # Core business logic and configuration
│   ├── config.py           # Application settings and configuration
│   ├── data_types.py       # Data type inference utilities  
│   ├── cleaning.py         # Data cleaning and normalization
│   └── schema.py           # Schema definitions
├── models/                  # Data models and database entities
│   ├── database.py         # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic data validation models
├── pipeline/                # Data processing pipeline
│   ├── orchestrator.py     # Main processing coordinator
│   └── processor.py        # Excel data processing engine
├── utils/                   # Utility functions
│   ├── files.py            # File handling utilities
│   └── logging.py          # Logging configuration
└── web/                     # Django web application
    ├── apps/               # Django applications
    ├── settings/           # Environment-specific settings
    ├── templates/          # HTML templates
    ├── static/             # Static files (CSS, JS)
    ├── urls.py             # URL routing
    └── wsgi.py             # WSGI application entry point
```

### Key Components

1. **Pipeline Layer**: `ExcelPipeline` orchestrates processing, `ExcelDataProcessor` handles data transformation
2. **Model Layer**: Pydantic schemas for validation, SQLAlchemy models for persistence  
3. **Web Layer**: Django views and REST API endpoints
4. **CLI Layer**: Click-based command interface with Rich formatting

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Modern Python features and type hints
- **Pandas 2.3+**: Data manipulation and analysis
- **SQLAlchemy 2.0+**: Database ORM and connection pooling
- **PostgreSQL**: Primary database for metadata storage
- **Pydantic 2.11+**: Data validation and settings management

### Excel Processing
- **openpyxl 3.1+**: Reading/writing XLSX, XLSM files
- **xlrd 2.0+**: Legacy XLS file support

### Web Framework
- **Django 5.2+**: Web framework and admin interface
- **Django REST Framework 3.16+**: API development

### CLI & User Interface
- **Click 8.2+**: Command line interface framework
- **Rich 14.1+**: Terminal formatting and progress bars

### Development Tools
- **pytest**: Testing framework with coverage reporting
- **Black**: Code formatting
- **flake8**: Code linting  
- **mypy**: Static type checking
- **pre-commit**: Git hooks for quality assurance

## Installation & Setup

### Prerequisites
- **Python 3.10 or higher**
- **PostgreSQL 12 or higher** 
- **Git** for version control

### Development Setup

#### 1. Clone Repository
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
```

#### 2. Create Virtual Environment
```bash
python3.10 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install Dependencies
```bash
# Upgrade pip first
pip install --upgrade pip

# Install development dependencies
pip install -r requirements-dev.txt

# Install package in editable mode
pip install -e .
```

#### 4. Environment Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings:
# - DATABASE_URL=postgresql://username:password@localhost:5432/excel_analyzing
# - DEBUG=True (for development)
# - SECRET_KEY=your-secret-key
```

#### 5. Database Setup
```bash
# Initialize database tables
python manage.py migrate

# Or use CLI command
excel-analyze init-db
```

### Docker Setup (Recommended)

#### Development Environment
```bash
# Start all services
docker-compose -f docker-compose.dev.yml up --build

# Access application at http://localhost:8000
# API endpoints at http://localhost:8000/api/
```

#### Production Deployment
```bash
# Configure production environment variables
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Start production services
docker-compose up -d
```

## Usage

### Command Line Interface

The CLI provides essential commands for Excel file processing:

#### Initialize Database
```bash
excel-analyze init-db
```

#### Process Excel Files
```bash
# Process a single file
excel-analyze process /path/to/workbook.xlsx

# Process directory recursively
excel-analyze process /path/to/excel/files --recursive

# Process with custom options
excel-analyze process /path/to/files \
    --recursive \
    --drop-empty-rows \
    --clean-column-names \
    --log-level DEBUG
```

#### Analyze Workbooks
```bash
# Basic analysis
excel-analyze analyze /path/to/workbook.xlsx

# Analysis with statistics
excel-analyze analyze /path/to/workbook.xlsx --include-statistics
```

### Python API

#### Basic Usage
```python
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions
from pathlib import Path

# Configure processing options
options = ProcessingOptions(
    drop_empty_rows=True,
    drop_empty_columns=True,
    clean_column_names=True,
    infer_data_types=True,
    null_threshold=0.9
)

# Initialize pipeline
pipeline = ExcelPipeline(processing_options=options)

# Process a workbook
result = pipeline.process_workbook(Path("workbook.xlsx"))

if result.success:
    print(f"Processed {result.rows_processed} rows in {result.processing_time_seconds:.2f}s")
else:
    print(f"Processing failed: {result.error_message}")
```

#### Data Processing
```python
from excel_analyzing.pipeline.processor import ExcelDataProcessor

# Initialize processor
processor = ExcelDataProcessor()

# Load workbook
workbook_info = processor.load_workbook("data.xlsx")
print(f"Found {workbook_info.sheet_count} sheets")

# Access sheet data
for sheet in workbook_info.sheets:
    print(f"Sheet: {sheet.name}, Rows: {sheet.row_count}, Columns: {sheet.column_count}")
```

### Web Interface

#### Development Server
```bash
# Start Django development server
python manage.py runserver

# Access web interface at http://localhost:8000
# API endpoints at http://localhost:8000/api/
```

#### API Endpoints

- `GET /api/workbooks/` - List processed workbooks
- `POST /api/workbooks/` - Upload and process new workbook
- `GET /api/workbooks/{id}/` - Get workbook details
- `GET /api/workbooks/{id}/sheets/` - List sheets in workbook  
- `GET /api/sheets/{id}/data/` - Get sheet data with optional filtering

## Configuration

The application uses environment-based configuration with support for development, test, and production environments.

### Environment Variables

#### Core Settings
- `ENVIRONMENT`: Application environment (development/test/production)
- `DEBUG`: Enable debug mode (default: False)
- `SECRET_KEY`: Django secret key for cryptographic operations

#### Database Configuration
- `DATABASE_URL`: PostgreSQL connection string
- `DATABASE_POOL_SIZE`: Connection pool size (default: 10)
- `DATABASE_MAX_OVERFLOW`: Maximum overflow connections (default: 20)

#### Application Settings
- `LOG_LEVEL`: Logging level (INFO/DEBUG/WARNING/ERROR)
- `MAX_FILE_SIZE_MB`: Maximum file size for uploads (default: 100MB)

### Processing Options

The `ProcessingOptions` class configures data processing behavior:

```python
from excel_analyzing.models.schemas import ProcessingOptions

options = ProcessingOptions(
    drop_empty_rows=True,           # Remove completely empty rows
    drop_empty_columns=True,        # Remove completely empty columns
    infer_data_types=True,          # Automatically detect data types
    clean_column_names=True,        # Normalize column names
    null_threshold=0.9,            # Drop columns with >90% null values
    max_sample_size=100            # Sample size for type inference
)
```

## Data Processing Pipeline

### 1. File Discovery
- Recursively scan directories for Excel files
- Filter by extension (.xlsx, .xls, .xlsm, .xlsb)
- Skip temporary files (starting with ~$)

### 2. Data Processing
- Load workbook metadata using openpyxl/xlrd
- Detect and validate sheet structure
- Infer data types for columns
- Clean and normalize column names
- Remove empty rows/columns based on thresholds

### 3. Database Storage
- Save workbook metadata to PostgreSQL
- Store sheet and column information
- Track processing results and errors

### 4. Data Access
- Query data through Django ORM
- REST API endpoints for programmatic access
- Export capabilities (CSV, JSON)

## Testing

The project includes comprehensive testing infrastructure with multiple test categories.

### Running Tests

#### Basic Test Execution
```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=excel_analyzing --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests only
```

#### Using the Test Runner
```bash
# Run comprehensive test suite
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit --integration
python run_tests.py --security --performance
python run_tests.py --e2e --headed
```

#### Docker-based Testing
```bash
# Run tests in container environment
docker-compose -f docker-compose.test.yml up

# Run specific test suites
docker-compose -f docker-compose.test.yml run test-service pytest tests/unit/
```

### Test Categories

- **Unit Tests** (`tests/unit/`): Test individual components and functions
- **Integration Tests** (`tests/integration/`): Test component interactions
- **Regression Tests** (`tests/regression/`): Prevent regression of fixed issues
- **Security Tests** (`tests/security/`): Security and vulnerability testing
- **Performance Tests** (`tests/performance/`): Performance benchmarking
- **End-to-End Tests** (`tests/e2e/`): Complete workflow testing

## Development

### Code Quality Tools

#### Formatting and Linting
```bash
# Format code with Black
black excel_analyzing/

# Sort imports with isort
isort excel_analyzing/

# Lint with flake8
flake8 excel_analyzing/

# Type checking with mypy
mypy excel_analyzing/
```

#### Pre-commit Hooks
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

### Development Workflow

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature
   ```

2. **Make Changes**
   - Follow PEP8 coding standards
   - Add tests for new functionality
   - Update documentation as needed

3. **Run Quality Checks**
   ```bash
   # Run formatting and linting
   black excel_analyzing/ && isort excel_analyzing/
   flake8 excel_analyzing/
   mypy excel_analyzing/
   
   # Run tests
   pytest
   ```

4. **Submit Pull Request**
   - Clear description of changes
   - Link to related issues
   - Ensure all checks pass

## API Documentation

### REST Endpoints

The web interface provides REST API endpoints for programmatic access:

#### Workbooks
- `GET /api/workbooks/` - List all processed workbooks
- `POST /api/workbooks/` - Upload and process a new workbook
- `GET /api/workbooks/{id}/` - Get workbook details
- `DELETE /api/workbooks/{id}/` - Delete workbook

#### Sheets
- `GET /api/workbooks/{id}/sheets/` - List sheets in workbook
- `GET /api/sheets/{id}/` - Get sheet details
- `GET /api/sheets/{id}/data/` - Get sheet data (supports filtering)

#### Processing
- `GET /api/processing/{workbook_id}/status/` - Get processing status
- `POST /api/processing/{workbook_id}/reprocess/` - Reprocess workbook

### Response Formats

All API endpoints return JSON responses with consistent structure:

```json
{
  "success": true,
  "data": {
    // Response data
  },
  "message": "Success message",
  "errors": []
}
```

Error responses include details for troubleshooting:

```json
{
  "success": false,
  "data": null,
  "message": "Error description",
  "errors": [
    {
      "field": "field_name",
      "code": "error_code",
      "message": "Detailed error message"
    }
  ]
}
```

## Deployment

### Docker Deployment

#### Production
```bash
# Configure production environment
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/db
export SECRET_KEY=your-secure-secret-key

# Start production services
docker-compose up -d

# Check service status
docker-compose ps
docker-compose logs web-service
```

#### Scaling
```bash
# Scale web service
docker-compose up -d --scale web-service=3

# Use load balancer for multiple instances
# Configure nginx or similar for load balancing
```

### Manual Deployment

#### Production Setup
```bash
# Install production dependencies
pip install -r requirements-prod.txt

# Configure environment variables
export ENVIRONMENT=production
export DEBUG=False
export DATABASE_URL=postgresql://user:pass@host:5432/db

# Collect static files
python manage.py collectstatic --noinput

# Run database migrations
python manage.py migrate

# Start with Gunicorn
gunicorn excel_analyzing.web.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120
```

## Contributing

We welcome contributions! Please follow these guidelines:

### Contribution Process

1. **Fork the Repository**
   - Create your own fork on GitHub
   - Clone your fork locally

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/description
   ```

3. **Make Changes**
   - Follow existing code patterns
   - Add tests for new functionality
   - Update documentation

4. **Quality Checks**
   ```bash
   # Run formatting
   black excel_analyzing/
   isort excel_analyzing/
   
   # Run linting
   flake8 excel_analyzing/
   mypy excel_analyzing/
   
   # Run tests
   pytest
   ```

5. **Submit Pull Request**
   - Clear description of changes
   - Reference related issues
   - Ensure CI passes

### Code Standards

- **PEP8 Compliance**: Use Black for formatting
- **Type Hints**: Add type annotations for public functions
- **Documentation**: Document public APIs with docstrings
- **Testing**: Include tests for new functionality
- **Commit Messages**: Use conventional commit format

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

For questions and support:

- **GitHub Issues**: Report bugs and request features
- **Documentation**: Check the `/docs` directory for detailed guides
- **Examples**: Review test files for usage examples

### Common Issues

1. **Database Connection**: Ensure PostgreSQL is running and accessible
2. **File Processing**: Check file permissions and format support
3. **Memory Usage**: Large Excel files may require increased memory limits
4. **Docker Issues**: Verify Docker and docker-compose installation

For additional help, please create an issue with:
- System information (OS, Python version)
- Error messages and stack traces
- Steps to reproduce the issue
- Expected vs actual behavior