# API Documentation

## REST API Endpoints

The Excel Analyzing application provides a RESTful API for programmatic access to workbook data and processing capabilities.

### Base URL

```
http://localhost:8000/api/
```

### Authentication

All API endpoints require authentication. Use Django's built-in authentication system or API tokens.

```bash
# Example with session authentication
curl -H "Content-Type: application/json" \
     -H "Cookie: sessionid=your-session-id" \
     http://localhost:8000/api/workbooks/

# Example with token authentication (if configured)
curl -H "Content-Type: application/json" \
     -H "Authorization: Token your-api-token" \
     http://localhost:8000/api/workbooks/
```

### Endpoints

#### Workbooks

##### List Workbooks
```http
GET /api/workbooks/
```

**Response:**
```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "file_name": "sales_data.xlsx",
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
  "file_path": "/uploads/sales_data.xlsx",
  "file_size_bytes": 1048576,
  "sheet_count": 3,
  "sheets": [
    {
      "id": 1,
      "name": "Summary",
      "row_count": 1000,
      "column_count": 10
    }
  ],
  "created_at": "2024-01-15T10:30:00Z",
  "processed_at": "2024-01-15T10:32:15Z"
}
```

##### Upload and Process Workbook
```http
POST /api/workbooks/
Content-Type: multipart/form-data
```

**Request:**
```bash
curl -X POST \
  -F "file=@sales_data.xlsx" \
  -F "processing_options={\"drop_empty_rows\": true, \"clean_column_names\": true}" \
  http://localhost:8000/api/workbooks/
```

