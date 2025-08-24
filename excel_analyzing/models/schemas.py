"""Pydantic data models for Excel analysis."""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


class DataType(str, Enum):
    """Supported data types for Excel columns."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    TIME = "time"


class ColumnInfo(BaseModel):
    """Information about a column in an Excel sheet."""

    name: str = Field(..., description="Column name from header")
    original_name: str = Field(..., description="Original column name before cleaning")
    position: int = Field(..., ge=0, description="Zero-based column position")
    data_type: DataType = Field(..., description="Detected data type")
    is_nullable: bool = Field(
        default=True, description="Whether column can contain null values"
    )
    sample_values: List[Any] = Field(
        default_factory=list, description="Sample values from column"
    )
    unique_count: Optional[int] = Field(
        None, ge=0, description="Number of unique values"
    )
    null_count: int = Field(default=0, ge=0, description="Number of null values")

    @validator("name")
    def validate_column_name(cls, v: str) -> str:
        """Ensure column name is valid."""
        if not v or not v.strip():
            raise ValueError("Column name cannot be empty")
        return v.strip()


class SheetInfo(BaseModel):
    """Information about an Excel sheet."""

    name: str = Field(..., description="Sheet name")
    original_name: str = Field(..., description="Original sheet name before cleaning")
    row_count: int = Field(..., ge=0, description="Total number of rows")
    column_count: int = Field(..., ge=0, description="Total number of columns")
    has_header: bool = Field(
        default=True, description="Whether first row contains headers"
    )
    header_row: int = Field(default=0, ge=0, description="Zero-based header row index")
    data_start_row: int = Field(
        default=1, ge=0, description="Zero-based data start row index"
    )
    columns: List[ColumnInfo] = Field(
        default_factory=list, description="Column information"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    @validator("name")
    def validate_sheet_name(cls, v: str) -> str:
        """Ensure sheet name is valid."""
        if not v or not v.strip():
            raise ValueError("Sheet name cannot be empty")
        return v.strip()

    @validator("data_start_row")
    def validate_data_start_row(cls, v: int, values: Dict[str, Any]) -> int:
        """Ensure data start row is after header row."""
        if "header_row" in values and v <= values["header_row"]:
            raise ValueError("Data start row must be after header row")
        return v


class WorkbookInfo(BaseModel):
    """Information about an Excel workbook."""

    file_path: Path = Field(..., description="Path to the Excel file")
    file_name: str = Field(..., description="Name of the Excel file")
    file_size_bytes: int = Field(..., ge=0, description="File size in bytes")
    sheet_count: int = Field(..., ge=0, description="Number of sheets in workbook")
    sheets: List[SheetInfo] = Field(
        default_factory=list, description="Sheet information"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    processed_at: Optional[datetime] = Field(
        None, description="When workbook was processed"
    )

    @validator("file_path")
    def validate_file_path(cls, v: Path) -> Path:
        """Ensure file path exists and is a file."""
        if not v.exists():
            raise ValueError(f"File does not exist: {v}")
        if not v.is_file():
            raise ValueError(f"Path is not a file: {v}")
        return v

    @validator("file_name")
    def validate_file_name(cls, v: str) -> str:
        """Ensure file name has valid Excel extension."""
        valid_extensions = {".xlsx", ".xls", ".xlsm", ".xlsb"}
        if not any(v.lower().endswith(ext) for ext in valid_extensions):
            raise ValueError(f"Invalid Excel file extension: {v}")
        return v

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            Path: str,
            datetime: lambda v: v.isoformat(),
        }


class ProcessingOptions(BaseModel):
    """Options for processing Excel files."""

    drop_empty_rows: bool = Field(
        default=True, description="Drop completely empty rows"
    )
    drop_empty_columns: bool = Field(
        default=True, description="Drop completely empty columns"
    )
    infer_data_types: bool = Field(
        default=True, description="Automatically infer column data types"
    )
    clean_column_names: bool = Field(
        default=True, description="Clean and normalize column names"
    )
    max_sample_size: int = Field(
        default=100, ge=1, description="Maximum sample size for type inference"
    )
    null_threshold: float = Field(
        default=0.9,
        ge=0,
        le=1,
        description="Threshold for dropping columns with too many nulls",
    )

    @validator("null_threshold")
    def validate_null_threshold(cls, v: float) -> float:
        """Ensure null threshold is between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Null threshold must be between 0 and 1")
        return v


class ProcessingResult(BaseModel):
    """Result of processing an Excel workbook."""

    workbook: WorkbookInfo = Field(..., description="Processed workbook information")
    success: bool = Field(..., description="Whether processing was successful")
    error_message: Optional[str] = Field(
        None, description="Error message if processing failed"
    )
    rows_processed: int = Field(
        default=0, ge=0, description="Total rows processed across all sheets"
    )
    columns_processed: int = Field(
        default=0, ge=0, description="Total columns processed across all sheets"
    )
    processing_time_seconds: float = Field(
        default=0, ge=0, description="Processing time in seconds"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        """Pydantic configuration."""

        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
