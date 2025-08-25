# Excel Analyzing

A comprehensive Python pipeline for analyzing Excel workbooks like databases, treating workbooks as databases and sheets as tables. Built with PEP8 standards and object-oriented design principles.

## Features

- **Excel Processing Pipeline**: Recursively discover and process Excel workbooks (.xlsx, .xls, .xlsm, .xlsb)
- **Database-like Treatment**: Treat workbooks as databases and sheets as tables with proper schema detection
- **Data Type Inference**: Automatically detect column data types (string, integer, float, boolean, datetime, date)
- **Data Cleaning**: Drop empty rows/columns, clean column names, handle null values
- **Multiple Environments**: Development, test, and production configurations
- **Web Interface**: Django-based web interface for managing and querying data
- **REST API**: RESTful API for programmatic access
- **Command Line Interface**: Rich CLI for batch processing and analysis
- **Database Storage**: PostgreSQL backend with SQLAlchemy ORM
- **Validation**: Pydantic models for data validation and serialization
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Detailed markdown documentation

## Architecture

The project implements a **containerized microservices architecture** with hostname-based service discovery:

```
excel_analyzing/
├── core/              # Configuration management and settings
│   ├── config.py      # Environment-specific configuration loading
│   ├── data_types.py  # Data type definitions and enums
│   ├── schema.py      # Schema validation utilities
│   └── cleaning.py    # Data cleaning utilities
├── models/            # Data models and persistence
│   ├── schemas.py     # Pydantic models for validation
│   └── database.py    # SQLAlchemy ORM models and database management
├── pipeline/          # Excel processing pipeline
│   ├── processor.py   # Pandas-based Excel data processing engine
│   └── orchestrator.py # Pipeline orchestration and database integration
├── web/               # Django web application
│   ├── apps/api/      # REST API endpoints
│   ├── apps/workbooks/ # Workbook management interface
│   ├── settings/      # Environment-specific Django settings
│   └── urls.py        # URL routing configuration
├── utils/             # Shared utility functions
└── cli.py             # Rich CLI with comprehensive commands
```

### Service Architecture (Containerized)

```
Production Environment:
┌─────────────────────┐    ┌─────────────────────┐    ┌─────────────────────┐
│   prod-web-service  │◄──►│  prod-db-service    │◄──►│ prod-cache-service  │
│   (Django/Alpine)   │    │ (PostgreSQL/Alpine) │    │   (Redis/Alpine)    │
└─────────────────────┘    └─────────────────────┘    └─────────────────────┘
           │
           ▼
┌─────────────────────┐    ┌─────────────────────┐
│ prod-worker-service │    │ prod-nginx-service  │
│  (Celery/Alpine)    │    │   (Nginx/Alpine)    │
└─────────────────────┘    └─────────────────────┘
```

### Configuration Management

The application uses **centralized environment-specific configuration** organized under `/env/service/subservice/`:

- **Dynamic Loading**: Configuration automatically loads based on `ENVIRONMENT` variable
- **Hostname-Based Services**: Uses service discovery (e.g., `prod-web-service`, `dev-db-service`)
- **Multi-Environment Support**: development, test, production with isolated configurations

## Technologies Used

- **Python 3.10+**: Core programming language (requires 3.10+ as per pyproject.toml)
- **Pandas**: Data manipulation and analysis engine for Excel processing
- **OpenPyXL**: Modern Excel file (.xlsx, .xlsm) reading and writing
- **xlrd**: Legacy Excel file (.xls) support
- **Pydantic**: Data validation, serialization, and settings management
- **SQLAlchemy**: Database ORM with async support
- **PostgreSQL**: Primary database with hostname-based service discovery
- **Redis**: Cache service for session management and task queuing
- **Django 5.2+**: Web framework with modern async capabilities
- **Django REST Framework**: API development with comprehensive endpoints
- **Click**: Command line interface with rich terminal output
- **Rich**: Terminal formatting and progress indicators
- **Docker**: Containerized deployment with Alpine Linux base images
- **Gunicorn**: WSGI server for production deployment
- **pytest**: Comprehensive testing framework with multiple test categories
- **Black**: Code formatting with 88-character line length
- **Flake8**: Code linting and style enforcement
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality

## Installation

### Prerequisites

- **Python 3.10+** (Required - see pyproject.toml)
- **PostgreSQL 12+** or containerized database service
- **Redis** (for caching and session management)
- **Docker & Docker Compose** (for containerized deployment)
- **Git** (for version control)

