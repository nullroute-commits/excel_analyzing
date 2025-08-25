# Developer Guide

## Architecture Overview

Excel Analyzing implements a **containerized microservices architecture** designed for scalable Excel workbook processing with modern DevOps practices.

### System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Excel Analyzing Platform                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   Client Layer                 API Gateway               Load Balancer      │
│  ┌─────────────┐    ┌─────────────────┐    ┌─────────────────┐            │
│  │ Web Browser │◄──►│ Nginx Reverse   │◄──►│ Docker Compose  │            │
│  │ CLI Tools   │    │ Proxy & SSL     │    │ Load Balancing  │            │
│  │ API Clients │    │ (Alpine)        │    │ (Multi-replica) │            │
│  └─────────────┘    └─────────────────┘    └─────────────────┘            │
│                               │                                             │
│   Application Services        ▼                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │   │
│  │  │ Web Service │  │Worker Service│  │CLI Interface│  │Processing│   │   │
│  │  │ (Django)    │  │(Background) │  │  (Click)    │  │  Engine  │   │   │
│  │  │  REST API   │◄►│  Pipeline   │◄►│Rich Output  │◄►│ (Pandas) │   │   │
│  │  │  Web UI     │  │ Orchestrator│  │   Async     │  │  Core    │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘   │   │
│  └─────────────────────────────┬───────────────────────────────────────┘   │
│                                │                                           │
│   Persistence & Caching       ▼                                           │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                                                                     │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐   │   │
│  │  │PostgreSQL DB│  │Redis Cache  │  │File Storage │  │Log Store │   │   │
│  │  │ (Metadata)  │  │(Sessions/   │  │ (Volumes)   │  │(Volumes) │   │   │
│  │  │ Alpine Base │  │ Task Queue) │  │ Excel Files │  │ App Logs │   │   │
│  │  │ Persistence │  │Alpine Base  │  │   Static    │  │ Metrics  │   │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Service Discovery & Communication

**Hostname-Based Architecture**: All services communicate using environment-specific hostnames:

```
Service Communication Pattern:
├── Development Environment
│   ├── dev-web-service:8000      # Django application
│   ├── dev-db-service:5432       # PostgreSQL database
│   ├── dev-cache-service:6379    # Redis cache
│   └── dev-worker-service        # Background processing
├── Test Environment
│   ├── test-web-service:8000     # Test Django instance
│   ├── test-db-service:5432      # Isolated test database
│   ├── test-cache-service:6379   # Test cache instance
│   └── test-worker-service       # Test background jobs
└── Production Environment
    ├── prod-web-service:8000     # Production Django
    ├── prod-db-service:5432      # Production database
    ├── prod-cache-service:6379   # Production cache
    ├── prod-worker-service       # Production background jobs
    └── prod-nginx-service:80/443 # Reverse proxy
```

### Container Strategy & Technology Stack

**Multi-Stage Alpine Containers**:
```dockerfile
# Build Strategy
Base Layer (python:3.12-alpine)
    ├── System dependencies (gcc, musl-dev, postgresql-dev)
    ├── Security updates and hardening
    └── Alpine package manager (apk)

Dependencies Layer
    ├── Python packages (pandas, django, pydantic)
    ├── Compiled extensions (psycopg2, numpy)
    └── Development vs production dependencies

Application Layer  
    ├── Source code integration
    ├── Static file compilation
    └── Configuration validation

Production Layer
    ├── Non-root user (excel:excel)
    ├── Health check implementation
    ├── Minimal runtime dependencies
    └── Security hardening
```

### Configuration Management Architecture

#### Centralized Environment Configuration

**Sophisticated Configuration System**: The application implements a **hierarchical configuration loading system** with environment-specific overrides:

