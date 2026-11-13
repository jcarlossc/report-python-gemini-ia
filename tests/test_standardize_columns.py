import logging
from typing import cast

import pandas as pd
import pytest

from report_python_gemini_ia.transformation.standardize_columns import (
    get_standardize_columns,
)


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """Create a sample DataFrame."""
    return pd.DataFrame(
        {
            "Order ID": [1, 2],
            "Customer Name": ["Carlos", "Maria"],
            "Product-Category": ["Notebook", "Mouse"],
        }
    )


@pytest.fixture
def columns_dict() -> dict:
    """Return required columns."""
    return {
        "order_id": {"type": "string"},
        "customer_name": {"type": "string"},
        "product_category": {"type": "string"},
    }


def test_standardize_column_names(
    dataframe: pd.DataFrame,
    columns_dict: dict,
) -> None:
    """Standardize column names."""
    result = get_standardize_columns(dataframe, columns_dict)

    assert list(result.columns) == [
        "order_id",
        "customer_name",
        "product_category",
    ]


def test_convert_columns_to_lowercase() -> None:
    """Convert column names to lowercase."""
    df = pd.DataFrame({"ORDER_ID": [1]})

    result = get_standardize_columns(df, {"order_id": {}})

    assert "order_id" in result.columns


def test_remove_accents() -> None:
    """Remove accents from column names."""
    df = pd.DataFrame({"Descrição": [1]})

    result = get_standardize_columns(df, {"descricao": {}})

    assert "descricao" in result.columns


def test_preserve_accents_when_disabled() -> None:
    """Preserve accents when remove_accents is False."""
    df = pd.DataFrame({"Descrição": [1]})

    result = get_standardize_columns(
        df,
        {"descrição": {}},
        remove_accents=False,
    )

    assert "descrição" in result.columns


def test_replace_spaces_and_hyphens() -> None:
    """Replace spaces and hyphens with underscores."""
    df = pd.DataFrame({"Order Date": [1], "Product-Name": ["Notebook"]})

    result = get_standardize_columns(
        df,
        {"order_date": {}, "product_name": {}},
    )

    assert list(result.columns) == ["order_date", "product_name"]


def test_remove_special_characters() -> None:
    """Remove unsupported special characters."""
    df = pd.DataFrame({"Order@ID!": [1]})

    result = get_standardize_columns(df, {"orderid": {}})

    assert "orderid" in result.columns


def test_generate_unique_column_names() -> None:
    """Generate unique names for duplicated normalized columns."""
    df = pd.DataFrame([[1, 2]], columns=["Order ID", "order-id"])

    result = get_standardize_columns(df, {})

    assert list(result.columns) == ["order_id", "order_id_1"]


def test_generate_fallback_for_empty_names() -> None:
    """Generate fallback names for empty column names."""
    df = pd.DataFrame([[1, 2]], columns=["", "!!!"])

    result = get_standardize_columns(df, {})

    assert list(result.columns) == ["column", "column_1"]


def test_preserve_original_dataframe(
    dataframe: pd.DataFrame,
    columns_dict: dict,
) -> None:
    """Ensure the original DataFrame is not modified."""
    original = dataframe.copy()

    get_standardize_columns(dataframe, columns_dict)

    pd.testing.assert_frame_equal(dataframe, original)


def test_reject_non_dataframe() -> None:
    """Raise TypeError when df is not a pandas DataFrame."""
    with pytest.raises(TypeError, match="pandas DataFrame"):
        get_standardize_columns([], {})


def test_reject_invalid_remove_accents() -> None:
    """Raise TypeError when remove_accents is not a boolean."""
    df = pd.DataFrame({"order_id": [1]})

    with pytest.raises(TypeError, match="boolean"):
        get_standardize_columns(
            df,
            {},
            remove_accents=cast(bool, "True"),
        )


def test_reject_missing_columns(
    dataframe: pd.DataFrame,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Raise KeyError when required columns are missing."""
    required_columns: dict[str, dict[str, str]] = {
        "order_id": {},
        "missing_column": {},
    }

    with caplog.at_level(logging.WARNING):
        with pytest.raises(KeyError, match="missing_column"):
            get_standardize_columns(dataframe, required_columns)

    assert "Colunas ausentes" in caplog.text


def test_accept_empty_required_columns() -> None:
    """Accept an empty dictionary of required columns."""
    df = pd.DataFrame({"Order ID": [1]})

    result = get_standardize_columns(df, {})

    assert list(result.columns) == ["order_id"]
