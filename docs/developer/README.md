# Developer Guide

## Architecture Overview

Excel Analyzing is built with a layered architecture that separates concerns and provides clear interfaces between components.

### System Components

```text
excel_analyzing/
├── cli.py                   # Command-line interface
├── core/                    # Core business logic
│   ├── config.py           # Configuration management
│   ├── data_types.py       # Data type inference
│   ├── cleaning.py         # Data cleaning utilities
│   └── schema.py           # Schema validation
├── models/                  # Data models
│   ├── schemas.py          # Pydantic models
│   └── database.py         # SQLAlchemy ORM models
├── pipeline/                # Processing pipeline
│   ├── orchestrator.py     # Main processing coordinator
│   └── processor.py        # Data processing engine
├── utils/                   # Utility functions
│   ├── files.py            # File operations
│   └── logging.py          # Logging configuration
└── web/                     # Django web application
    ├── apps/               # Django applications
    ├── settings/           # Environment-specific settings
    ├── urls.py             # URL routing
    └── wsgi.py             # WSGI application entry point
```

### Configuration Management Architecture

The application uses a hierarchical configuration system:

1. **Environment Variables**: Highest priority, OS-level settings
2. **Service-specific Files**: Environment-specific configuration files
3. **Global Configuration**: Root-level .env file
4. **Application Defaults**: Hardcoded defaults in config.py

#### Configuration Loading Process

```python
# Configuration files are loaded in this order:
env/web/django/.env.{environment}
env/database/postgresql/.env.{environment}
env/cache/redis/.env.{environment}
env/processing/core/.env.{environment}
.env (root level)
```

## Development Setup

### Prerequisites
- Python 3.10 or higher
- PostgreSQL 12 or higher
- Git for version control

### Quick Start

1. **Clone and setup**:
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
pip install -e .
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Initialize database**:
```bash
excel-analyze init-db
```

4. **Run tests**:
```bash
pytest
```

## Development Workflow

### Code Standards & Quality

#### Code Style Guide

**PEP8 Compliance with Modern Enhancements**:
- **Line Length**: 88 characters (Black default)
- **String Quotes**: Double quotes preferred
- **Import Organization**: isort with Black-compatible profile
- **Type Hints**: Required for public functions and methods
- **Docstrings**: Google-style docstrings for public APIs

#### Code Quality Tools

**Automated Code Formatting**:
```bash
# Format all code
black excel_analyzing/

# Sort imports
isort excel_analyzing/

# Combined formatting
black excel_analyzing/ && isort excel_analyzing/
```

**Code Linting & Analysis**:
```bash
# Lint code
flake8 excel_analyzing/

# Type checking
mypy excel_analyzing/

# Security scanning
bandit -r excel_analyzing/
```

**Pre-commit Hooks**:
```bash
# Install pre-commit hooks
pre-commit install

# Run hooks on all files
pre-commit run --all-files

# Update hook versions
pre-commit autoupdate
```

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

### API Development & Testing

**REST API Development**:
```python
# Adding new API endpoints in excel_analyzing/web/apps/api/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def custom_endpoint(request):
    # Implementation
    return Response({'status': 'success'})
```

**API Testing**:
```bash
# Manual API testing
curl -X GET http://localhost:8000/api/workbooks/ \
  -H "Content-Type: application/json"

# Automated API testing
pytest tests/integration/test_api.py -v
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
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class NewModel(Base):
    __tablename__ = 'new_models'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2. Processing Logic

Add processing functions in appropriate modules:

```python
# core/processing.py
def process_new_feature(data: pd.DataFrame) -> pd.DataFrame:
    """Process data with new feature."""
    # Implementation
    return processed_data
```

### 3. Web Interface

Add Django views in `web/apps/workbooks/views.py`:

```python
from django.shortcuts import render
from django.http import JsonResponse

def new_feature_view(request):
    """Handle new feature requests."""
    # Implementation
    return render(request, 'new_feature.html', context)
```

### 4. CLI Commands

Add CLI commands in `cli.py`:

```python
@cli.command()
@click.argument("parameter")
@click.option("--option", help="Option description")
def new_command(parameter: str, option: str) -> None:
    """New CLI command description."""
    # Implementation
    console.print("Command executed successfully!")
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

When adding new models or changing existing ones:

```bash
# Create migration
python manage.py makemigrations

# Apply migration
python manage.py migrate

# View migration SQL
python manage.py sqlmigrate app_name migration_name
```

## Performance Optimization

### Database Performance
- Use database indexes for frequently queried columns
- Implement connection pooling for production
- Use bulk operations for large datasets
- Monitor query performance with EXPLAIN

### Memory Management
- Process large files in chunks
- Use generators for memory-efficient iteration
- Monitor memory usage during development
- Implement proper cleanup in exception handlers

### Caching Strategy
- Cache frequently accessed data
- Use appropriate cache expiration times
- Implement cache invalidation strategies
- Monitor cache hit rates

## Testing Strategy

### Test Categories
- **Unit Tests**: Test individual functions and methods
- **Integration Tests**: Test component interactions
- **End-to-End Tests**: Test complete workflows
- **Performance Tests**: Benchmark processing performance

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=excel_analyzing --cov-report=html

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
pytest -m performance
```

## Deployment

### Local Development
```bash
# Start development server
python manage.py runserver

# Or with Docker
docker-compose -f docker-compose.dev.yml up
```

### Production Deployment
```bash
# Build production image
docker build -t excel-analyzing .

# Run with production settings
docker-compose up -d
```

## Contributing

### Pull Request Process

1. **Create Feature Branch**: `git checkout -b feature/your-feature`
2. **Make Changes**: Follow coding standards and add tests
3. **Run Tests**: Ensure all tests pass
4. **Update Documentation**: Update relevant documentation
5. **Submit PR**: Create pull request with clear description

### Code Review Guidelines

- Review for functionality, performance, and security
- Ensure tests cover new functionality
- Check documentation completeness
- Verify coding standards compliance
- Test in multiple environments if applicable

### Release Process

1. **Update Version**: Increment version in pyproject.toml
2. **Update Changelog**: Document changes and new features
3. **Create Tag**: `git tag v1.x.x && git push origin v1.x.x`
4. **Deploy**: Follow deployment procedures

## Troubleshooting

### Common Issues

**Database Connection Errors**:
- Check PostgreSQL service status
- Verify connection parameters in .env
- Ensure database exists and user has permissions

**Import Errors**:
- Verify virtual environment activation
- Check installed dependencies with `pip list`
- Ensure package is installed in editable mode

**Test Failures**:
- Check test database configuration
- Ensure test data is properly set up
- Review test isolation and cleanup

**Performance Issues**:
- Profile code with cProfile or py-spy
- Monitor database query performance
- Check memory usage patterns
- Review file processing chunk sizes

---

This guide provides the foundation for contributing to Excel Analyzing. For specific implementation details, refer to the source code and existing tests.