**Response:**
```json
{
  "id": 2,
  "file_name": "sales_data.xlsx",
  "file_size_bytes": 1048576,
  "processing_status": "processing",
  "created_at": "2024-01-15T10:30:00Z"
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
  "count": 3,
  "results": [
    {
      "id": 1,
      "name": "Summary",
      "workbook_id": 1,
      "row_count": 1000,
      "column_count": 10,
      "columns": [
        {
          "name": "product_name",
          "data_type": "string",
          "position": 0
        },
        {
          "name": "revenue",
          "data_type": "float",
          "position": 1
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

**Query Parameters:**
- `limit`: Number of rows to return (default: 100)
- `offset`: Number of rows to skip (default: 0)
- `filter`: Column filtering (e.g., `revenue__gt=1000`)
- `sort`: Sort by column (e.g., `revenue` or `-revenue` for descending)

**Response:**
```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/sheets/1/data/?offset=100",
  "previous": null,
  "data": [
    {
      "product_name": "Widget A",
      "revenue": 1500.00,
      "date": "2024-01-15"
    }
  ],
  "columns": [
    {
      "name": "product_name",
      "data_type": "string"
    },
    {
      "name": "revenue", 
      "data_type": "float"
    }
  ]
}
```

##### Query Sheet Data
```http
POST /api/sheets/{id}/query/
Content-Type: application/json
```

**Request:**
```json
{
  "select": ["product_name", "revenue"],
  "where": {
    "revenue__gt": 1000,
    "date__gte": "2024-01-01"
  },
  "order_by": ["-revenue"],
  "limit": 50
}
```

**Response:**
```json
{
  "data": [
    {
      "product_name": "Widget A",
      "revenue": 1500.00
    }
  ],
  "count": 25
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
POST /api/processing/{workbook_id}/reprocess/
Content-Type: application/json
```

**Request:**
```json
{
  "processing_options": {
    "drop_empty_rows": true,
    "clean_column_names": true,
    "infer_data_types": true,
    "null_threshold": 0.9
  }
}
```

**Response:**
```json
{
  "workbook_id": 1,
  "status": "processing",
  "message": "Reprocessing started"
}
```

### Error Responses

All API endpoints return standard HTTP status codes with detailed error information:

#### Validation Errors (400 Bad Request)
```json
{
  "error": "Validation failed",
  "details": {
    "field_name": ["This field is required."],
    "another_field": ["Invalid value."]
  }
}
```

#### Authentication Errors (401 Unauthorized)
```json
{
  "error": "Authentication required",
  "message": "Please provide valid authentication credentials."
}
```

#### Permission Errors (403 Forbidden)
```json
{
  "error": "Permission denied",
  "message": "You do not have permission to access this resource."
}
```

#### Not Found Errors (404 Not Found)
```json
{
  "error": "Resource not found",
  "message": "The requested workbook does not exist."
}
```

#### Server Errors (500 Internal Server Error)
```json
{
  "error": "Internal server error",
  "message": "An unexpected error occurred. Please try again later.",
  "request_id": "abc-123-def-456"
}
```

### Rate Limiting

API requests are rate-limited to prevent abuse:

- **Authenticated users**: 1000 requests per hour
- **Unauthenticated users**: 100 requests per hour

Rate limit headers are included in responses:
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1642262400
```

### Pagination

List endpoints use cursor-based pagination:

```json
{
  "count": 1000,
  "next": "http://localhost:8000/api/workbooks/?offset=20",
  "previous": "http://localhost:8000/api/workbooks/?offset=0",
  "results": []
}
```

**Query Parameters:**
- `limit`: Number of items per page (default: 20, max: 100)
- `offset`: Number of items to skip

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

### Health Check

Check API health and status:

```http
GET /api/health/
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00Z",
  "version": "1.0.0",
  "services": {
    "database": "healthy",
    "cache": "healthy"
  }
}
```

## Examples

### Complete Processing Workflow

```python
import requests
import time

base_url = "http://localhost:8000/api"
headers = {"Authorization": "Token your-api-token"}

# 1. Upload workbook
with open("sales_data.xlsx", "rb") as f:
    files = {"file": f}
    response = requests.post(f"{base_url}/workbooks/", files=files, headers=headers)
    workbook = response.json()

# 2. Monitor processing
workbook_id = workbook["id"]
while True:
    response = requests.get(f"{base_url}/processing/{workbook_id}/status/", headers=headers)
    status = response.json()
    
    if status["status"] == "completed":
        print("Processing completed!")
        break
    elif status["status"] == "failed":
        print(f"Processing failed: {status['results']['error_message']}")
        break
    
    time.sleep(5)  # Wait 5 seconds

# 3. Get processed data
response = requests.get(f"{base_url}/workbooks/{workbook_id}/sheets/", headers=headers)
sheets = response.json()["results"]

for sheet in sheets:
    response = requests.get(f"{base_url}/sheets/{sheet['id']}/data/", headers=headers)
    data = response.json()
    print(f"Sheet: {sheet['name']}, Rows: {data['count']}")
```

### Filtering and Querying

```python
# Query sheet data with filters
query = {
    "select": ["product_name", "revenue", "date"],
    "where": {
        "revenue__gt": 1000,
        "date__gte": "2024-01-01",
        "product_name__icontains": "widget"
    },
    "order_by": ["-revenue", "date"],
    "limit": 50
}

response = requests.post(
    f"{base_url}/sheets/{sheet_id}/query/",
    json=query,
    headers=headers
)
results = response.json()
```

### Batch Operations

```python
# Process multiple workbooks
workbook_files = ["file1.xlsx", "file2.xlsx", "file3.xlsx"]
workbook_ids = []

for file_path in workbook_files:
    with open(file_path, "rb") as f:
        files = {"file": f}
        response = requests.post(f"{base_url}/workbooks/", files=files, headers=headers)
        workbook_ids.append(response.json()["id"])

# Monitor all processing jobs
while workbook_ids:
    completed = []
    for workbook_id in workbook_ids:
        response = requests.get(f"{base_url}/processing/{workbook_id}/status/", headers=headers)
        status = response.json()
        
        if status["status"] in ["completed", "failed"]:
            completed.append(workbook_id)
            print(f"Workbook {workbook_id}: {status['status']}")
    
    for workbook_id in completed:
        workbook_ids.remove(workbook_id)
    
    if workbook_ids:
        time.sleep(10)
```

### Error Handling

```python
def safe_api_call(url, method="GET", **kwargs):
    """Make API call with proper error handling."""
    try:
        if method == "GET":
            response = requests.get(url, **kwargs)
        elif method == "POST":
            response = requests.post(url, **kwargs)
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 400:
            print(f"Validation error: {e.response.json()}")
        elif e.response.status_code == 401:
            print("Authentication required")
        elif e.response.status_code == 403:
            print("Permission denied")
        elif e.response.status_code == 404:
            print("Resource not found")
        elif e.response.status_code == 429:
            print("Rate limit exceeded")
        else:
            print(f"API error: {e}")
        return None
        
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
        return None

# Usage
workbooks = safe_api_call(f"{base_url}/workbooks/", headers=headers)
if workbooks:
    print(f"Found {workbooks['count']} workbooks")
```

## Common Use Cases

### Data Validation and Quality Assessment

```python
# Upload and analyze data quality
response = requests.post(
    f"{base_url}/workbooks/",
    files={"file": open("data.xlsx", "rb")},
    data={"processing_options": json.dumps({
        "drop_empty_rows": True,
        "clean_column_names": True,
        "infer_data_types": True,
        "null_threshold": 0.8
    })},
    headers=headers
)

workbook_id = response.json()["id"]

# Get data quality report
response = requests.get(f"{base_url}/workbooks/{workbook_id}/", headers=headers)
workbook = response.json()

print(f"Data Quality Summary:")
print(f"- Total sheets: {workbook['sheet_count']}")
for sheet in workbook['sheets']:
    print(f"- Sheet '{sheet['name']}': {sheet['row_count']} rows, {sheet['column_count']} columns")
```

### Data Integration and ETL

```python
# Extract data from multiple workbooks
source_workbooks = [1, 2, 3]  # Workbook IDs
consolidated_data = []

for workbook_id in source_workbooks:
    # Get all sheets from workbook
    response = requests.get(f"{base_url}/workbooks/{workbook_id}/sheets/", headers=headers)
    sheets = response.json()["results"]
    
    for sheet in sheets:
        # Extract data with specific filters
        query = {
            "select": ["date", "revenue", "region"],
            "where": {"date__gte": "2024-01-01"},
            "limit": 10000
        }
        
        response = requests.post(
            f"{base_url}/sheets/{sheet['id']}/query/",
            json=query,
            headers=headers
        )
        
        data = response.json()["data"]
        consolidated_data.extend(data)

print(f"Consolidated {len(consolidated_data)} records from {len(source_workbooks)} workbooks")
```

### Automated Reporting

```python
import pandas as pd

def generate_summary_report(workbook_id):
    """Generate summary report for a workbook."""
    # Get workbook details
    response = requests.get(f"{base_url}/workbooks/{workbook_id}/", headers=headers)
    workbook = response.json()
    
    report = {
        "workbook_name": workbook["file_name"],
        "total_sheets": workbook["sheet_count"],
        "sheets": []
    }
    
    for sheet_info in workbook["sheets"]:
        # Get sheet data for analysis
        response = requests.get(f"{base_url}/sheets/{sheet_info['id']}/data/?limit=1000", headers=headers)
        sheet_data = response.json()
        
        # Basic statistics
        df = pd.DataFrame(sheet_data["data"])
        sheet_summary = {
            "name": sheet_info["name"],
            "total_rows": sheet_data["count"],
            "columns": len(sheet_data["columns"]),
            "numeric_columns": len([col for col in sheet_data["columns"] if col["data_type"] in ["float", "integer"]]),
            "sample_data": sheet_data["data"][:5]  # First 5 rows
        }
        
        report["sheets"].append(sheet_summary)
    
    return report

# Generate reports for multiple workbooks
workbook_ids = [1, 2, 3]
reports = []

for workbook_id in workbook_ids:
    report = generate_summary_report(workbook_id)
    reports.append(report)
    print(f"Generated report for {report['workbook_name']}")
```