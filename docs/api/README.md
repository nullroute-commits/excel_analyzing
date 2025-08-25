# Excel Analyzing - Comprehensive RESTful API Specification

## Enterprise API Architecture & Design Philosophy

The Excel Analyzing RESTful API represents a sophisticated, enterprise-grade application programming interface designed following OpenAPI 3.0 specifications, REST architectural principles, and API-first development methodologies. This comprehensive API provides programmatic access to workbook processing, data analysis, and management capabilities with extensive authentication, authorization, rate limiting, and monitoring features.

### API Design Principles & Standards Compliance

The API implementation adheres to industry best practices and standards:

- **RESTful Architecture**: Full compliance with REST architectural constraints including statelessness, cacheability, and uniform interface
- **OpenAPI 3.0 Specification**: Complete API documentation with machine-readable schemas, examples, and validation rules
- **JSON:API Specification**: Consistent response formatting with standardized error handling and pagination
- **HTTP/2 Protocol Support**: Enhanced performance with multiplexing, server push, and header compression
- **GraphQL Federation**: Advanced query capabilities with field-level selection and relationship traversal
- **Semantic Versioning**: API versioning strategy ensuring backward compatibility and graceful deprecation

### Advanced API Gateway & Infrastructure

```
API Infrastructure Topology:
┌─────────────────────────────────────────────────────────────────────────┐
│                        API Gateway Cluster (Kong/Zuul)                  │
│  ┌─────────────────┬─────────────────┬─────────────────┬─────────────────┐ │
│  │   Load Balancer │  Rate Limiter   │   Auth Gateway  │  Cache Layer    │ │
│  │  (HAProxy/Nginx)│  (Redis-based)  │  (OAuth 2.0)    │  (Redis/Varnish)│ │
│  └─────────────────┴─────────────────┴─────────────────┴─────────────────┘ │
└─────────────────────────┬───────────────────────────────────────────────────┘
                          │
        ┌─────────────────┴─────────────────┐
        │                                   │
┌───────▼──────────┐                ┌───────▼──────────┐
│   API Service    │                │ WebSocket Gateway│
│ (Django REST)    │◄──────────────►│  (Django Channels)│
├─────────────────┬┤                ├─────────────────┬┤
│ • REST Endpoints││                │ • Real-time API ││
│ • GraphQL API   ││                │ • Event Streaming││
│ • OpenAPI Docs  ││                │ • Subscriptions ││
│ • Health Checks ││                │ • Notifications ││
└─────────────────┴┘                └─────────────────┴┘
        │                                   │
        └─────────────────┬─────────────────┘
                          │
    ┌─────────────────────▼─────────────────────┐
    │                                           │
┌───▼────────────┐    ┌────────────────┐    ┌──▼──────────────┐
│ Business Logic │    │   Data Layer   │    │  External APIs  │
│   Services     │◄──►│   (Database)   │◄──►│   Integration   │
│ (Domain Logic) │    │ (PostgreSQL)   │    │  (3rd Party)    │
└────────────────┘    └────────────────┘    └─────────────────┘
```

### Base URL Configuration & Environment Matrix

The API supports multiple deployment environments with distinct base URLs and configuration parameters:

| Environment | Base URL | Protocol | Load Balancer | CDN Integration |
|-------------|----------|----------|---------------|-----------------|
| **Development** | `http://localhost:8000/api/v1/` | HTTP/1.1 | None | Disabled |
| **Staging** | `https://staging-api.excel-analyzing.com/api/v1/` | HTTP/2 | AWS ALB | CloudFront |
| **Production** | `https://api.excel-analyzing.com/api/v1/` | HTTP/2 | Multi-AZ ALB | Global CDN |

#### API Versioning Strategy & Deprecation Policy

```http
# Version-specific endpoint access patterns
GET /api/v1/workbooks/          # Version 1.x (Current stable)
GET /api/v2/workbooks/          # Version 2.x (Latest features)
GET /api/beta/workbooks/        # Beta features (Unstable)

# Custom headers for version specification
Accept: application/vnd.excel-analyzing.v1+json
Accept: application/vnd.excel-analyzing.v2+json

# URL parameter version specification
GET /api/workbooks/?version=1.0
GET /api/workbooks/?version=2.0
```

**Deprecation Timeline**:
- **Notice Period**: 6 months advance notice for major version deprecation
- **Support Period**: 12 months parallel support for previous version
- **End-of-Life**: Complete removal after 18 months from deprecation notice

