"""Data cleaning utilities."""

import pandas as pd


def clean_data(
    data: pd.DataFrame, remove_duplicates: bool = True, handle_missing: str = "drop"
) -> pd.DataFrame:
    """Clean DataFrame by removing duplicates and handling missing values.

    Args:
        data: Input DataFrame
        remove_duplicates: Whether to remove duplicate rows
        handle_missing: How to handle missing values ("drop", "fill", "keep")

    Returns:
        Cleaned DataFrame
    """
    cleaned_data = data.copy()

    # Remove duplicates if requested
    if remove_duplicates:
        cleaned_data = cleaned_data.drop_duplicates()

    # Handle missing values
    if handle_missing == "drop":
        cleaned_data = cleaned_data.dropna()
    elif handle_missing == "fill":
        # Fill numeric columns with mean, string columns with mode
        for column in cleaned_data.columns:
            if pd.api.types.is_numeric_dtype(cleaned_data[column]):
                cleaned_data[column] = cleaned_data[column].fillna(
                    cleaned_data[column].mean()
                )
            else:
                mode_value = cleaned_data[column].mode()
                if len(mode_value) > 0:
                    cleaned_data[column] = cleaned_data[column].fillna(mode_value[0])
    # handle_missing == "keep" means do nothing

    return cleaned_data
