"""Data type inference utilities."""

from typing import Dict

import pandas as pd


def infer_data_types(data: pd.DataFrame) -> Dict[str, str]:
    """Infer data types for DataFrame columns.

    Args:
        data: Input DataFrame

    Returns:
        Dictionary mapping column names to inferred data types
    """
    type_mapping = {}

    for column in data.columns:
        series = data[column]

        # Check for numeric types first
        if pd.api.types.is_numeric_dtype(series):
            if pd.api.types.is_integer_dtype(series):
                type_mapping[column] = "integer"
            else:
                type_mapping[column] = "float"
        # Check for datetime
        elif pd.api.types.is_datetime64_any_dtype(series):
            type_mapping[column] = "datetime"
        # Check for boolean
        elif pd.api.types.is_bool_dtype(series):
            type_mapping[column] = "boolean"
        # Everything else is string
        else:
            type_mapping[column] = "string"

    return type_mapping