### Comprehensive Authentication & Authorization Framework

#### Multi-Factor Authentication & Token Management

The API implements a sophisticated authentication system supporting multiple authentication methods with comprehensive security features:

```python
# Authentication Configuration Matrix
AUTHENTICATION_METHODS = {
    "oauth2": {
        "provider": "OAuth 2.0 / OpenID Connect",
        "grant_types": ["authorization_code", "client_credentials", "refresh_token"],
        "token_endpoint": "/api/auth/token/",
        "authorization_endpoint": "/api/auth/authorize/",
        "userinfo_endpoint": "/api/auth/userinfo/",
        "jwks_endpoint": "/api/auth/.well-known/jwks.json",
        "scopes": ["read", "write", "admin", "analytics"],
        "token_lifetime": 3600,  # 1 hour
        "refresh_token_lifetime": 2592000,  # 30 days
        "pkce_required": True,  # Proof Key for Code Exchange
        "state_required": True,  # CSRF protection
    },
    "jwt": {
        "provider": "JSON Web Tokens",
        "algorithm": "RS256",  # RSA-SHA256 signature
        "public_key_endpoint": "/api/auth/.well-known/public-key.pem",
        "issuer": "https://api.excel-analyzing.com",
        "audience": "excel-analyzing-api",
        "leeway": 30,  # Clock skew tolerance in seconds
        "verify_signature": True,
        "verify_expiration": True,
        "verify_not_before": True,
        "require_issued_at": True,
    },
    "api_key": {
        "provider": "API Key Authentication",
        "header_name": "X-API-Key",
        "key_format": "ea_[a-zA-Z0-9]{32}",  # Prefixed random string
        "rate_limit_per_key": 1000,  # Requests per hour
        "rotation_period": 90,  # Days before rotation recommended
        "revocation_enabled": True,
        "usage_tracking": True,
    },
    "session": {
        "provider": "Django Session Authentication",
        "session_engine": "redis",
        "session_timeout": 3600,  # 1 hour
        "csrf_protection": True,
        "secure_cookies": True,
        "httponly_cookies": True,
        "samesite_strict": True,
    }
}

# Rate Limiting Configuration
RATE_LIMITING = {
    "global": {
        "requests_per_minute": 1000,
        "requests_per_hour": 10000,
        "requests_per_day": 100000,
        "burst_limit": 50,  # Burst allowance
    },
    "authenticated": {
        "requests_per_minute": 500,
        "requests_per_hour": 5000,
        "requests_per_day": 50000,
        "burst_limit": 25,
    },
    "unauthenticated": {
        "requests_per_minute": 100,
        "requests_per_hour": 1000,
        "requests_per_day": 5000,
        "burst_limit": 10,
    },
    "premium": {
        "requests_per_minute": 2000,
        "requests_per_hour": 20000,
        "requests_per_day": 200000,
        "burst_limit": 100,
    }
}
```

#### OAuth 2.0 Flow Implementation Example

```bash
# Step 1: Authorization Request
curl -X GET "https://api.excel-analyzing.com/api/auth/authorize/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "response_type=code" \
  -d "client_id=your_client_id" \
  -d "redirect_uri=https://yourapp.com/callback" \
  -d "scope=read write analytics" \
  -d "state=random_state_string" \
  -d "code_challenge=BASE64URL(SHA256(code_verifier))" \
  -d "code_challenge_method=S256"

# Step 2: Token Exchange
curl -X POST "https://api.excel-analyzing.com/api/auth/token/" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=authorization_code" \
  -d "code=authorization_code_from_step1" \
  -d "redirect_uri=https://yourapp.com/callback" \
  -d "client_id=your_client_id" \
  -d "client_secret=your_client_secret" \
  -d "code_verifier=original_code_verifier"

# Response:
{
  "access_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "refresh_token": "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9...",
  "scope": "read write analytics",
  "created_at": 1640995200
}

# Step 3: API Usage with Bearer Token
curl -X GET "https://api.excel-analyzing.com/api/v1/workbooks/" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Accept: application/vnd.excel-analyzing.v1+json"
```

## Comprehensive API Endpoints Documentation

### Workbook Management API

#### Advanced Workbook Listing with Complex Filtering

```http
GET /api/v1/workbooks/
```