```
Configuration Loading Hierarchy (Priority: High → Low):
├── 1. Environment Variables (OS level)
│   ├── ENVIRONMENT=development|test|production
│   ├── DATABASE_HOST=service-hostname  
│   └── Direct environment overrides
├── 2. Service-Specific Configuration Files
│   ├── env/web/django/.env.{environment}
│   ├── env/database/postgresql/.env.{environment}
│   ├── env/cache/redis/.env.{environment}
│   └── env/processing/core/.env.{environment}
├── 3. Global Configuration
│   └── .env (root-level overrides)
└── 4. Application Defaults
    └── Hardcoded defaults in core/config.py
```

**Dynamic Configuration Loading Process**:
```python
# Automatic environment-based configuration loading
def get_settings() -> Settings:
    env = os.getenv("ENVIRONMENT", "development")
    
    # Load environment-specific configuration files
    config_files = [
        f"env/web/django/.env.{env}",
        f"env/database/postgresql/.env.{env}", 
        f"env/cache/redis/.env.{env}",
        f"env/processing/core/.env.{env}",
        ".env"  # Root overrides
    ]
    
    # Dynamic hostname generation
    settings.database_host = f"{env}-db-service"
    settings.redis_host = f"{env}-cache-service"
    settings.allowed_hosts = [f"{env}-web-service", "localhost"]
    
    return settings
```

#### Configuration Schema & Validation

**Pydantic-Based Validation**:
```python
class Settings(BaseSettings):
    # Application Configuration
    app_name: str = "Excel Analyzing"
    debug: bool = False
    environment: Environment = Environment.DEVELOPMENT
    
    # Service Discovery Configuration
    database_host: str = "db-service"          # Auto-prefixed with environment
    database_port: int = 5432
    redis_host: str = "cache-service"          # Auto-prefixed with environment  
    redis_port: int = 6379
    
    # Processing Configuration
    max_file_size_mb: int = 100
    chunk_size: int = 1000
    max_sheets_per_workbook: int = 50
    processing_timeout: int = 300
    max_concurrent_jobs: int = 4
    
    # Security Configuration
    django_secret_key: str = Field(min_length=50)
    allowed_hosts: List[str] = ["web-service", "localhost"]
    
    # Computed Properties
    @property
    def database_url(self) -> str:
        return f"postgresql://{self.database_user}:{self.database_password}@{self.database_host}:{self.database_port}/{self.database_name}"
```

### Core Components & Technical Implementation

#### Core (`excel_analyzing.core`) - Configuration & Utilities
```python
Core Module Architecture:
├── config.py              # Environment-specific configuration management
│   ├── Settings class with Pydantic validation
│   ├── Dynamic hostname generation
│   ├── Environment-based configuration loading
│   └── Database/Redis URL construction
├── data_types.py          # Type definitions and enums
│   ├── DataType enum (STRING, INTEGER, FLOAT, BOOLEAN, DATETIME, DATE)
│   ├── Environment enum (DEVELOPMENT, TEST, PRODUCTION)
│   └── Processing state enums
├── schema.py              # Schema validation utilities
│   ├── Excel schema validation
│   ├── Column schema detection
│   └── Data integrity checks
└── cleaning.py            # Data cleaning utilities
    ├── Column name normalization
    ├── Data type cleaning
    └── Null value handling
```

#### Models (`excel_analyzing.models`) - Data Layer
```python
Models Architecture:
├── schemas.py             # Pydantic validation models
│   ├── WorkbookInfo       # Workbook metadata validation
│   ├── SheetInfo          # Sheet structure validation  
│   ├── ColumnInfo         # Column metadata validation
│   ├── ProcessingOptions  # Processing configuration
│   └── ProcessingResult   # Processing outcome validation
└── database.py            # SQLAlchemy ORM models
    ├── WorkbookModel       # Database persistence for workbooks
    ├── SheetModel          # Database persistence for sheets
    ├── ColumnModel         # Database persistence for columns
    ├── ProcessingResultModel # Processing results storage
    └── DatabaseManager     # Connection and session management
```

#### Pipeline (`excel_analyzing.pipeline`) - Processing Engine
```python
Pipeline Architecture:
├── processor.py           # Core pandas-based Excel processing
│   ├── ExcelDataProcessor # Main processing class
│   ├── File format detection (xlsx, xls, xlsm, xlsb)
│   ├── Header row detection algorithm
│   ├── Data type inference engine
│   ├── Column cleaning and normalization
│   └── Statistical analysis and profiling
└── orchestrator.py        # High-level pipeline coordination
    ├── ExcelPipeline      # Main orchestration class
    ├── File discovery and validation
    ├── Processing workflow management
    ├── Database integration and persistence
    ├── Error handling and recovery
    └── Progress tracking and reporting
```

#### Web (`excel_analyzing.web`) - Django Application
```python
Web Module Architecture:
├── apps/
│   ├── api/               # REST API implementation
│   │   ├── views.py       # API endpoint implementations
│   │   ├── urls.py        # URL routing configuration
│   │   └── serializers.py # Data serialization (future)
│   ├── workbooks/         # Workbook management interface
│   │   ├── views.py       # Web interface views
│   │   ├── models.py      # Django model wrappers
│   │   ├── management/    # Django management commands
│   │   └── templates/     # HTML templates
│   └── __init__.py
├── settings/              # Environment-specific Django settings
│   ├── base.py           # Shared Django configuration
│   ├── development.py    # Development overrides (DEBUG=True)
│   ├── test.py           # Test environment settings
│   └── production.py     # Production optimizations
├── urls.py               # Root URL configuration
├── wsgi.py               # WSGI application entry point
└── asgi.py               # ASGI application (future async support)
```

#### CLI (`excel_analyzing.cli`) - Command Line Interface
```python
CLI Architecture:
├── Rich-based terminal interface with progress bars
├── Click command group structure:
│   ├── init-db           # Database initialization
│   ├── reset-db          # Database reset with confirmation
│   ├── process           # Batch file processing
│   ├── analyze           # Single file analysis
│   ├── list-workbooks    # Database query interface
│   └── query             # Data querying with pandas syntax
├── Comprehensive error handling and user feedback
├── Logging integration with file and console output
└── Progress tracking for long-running operations
```

## Development Setup

### Prerequisites

- **Python 3.10+** (Required - see pyproject.toml for exact version requirements)
- **Docker & Docker Compose** (Recommended for consistent development environment)
- **PostgreSQL 12+** (If running locally without Docker)
- **Redis 6+** (If running locally without Docker)
- **Git** (For version control and pre-commit hooks)

### Environment Configuration Options

#### Option 1: Docker Compose Development (Recommended)

**Quick Start**:
```bash
# Clone repository
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing

# Start complete development environment
docker-compose -f docker-compose.dev.yml up -d

# View service logs
docker-compose -f docker-compose.dev.yml logs -f web-service

# Access development environment
# Web: http://localhost:8000
# API: http://localhost:8000/api/
# Database: localhost:5432 (from host)
```

**Development Environment Features**:
- **Hot Reloading**: Code changes automatically reflected
- **Volume Mounts**: Local code mounted into containers
- **Debug Mode**: Django debug mode enabled
- **Service Discovery**: `dev-*-service` hostnames
- **Isolated Networking**: Services communicate via Docker network

#### Option 2: Local Development Environment

**Setup Process**:
```bash
# Clone and create virtual environment
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with development dependencies
pip install -e ".[dev,test]"

# Configure environment
export ENVIRONMENT=development
export DATABASE_HOST=localhost  # For local PostgreSQL
export REDIS_HOST=localhost     # For local Redis

# Setup local database (requires PostgreSQL running)
createdb excel_analyzing_dev
excel-analyze init-db

# Start Redis (macOS with Homebrew)
brew services start redis
# Or Linux with systemd
sudo systemctl start redis

# Run development server
python manage.py runserver 0.0.0.0:8000
```

#### Option 3: Hybrid Development (Docker Services + Local App)

**Use Case**: When you want to run the application locally but use containerized services:

```bash
# Start only the services (database, cache)
docker-compose -f docker-compose.dev.yml up -d db-service cache-service

# Configure local app to use containerized services
export ENVIRONMENT=development
export DATABASE_HOST=localhost
export DATABASE_PORT=5432
export REDIS_HOST=localhost  
export REDIS_PORT=6379

# Install and run locally
pip install -e ".[dev,test]"
excel-analyze init-db
python manage.py runserver
```

### Environment-Specific Development

#### Development Environment Configuration
- **Services**: `dev-web-service:8000`, `dev-db-service:5432`, `dev-cache-service:6379`
- **Configuration Files**: `env/*/development/` directory
- **Features**:
  - Django DEBUG mode enabled
  - Hot reloading for code changes
  - Volume mounts for live development
  - Verbose logging and error pages
  - Development-specific database with sample data

#### Test Environment Configuration
- **Services**: `test-web-service:8000`, `test-db-service:5432`, `test-cache-service:6379`
- **Configuration Files**: `env/*/test/` directory  
- **Features**:
  - Isolated test database (separate from development)
  - Test-specific configuration optimizations
  - Faster container startup for CI/CD
  - Memory-optimized settings for testing
  - Comprehensive test data fixtures

#### Production Environment Configuration
- **Services**: `prod-web-service:8000`, `prod-db-service:5432`, `prod-cache-service:6379`, `prod-nginx-service:80/443`
- **Configuration Files**: `env/*/production/` directory
- **Features**:
  - Security hardening (non-root containers, minimal packages)
  - Performance optimizations (connection pooling, caching)
  - SSL/HTTPS configuration
  - Health checks and monitoring
  - Resource limits and auto-scaling

## Development Workflow

### Code Development Cycle

**1. Feature Development Workflow**:
```bash
# Create feature branch
git checkout -b feature/excel-processing-enhancement

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Make code changes with hot reloading
# Edit files in excel_analyzing/ directory

# Run tests during development
pytest tests/unit/ -v
python run_tests.py --unit --coverage

# Check code quality
black excel_analyzing/
flake8 excel_analyzing/
mypy excel_analyzing/

# Test API endpoints
curl -X GET http://localhost:8000/api/workbooks/
curl -X POST http://localhost:8000/api/workbooks/ -F "file=@test.xlsx"

# Test CLI commands
excel-analyze process tests/fixtures/ --recursive
excel-analyze analyze tests/fixtures/sample.xlsx
```

**2. Testing & Quality Assurance**:
```bash
# Run comprehensive test suite
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit --integration
python run_tests.py --security --performance
python run_tests.py --regression --e2e

# Run architecture validation
python test_architecture.py

# Generate coverage reports
pytest --cov=excel_analyzing --cov-report=html
open htmlcov/index.html  # View coverage report
```

**3. Docker Development Workflow**:
```bash
# Build development image
docker build -f Dockerfile.dev -t excel-analyzing:dev .

# Test production build locally
docker build -t excel-analyzing:prod .
docker run -d -p 8000:8000 excel-analyzing:prod

# Test multi-environment deployment
docker-compose -f docker-compose.test.yml up -d
docker-compose -f docker-compose.yml up -d  # Production
```

### Database Development

**Database Schema Management**:
```bash
# Initialize database
excel-analyze init-db

# Reset database with confirmation
excel-analyze reset-db --confirm

# Manual database operations
from excel_analyzing.models.database import db_manager
session = next(db_manager.get_session())

# Create custom database queries
from excel_analyzing.models.database import WorkbookModel, SheetModel
workbooks = session.query(WorkbookModel).filter_by(file_name='test.xlsx').all()
```

