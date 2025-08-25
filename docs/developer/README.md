# Excel Analyzing - Comprehensive Developer Implementation Guide

## Advanced System Architecture & Development Paradigms

Excel Analyzing implements a sophisticated, enterprise-grade software architecture utilizing Domain-Driven Design (DDD) principles, Clean Architecture patterns, and CQRS (Command Query Responsibility Segregation) with Event Sourcing for optimal scalability, maintainability, and testability. This comprehensive guide provides in-depth technical details for developers contributing to or extending the Excel Analyzing framework.

### Distributed Microservices Architecture Overview

The system architecture follows a hexagonal (ports and adapters) pattern with explicit service boundaries, dependency inversion, and interface segregation. Each microservice represents a distinct bounded context with its own data store, business logic, and external interfaces.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Load Balancer & API Gateway                          │
│                      (HAProxy/Nginx + Kong/Zuul)                           │
│  • SSL/TLS Termination      • Rate Limiting      • Authentication          │
│  • Request Routing          • Load Balancing     • API Versioning          │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼──────────┐                ┌───────▼──────────┐
│   Web Service    │                │  API Gateway     │
│ (web-service)    │◄──────────────►│   Service        │
├─────────────────┬┤                ├─────────────────┬┤
│ Django REST API ││                │ FastAPI/Flask   ││
│ • GraphQL API   ││                │ • OpenAPI 3.0   ││
│ • WebSocket     ││                │ • Rate Limiting ││
│ • Admin Panel   ││                │ • Auth Gateway  ││
│ • Static Files  ││                │ • Monitoring    ││
└─────────────────┴┘                └─────────────────┴┘
        │                                   │
        └─────────────────┬─────────────────┘
                          │
    ┌─────────────────────▼─────────────────────┐
    │                                           │
┌───▼────────────┐    ┌────────────────┐    ┌──▼──────────────┐
│ Processing     │    │   Database     │    │   Cache &       │
│ Service        │◄──►│   Service      │◄──►│  Message Queue  │
│ (proc-service) │    │ (db-service)   │    │ (cache-service) │
├────────────────┤    ├────────────────┤    ├─────────────────┤
│ • Excel Parser │    │ • PostgreSQL   │    │ • Redis Cluster │
│ • Data Proc.   │    │ • Read Replica │    │ • Pub/Sub       │
│ • ML Pipeline  │    │ • Migrations   │    │ • Session Store │
│ • ETL Engine   │    │ • Backups      │    │ • Task Queue    │
└────────────────┘    └────────────────┘    └─────────────────┘
        │                       │                      │
        └───────────────────────┼──────────────────────┘
                                │
    ┌───────────────────────────▼───────────────────────────┐
    │                                                       │
┌───▼───────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Worker Pool   │  │ Monitoring &    │  │ File Storage &  │
│ (workers)     │  │ Logging Service │  │ CDN Service     │
├───────────────┤  ├─────────────────┤  ├─────────────────┤
│ • Celery      │  │ • Prometheus    │  │ • MinIO/S3      │
│ • Task Queue  │  │ • Grafana       │  │ • File Upload   │
│ • Scheduler   │  │ • ELK Stack     │  │ • Static Assets │
│ • Dead Letter │  │ • Alertmanager  │  │ • CDN Cache     │
└───────────────┘  └─────────────────┘  └─────────────────┘
```

### Advanced Service Communication Patterns & Protocols

#### Inter-Service Communication Matrix

The Excel Analyzing framework implements multiple communication patterns optimized for different use cases:

1. **Synchronous RESTful APIs**: For real-time operations requiring immediate responses
2. **Asynchronous Message Queues**: For background processing and event-driven workflows
3. **GraphQL Federation**: For complex data fetching with multiple service integration
4. **gRPC Communication**: For high-performance internal service communication
5. **WebSocket Connections**: For real-time updates and streaming data

```python
# Advanced Service Communication Configuration
from enum import Enum
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
import asyncio
import aiohttp
import grpc
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer

class CommunicationProtocol(Enum):
    """Enumeration of supported inter-service communication protocols."""
    REST_API = "rest_api"
    GRAPHQL = "graphql"
    GRPC = "grpc"
    WEBSOCKET = "websocket"
    MESSAGE_QUEUE = "message_queue"
    EVENT_STREAM = "event_stream"

