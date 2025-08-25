"""Schema detection utilities."""

from typing import Any, Dict

import pandas as pd


def detect_schema(data: pd.DataFrame) -> Dict[str, Any]:
    """Detect schema information from DataFrame.

    Args:
        data: Input DataFrame

    Returns:
        Dictionary containing schema information
    """
    schema = {
        "columns": [],
        "total_rows": len(data),
        "total_columns": len(data.columns),
        "nullable_columns": [],
        "primary_key_candidates": [],
        "data_quality": {},
    }

    for column in data.columns:
        series = data[column]

        column_info = {
            "name": column,
            "dtype": str(series.dtype),
            "nullable": series.isnull().any(),
            "unique_values": series.nunique(),
            "missing_count": series.isnull().sum(),
            "sample_values": series.dropna().head(3).tolist(),
        }

        schema["columns"].append(column_info)

        # Track nullable columns
        if column_info["nullable"]:
            schema["nullable_columns"].append(column)

        # Identify potential primary key candidates
        if (
            column_info["unique_values"] == len(data)
            and column_info["missing_count"] == 0
        ):
            schema["primary_key_candidates"].append(column)

    # Calculate data quality metrics
    total_cells = len(data) * len(data.columns)
    missing_cells = data.isnull().sum().sum()

    schema["data_quality"] = {
        "completeness": (
            (total_cells - missing_cells) / total_cells if total_cells > 0 else 0
        ),
        "duplicate_rows": len(data) - len(data.drop_duplicates()),
        "total_missing_values": int(missing_cells),
    }

    return schema