### Development Setup

1. **Clone the repository**:
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
# Development with all optional dependencies
pip install -e ".[dev,test]"

# Or install from requirements files
pip install -r requirements-dev.txt
```

4. **Set up environment configuration**:
```bash
# The application uses structured environment configuration
# Example environment files are in env/*/
export ENVIRONMENT=development  # or test, production
```

5. **Initialize the database**:
```bash
# Using the CLI tool
excel-analyze init-db

# Or reset if needed
excel-analyze reset-db --confirm
```

6. **Start development services** (choose one):

   **Option A: Docker Compose (Recommended)**
   ```bash
   docker-compose -f docker-compose.dev.yml up -d
   ```

   **Option B: Local Development**
   ```bash
   # Start Django development server
   python manage.py runserver
   
   # In another terminal, start worker processes if needed
   excel-analyze process /path/to/excel/files --recursive
   ```

### Production Setup

1. **Deploy with Docker Compose** (Recommended):
```bash
# Production deployment with all services
docker-compose up -d

# This starts:
# - prod-web-service (Django app)
# - prod-db-service (PostgreSQL)
# - prod-cache-service (Redis)
# - prod-nginx-service (Nginx reverse proxy)
# - prod-worker-service (Background processing)
```

2. **Manual Installation**:
```bash
# Install production dependencies
pip install -e ".[prod]"

# Set up environment variables for production
export ENVIRONMENT=production
export DATABASE_HOST=prod-db-service  # or your PostgreSQL hostname
export REDIS_HOST=prod-cache-service   # or your Redis hostname
export DJANGO_SECRET_KEY=your-secret-key
export DJANGO_ALLOWED_HOSTS=your-domain.com,prod-web-service

# Initialize the database
excel-analyze init-db

# Run with Gunicorn
gunicorn --bind 0.0.0.0:8000 --workers 4 excel_analyzing.web.wsgi:application
```

3. **Environment-Specific Configuration**:
   
   The application automatically loads configurations from:
   ```
   env/web/django/.env.production
   env/database/postgresql/.env.production
   env/cache/redis/.env.production
   env/processing/core/.env.production
   ```

## Usage

### Command Line Interface

The CLI provides comprehensive commands for Excel processing:

**Process Excel files in a directory**:
```bash
excel-analyze process /path/to/excel/files --recursive
```

**Analyze a specific workbook with detailed output**:
```bash
excel-analyze analyze /path/to/workbook.xlsx
```

**Database management**:
```bash
# Initialize database tables
excel-analyze init-db

# Reset database (with confirmation)
excel-analyze reset-db --confirm

# List processed workbooks
excel-analyze list-workbooks
```

**Query data from processed sheets**:
```bash
excel-analyze query workbook_name sheet_name --filter "column > 100" --limit 20
```

**Processing options**:
```bash
excel-analyze process /path/to/files \
  --recursive \
  --drop-empty-rows \
  --drop-empty-columns \
  --clean-column-names \
  --null-threshold 0.8
```

### Python API

**Basic Processing Pipeline**:
```python
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions

# Create pipeline with custom processing options
options = ProcessingOptions(
    drop_empty_rows=True,
    drop_empty_columns=True,
    clean_column_names=True,
    infer_data_types=True,
    null_threshold=0.9,
    max_sample_size=100
)
pipeline = ExcelPipeline(options)

# Process a single workbook
result = pipeline.process_workbook("path/to/workbook.xlsx")
if result.success:
    print(f"Processed {result.rows_processed} rows in {result.processing_time_seconds:.2f}s")
    workbook_info = result.workbook
    for sheet in workbook_info.sheets:
        print(f"Sheet: {sheet.name} ({sheet.row_count} rows, {sheet.column_count} columns)")
else:
    print(f"Processing failed: {result.error_message}")

# Process entire directory
results = pipeline.process_directory("path/to/directory", recursive=True)
successful = [r for r in results if r.success]
print(f"Successfully processed {len(successful)} out of {len(results)} files")
```

**Direct Data Processing**:
```python
from excel_analyzing.pipeline.processor import ExcelDataProcessor
from excel_analyzing.models.schemas import ProcessingOptions

# Initialize processor
processor = ExcelDataProcessor(ProcessingOptions())

# Load and analyze workbook
workbook_info = processor.load_workbook("path/to/file.xlsx")

