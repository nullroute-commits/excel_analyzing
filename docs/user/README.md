# User Guide

## Overview

Excel Analyzing is a Python-based tool for processing Excel workbooks and converting them into structured database format. It provides both command-line and web interfaces for analyzing Excel files.

## Target Users

- **Data Analysts**: Process and analyze Excel files with structured querying
- **Business Users**: Convert Excel reports into searchable database format
- **Developers**: Integrate Excel processing into automated workflows
- **Researchers**: Analyze research data stored in Excel format

## Getting Started

### Prerequisites

- Python 3.10 or higher
- PostgreSQL database (local or remote)
- Basic familiarity with command line or web interfaces

### Installation

**Quick Setup:**
```bash
# Clone the repository
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Initialize database
excel-analyze init-db
```

**Docker Setup (Recommended):**
```bash
# Start with Docker Compose
docker-compose -f docker-compose.dev.yml up

# Access web interface at http://localhost:8000
```

## Using the Command Line Interface

### Basic Commands

**Process Excel Files:**
```bash
# Process a single file
excel-analyze process data/sales_report.xlsx

# Process all Excel files in a directory
excel-analyze process data/ --recursive

# Process with custom options
excel-analyze process data/ \
    --drop-empty-rows \
    --clean-column-names \
    --null-threshold 0.8
```

**Analyze Workbooks:**
```bash
# Get detailed information about a workbook
excel-analyze analyze data/sales_report.xlsx

# List all processed workbooks
excel-analyze list-workbooks
```

**Query Data:**
```bash
# Query data from a processed workbook
excel-analyze query sales_report sheet1

# Query with filter conditions
excel-analyze query sales_report sheet1 --filter "revenue > 1000"

# Limit results
excel-analyze query sales_report sheet1 --limit 50
```

### Processing Options

**Data Cleaning Options:**
- `--drop-empty-rows`: Remove completely empty rows
- `--drop-empty-columns`: Remove completely empty columns  
- `--clean-column-names`: Normalize column names (remove spaces, special characters)
- `--null-threshold X`: Drop columns with more than X% null values (0.0-1.0)

**Example with Options:**
```bash
excel-analyze process data/messy_data.xlsx \
    --drop-empty-rows \
    --drop-empty-columns \
    --clean-column-names \
    --null-threshold 0.9
```

## Using the Web Interface

### Accessing the Interface

Start the web server:
```bash
# Development server
python manage.py runserver

# Or with Docker
docker-compose -f docker-compose.dev.yml up
```

Navigate to http://localhost:8000 in your web browser.

### Web Interface Features

**File Upload:**
1. Click "Upload File" button
2. Select Excel file (.xlsx, .xls, .xlsm, .xlsb)
3. Configure processing options
4. Click "Process" to start processing

**Browse Data:**
1. View list of processed workbooks
2. Click on workbook to see sheets
3. Click on sheet to view data
4. Use filters to search data

**Export Data:**
1. Navigate to desired sheet
2. Apply any filters
3. Click "Export" button
4. Choose format (CSV, Excel, JSON)

## Processing Configuration

### Basic Configuration

Create a `.env` file with your settings:
```bash
# Database settings
DATABASE_HOST=localhost
DATABASE_PORT=5432
DATABASE_NAME=excel_analyzing
DATABASE_USER=postgres
DATABASE_PASSWORD=your_password

# Processing settings
MAX_FILE_SIZE_MB=100
CHUNK_SIZE=1000
PROCESSING_TIMEOUT=300

# Debug mode (development only)
DEBUG=True
```

### Advanced Processing Options

```python
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions

# Configure processing options
options = ProcessingOptions(
    drop_empty_rows=True,           # Remove empty rows
    drop_empty_columns=True,        # Remove empty columns
    clean_column_names=True,        # Clean column names
    infer_data_types=True,         # Auto-detect data types
    null_threshold=0.9,            # Drop columns >90% null
    max_sample_size=100            # Sample size for type inference
)

# Create pipeline and process
pipeline = ExcelPipeline(options)
result = pipeline.process_workbook("data/file.xlsx")
```

## Data Types and Processing

### Supported Excel Formats
- **.xlsx**: Excel 2007+ format (recommended)
- **.xls**: Excel 97-2003 format
- **.xlsm**: Excel with macros (macros ignored)
- **.xlsb**: Excel binary format

### Automatic Data Type Detection

The system automatically detects and assigns data types:

- **String**: Text data, mixed content
- **Integer**: Whole numbers without decimals
- **Float**: Numbers with decimal places
- **Boolean**: True/False values
- **Date**: Date values in various formats
- **DateTime**: Date and time combinations

### Data Cleaning Features

**Column Name Cleaning:**
- Remove special characters
- Replace spaces with underscores
- Convert to lowercase
- Handle duplicate names

**Data Cleaning:**
- Remove completely empty rows and columns
- Handle null values based on threshold
- Preserve data integrity during cleaning
- Maintain original data references

## Querying and Analysis

### Basic Querying

**Command Line Queries:**
```bash
# Simple query
excel-analyze query workbook_name sheet_name

# With filter
excel-analyze query sales_data transactions \
    --filter "amount > 100 AND date >= '2024-01-01'"

# With limit and ordering
excel-analyze query sales_data transactions \
    --filter "category == 'Electronics'" \
    --limit 25
```

### Database Access

Processed data is stored in PostgreSQL and can be queried directly:

```sql
-- View all workbooks
SELECT * FROM workbooks;

-- View sheets in a workbook  
SELECT * FROM sheets WHERE workbook_id = 1;

-- View column information
SELECT * FROM columns WHERE sheet_id = 1;
```

## Troubleshooting

### Common Issues

**File Processing Errors:**
- Check file format is supported (.xlsx, .xls, .xlsm, .xlsb)
- Verify file size is under limit (default 100MB)
- Ensure file is not password protected
- Check file is not corrupted

**Database Connection Issues:**
- Verify PostgreSQL is running
- Check database credentials in .env file
- Ensure database exists and user has permissions
- Test connection with `excel-analyze init-db`

**Memory Issues:**
- Reduce file size or split large files
- Increase available system memory
- Process files individually instead of in batch
- Check system resources during processing

**Performance Issues:**
- Use SSD storage for better I/O performance
- Increase database connection pool size
- Process smaller chunks of data
- Monitor system resource usage

### Getting Help

**Log Files:**
- Application logs: `excel_analyzing.log`
- Web server logs: Check console output
- Database logs: PostgreSQL logs

**Debug Mode:**
```bash
# Enable debug logging
excel-analyze --log-level DEBUG process file.xlsx

# Web interface debug mode
DEBUG=True python manage.py runserver
```

**Common Solutions:**
1. Restart the application
2. Check database connectivity
3. Verify file permissions
4. Clear temporary files
5. Update to latest version

## Best Practices

### File Organization
- Use descriptive file names
- Organize files in logical directory structure
- Keep backup copies of original files
- Use consistent naming conventions

### Processing Workflow
1. Test with small files first
2. Review processing options for your data
3. Monitor processing logs for errors
4. Validate results after processing
5. Export processed data for backup

### Performance Optimization
- Process files during off-peak hours
- Use batch processing for multiple files
- Monitor system resources
- Regular database maintenance
- Archive old processed data

---

For additional support, please refer to the technical documentation or create an issue on the GitHub repository.