**Advanced Query Parameters**:
| Parameter | Type | Description | Example Values | Validation Rules |
|-----------|------|-------------|----------------|------------------|
| `page` | Integer | Pagination page number | `1`, `2`, `10` | Min: 1, Max: 1000 |
| `page_size` | Integer | Items per page | `10`, `25`, `50`, `100` | Min: 1, Max: 100 |
| `search` | String | Full-text search query | `"sales data"`, `"Q1 2024"` | Max length: 255 chars |
| `ordering` | String | Sort field and direction | `created_at`, `-file_size` | Allowed fields list |
| `file_name__icontains` | String | Case-insensitive filename filter | `"sales"`, `"report"` | Regex validation |
| `file_size__gte` | Integer | Minimum file size in bytes | `1048576` (1MB) | Positive integer |
| `file_size__lte` | Integer | Maximum file size in bytes | `104857600` (100MB) | Positive integer |
| `created_at__gte` | DateTime | Created after timestamp | `2024-01-01T00:00:00Z` | ISO 8601 format |
| `created_at__lte` | DateTime | Created before timestamp | `2024-12-31T23:59:59Z` | ISO 8601 format |
| `status` | Enum | Processing status filter | `completed`, `processing` | Predefined enum |
| `user_id` | UUID | Filter by user ID | `550e8400-e29b-41d4-a716-446655440000` | Valid UUID v4 |
| `sheet_count__gte` | Integer | Minimum sheet count | `1`, `5`, `10` | Positive integer |
| `has_errors` | Boolean | Filter workbooks with errors | `true`, `false` | Boolean validation |
| `quality_rating` | Enum | Data quality filter | `excellent`, `good`, `fair` | Quality enum |
| `tags` | Array | Filter by tags | `["financial", "quarterly"]` | Max 10 tags |

**Comprehensive Response Schema**:
```json
{
  "pagination": {
    "count": 1247,
    "pages": 125,
    "current_page": 1,
    "page_size": 10,
    "has_next": true,
    "has_previous": false,
    "next_url": "https://api.excel-analyzing.com/api/v1/workbooks/?page=2",
    "previous_url": null
  },
  "facets": {
    "status_counts": {
      "completed": 1156,
      "processing": 23,
      "failed": 68
    },
    "quality_distribution": {
      "excellent": 412,
      "good": 587,
      "fair": 189,
      "poor": 59
    },
    "file_size_ranges": {
      "small": 623,      // < 1MB
      "medium": 498,     // 1MB - 10MB
      "large": 126       // > 10MB
    }
  },
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "file_name": "Q1_2024_Sales_Analysis.xlsx",
      "file_path": "/uploads/2024/01/Q1_2024_Sales_Analysis.xlsx",
      "file_size_bytes": 2485760,
      "file_size_human": "2.4 MB",
      "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
      "checksum_md5": "d41d8cd98f00b204e9800998ecf8427e",
      "checksum_sha256": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
      "sheet_count": 5,
      "total_rows": 12847,
      "total_columns": 23,
      "status": "completed",
      "quality_rating": "good",
      "processing_metrics": {
        "processing_time_seconds": 142.5,
        "memory_usage_mb": 67.3,
        "rows_processed": 12847,
        "columns_processed": 115,
        "errors_count": 0,
        "warnings_count": 3
      },
      "metadata": {
        "created_by": {
          "id": "123e4567-e89b-12d3-a456-426614174000",
          "username": "john.analyst",
          "display_name": "John Analyst"
        },
        "tags": ["financial", "quarterly", "sales"],
        "description": "Q1 2024 sales performance analysis with regional breakdown",
        "business_unit": "Sales Analytics",
        "confidentiality_level": "internal"
      },
      "timestamps": {
        "created_at": "2024-01-15T10:30:00.123456Z",
        "updated_at": "2024-01-15T10:32:45.789012Z",
        "processed_at": "2024-01-15T10:32:15.456789Z",
        "last_accessed": "2024-01-16T14:22:33.987654Z"
      },
      "urls": {
        "self": "https://api.excel-analyzing.com/api/v1/workbooks/550e8400-e29b-41d4-a716-446655440000/",
        "sheets": "https://api.excel-analyzing.com/api/v1/workbooks/550e8400-e29b-41d4-a716-446655440000/sheets/",
        "download": "https://api.excel-analyzing.com/api/v1/workbooks/550e8400-e29b-41d4-a716-446655440000/download/",
        "analysis": "https://api.excel-analyzing.com/api/v1/workbooks/550e8400-e29b-41d4-a716-446655440000/analysis/"
      }
    }
  ],
  "links": {
    "self": "https://api.excel-analyzing.com/api/v1/workbooks/?page=1",
    "first": "https://api.excel-analyzing.com/api/v1/workbooks/?page=1",
    "last": "https://api.excel-analyzing.com/api/v1/workbooks/?page=125",
    "next": "https://api.excel-analyzing.com/api/v1/workbooks/?page=2",
    "previous": null
  },
  "meta": {
    "api_version": "1.0",
    "request_id": "req_123e4567e89b12d3a456426614174000",
    "response_time_ms": 45,
    "cached": false,
    "total_query_time_ms": 23
  }
}
```