# Access processed data
df = processor.get_dataframe("filename", "sheet_name")
if df is not None:
    print(df.head())
    
    # Apply filters using pandas query syntax
    filtered_df = processor.apply_filter("filename", "sheet_name", "column_name > 100")
    
    # Get summary statistics
    summary = processor.get_summary_statistics("filename", "sheet_name")
    print(f"Memory usage: {summary['memory_usage_mb']:.2f} MB")
```

**Database Integration**:
```python
from excel_analyzing.models.database import db_manager
from sqlalchemy.orm import Session

# Get database session
session: Session = next(db_manager.get_session())

# Query workbooks directly
from excel_analyzing.models.database import WorkbookModel, SheetModel
workbooks = session.query(WorkbookModel).all()
for wb in workbooks:
    print(f"Workbook: {wb.file_name} ({wb.sheet_count} sheets)")
    for sheet in wb.sheets:
        print(f"  - {sheet.name}: {sheet.row_count} rows")

session.close()
```

### Web Interface

**Development Server**:
```bash
# Start Django development server
python manage.py runserver

# Access the web interface at http://localhost:8000
# API endpoints available at http://localhost:8000/api/
```

**Production Deployment**:
```bash
# Using Docker Compose (includes Nginx reverse proxy)
docker-compose up -d

# Access at configured domain or http://localhost:80
# HTTPS available if SSL certificates configured
```

**API Endpoints**:
- **Workbooks**: `GET/POST /api/workbooks/`
- **Workbook Details**: `GET/PUT/DELETE /api/workbooks/{id}/`
- **Data Queries**: `POST /api/query/`

**Authentication**: API endpoints require authentication except for data queries

## Configuration

### Environment Variables

The application supports **environment-specific configuration** with automatic loading:

| Variable | Description | Default | Environments |
|----------|-------------|---------|-------------|
| `ENVIRONMENT` | Application environment | `development` | development/test/production |
| `DATABASE_HOST` | Database hostname (service discovery) | `db-service` | Environment-specific prefixes |
| `DATABASE_PORT` | Database port | `5432` | All |
| `DATABASE_NAME` | Database name | `excel_analyzing` | All |
| `REDIS_HOST` | Redis hostname (service discovery) | `cache-service` | Environment-specific prefixes |
| `REDIS_PORT` | Redis port | `6379` | All |
| `DJANGO_SECRET_KEY` | Django secret key | Auto-generated | All |
| `DJANGO_ALLOWED_HOSTS` | Comma-separated allowed hosts | `web-service,localhost` | All |
| `DEBUG` | Enable debug mode | `False` | development=True |
| `MAX_FILE_SIZE_MB` | Maximum file size to process (MB) | `100` | All |
| `CHUNK_SIZE` | Processing chunk size | `1000` | All |
| `LOG_LEVEL` | Logging level | `INFO` | All |

### Hostname-Based Service Discovery

The application uses **hostname-based service discovery** for containerized deployments:

| Environment | Web Service | Database Service | Cache Service |
|------------|-------------|------------------|---------------|
| Development | `dev-web-service:8000` | `dev-db-service:5432` | `dev-cache-service:6379` |
| Test | `test-web-service:8000` | `test-db-service:5432` | `test-cache-service:6379` |
| Production | `prod-web-service:8000` | `prod-db-service:5432` | `prod-cache-service:6379` |

### Configuration File Structure

```
env/
├── web/django/           # Django-specific settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
├── database/postgresql/  # Database connection settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
├── cache/redis/         # Redis cache settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
└── processing/core/     # Processing pipeline settings
    ├── .env.development
    ├── .env.test
    └── .env.production
```

### Processing Options

Configure Excel processing behavior:

```python
from excel_analyzing.models.schemas import ProcessingOptions

