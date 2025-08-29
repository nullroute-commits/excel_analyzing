# Excel Analyzing: Excel Workbook Data Processing Framework

## Overview

Excel Analyzing is a Python-based data processing pipeline designed to analyze and transform Microsoft Excel workbook files (.xlsx, .xls, .xlsm, .xlsb) into structured database format. The framework treats Excel workbooks as database entities, where individual worksheets function as tables with automatic schema detection and data type inference.

The system follows clean architecture principles with a clear separation between core business logic, data access, and user interfaces. It provides both command-line and web interfaces for processing Excel files.

## Features

### Core Data Processing
- **Multi-Format Excel Support**: Process Excel workbooks in XLSX, XLS, XLSM, and XLSB formats
- **Database Integration**: Store processed workbook metadata in PostgreSQL with SQLAlchemy ORM
- **Data Type Inference**: Automatically detect and assign appropriate data types to columns
- **Data Cleaning**: Remove empty rows/columns, clean column names, and handle null values
- **Recursive File Discovery**: Scan directories for Excel files with configurable filters

### User Interfaces
- **Command Line Interface**: Click-based CLI with rich formatting for processing operations
- **Web Interface**: Django-based web application for file upload and workbook management
- **REST API**: Simple JSON endpoints for programmatic access to workbook data

### Data Storage & Querying
- **PostgreSQL Backend**: Metadata storage with proper indexing and relationships
- **Query Interface**: SQL-like querying capabilities through pandas integration
- **Data Export**: Export processed data in various formats

### Quality & Testing
- **Unit Tests**: Comprehensive test suite using pytest
- **Integration Tests**: Database and API integration testing
- **Code Quality**: Black formatting, Flake8 linting, and mypy type checking

## Architecture

The application follows a layered architecture with clear separation of concerns:

```text
excel_analyzing/
├── cli.py                   # Command-line interface using Click
├── core/                    # Core business logic and configuration
│   ├── config.py           # Application settings management
│   ├── data_types.py       # Data type inference utilities
│   ├── cleaning.py         # Data cleaning functions
│   └── schema.py           # Schema validation
├── models/                  # Data models and database layer
│   ├── schemas.py          # Pydantic data models
│   └── database.py         # SQLAlchemy ORM models
├── pipeline/                # Data processing pipeline
│   ├── orchestrator.py     # Main processing coordinator
│   └── processor.py        # Excel data processing engine
├── utils/                   # Utility functions
│   ├── files.py            # File handling utilities
│   └── logging.py          # Logging configuration
└── web/                     # Django web application
    ├── apps/               # Django applications
    ├── settings/           # Environment-specific settings
    ├── urls.py             # URL routing
    └── wsgi.py             # WSGI application entry point
```

## Technology Stack

### Core Dependencies
- **Python 3.10+**: Modern Python with type hints and performance improvements
- **Pandas 2.3+**: Data manipulation and analysis
- **Openpyxl 3.1+**: Excel file reading and writing
- **SQLAlchemy 2.0+**: Database ORM and query builder
- **PostgreSQL**: Database backend for metadata storage
- **Pydantic 2.11+**: Data validation and settings management

### Web Framework
- **Django 5.2+**: Web framework with admin interface
- **Django REST Framework 3.16+**: API development toolkit
- **Click 8.2+**: Command-line interface framework
- **Rich 14.1+**: Terminal formatting and progress bars

### Development Tools
- **Pytest 8.4+**: Testing framework
- **Black 25.0+**: Code formatting
- **Flake8 7.2+**: Code linting
- **MyPy 1.14+**: Static type checking
- **Pre-commit 4.1+**: Git hooks for code quality

## Installation & Setup

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 12 or higher
- Git for version control

### Development Setup

1. **Clone the repository**:
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements-dev.txt
pip install -e .
```

4. **Configure environment**:
```bash
cp .env.example .env
# Edit .env file with your database credentials
```

5. **Initialize database**:
```bash
excel-analyze init-db
```

### Docker Setup (Recommended)

Start the development environment:
```bash
docker-compose -f docker-compose.dev.yml up --build
```

This provides:
- Web interface: http://localhost:8000
- API: http://localhost:8000/api/
- PostgreSQL database
- Redis cache (if configured)

## Usage

### Command Line Interface

The CLI provides several commands for processing Excel files:

#### Process Excel Files
```bash
# Process a single file
excel-analyze process /path/to/workbook.xlsx

# Process all Excel files in a directory
excel-analyze process /path/to/excel/files --recursive

# Process with custom options
excel-analyze process /path/to/files \
    --recursive \
    --drop-empty-rows \
    --clean-column-names \
    --null-threshold 0.8
