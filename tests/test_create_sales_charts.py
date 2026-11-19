from __future__ import annotations

from pathlib import Path

import pytest

from report_python_gemini_ia.visualization.create_sales_charts import (
    get_create_sales_charts,
)


@pytest.fixture
def sales_summary() -> dict[str, object]:
    """Fornece um resumo de vendas válido para os testes."""

    return {
        "kpis": {
            "revenue": 3450.00,
            "profit": 690.00,
            "orders": 3,
            "average_ticket": 1150.00,
            "margin": 20.00,
        },
        "products": {
            "top_revenue": {
                "Notebook": 3000.00,
                "Mouse": 450.00,
            },
            "top_quantity": {
                "Mouse": 5,
                "Notebook": 2,
            },
            "lowest_revenue": {
                "Mouse": 450.00,
                "Notebook": 3000.00,
            },
        },
        "categories": {
            "revenue": {
                "Eletrônicos": 3450.00,
            },
            "quantity": {
                "Eletrônicos": 7,
            },
            "profit": {
                "Eletrônicos": 690.00,
            },
        },
        "customers": {
            "revenue": {
                "Carlos": 2000.00,
                "Maria": 1450.00,
            },
            "orders": {
                "Carlos": 2,
                "Maria": 1,
            },
            "segments": {
                "Corporate": 2000.00,
                "Consumer": 1450.00,
            },
        },
        "geography": {
            "countries": {
                "Brazil": 3450.00,
            },
            "regions": {
                "Northeast": 3450.00,
            },
        },
        "time": {
            "year": {
                "2026": 3450.00,
            },
            "month": {
                "2026-01": 2150.00,
                "2026-02": 1300.00,
            },
            "weekday": {
                "Monday": 1000.00,
                "Tuesday": 500.00,
                "Friday": 1950.00,
            },
        },
        "payments": {
            "methods": {
                "Credit Card": 2000.00,
                "Pix": 1450.00,
            },
            "orders": {
                "Credit Card": 2,
                "Pix": 1,
            },
        },
    }


def test_create_all_sales_charts(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Verifica a criação de todos os gráficos."""

    output_dir = tmp_path / "reports" / "charts"

    result = get_create_sales_charts(
        summary=sales_summary,
        output_dir=output_dir,
    )

    assert len(result) == 17
    assert output_dir.exists()

    for path in result.values():
        assert path.exists()
        assert path.is_file()
        assert path.suffix == ".png"
        assert path.stat().st_size > 0


def test_return_chart_paths(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Verifica se o retorno contém os caminhos dos gráficos."""

    output_dir = tmp_path / "charts"

    result = get_create_sales_charts(
        summary=sales_summary,
        output_dir=output_dir,
    )

    assert isinstance(result, dict)

    assert result["01_kpis.png"] == output_dir / "01_kpis.png"

    assert (
        result["02_products_top_revenue.png"]
        == output_dir / "02_products_top_revenue.png"
    )

    assert result["17_payments_orders.png"] == output_dir / "17_payments_orders.png"


def test_create_output_directory(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Verifica a criação automática do diretório."""

    output_dir = tmp_path / "new_folder" / "charts"

    assert not output_dir.exists()

    get_create_sales_charts(
        summary=sales_summary,
        output_dir=output_dir,
    )

    assert output_dir.exists()
    assert output_dir.is_dir()


def test_reject_non_dict_summary(tmp_path: Path) -> None:
    """Rejeita resumo que não seja um dicionário."""

    with pytest.raises(
        TypeError,
        match="summary deve ser um dicionário",
    ):
        get_create_sales_charts(
            summary=[],  # type: ignore[arg-type]
            output_dir=tmp_path,
        )


def test_reject_empty_summary(tmp_path: Path) -> None:
    """Rejeita resumo vazio."""

    with pytest.raises(
        ValueError,
        match="O resumo está vazio",
    ):
        get_create_sales_charts(
            summary={},
            output_dir=tmp_path,
        )


def test_reject_invalid_output_dir(
    sales_summary: dict[str, object],
) -> None:
    """Rejeita diretório que não seja Path."""

    with pytest.raises(
        TypeError,
        match="output_dir deve ser um pathlib Path",
    ):
        get_create_sales_charts(
            summary=sales_summary,
            output_dir="reports/charts",  # type: ignore[arg-type]
        )


def test_reject_missing_section(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Rejeita seção obrigatória ausente."""

    invalid_summary = sales_summary.copy()
    invalid_summary.pop("products")

    with pytest.raises(
        KeyError,
        match="products",
    ):
        get_create_sales_charts(
            summary=invalid_summary,
            output_dir=tmp_path,
        )


def test_reject_missing_kpi(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Rejeita KPI obrigatório ausente."""

    kpis = sales_summary["kpis"]
    assert isinstance(kpis, dict)

    kpis.pop("revenue")

    with pytest.raises(
        KeyError,
        match="revenue",
    ):
        get_create_sales_charts(
            summary=sales_summary,
            output_dir=tmp_path,
        )


def test_reject_invalid_numeric_mapping(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Rejeita valores não numéricos nas métricas."""

    products = sales_summary["products"]
    assert isinstance(products, dict)

    products["top_revenue"] = {
        "Notebook": "invalido",
    }

    with pytest.raises(
        ValueError,
        match="Valor inválido em top_revenue",
    ):
        get_create_sales_charts(
            summary=sales_summary,
            output_dir=tmp_path,
        )


def test_reject_invalid_kpi(
    sales_summary: dict[str, object],
    tmp_path: Path,
) -> None:
    """Rejeita KPI com tipo inválido."""

    kpis = sales_summary["kpis"]
    assert isinstance(kpis, dict)

    kpis["profit"] = "invalido"

    with pytest.raises(
        KeyError,
        match="KPI ausente ou inválido: profit",
    ):
        get_create_sales_charts(
            summary=sales_summary,
            output_dir=tmp_path,
        )
