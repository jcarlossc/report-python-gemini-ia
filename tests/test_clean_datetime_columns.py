import pandas as pd
import pytest

from report_python_gemini_ia.transformation.clean_datetime_columns import (
    get_clean_datetime_columns,
)


def test_convert_datetime_values() -> None:
    """Converte valores textuais para datetime."""
    df = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "2024-02-15", "2024-03-20"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "format": "%Y-%m-%d",
            "nullable": False,
        },
    }

    result = get_clean_datetime_columns(df, config)

    assert pd.api.types.is_datetime64_ns_dtype(result["order_date"].dtype)


def test_convert_datetime_with_format() -> None:
    """Respeita o formato de data definido no schema."""
    df = pd.DataFrame(
        {
            "order_date": ["10/01/2024", "15/02/2024"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "format": "%d/%m/%Y",
        },
    }

    result = get_clean_datetime_columns(df, config)

    assert result.loc[0, "order_date"] == pd.Timestamp("2024-01-10")


def test_convert_invalid_values_to_nat(
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Converte datas inválidas para NaT quando permitido."""
    df = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "invalid", "2024-03-20"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "format": "%Y-%m-%d",
            "nullable": True,
        },
    }

    with caplog.at_level("WARNING"):
        result = get_clean_datetime_columns(df, config)

    assert result["order_date"].isna().sum() == 1
    assert "valor(es) inválido(s)" in caplog.text


def test_reject_null_when_not_nullable() -> None:
    """Rejeita datas ausentes quando nullable é False."""
    df = pd.DataFrame(
        {
            "order_date": ["2024-01-10", None],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "nullable": False,
        },
    }

    with pytest.raises(ValueError, match="não permite valores nulos"):
        get_clean_datetime_columns(df, config)


def test_reject_invalid_date_when_not_nullable() -> None:
    """Rejeita datas inválidas quando nullable é False."""
    df = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "invalid"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "nullable": False,
        },
    }

    with pytest.raises(ValueError, match="não permite valores nulos"):
        get_clean_datetime_columns(df, config)


def test_ignore_non_datetime_columns() -> None:
    """Ignora colunas que não estejam configuradas como datetime."""
    df = pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "customer_name": ["Carlos", "Maria", "João"],
        }
    )

    config: dict[str, dict[str, object]] = {
        "order_id": {
            "type": "int64",
        },
        "customer_name": {
            "type": "string",
        },
    }

    result = get_clean_datetime_columns(df, config)

    pd.testing.assert_frame_equal(result, df)


def test_preserve_original_dataframe() -> None:
    """Preserva o DataFrame original durante a conversão."""
    df = pd.DataFrame(
        {
            "order_date": ["2024-01-10", "2024-02-15"],
        }
    )

    original = df.copy()

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
        },
    }

    get_clean_datetime_columns(df, config)

    pd.testing.assert_frame_equal(df, original)


def test_reject_non_dataframe() -> None:
    """Rejeita argumentos que não sejam DataFrames."""
    with pytest.raises(TypeError, match="DataFrame do pandas"):
        get_clean_datetime_columns(
            [],  # type: ignore[arg-type]
            {},
        )


def test_reject_non_dictionary_config() -> None:
    """Rejeita configurações que não sejam dicionários."""
    df = pd.DataFrame({"order_date": ["2024-01-10"]})

    with pytest.raises(TypeError, match="dicionário"):
        get_clean_datetime_columns(
            df,
            [],  # type: ignore[arg-type]
        )


def test_reject_missing_datetime_column() -> None:
    """Rejeita colunas datetime ausentes no DataFrame."""
    df = pd.DataFrame({"order_id": [1]})

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
        },
    }

    with pytest.raises(KeyError, match="order_date"):
        get_clean_datetime_columns(df, config)


def test_reject_invalid_nullable_configuration() -> None:
    """Rejeita configurações nullable que não sejam booleanas."""
    df = pd.DataFrame({"order_date": ["2024-01-10"]})

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "nullable": "false",
        },
    }

    with pytest.raises(TypeError, match="nullable"):
        get_clean_datetime_columns(df, config)


def test_reject_invalid_format_configuration() -> None:
    """Rejeita formatos de data que não sejam strings."""
    df = pd.DataFrame({"order_date": ["2024-01-10"]})

    config: dict[str, dict[str, object]] = {
        "order_date": {
            "type": "datetime",
            "format": 123,
        },
    }

    with pytest.raises(TypeError, match="format"):
        get_clean_datetime_columns(df, config)