options = ProcessingOptions(
    drop_empty_rows=True,           # Drop completely empty rows
    drop_empty_columns=True,        # Drop completely empty columns
    infer_data_types=True,          # Automatically infer column data types
    clean_column_names=True,        # Clean and normalize column names
    max_sample_size=100,            # Maximum sample size for type inference
    null_threshold=0.9              # Drop columns with >90% null values
)
```

## Data Pipeline

### Pipeline Architecture

The Excel processing pipeline implements a **4-stage architecture** with comprehensive data handling:

### 1. Discovery & Validation
- **Recursive scanning** of directories for Excel files
- **File type validation**: Supports `.xlsx`, `.xls`, `.xlsm`, `.xlsb` formats
- **Size filtering**: Configurable file size limits (default: 100MB)
- **Temporary file exclusion**: Skips files starting with `~$`
- **Accessibility checks**: Validates file permissions and readability

### 2. Processing & Analysis
- **Workbook metadata extraction** using OpenPyXL and xlrd engines
- **Automatic header detection**: Intelligent row scanning for headers
- **Data type inference**: Automatic detection of string, integer, float, boolean, datetime, date types
- **Column analysis**: Null counts, unique values, sample data extraction
- **Data cleaning pipeline**:
  - Column name normalization (spaces → underscores, special character handling)
  - Sheet name cleaning and validation
  - Empty row/column removal (configurable)
  - Null threshold filtering (configurable percentage)

**Processing Options Configuration**:
```python
ProcessingOptions(
    drop_empty_rows=True,           # Remove completely empty rows
    drop_empty_columns=True,        # Remove completely empty columns
    infer_data_types=True,          # Automatic type detection
    clean_column_names=True,        # Normalize column names
    max_sample_size=100,            # Sample size for type inference
    null_threshold=0.9              # Drop columns with >90% null values
)
```

### 3. Database Storage & Persistence
- **Hierarchical data model**: Workbooks → Sheets → Columns
- **Metadata storage**: File information, processing timestamps, statistics
- **Column schema storage**: Data types, null counts, sample values
- **Processing results tracking**: Success/failure, timing, error messages
- **Incremental updates**: Support for reprocessing and updates

**Database Schema**:
```sql
workbooks (id, file_path, file_name, file_size_bytes, sheet_count, created_at, processed_at)
├── sheets (id, workbook_id, name, original_name, row_count, column_count, has_header, header_row)
│   └── columns (id, sheet_id, name, original_name, position, data_type, null_count, unique_count)
└── processing_results (id, workbook_id, success, error_message, processing_time_seconds)
```

### 4. Querying & Data Access
- **Pandas integration**: Direct DataFrame access for processed data
- **Query capabilities**: SQL-like filtering using pandas query syntax
- **Transformation support**: Grouping, sorting, column selection
- **Export functionality**: Multiple output formats
- **Statistical analysis**: Summary statistics and data profiling

**Query Examples**:
```python
# Filter data using pandas query syntax
df = processor.apply_filter("workbook", "sheet", "column_name > 100 and status == 'active'")

# Apply transformations
transformed = processor.apply_transformation("workbook", "sheet", {
    "operation": "group_by",
    "columns": ["category"],
    "agg_func": "mean"
})