**Database Migration Strategy** (Future Enhancement):
```bash
# Django-style migrations (when implemented)
python manage.py makemigrations
python manage.py migrate

# Manual schema updates
# Direct SQL execution through db_manager
```

### API Development & Testing

**REST API Development**:
```python
# Adding new API endpoints in excel_analyzing/web/apps/api/views.py
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def custom_endpoint(request):
    # Implementation
    pass

# URL configuration in excel_analyzing/web/apps/api/urls.py
urlpatterns = [
    path('custom/', views.custom_endpoint, name='custom-endpoint'),
]
```

**API Testing**:
```bash
# Manual API testing
curl -X GET http://localhost:8000/api/workbooks/ -H "Content-Type: application/json"

# Automated API testing
pytest tests/integration/test_api.py -v

# Load testing (future enhancement)
# locust -f tests/performance/locustfile.py --host=http://localhost:8000
```

### CLI Development

**CLI Command Development**:
```python
# Adding new CLI commands in excel_analyzing/cli.py
@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--option', help='Custom option')
def new_command(path, option):
    """New command description."""
    # Implementation
    pass
```

**CLI Testing**:
```bash
# Test CLI commands
excel-analyze --help
excel-analyze process --help
excel-analyze analyze tests/fixtures/sample.xlsx

# Test CLI with different environments
ENVIRONMENT=test excel-analyze process tests/fixtures/
ENVIRONMENT=production excel-analyze list-workbooks
```

## Code Standards & Quality

### Code Style Guide

**PEP8 Compliance with Modern Enhancements**:
- **Line Length**: 88 characters (Black default for better readability)
- **String Quotes**: Double quotes preferred for consistency
- **Import Organization**: isort with Black-compatible profile
- **Type Hints**: Required for public functions and class methods
- **Docstrings**: Google-style docstrings for all public APIs

### Code Quality Tools & Automation

#### Automated Code Formatting
```bash
# Black: Uncompromising Python code formatter
black excel_analyzing/ tests/
black --check excel_analyzing/  # Check without modifying

# isort: Import statement organizer
isort excel_analyzing/ tests/
isort --check-only excel_analyzing/  # Check without modifying

# Combined formatting
black excel_analyzing/ && isort excel_analyzing/
```

#### Code Linting & Analysis
```bash
# Flake8: Style guide enforcement
flake8 excel_analyzing/
flake8 --statistics excel_analyzing/  # Show error statistics

# mypy: Static type checking
mypy excel_analyzing/
mypy --strict excel_analyzing/  # Strict type checking

# Combined linting
flake8 excel_analyzing/ && mypy excel_analyzing/
```

#### Pre-commit Hooks Integration
```bash
# Install pre-commit hooks (one-time setup)
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate

# Pre-commit configuration (.pre-commit-config.yaml):
# - Black formatting
# - isort import sorting  
# - Flake8 linting
# - mypy type checking
# - Security scanning with bandit
```

#### Testing & Coverage
```bash
# Unit tests with pytest
pytest tests/unit/ -v
pytest tests/unit/ --tb=short  # Shorter traceback format

# Integration tests
pytest tests/integration/ -v

# Coverage analysis
pytest --cov=excel_analyzing --cov-report=html
pytest --cov=excel_analyzing --cov-report=term-missing

# Performance testing
pytest tests/performance/ -v --benchmark-only

# Security testing
pytest tests/security/ -v

# Comprehensive test runner
python run_tests.py --all --coverage
python run_tests.py --unit --integration --lint
```

### Development Tools Configuration

#### IDE/Editor Configuration

**VS Code Settings** (`.vscode/settings.json`):
```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.formatting.provider": "black",
    "python.sortImports.args": ["--profile", "black"],
    "[python]": {
        "editor.formatOnSave": true,
        "editor.codeActionsOnSave": {
            "source.organizeImports": true
        }
    }
}
```

**PyCharm Configuration**:
- Black integration for formatting
- isort for import organization
- Flake8 and mypy as external tools
- Django integration for web development
- Docker Compose integration

