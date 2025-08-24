# User Guide

## Getting Started

Excel Analyzing is a powerful tool for processing and analyzing Excel workbooks as if they were databases. This guide will help you get started with the system.

### Prerequisites

- Python 3.9 or higher
- PostgreSQL database
- Excel files (.xlsx, .xls, .xlsm, .xlsb)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/nullroute-commits/excel_analyzing.git
   cd excel_analyzing
   ```

2. **Set up virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   pip install -e .
   ```

4. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

5. **Initialize database:**
   ```bash
   excel-analyze init-db
   ```

## Command Line Usage

### Processing Excel Files

#### Process a single file
```bash
excel-analyze process /path/to/workbook.xlsx
```

#### Process an entire directory
```bash
excel-analyze process /path/to/excel/files --recursive
```

#### Process with custom options
```bash
excel-analyze process /path/to/files \
  --recursive \
  --drop-empty-rows \
  --drop-empty-columns \
  --clean-column-names \
  --null-threshold 0.8
```

### Analyzing Workbooks

#### Get detailed information about a workbook
```bash
excel-analyze analyze /path/to/workbook.xlsx
```

This will show:
- File information (size, sheets count)
- Sheet details (dimensions, column types)
- Column analysis (data types, null counts, sample values)

#### List all processed workbooks
```bash
excel-analyze list-workbooks
```

### Querying Data

#### Query data from a specific sheet
```bash
excel-analyze query workbook_name sheet_name
```

#### Apply filters to your query
```bash
excel-analyze query sales_data summary --filter "revenue > 1000" --limit 50
```

#### Available filter expressions
- Numeric comparisons: `revenue > 1000`, `quantity <= 50`
- String matching: `product_name.str.contains('Widget')`
- Date filtering: `date >= '2024-01-01'`
- Complex conditions: `(revenue > 1000) & (quantity > 10)`

### Database Management

#### Initialize database tables
```bash
excel-analyze init-db
```

#### Reset database (removes all data)
```bash
excel-analyze reset-db --confirm
```

## Web Interface

### Starting the Server

#### Development mode
```bash
python manage.py runserver
```

#### Production mode
```bash
gunicorn excel_analyzing.web.wsgi:application
```

### Web Features

#### Dashboard
- Overview of processed workbooks
- Processing statistics
- Recent activity

#### Workbook Management
- Upload and process new workbooks
- View workbook details and metadata
- Browse sheet structure and column information

#### Data Explorer
- Interactive data browsing
- Filter and sort functionality
- Export capabilities

#### Processing Monitor
- Real-time processing status
- Progress tracking
- Error reporting

## Python API

### Basic Usage

```python
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions

# Create pipeline
pipeline = ExcelPipeline()

# Process a single workbook
result = pipeline.process_workbook("data.xlsx")
print(f"Processed {result.rows_processed} rows in {result.processing_time_seconds:.2f}s")

# Process entire directory
results = pipeline.process_directory("/path/to/excel/files")
successful = [r for r in results if r.success]
print(f"Successfully processed {len(successful)} files")
```

### Custom Processing Options

```python
from excel_analyzing.models.schemas import ProcessingOptions

# Configure processing
options = ProcessingOptions(
    drop_empty_rows=True,
    drop_empty_columns=True,
    clean_column_names=True,
    infer_data_types=True,
    null_threshold=0.9,
    max_sample_size=100
)

pipeline = ExcelPipeline(options)
```

### Working with Data

```python
from excel_analyzing.pipeline.processor import ExcelDataProcessor

processor = ExcelDataProcessor()

# Load workbook
workbook_info = processor.load_workbook("sales_data.xlsx")

# Get processed dataframe
df = processor.get_dataframe("sales_data", "summary")

# Apply filters
filtered_df = processor.apply_filter("sales_data", "summary", "revenue > 1000")

# Apply transformations
aggregated_df = processor.apply_transformation("sales_data", "summary", {
    "operation": "group_by",
    "columns": ["product_category"],
    "agg_func": "sum"
})

# Get statistics
stats = processor.get_summary_statistics("sales_data", "summary")
print(f"Total rows: {stats['total_rows']}")
print(f"Memory usage: {stats['memory_usage_mb']:.2f} MB")
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://localhost/excel_analyzing` |
| `ENVIRONMENT` | Application environment | `development` |
| `DEBUG` | Enable debug mode | `False` |
| `MAX_FILE_SIZE_MB` | Maximum file size to process | `100` |
| `LOG_LEVEL` | Logging level | `INFO` |

### Processing Options

#### Drop Empty Data
- `drop_empty_rows`: Remove completely empty rows
- `drop_empty_columns`: Remove completely empty columns
- `null_threshold`: Drop columns with more than X% null values (0.0-1.0)

#### Data Type Inference
- `infer_data_types`: Automatically detect column data types
- `max_sample_size`: Number of rows to sample for type inference

#### Column Name Cleaning
- `clean_column_names`: Normalize column names (remove special characters, convert to lowercase)

## Best Practices

### File Organization
- Use descriptive file names
- Organize files in logical directory structures
- Keep backup copies of original files

### Data Quality
- Ensure first row contains column headers
- Avoid merged cells in data areas
- Use consistent data formats within columns

### Performance
- Process large files during off-peak hours
- Use appropriate null thresholds to avoid memory issues
- Monitor system resources during processing

### Security
- Store sensitive Excel files in secure locations
- Use environment variables for database credentials
- Regularly backup processed data

## Troubleshooting

### Common Issues

#### File Not Processing
- Check file permissions
- Verify file is not corrupted
- Ensure file size is within limits

#### Memory Errors
- Reduce `max_sample_size`
- Increase `null_threshold` to drop sparse columns
- Process files individually instead of batch processing

#### Database Connection Errors
- Verify PostgreSQL is running
- Check `DATABASE_URL` configuration
- Ensure database exists and user has permissions

#### Type Inference Issues
- Disable `infer_data_types` if causing problems
- Check for mixed data types in columns
- Review sample data for inconsistencies

### Getting Help

1. Check the logs for detailed error messages
2. Review the API documentation for programmatic access
3. Submit issues on GitHub with:
   - Error messages
   - Sample files (if possible)
   - System information

### Performance Tuning

#### For Large Files
```python
options = ProcessingOptions(
    drop_empty_rows=True,
    drop_empty_columns=True,
    null_threshold=0.95,  # More aggressive null filtering
    max_sample_size=50    # Smaller sample size
)
```

#### For Many Small Files
```python
# Process in batches
import os
from pathlib import Path

def process_in_batches(directory, batch_size=10):
    files = list(Path(directory).glob("*.xlsx"))
    for i in range(0, len(files), batch_size):
        batch = files[i:i+batch_size]
        for file in batch:
            result = pipeline.process_workbook(file)
            print(f"Processed: {file.name}")
```