```

#### Analyze Workbooks
```bash
# Get detailed information about a workbook
excel-analyze analyze /path/to/workbook.xlsx

# List all processed workbooks
excel-analyze list-workbooks
```

#### Query Data
```bash
# Query data from a processed workbook
excel-analyze query workbook_name sheet_name

# Query with filter condition
excel-analyze query workbook_name sheet_name --filter "column_name > 100"

# Limit results
excel-analyze query workbook_name sheet_name --limit 50
```

#### Database Management
```bash
# Initialize database tables
excel-analyze init-db

# Reset database (careful - this deletes all data!)
excel-analyze reset-db --confirm
```

### Python API

Use the framework programmatically:

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
pipeline = ExcelPipeline(options)

# Process a single workbook
file_path = Path("/path/to/workbook.xlsx")
result = pipeline.process_workbook(file_path)

if result.success:
    print(f"Processed {result.workbook.file_name}")
    print(f"Sheets: {len(result.workbook.sheets)}")
    print(f"Processing time: {result.processing_time_seconds:.2f}s")
else:
    print(f"Error: {result.error_message}")

# Process directory
results = pipeline.process_directory(Path("/path/to/excel/files"))
successful = [r for r in results if r.success]
print(f"Successfully processed {len(successful)} files")
```

### Web Interface

Start the Django development server:
```bash
python manage.py runserver
```

Access the web interface at http://localhost:8000:
- Upload Excel files through the web interface
- View processed workbooks and their metadata
- Browse sheet data and column information
- Use the admin interface for advanced management

### REST API

The application provides a RESTful API for programmatic access:

#### Endpoints
- `GET /api/workbooks/` - List all processed workbooks
- `POST /api/workbooks/` - Upload and process a new workbook
- `GET /api/workbooks/{id}/` - Get workbook details
- `GET /api/workbooks/{id}/sheets/` - List sheets in a workbook
- `GET /api/sheets/{id}/data/` - Get sheet data
- `POST /api/sheets/{id}/query/` - Query sheet data with filters

#### Example API Usage
```bash
# List workbooks
curl -X GET http://localhost:8000/api/workbooks/

# Upload and process a workbook
curl -X POST -F "file=@workbook.xlsx" http://localhost:8000/api/workbooks/

# Get workbook details
curl -X GET http://localhost:8000/api/workbooks/1/

# Query sheet data
curl -X POST http://localhost:8000/api/sheets/1/query/ \
  -H "Content-Type: application/json" \
  -d '{"filter": "column_name > 100", "limit": 50}'
```

## Configuration

The application uses environment-based configuration with support for multiple deployment environments.

### Environment Variables

Basic configuration is managed through environment variables:

```bash
# Application settings
ENVIRONMENT=development  # development|test|production
DEBUG=True              # Enable debug mode (development only)
DJANGO_SECRET_KEY=your-secret-key

# Database settings
DATABASE_HOST=db-service     # Database hostname
DATABASE_PORT=5432           # Database port
DATABASE_NAME=excel_analyzing
DATABASE_USER=postgres
DATABASE_PASSWORD=password

# Redis cache settings (optional)
REDIS_HOST=cache-service
REDIS_PORT=6379
REDIS_DB=0

# Processing settings
MAX_FILE_SIZE_MB=100        # Maximum file size for processing
CHUNK_SIZE=1000            # Processing chunk size
PROCESSING_TIMEOUT=300     # Timeout in seconds

# Web server settings
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Configuration Files

Environment-specific configuration can be placed in the `env/` directory:

```text
env/
├── web/django/.env.development
├── database/postgresql/.env.development
├── cache/redis/.env.development
└── processing/core/.env.development
```

Example `.env.development`:
```bash
DJANGO_DEBUG=True
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,web-service
DATABASE_HOST=localhost
DATABASE_NAME=excel_analyzing_dev
```

## Data Processing Pipeline

The framework processes Excel files through a multi-stage pipeline:

### 1. File Discovery
- Recursively scan directories for Excel files (.xlsx, .xls, .xlsm, .xlsb)
- Skip temporary files (starting with ~$)
- Validate file accessibility and size limits
- Filter by file patterns and size constraints

### 2. Workbook Processing
- Load workbook metadata using openpyxl/xlrd
- Detect header rows automatically in each sheet
- Clean and normalize sheet names and column names
- Infer appropriate data types for each column
- Remove empty rows and columns based on thresholds
- Handle null values and data quality issues

### 3. Data Storage
- Save workbook metadata to PostgreSQL database
- Store sheet structure and column information
- Track processing results, errors, and performance metrics
- Support for incremental updates and reprocessing

### 4. Data Access
- Query processed data using SQL-like syntax
- Filter and transform data through pandas integration
- Support aggregation and grouping operations
- Export data in multiple formats (CSV, Excel, JSON)

## Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
pytest

# Run with coverage reporting
pytest --cov=excel_analyzing --cov-report=html

# Run specific test categories
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
pytest tests/e2e/          # End-to-end tests
pytest -m performance      # Performance tests
```