#### Git Hooks & Version Control

**Git Configuration**:
```bash
# Setup git hooks
git config core.hooksPath .githooks

# Conventional commit messages
git commit -m "feat: add Excel type inference engine"
git commit -m "fix: resolve database connection timeout"
git commit -m "docs: update API documentation"
git commit -m "test: add unit tests for data processor"
```

**Branch Naming Conventions**:
- `feature/description` - New features
- `bugfix/description` - Bug fixes
- `hotfix/description` - Critical production fixes
- `docs/description` - Documentation updates
- `refactor/description` - Code refactoring
- `test/description` - Test additions/improvements
python run_tests.py --e2e --headed --video

# Using pytest directly
pytest tests/unit/ -v
pytest tests/integration/ -v --tb=short
pytest tests/security/ -v
pytest tests/performance/ -v --benchmark-json=benchmark.json
pytest tests/regression/ -v
pytest tests/e2e/ -v

# Using tox for multiple environments
tox -e py311,integration,security
tox -e performance
tox -e e2e

# With coverage
pytest --cov=excel_analyzing --cov-report=html

# Specific test files
pytest tests/unit/test_models.py
pytest tests/integration/test_pipeline_integration.py

# Integration tests
pytest tests/integration/

# Security tests
pytest tests/security/
bandit -r excel_analyzing/
safety check

# Performance benchmarking
pytest tests/performance/ --benchmark-json=benchmark.json
```

## Adding New Features

### 1. Data Models

#### Pydantic Schemas
Add validation models in `models/schemas.py`:

```python
from pydantic import BaseModel, Field, validator

class NewDataModel(BaseModel):
    """Description of the model."""
    
    name: str = Field(..., description="Field description")
    value: int = Field(ge=0, description="Non-negative integer")
    
    @validator("name")
    def validate_name(cls, v: str) -> str:
        """Custom validation logic."""
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()
```

#### SQLAlchemy Models
Add database models in `models/database.py`:

```python
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

class NewDatabaseModel(Base):
    """Database model description."""
    
    __tablename__ = "new_table"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self) -> str:
        return f"<NewDatabaseModel(id={self.id}, name='{self.name}')>"
