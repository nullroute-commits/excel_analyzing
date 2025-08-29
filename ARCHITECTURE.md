# Excel Analyzing - Technical Architecture Guide

## Executive Summary

Excel Analyzing is a Python-based data processing framework designed to convert Excel workbooks into structured database format. The system follows a layered architecture with clear separation between data processing, storage, and user interfaces.

## Technical Architecture Overview

### Core Architecture Pattern

The application implements a **layered architecture** with the following components:

1. **Presentation Layer**: Web interface (Django) and CLI (Click)
2. **Application Layer**: Processing pipeline and orchestration
3. **Domain Layer**: Business logic and data models
4. **Infrastructure Layer**: Database access and external services

### Key Design Principles

- **Single Responsibility**: Each component has a focused purpose
- **Dependency Injection**: Loose coupling between layers
- **Configuration Management**: Environment-based settings
- **Error Handling**: Comprehensive exception management
- **Type Safety**: Full type annotations with mypy validation

## System Components

### 1. Data Processing Architecture

The core data processing follows a pipeline pattern:

```text
File Input → Discovery → Processing → Validation → Storage → Output
```

#### Pipeline Components

- **ExcelPipeline** (`pipeline/orchestrator.py`): Main coordinator
- **ExcelDataProcessor** (`pipeline/processor.py`): Data transformation engine
- **DataTypeInference** (`core/data_types.py`): Type detection logic
- **DataCleaning** (`core/cleaning.py`): Data sanitization functions

### 2. Configuration Management Architecture

Environment-based configuration system:

```text
config/
├── .env (root level)
├── env/web/django/.env.{environment}
├── env/database/postgresql/.env.{environment}
└── env/processing/core/.env.{environment}
```

#### Configuration Loading Order (High to Low Priority)
1. Environment Variables (OS level)
2. Service-specific configuration files
3. Global .env file
4. Application defaults

### 3. Data Storage Architecture

PostgreSQL-based storage with SQLAlchemy ORM:

```text
Database Schema:
├── workbooks (file metadata)
├── sheets (worksheet information)
├── columns (column definitions)
└── processing_results (processing logs)
```

### 4. Web Application Architecture

Django-based web interface:

```text
web/
├── apps/
│   ├── workbooks/ (workbook management)
│   └── api/ (REST API endpoints)
├── settings/ (environment configs)
├── templates/ (HTML templates)
└── static/ (CSS/JS assets)
```

## Container Strategy

### Docker Configuration

The application supports containerized deployment with:

- **Base Images**: Python Alpine for minimal size
- **Multi-stage Builds**: Separate build and runtime stages
- **Environment Support**: Development, test, and production containers

#### Container Structure
```dockerfile
FROM python:3.11-alpine AS base
# System dependencies and security updates

FROM base AS dependencies  
# Python packages and compilation

FROM base AS production
# Runtime dependencies and application code
```

### Development vs Production

- **Development**: Single container with debug enabled
- **Production**: Multi-container with optimized settings
- **Testing**: Isolated containers with test data

## Service Communication

### Hostname-Based Discovery

Services communicate using hostname resolution:

- `web-service`: Django application
- `db-service`: PostgreSQL database  
- `cache-service`: Redis cache (optional)

### Communication Patterns

1. **Synchronous**: HTTP requests between services
2. **Database**: Direct PostgreSQL connections
3. **Configuration**: Environment variable injection

## Deployment Environments

### Development Environment
- Local development with hot reloading
- SQLite or PostgreSQL database
- Debug mode enabled
- Rich logging and error messages

### Test Environment  
- Isolated test database
- Automated test execution
- Coverage reporting
- Performance benchmarking

### Production Environment
- Optimized container images
- Production database with connection pooling
- Security hardening
- Monitoring and logging

## Performance Considerations

### Database Optimization
- Connection pooling (default: 10 connections)
- Query optimization with SQLAlchemy
- Indexed columns for fast lookups
- Bulk insert operations for large datasets

### Memory Management
- Chunked processing for large files
- Configurable memory limits
- Garbage collection tuning
- Memory monitoring and alerts

### Caching Strategy
- Redis-based caching (optional)
- Query result caching
- File metadata caching
- Session storage

## Security Implementation

### Input Validation
- File type and size validation
- Pydantic schema validation
- SQL injection prevention
- Path traversal protection

### Access Control
- Django session-based authentication
- CSRF protection
- Secure headers implementation
- Rate limiting capabilities

### Data Protection
- Environment variable encryption
- Secure secret management
- Database connection encryption
- Audit logging

## Monitoring & Observability

### Logging Strategy
- Structured logging with configurable levels
- Error tracking and aggregation
- Performance metrics collection
- Audit trail maintenance

### Health Monitoring
- Service health checks
- Database connectivity monitoring
- Resource usage tracking
- Error rate monitoring

## Migration Guide

### From Legacy Architecture

1. **Update environment variables**:
   - Use hostname-based service discovery
   - Move to centralized configuration structure

2. **Update Docker configurations**:
   - Migrate to Alpine base images
   - Implement multi-stage builds

3. **Application updates**:
   - Use new configuration system
   - Test service connectivity

4. **Validation**:
   - Run architecture validation tests
   - Verify all environments

## Best Practices

### Development
- Use virtual environments for isolation
- Follow PEP 8 coding standards
- Write comprehensive tests
- Document all public APIs

### Deployment
- Use environment-specific configurations
- Implement proper logging
- Monitor resource usage
- Regular security updates

### Operations
- Regular database maintenance
- Monitor performance metrics
- Implement backup strategies
- Plan for scaling requirements

---

*This architecture provides a solid foundation for scalable Excel processing while maintaining simplicity and maintainability.*