# Get summary statistics
stats = processor.get_summary_statistics("workbook", "sheet")
print(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")
print(f"Numeric columns: {stats['numeric_columns']}")
```

## Testing

The project implements **comprehensive testing infrastructure** with multiple test categories:

### Test Categories

**Run all tests**:
```bash
pytest
```

**Run with coverage reporting**:
```bash
pytest --cov=excel_analyzing --cov-report=html --cov-report=term-missing
```

**Run specific test categories**:
```bash
# Unit tests (fast, isolated)
pytest tests/unit/ -v

# Integration tests (database, service integration)
pytest tests/integration/ -v

# Regression tests (ensure no breaking changes)
pytest tests/regression/ -v

# Security tests (vulnerability scanning)
pytest tests/security/ -v

# Performance tests (benchmarking)
pytest tests/performance/ -v

# End-to-end tests (full workflow)
pytest tests/e2e/ -v

# Architecture validation tests
python test_architecture.py
```

**Run tests by markers**:
```bash
pytest -m "unit"           # Unit tests only
pytest -m "integration"    # Integration tests only
pytest -m "slow"           # Long-running tests
pytest -m "security"       # Security tests only
```

### Testing Infrastructure

**Test Configuration**:
- **pytest** with comprehensive markers and fixtures
- **pytest-django** for Django integration testing
- **pytest-cov** for coverage reporting
- **factory-boy** for test data generation
- **pytest-playwright** for end-to-end browser testing

**Architecture Testing**:
- **Environment configuration validation**
- **Hostname-based service discovery verification**
- **Alpine container usage validation**
- **Docker Compose configuration testing**
- **Multistage Dockerfile verification**

**Coverage Requirements**:
- **Unit test coverage**: >90% target
- **Integration tests**: All environments tested
- **Security tests**: No critical/high vulnerabilities
- **Performance tests**: <10% regression tolerance

### Continuous Integration

**GitHub Actions Workflows**:
- **Comprehensive testing pipeline**: Multi-environment testing
- **Security testing pipeline**: Vulnerability scanning
- **Performance benchmarking**: Automated performance tracking
- **Code quality checks**: Linting, formatting, type checking

## Code Quality

Format code with Black:
```bash
black excel_analyzing/
```

Lint with Flake8:
```bash
flake8 excel_analyzing/
```

Type checking with mypy:
```bash
mypy excel_analyzing/
```

## Deployment

### Containerized Deployment (Recommended)

**Production deployment with Docker Compose**:
```bash
# Start all services in production mode
docker-compose up -d

# Services started:
# - prod-web-service: Django application (port 8000)
# - prod-db-service: PostgreSQL database
# - prod-cache-service: Redis cache
# - prod-nginx-service: Nginx reverse proxy (ports 80/443)
# - prod-worker-service: Background processing
```

**Development deployment**:
```bash
docker-compose -f docker-compose.dev.yml up -d
```

**Test deployment**:
```bash
docker-compose -f docker-compose.test.yml up -d
```

### Docker Architecture

**Multi-stage Dockerfile**:
- **Base stage**: Alpine Linux with system dependencies
- **Dependencies stage**: Python package installation
- **Builder stage**: Application code integration
- **Production stage**: Optimized runtime image

**Security Features**:
- **Non-root user**: Application runs as user `excel`
- **Alpine Linux**: Minimal attack surface
- **Health checks**: Container health monitoring
- **Resource limits**: Memory and CPU constraints

### Manual Deployment

**System requirements**:
```bash
# Install system dependencies
sudo apt-get update
sudo apt-get install python3.10+ postgresql-client redis-tools

# Install application
pip install -e ".[prod]"
```

**Environment setup**:
```bash
export ENVIRONMENT=production
export DATABASE_HOST=your-db-host
export REDIS_HOST=your-redis-host
export DJANGO_SECRET_KEY=your-secret-key
export DJANGO_ALLOWED_HOSTS=your-domain.com
```

**Run with Gunicorn**:
```bash
gunicorn --bind 0.0.0.0:8000 \
         --workers 4 \
         --timeout 120 \
         --worker-class sync \
         excel_analyzing.web.wsgi:application
```

### Load Balancing & Scaling

**Horizontal scaling**:
- Multiple web service replicas
- Shared database and cache
- Nginx load balancing
- Worker service scaling

**Performance optimization**:
- **Static file serving**: Nginx with compression
- **Database connection pooling**: SQLAlchemy pool management
- **Redis caching**: Session and data caching
- **Async processing**: Background task queuing

## API Documentation

### REST API Endpoints

**Base URL**: `http://localhost:8000/api/` (development) or `https://your-domain.com/api/` (production)

**Authentication**: Most endpoints require authentication (Django session or token-based)

#### Workbook Management

**List workbooks**:
```http
GET /api/workbooks/
Authorization: Required
Response: JSON array of workbook objects
```

**Create workbook** (upload and process):
```http
POST /api/workbooks/
Authorization: Required
Content-Type: multipart/form-data
Body: Excel file upload
Response: 201 Created with workbook ID
```

**Get workbook details**:
```http
GET /api/workbooks/{id}/
Authorization: Required
Response: Detailed workbook information with sheets
```

**Update workbook**:
```http
PUT /api/workbooks/{id}/
Authorization: Required
Body: JSON with updated fields
Response: Updated workbook object
```

**Delete workbook**:
```http
DELETE /api/workbooks/{id}/
Authorization: Required
Response: 204 No Content
```

#### Data Querying

**Query sheet data**:
```http
POST /api/query/
Authorization: Not required (for testing)
Content-Type: application/json
Body: {
  "workbook": "workbook_name",
  "sheet": "sheet_name", 
  "filters": {
    "column_name": {"operator": ">", "value": 100},
    "status": {"operator": "==", "value": "active"}
  },
  "limit": 1000,
  "offset": 0
}
Response: {
  "results": [...],
  "count": 1500,
  "filters_applied": {...}
}
```

#### Error Responses

All endpoints return consistent error responses:
```json
{
  "error": "Error description",
  "details": "Additional error details",
  "code": "ERROR_CODE"
}
```

**HTTP Status Codes**:
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Authentication required
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

### WebSocket Events (Future Enhancement)

The application is designed to support real-time updates:

- `workbook.processing.started` - Processing started
- `workbook.processing.progress` - Processing progress update
- `workbook.processing.completed` - Processing completed
- `workbook.processing.failed` - Processing failed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following PEP8 standards
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples
