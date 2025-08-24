# API Documentation

## REST API Endpoints

The Excel Analyzing application provides a RESTful API for programmatic access to workbook data and processing capabilities.

### Base URL

```
http://localhost:8000/api/
```

### Authentication

All API endpoints require authentication. Use Django's built-in authentication system or API tokens.

### Endpoints

#### Workbooks

##### List Workbooks
```http
GET /api/workbooks/
```

**Parameters:**
- `page` (int): Page number for pagination
- `search` (string): Search query for workbook names
- `ordering` (string): Field to order by (`created_at`, `file_name`, `file_size_bytes`)

**Response:**
```json
{
  "count": 42,
  "next": "http://localhost:8000/api/workbooks/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "file_name": "sales_data.xlsx",
      "file_path": "/path/to/sales_data.xlsx",
      "file_size_bytes": 1048576,
      "sheet_count": 3,
      "created_at": "2024-01-15T10:30:00Z",
      "processed_at": "2024-01-15T10:32:15Z"
    }
  ]
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