@dataclass
class ServiceEndpoint:
    """Service endpoint configuration with protocol-specific settings."""
    service_name: str
    protocol: CommunicationProtocol
    base_url: str
    port: int
    authentication: Dict[str, Any]
    circuit_breaker: Dict[str, Any]
    retry_policy: Dict[str, Any]
    timeout_settings: Dict[str, Any]
    health_check: Dict[str, Any]

class AdvancedServiceCommunicator:
    """
    Sophisticated service communication manager implementing
    circuit breaker patterns, retry logic, and failover mechanisms.
    """
    
    def __init__(self, service_registry: Dict[str, ServiceEndpoint]):
        self.service_registry = service_registry
        self.circuit_breakers = {}
        self.connection_pools = {}
        self.metrics_collector = MetricsCollector()
        
    async def make_service_call(
        self,
        target_service: str,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute service call with comprehensive error handling and monitoring.
        
        Args:
            target_service: Name of the target service
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: Service endpoint path
            data: Request payload data
            headers: Additional HTTP headers
            timeout: Request timeout in seconds
            
        Returns:
            Dict containing response data and metadata
            
        Raises:
            ServiceUnavailableError: When service is down or unresponsive
            CircuitBreakerOpenError: When circuit breaker is open
            ServiceTimeoutError: When request times out
        """
        service_config = self.service_registry.get(target_service)
        if not service_config:
            raise ServiceNotFoundError(f"Service {target_service} not found in registry")
        
        # Circuit breaker check
        circuit_breaker = self.get_circuit_breaker(target_service)
        if circuit_breaker.is_open():
            raise CircuitBreakerOpenError(f"Circuit breaker open for {target_service}")
        
        # Prepare request configuration
        request_config = self.prepare_request_config(
            service_config, method, endpoint, data, headers, timeout
        )
        
        # Execute request with retry logic
        response = await self.execute_with_retry(
            service_config, request_config, circuit_breaker
        )
        
        # Collect metrics
        self.metrics_collector.record_service_call(
            target_service, method, endpoint, response.status_code, response.elapsed
        )
        
        return {
            "status_code": response.status_code,
            "data": await response.json() if response.content_type == "application/json" else await response.text(),
            "headers": dict(response.headers),
            "elapsed_time": response.elapsed.total_seconds(),
            "service_metadata": {
                "service_name": target_service,
                "protocol": service_config.protocol.value,
                "endpoint": endpoint
            }
        }

# GraphQL Federation Configuration for Complex Data Fetching
GRAPHQL_FEDERATION_CONFIG = {
    "gateway_url": "http://graphql-gateway:4000/graphql",
    "services": {
        "workbook_service": {
            "url": "http://workbook-service:4001/graphql",
            "schema_file": "schemas/workbook.graphql"
        },
        "analysis_service": {
            "url": "http://analysis-service:4002/graphql", 
            "schema_file": "schemas/analysis.graphql"
        },
        "user_service": {
            "url": "http://user-service:4003/graphql",
            "schema_file": "schemas/user.graphql"
        }
    },
    "federation_settings": {
        "query_planning": True,
        "query_caching": True,
        "introspection_enabled": False,  # Disabled in production
        "playground_enabled": False,     # Disabled in production
        "tracing_enabled": True,
        "metrics_enabled": True
    }
}

# gRPC Service Configuration for High-Performance Communication
GRPC_SERVICE_CONFIG = {
    "processing_service": {
        "address": "processing-service:50051",
        "proto_file": "protos/processing.proto",
        "options": {
            "grpc.keepalive_time_ms": 120000,
            "grpc.keepalive_timeout_ms": 5000,
            "grpc.keepalive_permit_without_calls": True,
            "grpc.http2.max_pings_without_data": 0,
            "grpc.http2.min_time_between_pings_ms": 10000,
            "grpc.http2.min_ping_interval_without_data_ms": 300000
        }
    },
    "analytics_service": {
        "address": "analytics-service:50052",
        "proto_file": "protos/analytics.proto",
        "compression": grpc.Compression.Gzip,
        "max_message_length": 100 * 1024 * 1024  # 100MB
    }
}
```

### Comprehensive Development Environment Setup & Toolchain

#### Advanced Development Environment Configuration

The development environment implements sophisticated tooling for productivity, debugging, and code quality assurance:

```bash
# Advanced Development Environment Setup Script
#!/bin/bash

# Development Environment Setup with Comprehensive Tooling
setup_development_environment() {
    echo "🚀 Setting up Excel Analyzing development environment..."
    
    # Python Environment Setup with Optimization
    echo "📦 Configuring Python environment..."
    python3.11 -m venv venv --copies --clear
    source venv/bin/activate
    
    # Upgrade core tools with specific versions for reproducibility
    pip install --upgrade \
        pip==23.0.1 \
        setuptools==67.6.0 \
        wheel==0.40.0
    
    # Install development dependencies with hash verification
    pip install -r requirements-dev.txt --require-hashes
    
    # Install pre-commit hooks for code quality
    pre-commit install --install-hooks
    pre-commit install --hook-type commit-msg
    pre-commit install --hook-type pre-push
    
    # Configure Git hooks for enhanced workflow
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Advanced pre-commit hook with comprehensive checks
set -e

echo "🔍 Running pre-commit validation..."

# Static analysis with Bandit
echo "🛡️  Running security analysis..."
bandit -r excel_analyzing/ -f json -o security-report.json || {
    echo "❌ Security issues found. Check security-report.json"
    exit 1
}

# Code quality analysis with SonarQube
echo "📊 Running code quality analysis..."
sonar-scanner \
    -Dsonar.projectKey=excel-analyzing \
    -Dsonar.sources=excel_analyzing/ \
    -Dsonar.tests=tests/ \
    -Dsonar.python.coverage.reportPaths=coverage.xml \
    -Dsonar.python.xunit.reportPath=test-results.xml

# Type checking with MyPy
echo "🔍 Running type checking..."
mypy excel_analyzing/ --config-file mypy.ini

# Import sorting verification
echo "📚 Checking import organization..."
isort --check-only --diff excel_analyzing/ tests/

# Code formatting verification
echo "🎨 Checking code formatting..."
black --check --diff excel_analyzing/ tests/

# Dependency vulnerability scanning
echo "🔒 Scanning dependencies for vulnerabilities..."
safety check --json --output safety-report.json

echo "✅ All pre-commit checks passed!"
EOF

    chmod +x .git/hooks/pre-commit
    
    # Configure development database
    echo "🗄️  Setting up development database..."
    docker-compose -f docker-compose.dev.yml up -d db-service
    
    # Wait for database to be ready
    echo "⏳ Waiting for database to be ready..."
    until docker-compose -f docker-compose.dev.yml exec db-service pg_isready -U postgres; do
        sleep 2
    done
    
    # Run database migrations
    echo "🔄 Running database migrations..."
    python manage.py migrate --verbosity=2
    
    # Create development superuser
    echo "👤 Creating development superuser..."
    python manage.py createsuperuser \
        --username admin \
        --email admin@excel-analyzing.local \
        --noinput
    
    # Load development fixtures
    echo "📊 Loading development fixtures..."
    python manage.py loaddata fixtures/dev_data.json
    
    # Configure development cache
    echo "🚀 Setting up development cache..."
    docker-compose -f docker-compose.dev.yml up -d cache-service
    
    # Setup development monitoring
    echo "📈 Configuring development monitoring..."
    docker-compose -f docker-compose.dev.yml up -d \
        prometheus \
        grafana \
        jaeger
    
    # Install development browser tools
    echo "🌐 Installing browser development tools..."
    playwright install chromium firefox webkit
    
    # Configure IDE settings
    echo "⚙️  Configuring IDE settings..."
    setup_vscode_configuration
    setup_pycharm_configuration
    
    echo "🎉 Development environment setup complete!"
    echo "📋 Next steps:"
    echo "   1. Start development server: python manage.py runserver"
    echo "   2. Access admin panel: http://localhost:8000/admin/"
    echo "   3. Access API docs: http://localhost:8000/api/docs/"
    echo "   4. Access Grafana: http://localhost:3000/"
    echo "   5. Access Jaeger: http://localhost:16686/"
}

# VSCode Configuration Setup
setup_vscode_configuration() {
    mkdir -p .vscode
    
    cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": false,
    "python.linting.flake8Enabled": true,
    "python.linting.mypyEnabled": true,
    "python.linting.banditEnabled": true,
    "python.formatting.provider": "black",
    "python.formatting.blackArgs": ["--line-length", "88"],
    "python.sortImports.args": ["--profile", "black"],
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests/",
        "--cov=excel_analyzing",
        "--cov-report=html",
        "--cov-report=xml"
    ],
    "files.exclude": {
        "**/__pycache__": true,
        "**/*.pyc": true,
        ".coverage": true,
        "htmlcov/": true,
        ".pytest_cache/": true,
        ".mypy_cache/": true
    },
    "editor.rulers": [88],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
EOF

    cat > .vscode/launch.json << 'EOF'
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django Debug Server",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver", "0.0.0.0:8000"],
            "django": true,
            "console": "integratedTerminal",
            "env": {
                "ENVIRONMENT": "development",
                "DEBUG": "True"
            }
        },
        {
            "name": "Django Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v", "--tb=short"],
            "console": "integratedTerminal",
            "env": {
                "ENVIRONMENT": "test"
            }
        },
        {
            "name": "Celery Worker",
            "type": "python",
            "request": "launch",
            "module": "celery",
            "args": ["worker", "-A", "excel_analyzing.web.celery", "--loglevel=debug"],
            "console": "integratedTerminal"
        }
    ]
}
EOF
}

# PyCharm Configuration Setup
setup_pycharm_configuration() {
    mkdir -p .idea
    
    cat > .idea/misc.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.11 (excel_analyzing)" project-jdk-type="Python SDK" />
  <component name="PyCharmProfessionalAdvertiser">
    <option name="shown" value="true" />
  </component>
</project>
EOF
    
    cat > .idea/excel_analyzing.iml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="FacetManager">
    <facet type="django" name="Django">
      <configuration>
        <option name="rootFolder" value="$MODULE_DIR$" />
        <option name="settingsModule" value="excel_analyzing/web/settings/development.py" />
        <option name="manageScript" value="$MODULE_DIR$/manage.py" />
        <option name="environment" value="&lt;map/&gt;" />
        <option name="doNotUseTestRunner" value="false" />
        <option name="trackFilePattern" value="migrations" />
      </configuration>
    </facet>
  </component>
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$">
      <excludeFolder url="file://$MODULE_DIR$/venv" />
      <excludeFolder url="file://$MODULE_DIR$/.pytest_cache" />
      <excludeFolder url="file://$MODULE_DIR$/.mypy_cache" />
      <excludeFolder url="file://$MODULE_DIR$/htmlcov" />
    </content>
    <orderEntry type="inheritedJdk" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
  <component name="TemplatesService">
    <option name="TEMPLATE_CONFIGURATION" value="Django" />
    <option name="TEMPLATE_FOLDERS">
      <list>
        <option value="$MODULE_DIR$/excel_analyzing/web/templates" />
      </list>
    </option>
  </component>
</module>
EOF
}
```

### Domain-Driven Design Implementation & Bounded Contexts

#### Core Domain Models & Aggregate Design

The Excel Analyzing framework implements sophisticated domain modeling using DDD principles with clear aggregate boundaries and domain events:

```python
# Domain Models with Advanced DDD Patterns
from typing import List, Optional, Dict, Any, Protocol
from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from decimal import Decimal
import uuid
from abc import ABC, abstractmethod

class DomainEvent(ABC):
    """Base class for all domain events in the system."""
    
    def __init__(self):
        self.event_id = uuid.uuid4()
        self.occurred_at = datetime.utcnow()
        self.version = 1
    
    @abstractmethod
    def event_type(self) -> str:
        """Return the type identifier for this event."""
        pass

class AggregateRoot(ABC):
    """Base class for aggregate roots implementing event sourcing."""
    
    def __init__(self):
        self._domain_events: List[DomainEvent] = []
        self._version = 0
    
    def mark_events_as_committed(self) -> None:
        """Mark all pending domain events as committed."""
        self._domain_events.clear()
    
    def get_uncommitted_events(self) -> List[DomainEvent]:
        """Return list of uncommitted domain events."""
        return self._domain_events.copy()
    
    def _add_domain_event(self, event: DomainEvent) -> None:
        """Add a domain event to the pending events list."""
        self._domain_events.append(event)
        self._version += 1

# Workbook Aggregate with Rich Domain Logic
class WorkbookStatus(Enum):
    """Enumeration of possible workbook processing states."""
    UPLOADED = "uploaded"
    VALIDATING = "validating"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    ARCHIVED = "archived"

class DataQuality(Enum):
    """Enumeration of data quality assessment levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNACCEPTABLE = "unacceptable"

@dataclass(frozen=True)
class FileMetadata:
    """Value object containing file metadata information."""
    original_filename: str
    file_size_bytes: int
    mime_type: str
    checksum_md5: str
    checksum_sha256: str
    upload_timestamp: datetime
    
    def __post_init__(self):
        if self.file_size_bytes <= 0:
            raise ValueError("File size must be positive")
        if not self.original_filename.strip():
            raise ValueError("Filename cannot be empty")

@dataclass(frozen=True)
class SheetDimensions:
    """Value object representing sheet dimensions and statistics."""
    total_rows: int
    total_columns: int
    data_rows: int
    data_columns: int
    empty_cells: int
    filled_cells: int
    
    @property
    def fill_ratio(self) -> float:
        """Calculate the ratio of filled cells to total cells."""
        total_cells = self.total_rows * self.total_columns
        return self.filled_cells / total_cells if total_cells > 0 else 0.0
    
    @property
    def data_density(self) -> float:
        """Calculate the data density of the sheet."""
        data_cells = self.data_rows * self.data_columns
        return self.filled_cells / data_cells if data_cells > 0 else 0.0

class Sheet:
    """Entity representing an individual Excel sheet within a workbook."""
    
    def __init__(
        self,
        sheet_id: uuid.UUID,
        name: str,
        index: int,
        dimensions: SheetDimensions,
        workbook_id: uuid.UUID
    ):
        self.sheet_id = sheet_id
        self.workbook_id = workbook_id
        self._name = name
        self._index = index
        self._dimensions = dimensions
        self._columns: List[ColumnDefinition] = []
        self._data_quality: Optional[DataQuality] = None
        self._processing_metadata: Dict[str, Any] = {}
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
    
    @property
    def name(self) -> str:
        return self._name
    
    @property
    def dimensions(self) -> SheetDimensions:
        return self._dimensions
    
    def add_column_definition(self, column: 'ColumnDefinition') -> None:
        """Add a column definition to this sheet."""
        if column.sheet_id != self.sheet_id:
            raise ValueError("Column does not belong to this sheet")
        
        # Check for duplicate column names
        existing_names = {col.name for col in self._columns}
        if column.name in existing_names:
            raise ValueError(f"Column '{column.name}' already exists")
        
        self._columns.append(column)
        self._updated_at = datetime.utcnow()
    
    def assess_data_quality(self) -> DataQuality:
        """Assess and return the data quality of this sheet."""
        # Implement sophisticated data quality assessment logic
        quality_score = 0.0
        
        # Factor 1: Fill ratio (30% weight)
        fill_ratio_score = min(self.dimensions.fill_ratio * 1.5, 1.0)
        quality_score += fill_ratio_score * 0.3
        
        # Factor 2: Data consistency (25% weight)
        consistency_score = self._calculate_data_consistency()
        quality_score += consistency_score * 0.25
        
        # Factor 3: Column completeness (25% weight)
        completeness_score = self._calculate_column_completeness()
        quality_score += completeness_score * 0.25
        
        # Factor 4: Data type consistency (20% weight)
        type_consistency_score = self._calculate_type_consistency()
        quality_score += type_consistency_score * 0.20
        
        # Convert quality score to enum
        if quality_score >= 0.9:
            self._data_quality = DataQuality.EXCELLENT
        elif quality_score >= 0.75:
            self._data_quality = DataQuality.GOOD
        elif quality_score >= 0.6:
            self._data_quality = DataQuality.FAIR
        elif quality_score >= 0.4:
            self._data_quality = DataQuality.POOR
        else:
            self._data_quality = DataQuality.UNACCEPTABLE
        
        return self._data_quality

class Workbook(AggregateRoot):
    """Aggregate root for Excel workbook domain logic."""
    
    def __init__(
        self,
        workbook_id: uuid.UUID,
        file_metadata: FileMetadata,
        user_id: uuid.UUID
    ):
        super().__init__()
        self.workbook_id = workbook_id
        self.user_id = user_id
        self._file_metadata = file_metadata
        self._status = WorkbookStatus.UPLOADED
        self._sheets: List[Sheet] = []
        self._processing_started_at: Optional[datetime] = None
        self._processing_completed_at: Optional[datetime] = None
        self._error_message: Optional[str] = None
        self._quality_assessment: Optional[DataQuality] = None
        self._created_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Emit domain event
        self._add_domain_event(WorkbookUploadedEvent(workbook_id, file_metadata, user_id))
    
    def start_processing(self) -> None:
        """Initiate workbook processing workflow."""
        if self._status != WorkbookStatus.UPLOADED:
            raise InvalidWorkbookStateError(
                f"Cannot start processing. Current status: {self._status.value}"
            )
        
        self._status = WorkbookStatus.PROCESSING
        self._processing_started_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Emit domain event
        self._add_domain_event(WorkbookProcessingStartedEvent(self.workbook_id))
    
    def complete_processing(self, sheets: List[Sheet]) -> None:
        """Complete workbook processing with sheet data."""
        if self._status != WorkbookStatus.PROCESSING:
            raise InvalidWorkbookStateError(
                f"Cannot complete processing. Current status: {self._status.value}"
            )
        
        self._sheets = sheets
        self._status = WorkbookStatus.COMPLETED
        self._processing_completed_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Assess overall workbook quality
        self._assess_workbook_quality()
        
        # Emit domain event
        self._add_domain_event(
            WorkbookProcessingCompletedEvent(
                self.workbook_id,
                len(sheets),
                self._quality_assessment
            )
        )
    
    def fail_processing(self, error_message: str) -> None:
        """Mark workbook processing as failed with error details."""
        self._status = WorkbookStatus.FAILED
        self._error_message = error_message
        self._processing_completed_at = datetime.utcnow()
        self._updated_at = datetime.utcnow()
        
        # Emit domain event
        self._add_domain_event(
            WorkbookProcessingFailedEvent(self.workbook_id, error_message)
        )

# Domain Events for Event Sourcing
class WorkbookUploadedEvent(DomainEvent):
    """Event emitted when a workbook is uploaded."""
    
    def __init__(self, workbook_id: uuid.UUID, file_metadata: FileMetadata, user_id: uuid.UUID):
        super().__init__()
        self.workbook_id = workbook_id
        self.file_metadata = file_metadata
        self.user_id = user_id
    
    def event_type(self) -> str:
        return "workbook.uploaded"

class WorkbookProcessingStartedEvent(DomainEvent):
    """Event emitted when workbook processing begins."""
    
    def __init__(self, workbook_id: uuid.UUID):
        super().__init__()
        self.workbook_id = workbook_id
    
    def event_type(self) -> str:
        return "workbook.processing.started"

class WorkbookProcessingCompletedEvent(DomainEvent):
    """Event emitted when workbook processing completes successfully."""
    
    def __init__(self, workbook_id: uuid.UUID, sheet_count: int, quality: DataQuality):
        super().__init__()
        self.workbook_id = workbook_id
        self.sheet_count = sheet_count
        self.quality = quality
    
    def event_type(self) -> str:
        return "workbook.processing.completed"

# Domain Services for Complex Business Logic
class WorkbookProcessingService:
    """Domain service for coordinating workbook processing workflows."""
    
    def __init__(
        self,
        file_parser: 'FileParserProtocol',
        data_analyzer: 'DataAnalyzerProtocol',
        quality_assessor: 'QualityAssessorProtocol'
    ):
        self.file_parser = file_parser
        self.data_analyzer = data_analyzer
        self.quality_assessor = quality_assessor
    
    async def process_workbook(self, workbook: Workbook) -> None:
        """Execute complete workbook processing workflow."""
        try:
            # Start processing
            workbook.start_processing()
            
            # Parse file structure
            file_structure = await self.file_parser.parse_structure(
                workbook._file_metadata
            )
            
            # Process each sheet
            sheets = []
            for sheet_info in file_structure.sheets:
                sheet = await self._process_sheet(workbook.workbook_id, sheet_info)
                sheets.append(sheet)
            
            # Complete processing
            workbook.complete_processing(sheets)
            
        except Exception as e:
            workbook.fail_processing(str(e))
            raise
```

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