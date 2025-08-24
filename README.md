# Excel Analyzing

A comprehensive Python pipeline for analyzing Excel workbooks like databases, treating workbooks as databases and sheets as tables. Built with PEP8 standards and object-oriented design principles.

## Features

- **Excel Processing Pipeline**: Recursively discover and process Excel workbooks (.xlsx, .xls, .xlsm, .xlsb)
- **Database-like Treatment**: Treat workbooks as databases and sheets as tables with proper schema detection
- **Data Type Inference**: Automatically detect column data types (string, integer, float, boolean, datetime, date)
- **Data Cleaning**: Drop empty rows/columns, clean column names, handle null values
- **Multiple Environments**: Development, test, and production configurations
- **Web Interface**: Django-based web interface for managing and querying data
- **REST API**: RESTful API for programmatic access
- **Command Line Interface**: Rich CLI for batch processing and analysis
- **Database Storage**: PostgreSQL backend with SQLAlchemy ORM
- **Validation**: Pydantic models for data validation and serialization
- **Testing**: Comprehensive test suite with pytest
- **Documentation**: Detailed markdown documentation

## Architecture

The project follows a layered architecture:

```
excel_analyzing/
├── core/              # Core configuration and settings
├── models/            # Data models (Pydantic schemas, SQLAlchemy models)
├── pipeline/          # Excel processing pipeline
├── web/               # Django web interface
├── utils/             # Utility functions
└── cli.py             # Command line interface
```

## Technologies Used

- **Python 3.9+**: Core programming language
- **Pandas**: Data manipulation and analysis
- **Pydantic**: Data validation and serialization
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database
- **Django**: Web framework
- **Django REST Framework**: API development
- **Click**: Command line interface
- **Rich**: Terminal formatting
- **pytest**: Testing framework
- **Black**: Code formatting
- **Flake8**: Code linting

## Installation

### Prerequisites

- Python 3.9 or higher
- PostgreSQL 12 or higher
- Git

### Development Setup

1. Clone the repository:
```bash
git clone https://github.com/nullroute-commits/excel_analyzing.git
cd excel_analyzing
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements-dev.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Initialize the database:
```bash
excel-analyze init-db
```

### Production Setup

1. Install production dependencies:
```bash
pip install -r requirements-prod.txt
```

2. Set up environment variables for production:
```bash
export ENVIRONMENT=production
export DATABASE_URL=postgresql://user:password@host:port/database
export DJANGO_SECRET_KEY=your-secret-key
export ALLOWED_HOSTS=your-domain.com
```

3. Initialize the database:
```bash
excel-analyze init-db
```

4. Run with Gunicorn:
```bash
gunicorn excel_analyzing.web.wsgi:application
```

## Usage

### Command Line Interface

Process Excel files in a directory:
```bash
excel-analyze process /path/to/excel/files --recursive
```

Analyze a specific workbook:
```bash
excel-analyze analyze /path/to/workbook.xlsx
```

List processed workbooks:
```bash
excel-analyze list-workbooks
```

Query data from a sheet:
```bash
excel-analyze query workbook_name sheet_name --filter "column > 100"
```

### Python API

```python
from excel_analyzing.pipeline.orchestrator import ExcelPipeline
from excel_analyzing.models.schemas import ProcessingOptions

# Create pipeline with custom options
options = ProcessingOptions(
    drop_empty_rows=True,
    clean_column_names=True,
    null_threshold=0.8
)
pipeline = ExcelPipeline(options)

# Process a single workbook
result = pipeline.process_workbook("path/to/workbook.xlsx")

# Process entire directory
results = pipeline.process_directory("path/to/directory")
```

### Web Interface

Start the Django development server:
```bash
python manage.py runserver
```

Access the web interface at `http://localhost:8000`

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ENVIRONMENT` | Application environment (development/test/production) | development |
| `DATABASE_URL` | PostgreSQL connection URL | postgresql://localhost/excel_analyzing |
| `DEBUG` | Enable debug mode | False |
| `DJANGO_SECRET_KEY` | Django secret key | dev-secret-key |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | localhost,127.0.0.1 |
| `MAX_FILE_SIZE_MB` | Maximum file size to process (MB) | 100 |
| `LOG_LEVEL` | Logging level | INFO |

### Processing Options

Configure Excel processing behavior:

```python
from excel_analyzing.models.schemas import ProcessingOptions

options = ProcessingOptions(
    drop_empty_rows=True,           # Drop completely empty rows
    drop_empty_columns=True,        # Drop completely empty columns
    infer_data_types=True,          # Automatically infer column data types
    clean_column_names=True,        # Clean and normalize column names
    max_sample_size=100,            # Maximum sample size for type inference
    null_threshold=0.9              # Drop columns with >90% null values
)
```

## Data Pipeline

### 1. Discovery
- Recursively scan directories for Excel files
- Filter by file extension (.xlsx, .xls, .xlsm, .xlsb)
- Skip temporary files (starting with ~$)
- Validate file accessibility and size

### 2. Processing
- Load workbook metadata
- Detect header rows automatically
- Clean column names and sheet names
- Infer data types for each column
- Drop empty rows and columns
- Handle null values based on threshold

### 3. Storage
- Save workbook metadata to PostgreSQL
- Store sheet and column information
- Track processing results and errors
- Support for incremental updates

### 4. Querying
- SQL-like queries through pandas
- Filtering and transformation support
- Aggregation and grouping operations
- Export capabilities

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=excel_analyzing --cov-report=html
```

Run specific test categories:
```bash
pytest tests/unit/          # Unit tests only
pytest tests/integration/   # Integration tests only
```

## Code Quality

Format code with Black:
```bash
black excel_analyzing/
```

Lint with Flake8:
```bash
flake8 excel_analyzing/
```

Type checking with mypy:
```bash
mypy excel_analyzing/
```

## Deployment

### Docker

Build the Docker image:
```bash
docker build -t excel-analyzing .
```

Run with Docker Compose:
```bash
docker-compose up -d
```

### Environment-Specific Deployments

The application supports three environments:

1. **Development**: Local development with debug enabled
2. **Test**: Automated testing with in-memory database
3. **Production**: Production deployment with optimized settings

## API Documentation

### REST Endpoints

- `GET /api/workbooks/` - List workbooks
- `POST /api/workbooks/` - Upload and process workbook
- `GET /api/workbooks/{id}/` - Get workbook details
- `GET /api/workbooks/{id}/sheets/` - List sheets in workbook
- `GET /api/sheets/{id}/data/` - Get sheet data
- `POST /api/sheets/{id}/query/` - Query sheet data

### WebSocket Events

- `workbook.processing.started` - Processing started
- `workbook.processing.completed` - Processing completed
- `workbook.processing.failed` - Processing failed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes following PEP8 standards
4. Add tests for new functionality
5. Run the test suite
6. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the test examples