#### Advanced Workbook Upload with Processing Options

```http
POST /api/v1/workbooks/
Content-Type: multipart/form-data
```

**Request Parameters**:
```bash
curl -X POST "https://api.excel-analyzing.com/api/v1/workbooks/" \
  -H "Authorization: Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/sales_data.xlsx" \
  -F "processing_options='{
    "drop_empty_rows": true,
    "drop_empty_columns": true,
    "infer_data_types": true,
    "clean_column_names": true,
    "null_threshold": 0.9,
    "max_sample_size": 10000,
    "enable_quality_assessment": true,
    "generate_statistics": true,
    "create_data_dictionary": true,
    "enable_profiling": true
  }'" \
  -F "metadata='{
    "description": "Monthly sales report with regional breakdown",
    "tags": ["sales", "monthly", "regional"],
    "business_unit": "Sales Analytics",
    "confidentiality_level": "internal",
    "retention_period_days": 2555,
    "notify_on_completion": true,
    "notification_emails": ["analyst@company.com"]
  }'" \
  -F "validation_options='{
    "strict_validation": true,
    "schema_validation": true,
    "data_integrity_checks": true,
    "duplicate_detection": true,
    "anomaly_detection": true,
    "compliance_checks": ["gdpr", "ccpa"]
  }'"
```

**Upload Response with Processing Status**:
```json
{
  "workbook": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "file_name": "sales_data.xlsx",
    "status": "uploading",
    "upload_session_id": "upload_789e1234-e56f-78a9-0123-456789abcdef",
    "estimated_processing_time_seconds": 180,
    "processing_queue_position": 3
  },
  "upload_info": {
    "bytes_uploaded": 2485760,
    "total_bytes": 2485760,
    "upload_percentage": 100.0,
    "upload_speed_bps": 1048576,
    "chunks_uploaded": 1,
    "total_chunks": 1
  },
  "processing_options": {
    "drop_empty_rows": true,
    "drop_empty_columns": true,
    "infer_data_types": true,
    "clean_column_names": true,
    "null_threshold": 0.9,
    "max_sample_size": 10000,
    "enable_quality_assessment": true,
    "generate_statistics": true,
    "create_data_dictionary": true,
    "enable_profiling": true
  },
  "validation_results": {
    "file_format_valid": true,
    "file_size_acceptable": true,
    "virus_scan_clean": true,
    "metadata_complete": true,
    "permissions_valid": true
  },
  "next_steps": {
    "polling_url": "https://api.excel-analyzing.com/api/v1/workbooks/550e8400-e29b-41d4-a716-446655440000/status/",
    "webhook_url": "https://api.excel-analyzing.com/api/v1/webhooks/processing/",
    "websocket_url": "wss://api.excel-analyzing.com/ws/workbooks/550e8400-e29b-41d4-a716-446655440000/"
  },
  "meta": {
    "request_id": "req_456f7890a123b456c789012345678901",
    "api_version": "1.0",
    "processing_started_at": "2024-01-15T10:30:00.123456Z"
  }
}
```

##### Get Workbook Details
```http
GET /api/workbooks/{id}/
```

**Response:**
```json
{
  "id": 1,
  "file_name": "sales_data.xlsx",
  "file_path": "/path/to/sales_data.xlsx",
  "file_size_bytes": 1048576,
  "sheet_count": 3,
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:32:15Z",
  "sheets": [
    {
      "id": 1,
      "name": "sales_summary",
      "original_name": "Sales Summary",
      "row_count": 1000,
      "column_count": 8,
      "has_header": true,
      "header_row": 0,
      "data_start_row": 1
    }
  ]
}
```

##### Upload and Process Workbook
```http
POST /api/workbooks/
```

**Request:**
```json
{
  "file": "base64_encoded_file_content",
  "processing_options": {
    "drop_empty_rows": true,
    "drop_empty_columns": true,
    "clean_column_names": true,
    "null_threshold": 0.9
  }
}
```

