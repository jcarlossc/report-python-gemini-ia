import pandas as pd
import pytest

from report_python_gemini_ia.transformation.clean_numeric_columns import (
    get_clean_numeric_columns,
)


def test_clean_integer_columns() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "20", "30"],
        }
    )

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": False,
        }
    }

    result = get_clean_numeric_columns(df, columns_dict)

    assert result["quantity"].tolist() == [10, 20, 30]
    assert result["quantity"].dtype == "int64"


def test_clean_nullable_integer_columns() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "", "30"],
        }
    )

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": True,
        }
    }

    result = get_clean_numeric_columns(df, columns_dict)

    assert result["quantity"].iloc[0] == 10
    assert pd.isna(result["quantity"].iloc[1])
    assert result["quantity"].iloc[2] == 30

    assert result["quantity"].dtype == "Int64"


def test_clean_float_columns() -> None:
    df = pd.DataFrame(
        {
            "unit_price": ["10.50", "20.75", "30.25"],
        }
    )

    columns_dict = {
        "unit_price": {
            "type": "float64",
            "nullable": False,
        }
    }

    result = get_clean_numeric_columns(df, columns_dict)

    assert result["unit_price"].tolist() == [
        10.50,
        20.75,
        30.25,
    ]

    assert result["unit_price"].dtype == "float64"


def test_clean_nullable_float_columns() -> None:
    df = pd.DataFrame(
        {
            "unit_price": ["10.50", "", "30.25"],
        }
    )

    columns_dict = {
        "unit_price": {
            "type": "float64",
            "nullable": True,
        }
    }

    result = get_clean_numeric_columns(df, columns_dict)

    assert result["unit_price"].iloc[0] == 10.50
    assert pd.isna(result["unit_price"].iloc[1])
    assert result["unit_price"].iloc[2] == 30.25

    assert result["unit_price"].dtype == "Float64"


def test_invalid_numeric_values_become_na() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "abc", "30"],
        }
    )

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": True,
        }
    }

    result = get_clean_numeric_columns(df, columns_dict)

    assert result["quantity"].iloc[0] == 10
    assert pd.isna(result["quantity"].iloc[1])
    assert result["quantity"].iloc[2] == 30


def test_integer_column_rejects_fractional_values() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "20.5", "30"],
        }
    )

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": True,
        }
    }

    with pytest.raises(
        ValueError,
        match="valores não inteiros",
    ):
        get_clean_numeric_columns(df, columns_dict)


def test_non_nullable_column_rejects_null_values() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "", "30"],
        }
    )

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": False,
        }
    }

    with pytest.raises(
        ValueError,
        match="não permite valores nulos",
    ):
        get_clean_numeric_columns(df, columns_dict)


def test_original_dataframe_is_preserved() -> None:
    df = pd.DataFrame(
        {
            "quantity": ["10", "20", "30"],
        }
    )

    original = df.copy(deep=True)

    columns_dict = {
        "quantity": {
            "type": "int64",
            "nullable": False,
        }
    }

    get_clean_numeric_columns(df, columns_dict)

    pd.testing.assert_frame_equal(df, original)


def test_missing_numeric_column_raises_key_error() -> None:
    df = pd.DataFrame(
        {
            "quantity": [10, 20],
        }
    )

    columns_dict = {
        "unit_price": {
            "type": "float64",
            "nullable": True,
        }
    }

    with pytest.raises(
        KeyError,
        match="Coluna numérica ausente",
    ):
        get_clean_numeric_columns(df, columns_dict)