### Test Categories
- **Unit Tests**: Test individual components and functions
- **Integration Tests**: Test component interactions and database operations
- **End-to-End Tests**: Test complete workflows through the web interface
- **Performance Tests**: Benchmark processing performance and memory usage
- **Security Tests**: Validate security measures and input sanitization

## Code Quality

The project enforces code quality through automated tools:

```bash
# Format code with Black
black excel_analyzing/

# Lint with Flake8
flake8 excel_analyzing/

# Type checking with mypy
mypy excel_analyzing/

# Run pre-commit hooks
pre-commit run --all-files
```

## Deployment

### Docker Deployment

Build and run with Docker:
```bash
# Build production image
docker build -t excel-analyzing .

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f
```

### Environment-Specific Deployments

The application supports multiple environments:

1. **Development**: Local development with debug enabled
2. **Test**: Automated testing with in-memory database options
3. **Production**: Production deployment with optimized settings and security

Switch environments by setting the `ENVIRONMENT` variable:
```bash
export ENVIRONMENT=production
python manage.py runserver
```

## API Documentation

The application provides RESTful API endpoints for programmatic access. The API supports JSON request/response format and includes proper error handling.

### Authentication
Currently, the API uses Django's session-based authentication. Future versions will include token-based authentication for API access.

### API Endpoints

#### Workbooks
- `GET /api/workbooks/` - List all processed workbooks
- `POST /api/workbooks/` - Upload and process a new workbook
- `GET /api/workbooks/{id}/` - Get detailed workbook information
- `DELETE /api/workbooks/{id}/` - Delete a workbook and its data

#### Sheets
- `GET /api/workbooks/{id}/sheets/` - List sheets in a workbook
- `GET /api/sheets/{id}/` - Get sheet details and metadata
- `GET /api/sheets/{id}/data/` - Get sheet data with pagination

#### Querying
- `POST /api/sheets/{id}/query/` - Query sheet data with filters
- `GET /api/sheets/{id}/columns/` - Get column information

### Example Requests

```bash
# List all workbooks
curl -X GET http://localhost:8000/api/workbooks/

# Upload a workbook
curl -X POST -F "file=@data.xlsx" http://localhost:8000/api/workbooks/

# Get workbook details
curl -X GET http://localhost:8000/api/workbooks/1/

# Query sheet data with filters
curl -X POST http://localhost:8000/api/sheets/1/query/ \
  -H "Content-Type: application/json" \
  -d '{
    "filter": "revenue > 1000", 
    "limit": 100,
    "offset": 0,
    "columns": ["product_name", "revenue", "date"]
  }'
```

## Contributing

We welcome contributions to the Excel Analyzing project. Please follow these guidelines:

### Development Process

1. **Fork the repository** and create a feature branch
2. **Make your changes** following the coding standards
3. **Add tests** for new functionality
4. **Run the test suite** to ensure nothing breaks
5. **Update documentation** if needed
6. **Submit a pull request** with a clear description

### Coding Standards

- Follow PEP 8 style guidelines
- Use type hints for function signatures
- Write docstrings for public functions and classes
- Maintain test coverage above 90%
- Use meaningful variable and function names

### Testing Requirements

- Add unit tests for new functions and methods
- Include integration tests for new features
- Ensure all tests pass before submitting PR
- Update test documentation when needed

### Documentation

- Update README.md for significant changes
- Add docstrings with Google-style formatting
- Include code examples for new features
- Update API documentation for endpoint changes

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

The GPL v3.0 license ensures that:
- The software remains free and open source
- Derivatives must also be open source
- Commercial use is permitted with proper attribution
- No warranty is provided

## Support & Community

### Getting Help

- **Issues**: Report bugs and request features on [GitHub Issues](https://github.com/nullroute-commits/excel_analyzing/issues)
- **Documentation**: Check the comprehensive documentation in the `docs/` directory
- **Examples**: Review example code in the `tests/` directory

### Project Status

This project is actively maintained and under continuous development. We aim to:
- Maintain backward compatibility within major versions
- Provide timely bug fixes and security updates
- Add new features based on community feedback
- Improve performance and scalability

### Roadmap

Future enhancements planned:
- Enhanced REST API with token authentication
- Real-time processing updates via WebSockets
- Advanced data transformation capabilities
- Integration with popular data science tools
- Performance optimizations for large files
- Cloud deployment templates