**Response:**
```json
{
  "id": 2,
  "file_name": "uploaded_data.xlsx",
  "processing_result": {
    "success": true,
    "rows_processed": 5000,
    "columns_processed": 25,
    "processing_time_seconds": 2.45
  }
}
```

#### Sheets

##### List Sheets in Workbook
```http
GET /api/workbooks/{workbook_id}/sheets/
```

**Response:**
```json
{
  "results": [
    {
      "id": 1,
      "name": "sales_summary",
      "original_name": "Sales Summary",
      "row_count": 1000,
      "column_count": 8,
      "has_header": true,
      "columns": [
        {
          "id": 1,
          "name": "product_name",
          "original_name": "Product Name",
          "data_type": "string",
          "position": 0,
          "null_count": 0,
          "unique_count": 250
        }
      ]
    }
  ]
}
```

##### Get Sheet Data
```http
GET /api/sheets/{id}/data/
```

**Parameters:**
- `limit` (int): Number of rows to return (default: 100, max: 1000)
- `offset` (int): Number of rows to skip
- `columns` (string): Comma-separated list of columns to include
- `filter` (string): Pandas query filter expression

**Response:**
```json
{
  "count": 1000,
  "columns": ["product_name", "sales_amount", "date"],
  "data": [
    {
      "product_name": "Widget A",
      "sales_amount": 150.50,
      "date": "2024-01-15"
    }
  ],
  "meta": {
    "data_types": {
      "product_name": "string",
      "sales_amount": "float",
      "date": "date"
    }
  }
}
```

##### Query Sheet Data
```http
POST /api/sheets/{id}/query/
```

**Request:**
```json
{
  "filter": "sales_amount > 100",
  "columns": ["product_name", "sales_amount"],
  "aggregation": {
    "operation": "group_by",
    "columns": ["product_name"],
    "agg_func": "sum"
  },
  "limit": 50
}
```

**Response:**
```json
{
  "query": {
    "filter": "sales_amount > 100",
    "columns": ["product_name", "sales_amount"],
    "execution_time_ms": 45
  },
  "results": {
    "count": 25,
    "data": [
      {
        "product_name": "Widget A",
        "sales_amount": 1250.75
      }
    ]
  }
}
```

#### Processing

##### Get Processing Status
```http
GET /api/processing/{workbook_id}/status/
```

**Response:**
```json
{
  "workbook_id": 1,
  "status": "completed",
  "progress": 100,
  "current_step": "Analysis complete",
  "started_at": "2024-01-15T10:30:00Z",
  "completed_at": "2024-01-15T10:32:15Z",
  "results": {
    "success": true,
    "rows_processed": 5000,
    "columns_processed": 25,
    "processing_time_seconds": 135.2,
    "error_message": null
  }
}
```

##### Reprocess Workbook
```http
POST /api/workbooks/{id}/reprocess/
```

**Request:**
```json
{
  "processing_options": {
    "drop_empty_rows": true,
    "drop_empty_columns": false,
    "clean_column_names": true,
    "null_threshold": 0.8
  }
}
```

### Error Responses

All endpoints return appropriate HTTP status codes and error messages:

#### 400 Bad Request
```json
{
  "error": "Invalid request",
  "details": {
    "processing_options": ["null_threshold must be between 0 and 1"]
  }
}
```

#### 404 Not Found
```json
{
  "error": "Workbook not found",
  "message": "No workbook with ID 999"
}
```

#### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Failed to process workbook"
}
```

### Rate Limiting

API endpoints are rate-limited to prevent abuse:
- Authenticated users: 1000 requests per hour
- Anonymous users: 100 requests per hour

### Pagination

List endpoints support pagination using limit/offset:
- Default page size: 20
- Maximum page size: 100
- Use `next` and `previous` URLs for navigation

### Data Export

#### Export Sheet as CSV
```http
GET /api/sheets/{id}/export/?format=csv
```

#### Export Sheet as JSON
```http
GET /api/sheets/{id}/export/?format=json
```

#### Export Workbook Metadata
```http
GET /api/workbooks/{id}/export/?format=json
```

### WebSocket Events

Real-time updates are available via WebSocket connections:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/processing/');

ws.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Processing update:', data);
};
```

**Event Types:**
- `processing.started`: Processing has begun
- `processing.progress`: Progress update with percentage
- `processing.completed`: Processing finished successfully
- `processing.failed`: Processing failed with error details