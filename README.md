# excel_analyzing
Analyze Excel workbooks like databases and sheets like tables

A Python tool for analyzing Excel files with database-like operations, providing insights into data structure, statistics, and query capabilities.

## Features

- Load and analyze Excel workbooks (.xlsx, .xls)
- Treat sheets like database tables
- Get comprehensive statistics and data summaries
- Query sheets using pandas query syntax
- Export analysis results to JSON

## Installation

1. Clone this repository:
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Command Line Interface

Analyze an entire workbook:
```bash
python main.py data.xlsx --summary
```

Analyze a specific sheet:
```bash
python main.py data.xlsx --sheet "Sheet1"
```

Query data in a sheet:
```bash
python main.py data.xlsx --sheet "Sheet1" --query "column_name > 100"
```

Save results to file:
```bash
python main.py data.xlsx --summary --output analysis.json
```

### Python API

```python
from excel_analyzer import ExcelAnalyzer

# Initialize analyzer
analyzer = ExcelAnalyzer('data.xlsx')

# List all sheets
sheets = analyzer.list_sheets()

# Analyze a specific sheet
analysis = analyzer.analyze_sheet('Sheet1')

# Query data
results = analyzer.query_sheet('Sheet1', 'column_name > 100')

# Get workbook summary
summary = analyzer.get_workbook_summary()
```

## Requirements

- Python 3.7+
- pandas >= 1.5.0
- openpyxl >= 3.0.0
- xlrd >= 2.0.0

## License

This project is licensed under the GPL v3 License - see the LICENSE file for details.
