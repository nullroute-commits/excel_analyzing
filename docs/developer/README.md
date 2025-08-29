# Developer Guide

## Overview

This guide provides technical details for developers working on the Excel Analyzing framework. The project follows modern Python development practices with clear separation of concerns and comprehensive testing.

## Architecture

### System Components

The Excel Analyzing framework consists of several key components:

1. **Core Layer** (`excel_analyzing/core/`): Configuration, data types, and shared utilities
2. **Models Layer** (`excel_analyzing/models/`): Database models and data validation schemas  
3. **Pipeline Layer** (`excel_analyzing/pipeline/`): Data processing orchestration and transformation
4. **Web Layer** (`excel_analyzing/web/`): Django web application and REST API
5. **CLI Layer** (`excel_analyzing/cli.py`): Command-line interface
6. **Utils Layer** (`excel_analyzing/utils/`): Helper functions and utilities

### Component Dependencies

```text
┌─────────────────────┐
│     CLI & Web       │  ← User interfaces
├─────────────────────┤
│      Pipeline       │  ← Processing orchestration
├─────────────────────┤  
│       Models        │  ← Data validation & persistence
├─────────────────────┤
│        Core         │  ← Configuration & shared logic
├─────────────────────┤
│       Utils         │  ← Helper functions
└─────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Database access abstracted through SQLAlchemy models
- **Factory Pattern**: Used for creating different Excel processors based on file type
- **Configuration Pattern**: Environment-specific settings using Pydantic
- **Dependency Injection**: Components receive dependencies through constructors

## Development Setup

### Local Development Environment

1. **Clone Repository**
   ```bash
   git clone https://github.com/nullroute-commits/excel_analyzing.git
   cd excel_analyzing
   ```

2. **Setup Virtual Environment**
   ```bash
   python3.10 -m venv venv
   source venv/bin/activate
   pip install --upgrade pip
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements-dev.txt
   pip install -e .
   ```

4. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database credentials and settings
   ```

5. **Initialize Database**
   ```bash
   python manage.py migrate
   # Or: excel-analyze init-db
   ```

### Docker Development

For containerized development:

```bash
# Start development services
docker-compose -f docker-compose.dev.yml up --build

# Run tests in container
docker-compose -f docker-compose.test.yml up

# Access services:
# - Web: http://localhost:8000
# - API: http://localhost:8000/api/
# - Database: localhost:5432
```

## Development Workflow

### Code Organization

The codebase follows Python package conventions with clear module separation:

```text
excel_analyzing/
├── __init__.py              # Package initialization
├── _version.py              # Version information
├── cli.py                   # Command-line interface
├── core/                    # Core business logic
│   ├── __init__.py
│   ├── config.py           # Settings and configuration
│   ├── data_types.py       # Data type inference
│   ├── cleaning.py         # Data cleaning utilities
│   └── schema.py           # Schema definitions
├── models/                  # Data models
│   ├── __init__.py
│   ├── database.py         # SQLAlchemy ORM models
│   └── schemas.py          # Pydantic validation models
├── pipeline/                # Processing pipeline
│   ├── __init__.py
│   ├── orchestrator.py     # Main coordinator
│   └── processor.py        # Data processor
├── utils/                   # Utility modules
│   ├── __init__.py
│   ├── files.py            # File operations
│   └── logging.py          # Logging setup
└── web/                     # Django web application
    ├── __init__.py
    ├── apps/               # Django applications
    ├── settings/           # Environment settings
    ├── urls.py             # URL routing
    └── wsgi.py             # WSGI entry point
```

### Adding New Features

#### 1. Processing Features

To add new data processing capabilities:

1. **Create processing function in `core/`**
   ```python
   # excel_analyzing/core/my_feature.py
   def my_processing_function(data: pd.DataFrame) -> pd.DataFrame:
       """Process data with new feature."""
       # Implementation here
       return processed_data
   ```

2. **Add configuration options**
   ```python
   # excel_analyzing/models/schemas.py
   class ProcessingOptions(BaseModel):
       # Existing options...
       my_feature_enabled: bool = Field(default=False)
   ```

3. **Integrate into processor**
   ```python
   # excel_analyzing/pipeline/processor.py
   def process_sheet(self, sheet_data: pd.DataFrame) -> pd.DataFrame:
       if self.options.my_feature_enabled:
           sheet_data = my_processing_function(sheet_data)
       return sheet_data
   ```

#### 2. API Endpoints

To add new REST API endpoints:

1. **Create Django app** (if needed)
   ```bash
   cd excel_analyzing/web/apps
   python ../../manage.py startapp my_app
   ```

2. **Define views**
   ```python
   # excel_analyzing/web/apps/my_app/views.py
   from rest_framework.views import APIView
   from rest_framework.response import Response
   
   class MyAPIView(APIView):
       def get(self, request):
           # Implementation
           return Response({"data": "result"})
   ```

