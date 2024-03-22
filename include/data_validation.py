from typing import List, Type
from pydantic import BaseModel, ValidationError

class Pokemon(BaseModel):
    Name: str
    Abilities: List[str]
    Types: List[str]
    Height: int
    Weight: int

class DataFrameValidationError(Exception):
    """Custom exception for DataFrame validation errors."""

def validate_df(df, model: Type[BaseModel]):
    """
    Validates each row of a df againsta  Pydantic Model
    Raises DataFrameValidationError if any row fails

    :param df: df to validate
    :param model: pydantic model to validate against
    :raises: DataFrameValidationError
    """
    errors = []

    for i, row in enumerate(df.to_dicts()):
        try:
            model(**row)
        except ValidationError as e:
            errors.append(f"Row {i} failed validation: {e}")

    if errors:
        error_message = "\n".join(errors)
        raise DataFrameValidationError(
            f"df validation failed with the following errors:\n{error_message}"
        )