```

### 2. Processing Logic

#### Extending the Processor
Add new processing methods to `pipeline/processor.py`:

```python
class ExcelDataProcessor:
    def new_processing_method(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add new data processing capability."""
        # Implementation here
        return processed_df
```

#### Pipeline Integration
Update `pipeline/orchestrator.py` to use new functionality:

```python
class ExcelPipeline:
    def new_pipeline_step(self, workbook_info: WorkbookInfo) -> ProcessingResult:
        """Add new pipeline step."""
        # Implementation here
        return result
```

### 3. Web Interface

#### Django Apps
Create new Django apps in `web/apps/`:

```bash
mkdir -p excel_analyzing/web/apps/new_app
```

#### Views
Add views in `web/apps/new_app/views.py`:

```python
from django.views.generic import ListView
from rest_framework.viewsets import ModelViewSet

class NewModelViewSet(ModelViewSet):
    """API viewset for new model."""
    
    queryset = NewDatabaseModel.objects.all()
    serializer_class = NewModelSerializer
```

#### URLs
Add URL patterns in `web/apps/new_app/urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'new-models', views.NewModelViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
```

### 4. CLI Commands

Add new commands in `cli.py`:

```python
@cli.command()
@click.argument('input_path', type=click.Path(exists=True))
@click.option('--option', default='value', help='Option description')
def new_command(input_path: str, option: str) -> None:
    """Description of new command."""
    # Implementation here
    console.print(f"Executed with {input_path} and {option}")
```

### 5. Tests

#### Unit Tests
Add tests in `tests/unit/test_new_feature.py`:

```python
import pytest
from excel_analyzing.models.schemas import NewDataModel

class TestNewDataModel:
    """Test the new data model."""
    
    def test_model_creation(self):
        """Test creating model instance."""
        model = NewDataModel(name="test", value=42)
        assert model.name == "test"
        assert model.value == 42
    
    def test_validation(self):
        """Test model validation."""
        with pytest.raises(ValueError):
            NewDataModel(name="", value=42)
```

#### Integration Tests
Add tests in `tests/integration/test_new_feature_integration.py`:

```python
import pytest
from excel_analyzing.pipeline.orchestrator import ExcelPipeline

class TestNewFeatureIntegration:
    """Test new feature integration."""
    
    def test_end_to_end_workflow(self, sample_excel_file):
        """Test complete workflow with new feature."""
        pipeline = ExcelPipeline()
        result = pipeline.process_workbook(sample_excel_file)
        assert result.success
```

## Database Migrations

### Django Migrations
```bash
# Create migration
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

### SQLAlchemy Schema Changes
```python
# In models/database.py, update the model
# Then run:
from excel_analyzing.models.database import db_manager

# Drop and recreate (development only)
db_manager.drop_tables()
db_manager.create_tables()
```

## Performance Optimization

### Database Optimization

#### Indexing
```python
# Add indexes to frequently queried columns
class WorkbookModel(Base):
    __tablename__ = "workbooks"
    
    file_path = Column(String(1000), nullable=False, unique=True, index=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), index=True)
```

#### Query Optimization
```python
# Use select_related and prefetch_related
workbooks = WorkbookModel.objects.select_related('sheets').prefetch_related('sheets__columns')
```

### Memory Optimization

#### Chunked Processing
```python
def process_large_file(file_path: Path, chunk_size: int = 10000):
    """Process large files in chunks."""
    for chunk in pd.read_excel(file_path, chunksize=chunk_size):
        # Process chunk
        yield process_chunk(chunk)
```

#### Memory Profiling
```python
# Add memory profiling
from memory_profiler import profile

@profile
def memory_intensive_function():
    # Function implementation
    pass
```

## Testing Strategy

### Test Categories

#### Unit Tests
- Test individual functions/methods
- Mock external dependencies
- Fast execution (< 1s per test)
- Location: `tests/unit/`

#### Integration Tests
- Test component interactions
- Use test database
- Moderate execution time
- Location: `tests/integration/`

#### Regression Tests
- Ensure changes don't break existing functionality
- Compare against baselines
- Detect performance regressions
- Location: `tests/regression/`

#### Security Tests
- Input sanitization and validation
- Authentication/authorization testing
- Vulnerability scanning
- Location: `tests/security/`

#### Performance Tests
- Monitor execution time and memory usage
- Benchmark critical operations
- Scalability testing
- Location: `tests/performance/`

#### End-to-End Tests
- Test complete workflows
- Browser automation with Playwright
- User journey validation
- Location: `tests/e2e/`

### Test Data

#### Creating Test Files
```python
import pandas as pd
from pathlib import Path

def create_test_excel(path: Path, sheets: dict):
    """Create test Excel file with specified sheets."""
    with pd.ExcelWriter(path) as writer:
        for sheet_name, data in sheets.items():
            df = pd.DataFrame(data)
            df.to_excel(writer, sheet_name=sheet_name, index=False)
```

#### Fixtures
```python
@pytest.fixture
def sample_workbook(tmp_path):
    """Create sample workbook for testing."""
    file_path = tmp_path / "test.xlsx"
    create_test_excel(file_path, {
        "Sheet1": {
            "Name": ["Alice", "Bob", "Charlie"],
            "Age": [25, 30, 35],
            "Salary": [50000, 60000, 70000]
        }
    })
    return file_path
```

## Deployment

### Environment Setup

All environments use hostname-based service discovery and centralized configuration management.

#### Development
```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# Environment automatically loads from:
# - env/web/django/.env.development
# - env/database/postgresql/.env.development  
# - env/cache/redis/.env.development
# - env/processing/core/.env.development
```

#### Test  
```bash
# Start test environment
docker-compose -f docker-compose.test.yml up -d

# Run tests
docker-compose -f docker-compose.test.yml exec web-service python -m pytest
```

#### Production
```bash
# Set production secrets
export DATABASE_PASSWORD=your-secure-password
export DJANGO_SECRET_KEY=your-secure-secret-key
export REDIS_PASSWORD=your-redis-password

# Start production environment
docker-compose up -d

# Environment automatically loads from:
# - env/web/django/.env.production
# - env/database/postgresql/.env.production
# - env/cache/redis/.env.production
# - env/processing/core/.env.production
```

### Docker Deployment

#### Build Images

**Development Image (Alpine-based)**
```bash
docker build -f Dockerfile.dev -t excel-analyzing:dev .
```

**Test Image (Alpine-based)**
```bash
docker build -f Dockerfile.test -t excel-analyzing:test .
```

**Production Image (Alpine-based, Multistage)**
```bash
docker build -t excel-analyzing:latest .
```

#### Container Architecture
- **Base Images**: All containers use Alpine Linux for minimal size
- **Multistage Builds**: Production builds use multistage pattern for better caching
- **Security**: Non-root users, minimal attack surface
- **Networking**: Isolated Docker networks per environment

### Service Discovery

Each environment uses hostname-based service discovery:

| Environment | Web Service | Database Service | Cache Service |
|------------|-------------|------------------|---------------|
| Development | `dev-web-service:8000` | `dev-db-service:5432` | `dev-cache-service:6379` |
| Test | `test-web-service:8000` | `test-db-service:5432` | `test-cache-service:6379` |
| Production | `prod-web-service:8000` | `prod-db-service:5432` | `prod-cache-service:6379` |

### Monitoring

#### Logging
```python
import logging
from excel_analyzing.utils.logging import get_logger

logger = get_logger(__name__)

def monitored_function():
    logger.info("Function started")
    try:
        # Function logic
        logger.info("Function completed successfully")
    except Exception as e:
        logger.error(f"Function failed: {e}")
        raise
```

#### Metrics
```python
import time
from excel_analyzing.utils.logging import log_execution_time

@log_execution_time
def timed_function():
    """Function with automatic timing."""
    time.sleep(1)  # Simulated work
```

## Contributing

### Pull Request Process

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/new-feature
   ```

2. **Make Changes**
   - Follow code standards
   - Add tests
   - Update documentation

3. **Run Quality Checks**
   ```bash
   pre-commit run --all-files
   pytest
   ```

4. **Submit PR**
   - Clear description
   - Link to issues
   - Request reviews

### Code Review Guidelines

#### For Authors
- Keep PRs focused and small
- Write clear commit messages
- Add appropriate tests
- Update documentation

#### For Reviewers
- Review for correctness
- Check test coverage
- Verify documentation updates
- Suggest improvements

### Release Process

1. **Update Version**
   ```bash
   # In pyproject.toml
   version = "1.2.0"
   ```

2. **Update Changelog**
   ```markdown
   ## [1.2.0] - 2024-01-15
   ### Added
   - New feature X
   ### Changed
   - Improved Y
   ### Fixed
   - Bug Z
   ```

3. **Create Release**
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

## Troubleshooting

### Common Development Issues

#### Import Errors
```bash
# Ensure package is installed in development mode
pip install -e .
```

#### Database Issues
```bash
# Reset database
excel-analyze reset-db --confirm
excel-analyze init-db
```

#### Test Failures
```bash
# Run specific test with verbose output
pytest -xvs tests/unit/test_specific.py::test_function
```

### Performance Issues

#### Memory Leaks
```python
# Use memory profiling
pip install memory-profiler
python -m memory_profiler script.py
```

#### Slow Queries
```python
# Enable SQL logging in Django
LOGGING = {
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```