3. **Add URL routing**
   ```python
   # excel_analyzing/web/apps/my_app/urls.py
   from django.urls import path
   from .views import MyAPIView
   
   urlpatterns = [
       path('my-endpoint/', MyAPIView.as_view()),
   ]
   ```

#### 3. CLI Commands

To add new CLI commands:

```python
# excel_analyzing/cli.py
@cli.command()
@click.option('--option', help='Description')
def my_command(option: str) -> None:
    """My new command description."""
    # Implementation
    console.print(f"Running with option: {option}")
```

### Database Changes

#### Creating Migrations

1. **Modify models in `models/database.py`**
2. **Create migration**
   ```bash
   python manage.py makemigrations
   ```
3. **Apply migration**
   ```bash
   python manage.py migrate
   ```

#### Model Examples

```python
# excel_analyzing/models/database.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class MyModel(Base):
    __tablename__ = 'my_table'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

## Code Standards & Quality

### Code Style Guide

**PEP8 Compliance with Modern Enhancements**:
- **Line Length**: 88 characters (Black default)
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
```

Pre-commit configuration includes:
- Black formatting
- isort import sorting  
- Flake8 linting
- mypy type checking
- Security scanning with bandit

#### Testing & Coverage
```bash
# Run unit tests
pytest tests/unit/ -v

# Run with coverage
pytest --cov=excel_analyzing --cov-report=html --cov-report=term-missing

# Run specific test types
pytest -m unit tests/
pytest -m integration tests/
pytest -m e2e tests/
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

## Testing Strategy

### Test Categories

1. **Unit Tests** (`tests/unit/`): Fast, isolated tests for individual functions
2. **Integration Tests** (`tests/integration/`): Test component interactions
3. **Regression Tests** (`tests/regression/`): Prevent regression of fixed issues
4. **Security Tests** (`tests/security/`): Security and vulnerability testing
5. **Performance Tests** (`tests/performance/`): Performance benchmarking
6. **End-to-End Tests** (`tests/e2e/`): Complete workflow testing

### Writing Tests

#### Test Structure
```python
# tests/unit/test_processor.py
import pytest
from excel_analyzing.pipeline.processor import ExcelDataProcessor
from excel_analyzing.models.schemas import ProcessingOptions

class TestExcelDataProcessor:
    """Test ExcelDataProcessor class."""
    
    def test_processor_initialization(self):
        """Test processor initialization."""
        processor = ExcelDataProcessor()
        assert processor.options is not None
        
    def test_processor_with_custom_options(self):
        """Test processor with custom options."""
        options = ProcessingOptions(drop_empty_rows=False)
        processor = ExcelDataProcessor(options)
        assert processor.options.drop_empty_rows is False
```

#### Test Fixtures
```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_excel_file():
    """Provide sample Excel file for testing."""
    return Path("test_data/sample.xlsx")

@pytest.fixture
def processing_options():
    """Provide default processing options."""
    return ProcessingOptions(
        drop_empty_rows=True,
        clean_column_names=True
    )
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=excel_analyzing --cov-report=html

# Run specific test files
pytest tests/unit/test_processor.py -v

# Run tests with markers
pytest -m "unit and not slow"

# Run tests in parallel
pytest -n auto  # Requires pytest-xdist
```

## Configuration Management

### Environment-Specific Settings

The application uses Pydantic for configuration management with environment-specific settings:

```python
# excel_analyzing/core/config.py
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    # Database settings
    database_host: str = Field(default="localhost")
    database_port: int = Field(default=5432)
    database_name: str = Field(default="excel_analyzing")
    
    # Application settings
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

### Environment Files

Environment configuration is managed through `.env` files:

```bash
# .env.development
ENVIRONMENT=development
DEBUG=True
DATABASE_HOST=localhost
LOG_LEVEL=DEBUG

# .env.production
ENVIRONMENT=production
DEBUG=False
DATABASE_HOST=db-service
LOG_LEVEL=INFO
```

## Debugging & Troubleshooting

### Common Development Issues

1. **Import Errors**: Ensure virtual environment is activated and package is installed in editable mode
2. **Database Connections**: Check PostgreSQL is running and credentials are correct
3. **Test Failures**: Run tests individually to isolate issues
4. **Type Checking**: Address mypy errors before committing

### Debugging Tools

```bash
# Python debugger
python -m pdb script.py

# Django shell for debugging
python manage.py shell

# Database inspection
python manage.py dbshell

# View logs
tail -f excel_analyzing.log
```

### Performance Profiling

```python
# Using cProfile
import cProfile
cProfile.run('my_function()')

# Using line_profiler
@profile
def my_function():
    # Function code
    pass
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

## Additional Resources

- [Python Type Hints](https://docs.python.org/3/library/typing.html)
- [Django Documentation](https://docs.djangoproject.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)
- [pytest Documentation](https://docs.pytest.org/)
- [Black Code Formatter](https://black.readthedocs.io/)