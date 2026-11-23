import pandas as pd
import pytest

from report_python_gemini_ia.transformation.clean_category_columns import (
    get_clean_category_columns,
)


def test_clean_category_columns() -> None:
    df = pd.DataFrame(
        {
            "customer_name": [
                "  Carlos  ",
                "Maria   Silva",
                "",
                None,
            ]
        }
    )

    columns_dict = {
        "customer_name": {
            "type": "string",
            "nullable": True,
        }
    }

    result = get_clean_category_columns(df, columns_dict)

    assert result["customer_name"].iloc[0] == "Carlos"
    assert result["customer_name"].iloc[1] == "Maria Silva"
    assert pd.isna(result["customer_name"].iloc[2])
    assert pd.isna(result["customer_name"].iloc[3])

    assert isinstance(result["customer_name"].dtype, pd.StringDtype)


def test_nullable_false_raises_value_error() -> None:
    df = pd.DataFrame({"customer_name": ["Carlos", ""]})

    columns_dict = {
        "customer_name": {
            "type": "string",
            "nullable": False,
        }
    }

    with pytest.raises(
        ValueError,
        match="não permite valores nulos",
    ):
        get_clean_category_columns(df, columns_dict)


def test_original_dataframe_is_preserved() -> None:
    df = pd.DataFrame({"customer_name": ["  Carlos  "]})

    original = df.copy(deep=True)

    columns_dict = {
        "customer_name": {
            "type": "string",
            "nullable": True,
        }
    }

    get_clean_category_columns(df, columns_dict)

    pd.testing.assert_frame_equal(df, original)


def test_missing_column_raises_key_error() -> None:
    df = pd.DataFrame({"customer_name": ["Carlos"]})

    columns_dict = {
        "customer_email": {
            "type": "string",
            "nullable": True,
        }
    }

    with pytest.raises(
        KeyError,
        match="Coluna configurada não encontrada",
    ):
        get_clean_category_columns(df, columns_dict)
