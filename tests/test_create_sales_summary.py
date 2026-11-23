import pandas as pd
import pytest

from typing import Any

from report_python_gemini_ia.analytics.create_sales_summary import (
    get_create_sales_summary,
)


@pytest.fixture
def sales_dataframe() -> pd.DataFrame:
    """Cria um DataFrame de vendas para os testes."""

    return pd.DataFrame(
        {
            "order_id": ["001", "001", "002", "003"],
            "order_date": pd.to_datetime(
                [
                    "2025-01-10",
                    "2025-01-10",
                    "2025-02-15",
                    "2025-02-20",
                ]
            ),
            "customer_name": [
                "Carlos",
                "Carlos",
                "Maria",
                "João",
            ],
            "customer_segment": [
                "Corporate",
                "Corporate",
                "Consumer",
                "Consumer",
            ],
            "country": [
                "Brazil",
                "Brazil",
                "Brazil",
                "Portugal",
            ],
            "region": [
                "South",
                "South",
                "North",
                "Europe",
            ],
            "product_category": [
                "Technology",
                "Technology",
                "Furniture",
                "Technology",
            ],
            "product_name": [
                "Notebook",
                "Mouse",
                "Chair",
                "Notebook",
            ],
            "quantity": [2, 3, 1, 1],
            "unit_price": [1000.0, 50.0, 300.0, 1000.0],
            "discount_percent": [10.0, 5.0, 0.0, 10.0],
            "total_sales": [2000.0, 150.0, 300.0, 1000.0],
            "shipping_cost": [50.0, 10.0, 20.0, 30.0],
            "profit": [400.0, 30.0, 60.0, 200.0],
            "payment_method": [
                "Credit Card",
                "Credit Card",
                "Cash",
                "Pix",
            ],
        }
    )


@pytest.fixture
def columns_dict() -> dict[str, dict[str, object]]:
    """Fornece o schema de colunas utilizado nos testes."""

    return {
        "order_id": {"type": "string", "nullable": False},
        "order_date": {"type": "datetime", "nullable": False},
        "customer_name": {"type": "string", "nullable": False},
        "customer_segment": {"type": "string"},
        "country": {"type": "string"},
        "region": {"type": "string"},
        "product_category": {"type": "string"},
        "product_name": {"type": "string"},
        "quantity": {"type": "int64", "nullable": False},
        "unit_price": {"type": "float64"},
        "discount_percent": {"type": "float64"},
        "total_sales": {"type": "float64"},
        "shipping_cost": {"type": "float64"},
        "profit": {"type": "float64"},
        "payment_method": {"type": "string"},
    }


def test_create_sales_summary(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica a estrutura do resumo analítico."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    assert isinstance(result, dict)

    assert "metadata" in result
    assert "kpis" in result
    assert "products" in result
    assert "categories" in result
    assert "customers" in result
    assert "geography" in result
    assert "time" in result
    assert "payments" in result


def test_summary_metadata(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica os metadados do resumo."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    metadata = result["metadata"]

    assert metadata["rows"] == 4
    assert metadata["columns"] == 15
    assert metadata["orders"] == 3
    assert metadata["customers"] == 3
    assert metadata["products"] == 3
    assert metadata["categories"] == 2


def test_summary_period(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica o período das vendas."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    period = result["metadata"]["period"]

    assert period["start"].startswith("2025-01-10")
    assert period["end"].startswith("2025-02-20")


def test_summary_kpis(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica os indicadores principais de vendas."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    kpis = result["kpis"]

    assert kpis["revenue"] == 3450.00
    assert kpis["profit"] == 690.00
    assert kpis["orders"] == 3
    assert kpis["items_sold"] == 7
    assert kpis["average_ticket"] == 1150.00
    assert kpis["average_discount"] == 6.25
    assert kpis["margin"] == 20.00
    assert kpis["shipping_cost"] == 110.00


def test_summary_products(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas de produtos."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    products = result["products"]

    assert products["top_revenue"]["Notebook"] == 3000.00
    assert products["top_revenue"]["Mouse"] == 150.00
    assert products["top_quantity"]["Mouse"] == 3
    assert products["lowest_revenue"]["Chair"] == 300.00


def test_summary_categories(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas de categorias."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    categories = result["categories"]

    assert categories["revenue"]["Technology"] == 3150.00
    assert categories["revenue"]["Furniture"] == 300.00
    assert categories["quantity"]["Technology"] == 6
    assert categories["profit"]["Technology"] == 630.00


def test_summary_customers(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas de clientes."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    customers = result["customers"]

    assert customers["revenue"]["Carlos"] == 2150.00
    assert customers["revenue"]["Maria"] == 300.00
    assert customers["orders"]["Carlos"] == 1
    assert customers["segments"]["Corporate"] == 2150.00


def test_summary_geography(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas geográficas."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    geography = result["geography"]

    assert geography["countries"]["Brazil"] == 2450.00
    assert geography["countries"]["Portugal"] == 1000.00
    assert geography["regions"]["South"] == 2150.00


def test_summary_time(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas temporais."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    time = result["time"]

    assert time["year"][2025] == 3450.00
    assert time["month"]["2025-01"] == 2150.00
    assert time["month"]["2025-02"] == 1300.00
    assert time["weekday"]["Friday"] == 2150.00


def test_summary_payments(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica as métricas de pagamento."""

    result: dict[str, Any] = get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    payments = result["payments"]

    assert payments["methods"]["Credit Card"] == 2150.00
    assert payments["methods"]["Cash"] == 300.00
    assert payments["methods"]["Pix"] == 1000.00

    assert payments["orders"]["Credit Card"] == 1
    assert payments["orders"]["Cash"] == 1
    assert payments["orders"]["Pix"] == 1


def test_reject_non_dataframe(
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Rejeita argumentos que não sejam DataFrame."""

    with pytest.raises(
        TypeError,
        match="pandas DataFrame",
    ):
        get_create_sales_summary([], columns_dict)  # type: ignore[arg-type]


def test_reject_invalid_columns_dict(
    sales_dataframe: pd.DataFrame,
) -> None:
    """Rejeita schema que não seja um dicionário."""

    with pytest.raises(
        TypeError,
        match="dicionário",
    ):
        get_create_sales_summary(
            sales_dataframe,
            [],  # type: ignore[arg-type]
        )


def test_reject_empty_dataframe(
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Rejeita DataFrame vazio."""

    with pytest.raises(
        ValueError,
        match="vazio",
    ):
        get_create_sales_summary(
            pd.DataFrame(),
            columns_dict,
        )


def test_reject_empty_columns_dict(
    sales_dataframe: pd.DataFrame,
) -> None:
    """Rejeita schema vazio."""

    with pytest.raises(
        ValueError,
        match="schema de colunas está vazio",
    ):
        get_create_sales_summary(
            sales_dataframe,
            {},
        )


def test_reject_missing_columns(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Rejeita colunas do schema ausentes no DataFrame."""

    columns_dict = columns_dict.copy()
    columns_dict["unknown_column"] = {
        "type": "string",
    }

    with pytest.raises(
        KeyError,
        match="Colunas obrigatórias ausentes",
    ):
        get_create_sales_summary(
            sales_dataframe,
            columns_dict,
        )


def test_preserve_original_dataframe(
    sales_dataframe: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> None:
    """Verifica se o DataFrame original permanece inalterado."""

    original = sales_dataframe.copy(deep=True)

    get_create_sales_summary(
        sales_dataframe,
        columns_dict,
    )

    pd.testing.assert_frame_equal(
        sales_dataframe,
        original,
    )
