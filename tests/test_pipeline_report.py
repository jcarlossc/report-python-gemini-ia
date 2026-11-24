from pathlib import Path
from unittest.mock import Mock

import pandas as pd
import pytest

import report_python_gemini_ia.pipeline_report as pipeline


@pytest.fixture
def dataframe() -> pd.DataFrame:
    """Cria DataFrame para os testes."""

    return pd.DataFrame(
        {
            "order_id": [1, 2, 3],
            "quantity": [10, 20, 30],
            "total_sales": [100.0, 200.0, 300.0],
        }
    )


@pytest.fixture
def columns_dict() -> dict[str, dict[str, str]]:
    """Fornece configurações de colunas."""

    return {
        "order_id": {"type": "integer"},
        "quantity": {"type": "integer"},
        "total_sales": {"type": "float"},
    }


def test_load_configs_task(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Testa o carregamento das configurações YAML."""

    expected = {"logging": {"level": "INFO"}}

    mock_load = Mock(return_value=expected)

    monkeypatch.setattr(
        pipeline,
        "load_all_configs",
        mock_load,
    )

    result = pipeline.load_configs_task.fn(tmp_path)

    assert result == expected

    mock_load.assert_called_once_with(tmp_path)


def test_load_csv_task(
    monkeypatch: pytest.MonkeyPatch,
    dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Testa o carregamento dos dados CSV."""

    mock_load = Mock(return_value=dataframe)

    monkeypatch.setattr(
        pipeline,
        "get_load_csv",
        mock_load,
    )

    result = pipeline.load_csv_task.fn(tmp_path / "data.csv")

    pd.testing.assert_frame_equal(result, dataframe)

    mock_load.assert_called_once()


@pytest.mark.parametrize(
    ("task_name", "function_name"),
    [
        (
            "standardize_columns_task",
            "get_standardize_columns",
        ),
        (
            "clean_numeric_columns_task",
            "get_clean_numeric_columns",
        ),
        (
            "clean_category_columns_task",
            "get_clean_category_columns",
        ),
        (
            "clean_datetime_columns_task",
            "get_clean_datetime_columns",
        ),
    ],
)
def test_transformation_tasks(
    monkeypatch: pytest.MonkeyPatch,
    dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, str]],
    task_name: str,
    function_name: str,
) -> None:
    """Testa as Tasks de transformação dos dados."""

    mock_function = Mock(return_value=dataframe)

    monkeypatch.setattr(
        pipeline,
        function_name,
        mock_function,
    )

    task = getattr(pipeline, task_name)

    result = task.fn(dataframe, columns_dict)

    pd.testing.assert_frame_equal(result, dataframe)

    mock_function.assert_called_once_with(
        dataframe,
        columns_dict,
    )


def test_save_processed_data_task(
    dataframe: pd.DataFrame,
    tmp_path: Path,
) -> None:
    """Testa o salvamento do DataFrame processado."""

    processed_path = tmp_path / "data_processed" / "processed.csv"

    result = pipeline.save_processed_data_task.fn(
        dataframe,
        processed_path,
    )

    assert result == processed_path

    assert processed_path.exists()

    saved_df = pd.read_csv(processed_path)

    pd.testing.assert_frame_equal(
        saved_df,
        dataframe,
    )


def test_create_sales_summary_task(
    monkeypatch: pytest.MonkeyPatch,
    dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, str]],
) -> None:
    """Testa a geração do resumo analítico."""

    expected = {"total_sales": 600.0}

    mock_function = Mock(return_value=expected)

    monkeypatch.setattr(
        pipeline,
        "get_create_sales_summary",
        mock_function,
    )

    result = pipeline.create_sales_summary_task.fn(
        dataframe,
        columns_dict,
    )

    assert result == expected

    mock_function.assert_called_once_with(
        dataframe,
        columns_dict,
    )


def test_create_sales_charts_task(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Testa a geração dos gráficos."""

    analytics = {"total_sales": 600.0}

    expected = {"sales_chart": "sales.png"}

    mock_function = Mock(return_value=expected)

    monkeypatch.setattr(
        pipeline,
        "get_create_sales_charts",
        mock_function,
    )

    result = pipeline.create_sales_charts_task.fn(
        analytics,
        tmp_path,
    )

    assert result == expected

    mock_function.assert_called_once_with(
        analytics,
        tmp_path,
    )


def test_create_sales_report_task(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """Testa a geração do relatório PDF."""

    analytics = {"total_sales": 600.0}

    charts = {"sales_chart": "sales.png"}

    report_path = tmp_path / "report.pdf"

    mock_function = Mock()

    monkeypatch.setattr(
        pipeline,
        "get_create_sales_report",
        mock_function,
    )

    result = pipeline.create_sales_report_task.fn(
        analytics,
        charts,
        report_path,
    )

    assert result is None

    mock_function.assert_called_once_with(
        analytics=analytics,
        charts=charts,
        output_path=report_path,
        company_name="DataQuantum",
    )
