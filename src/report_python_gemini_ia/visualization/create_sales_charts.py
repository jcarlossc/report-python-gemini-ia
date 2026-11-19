from __future__ import annotations

import logging
from collections.abc import Mapping
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter


def get_create_sales_charts(
    summary: dict[str, object],
    output_dir: Path = Path("reports/charts"),
) -> dict[str, Path]:
    logger = logging.getLogger(__name__)

    NAVY = "#022287"
    CYAN = "#3ADDF7"
    BLUE = "#0466C8"
    GRAY = "#979DAC"
    DARK = "#010417"

    generated_charts: dict[str, Path] = {}

    currency_formatter = FuncFormatter(
        lambda value, _: f"R$ {value:,.0f}".replace(",", ".")
    )

    try:
        logger.info("Iniciando criação dos gráficos de vendas.")

        if not isinstance(summary, dict):
            raise TypeError("summary deve ser um dicionário.")

        if not summary:
            raise ValueError("O resumo está vazio.")

        if not isinstance(output_dir, Path):
            raise TypeError("output_dir deve ser um pathlib Path.")

        output_dir.mkdir(parents=True, exist_ok=True)

        def get_section(
            section_name: str,
        ) -> Mapping[str, object]:
            section = summary.get(section_name)

            if not isinstance(section, Mapping):
                raise KeyError(f"Seção obrigatória ausente ou inválida: {section_name}")

            return section

        def get_numeric_mapping(
            section: Mapping[str, object],
            key: str,
        ) -> dict[str, float]:
            values = section.get(key)

            if not isinstance(values, Mapping):
                raise KeyError(f"Métrica ausente ou inválida: {key}")

            result: dict[str, float] = {}

            for label, value in values.items():
                if not isinstance(value, (int, float)):
                    raise ValueError(f"Valor inválido em {key}: {label}.")

                result[str(label)] = float(value)

            return result

        def save_bar_chart(
            title: str,
            values: dict[str, float],
            filename: str,
            color: str = NAVY,
            currency: bool = False,
        ) -> None:
            if not values:
                return

            labels = list(values.keys())
            numbers = list(values.values())

            fig, ax = plt.subplots(figsize=(11, 6))

            try:
                bars = ax.barh(
                    labels[::-1],
                    numbers[::-1],
                    color=color,
                    edgecolor="none",
                    height=0.65,
                )

                ax.set_title(
                    title,
                    fontsize=15,
                    fontweight="bold",
                    color=DARK,
                    pad=18,
                )

                ax.set_xlabel(
                    "Valor",
                    fontsize=10,
                    color=DARK,
                )

                if currency:
                    ax.xaxis.set_major_formatter(currency_formatter)

                ax.bar_label(
                    bars,
                    fmt="%.0f",
                    padding=5,
                    fontsize=9,
                    color=DARK,
                )

                ax.grid(
                    axis="x",
                    linestyle="--",
                    alpha=0.25,
                )

                ax.set_axisbelow(True)
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                ax.spines["left"].set_visible(False)
                ax.spines["bottom"].set_color(GRAY)

                ax.tick_params(
                    axis="both",
                    labelsize=9,
                    colors=DARK,
                )

                fig.tight_layout()

                path = output_dir / filename
                fig.savefig(
                    path,
                    dpi=150,
                    bbox_inches="tight",
                    facecolor="white",
                )

                generated_charts[filename] = path

            finally:
                plt.close(fig)

        def save_line_chart(
            title: str,
            values: dict[str, float],
            filename: str,
            color: str = BLUE,
        ) -> None:
            if not values:
                return

            labels = list(values.keys())
            numbers = list(values.values())

            fig, ax = plt.subplots(figsize=(11, 5))

            try:
                ax.plot(
                    labels,
                    numbers,
                    marker="o",
                    linewidth=2.5,
                    markersize=7,
                    color=color,
                )

                ax.set_title(
                    title,
                    fontsize=15,
                    fontweight="bold",
                    color=DARK,
                    pad=18,
                )

                ax.set_ylabel("Faturamento", color=DARK)
                ax.yaxis.set_major_formatter(currency_formatter)

                ax.grid(
                    axis="y",
                    linestyle="--",
                    alpha=0.25,
                )

                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)

                ax.tick_params(
                    axis="x",
                    rotation=35,
                    labelsize=9,
                )

                fig.tight_layout()

                path = output_dir / filename
                fig.savefig(
                    path,
                    dpi=150,
                    bbox_inches="tight",
                    facecolor="white",
                )

                generated_charts[filename] = path

            finally:
                plt.close(fig)

        kpis = get_section("kpis")

        required_kpis = {
            "revenue": "Faturamento",
            "profit": "Lucro",
            "orders": "Pedidos",
            "average_ticket": "Ticket médio",
            "margin": "Margem",
        }

        fig, axes = plt.subplots(
            1,
            5,
            figsize=(16, 4),
        )

        try:
            for ax, (key, label) in zip(
                axes,
                required_kpis.items(),
            ):
                value = kpis.get(key)

                if not isinstance(value, (int, float)):
                    raise KeyError(f"KPI ausente ou inválido: {key}")

                if key in {"revenue", "profit", "average_ticket"}:
                    formatted = f"R$ {value:,.2f}"
                elif key == "margin":
                    formatted = f"{value:.2f}%"
                else:
                    formatted = f"{value:,.0f}"

                ax.set_facecolor("#F4F7FB")

                ax.text(
                    0.5,
                    0.65,
                    label,
                    ha="center",
                    fontsize=11,
                    color=GRAY,
                    transform=ax.transAxes,
                )

                ax.text(
                    0.5,
                    0.40,
                    formatted,
                    ha="center",
                    fontsize=14,
                    fontweight="bold",
                    color=NAVY,
                    transform=ax.transAxes,
                )

                ax.set_xticks([])
                ax.set_yticks([])

                for spine in ax.spines.values():
                    spine.set_visible(False)

            fig.suptitle(
                "Indicadores de desempenho de vendas",
                fontsize=17,
                fontweight="bold",
                color=DARK,
            )

            fig.tight_layout()

            filename = "01_kpis.png"
            path = output_dir / filename

            fig.savefig(
                path,
                dpi=150,
                bbox_inches="tight",
                facecolor="white",
            )

            generated_charts[filename] = path

        finally:
            plt.close(fig)

        products = get_section("products")

        save_bar_chart(
            "Top 10 produtos por faturamento",
            get_numeric_mapping(products, "top_revenue"),
            "02_products_top_revenue.png",
            NAVY,
            currency=True,
        )

        save_bar_chart(
            "Top 10 produtos por quantidade vendida",
            get_numeric_mapping(products, "top_quantity"),
            "03_products_top_quantity.png",
            CYAN,
        )

        save_bar_chart(
            "10 produtos com menor faturamento",
            get_numeric_mapping(products, "lowest_revenue"),
            "04_products_lowest_revenue.png",
            GRAY,
            currency=True,
        )

        categories = get_section("categories")

        save_bar_chart(
            "Faturamento por categoria",
            get_numeric_mapping(categories, "revenue"),
            "05_categories_revenue.png",
            NAVY,
            currency=True,
        )

        save_bar_chart(
            "Quantidade vendida por categoria",
            get_numeric_mapping(categories, "quantity"),
            "06_categories_quantity.png",
            CYAN,
        )

        save_bar_chart(
            "Lucro por categoria",
            get_numeric_mapping(categories, "profit"),
            "07_categories_profit.png",
            BLUE,
            currency=True,
        )

        customers = get_section("customers")

        save_bar_chart(
            "Top 10 clientes por faturamento",
            get_numeric_mapping(customers, "revenue"),
            "08_customers_revenue.png",
            NAVY,
            currency=True,
        )

        save_bar_chart(
            "Top 10 clientes por quantidade de pedidos",
            get_numeric_mapping(customers, "orders"),
            "09_customers_orders.png",
            CYAN,
        )

        save_bar_chart(
            "Faturamento por segmento de clientes",
            get_numeric_mapping(customers, "segments"),
            "10_customers_segments.png",
            BLUE,
            currency=True,
        )

        geography = get_section("geography")

        save_bar_chart(
            "Faturamento por país",
            get_numeric_mapping(geography, "countries"),
            "11_geography_countries.png",
            NAVY,
            currency=True,
        )

        save_bar_chart(
            "Faturamento por região",
            get_numeric_mapping(geography, "regions"),
            "12_geography_regions.png",
            CYAN,
            currency=True,
        )

        time = get_section("time")

        year_values = get_numeric_mapping(time, "year")
        month_values = get_numeric_mapping(time, "month")
        weekday_values = get_numeric_mapping(time, "weekday")

        year_values = dict(sorted(year_values.items()))

        month_values = dict(sorted(month_values.items()))

        weekday_order = [
            "Monday",
            "Tuesday",
            "Wednesday",
            "Thursday",
            "Friday",
            "Saturday",
            "Sunday",
        ]

        weekday_values = {
            day: weekday_values[day] for day in weekday_order if day in weekday_values
        }

        save_line_chart(
            "Evolução anual do faturamento",
            year_values,
            "13_time_year.png",
        )

        save_line_chart(
            "Evolução mensal do faturamento",
            month_values,
            "14_time_month.png",
        )

        save_bar_chart(
            "Faturamento por dia da semana",
            weekday_values,
            "15_time_weekday.png",
            CYAN,
            currency=True,
        )

        payments = get_section("payments")

        save_bar_chart(
            "Faturamento por método de pagamento",
            get_numeric_mapping(payments, "methods"),
            "16_payments_methods.png",
            NAVY,
            currency=True,
        )

        save_bar_chart(
            "Quantidade de pedidos por método de pagamento",
            get_numeric_mapping(payments, "orders"),
            "17_payments_orders.png",
            CYAN,
        )

        logger.info(
            "Gráficos criados com sucesso: %s arquivos.",
            len(generated_charts),
        )

        return generated_charts

    except (TypeError, ValueError, KeyError):
        logger.exception("Erro de validação ao criar gráficos.")
        raise

    except Exception:
        logger.exception("Erro inesperado durante a criação dos gráficos.")
        raise
