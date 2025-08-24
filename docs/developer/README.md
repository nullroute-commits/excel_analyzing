# Developer Guide

# Developer Guide

## Architecture Overview

Excel Analyzing follows a containerized microservices architecture with clear separation of concerns and hostname-based service communication:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Service   │◄──►│  Database Svc   │◄──►│   Cache Service │
│  (web-service)  │    │  (db-service)   │    │ (cache-service) │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ Django REST API │    │ PostgreSQL      │    │ Redis Cache     │
│ Web Interface   │    │ Alpine Based    │    │ Alpine Based    │
│ Alpine Based    │    └─────────────────┘    └─────────────────┘
└─────────────────┘
        │
        ▼
┌─────────────────┐    ┌─────────────────┐
│ Worker Service  │    │ Processing Core │
│(worker-service) │◄──►│   (Internal)    │
├─────────────────┤    ├─────────────────┤
│ Background Jobs │    │ Excel Analysis  │
│ Alpine Based    │    │ Core Logic      │
└─────────────────┘    └─────────────────┘
```

### Service Architecture

#### Hostname-Based Communication
All services communicate using hostnames instead of localhost/IP addresses:
- **Development**: `dev-web-service`, `dev-db-service`, `dev-cache-service`
- **Test**: `test-web-service`, `test-db-service`, `test-cache-service`  
- **Production**: `prod-web-service`, `prod-db-service`, `prod-cache-service`

#### Container Strategy
- **Alpine Base Images**: All containers use Alpine Linux for minimal size
- **Multistage Builds**: Production containers use multistage builds for better caching
- **Environment Separation**: Dedicated Dockerfiles for dev, test, and production

### Configuration Management

#### Centralized Environment Structure
Configuration is organized in `/env/service/subservice/` pattern:

```
env/
├── web/django/           # Web service Django settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
├── database/postgresql/  # Database service settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
├── cache/redis/         # Cache service settings
│   ├── .env.development
│   ├── .env.test
│   └── .env.production
└── processing/core/     # Processing service settings
    ├── .env.development
    ├── .env.test
    └── .env.production
```

#### Dynamic Configuration Loading
The application automatically loads environment-specific configurations based on the `ENVIRONMENT` variable:
- `ENVIRONMENT=development` → loads `.env.development` files
- `ENVIRONMENT=test` → loads `.env.test` files
- `ENVIRONMENT=production` → loads `.env.production` files

### Components

#### Core (`excel_analyzing.core`)
- **Configuration**: Environment-specific settings using Pydantic
- **Base classes**: Common functionality and interfaces

#### Models (`excel_analyzing.models`)
- **Schemas**: Pydantic data validation models
- **Database**: SQLAlchemy ORM models for persistence

#### Pipeline (`excel_analyzing.pipeline`)
- **Processor**: Pandas-based Excel data processing
- **Orchestrator**: High-level pipeline coordination

#### Web (`excel_analyzing.web`)
- **Django**: Web framework setup and configuration
- **Apps**: Modular Django applications
- **APIs**: REST endpoints for programmatic access

#### Utils (`excel_analyzing.utils`)
- **Logging**: Centralized logging configuration
- **Files**: File system utilities and helpers

## Development Setup

### Prerequisites
- Python 3.9+
- Docker & Docker Compose
- Git

### Environment Configuration

#### Quick Start with Docker (Recommended)
```bash
# Clone and setup
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing

# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f
```

#### Local Development (Alternative)
```bash
# Clone and setup
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-dev.txt
pip install -e .

# Set environment
export ENVIRONMENT=development

# Setup database (requires PostgreSQL running)
createdb excel_analyzing_dev
excel-analyze init-db

# Run development server
python manage.py runserver 0.0.0.0:8000
```

### Environment-Specific Setup

#### Development Environment
- **Services**: `dev-web-service`, `dev-db-service`, `dev-cache-service`
- **Configuration**: Loaded from `env/*/development` files
- **Features**: Debug enabled, local volume mounts, hot reloading

#### Test Environment  
- **Services**: `test-web-service`, `test-db-service`, `test-cache-service`
- **Configuration**: Loaded from `env/*/test` files
- **Features**: Optimized for testing, isolated test database

#### Production Environment
- **Services**: `prod-web-service`, `prod-db-service`, `prod-cache-service`
- **Configuration**: Loaded from `env/*/production` files
- **Features**: Security hardened, optimized performance, SSL enabled

## Code Standards

### Style Guide
We follow PEP8 with some modifications:
- Line length: 88 characters (Black default)
- String quotes: Double quotes preferred
- Import sorting: isort with Black profile

### Code Quality Tools

#### Linting
```bash
# Black formatting
black excel_analyzing/

# Flake8 linting
flake8 excel_analyzing/

# Import sorting
isort excel_analyzing/

# Type checking
mypy excel_analyzing/
```

#### Pre-commit Hooks
```bash
pre-commit install
pre-commit run --all-files
```

#### Testing
```bash
# Run all tests
python run_tests.py --all

# Run specific test categories
python run_tests.py --unit --lint
python run_tests.py --integration --security
python run_tests.py --performance --regression

# Run with additional options
python run_tests.py --unit --coverage
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