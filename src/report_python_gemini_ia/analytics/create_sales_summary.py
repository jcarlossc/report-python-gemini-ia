from __future__ import annotations

import logging
import pandas as pd


def get_create_sales_summary(
    df: pd.DataFrame,
    columns_dict: dict[str, dict[str, object]],
) -> dict[str, object]:
    logger = logging.getLogger(__name__)

    logger.info("Iniciando criação de métricas e KPIs.")

    try:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df deve ser um pandas DataFrame.")

        if not isinstance(columns_dict, dict):
            raise TypeError("columns_dict deve ser um dicionário.")

        if df.empty:
            raise ValueError("O DataFrame está vazio.")

        required_columns = list(columns_dict.keys())

        missing = [column for column in required_columns if column not in df.columns]

        if missing:
            logger.warning("Colunas ausentes: %s", missing)
            raise KeyError(f"Colunas obrigatórias ausentes: {missing}")

        data = df.copy()

        data["year"] = data["order_date"].dt.year
        data["month"] = data["order_date"].dt.strftime("%Y-%m")
        data["weekday"] = data["order_date"].dt.day_name()

        summary: dict[str, object] = {
            "metadata": {
                "rows": len(data),
                "columns": len(df.columns),
                "orders": data["order_id"].nunique(),
                "customers": data["customer_name"].nunique(),
                "products": data["product_name"].nunique(),
                "categories": data["product_category"].nunique(),
                "period": {
                    "start": str(data["order_date"].min()),
                    "end": str(data["order_date"].max()),
                },
            },
            "kpis": {
                "revenue": round(data["total_sales"].sum(), 2),
                "profit": round(data["profit"].sum(), 2),
                "orders": int(data["order_id"].nunique()),
                "items_sold": int(data["quantity"].sum()),
                "average_ticket": round(
                    data.groupby("order_id")["total_sales"].sum().mean(),
                    2,
                ),
                "average_discount": round(
                    data["discount_percent"].mean(),
                    2,
                ),
                "margin": round(
                    (data["profit"].sum() / data["total_sales"].sum()) * 100,
                    2,
                )
                if data["total_sales"].sum()
                else 0.0,
                "shipping_cost": round(
                    data["shipping_cost"].sum(),
                    2,
                ),
            },
            "products": {
                "top_revenue": (
                    data.groupby("product_name")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .head(10)
                    .to_dict()
                ),
                "top_quantity": (
                    data.groupby("product_name")["quantity"]
                    .sum()
                    .sort_values(ascending=False)
                    .head(10)
                    .to_dict()
                ),
                "lowest_revenue": (
                    data.groupby("product_name")["total_sales"]
                    .sum()
                    .sort_values()
                    .round(2)
                    .head(10)
                    .to_dict()
                ),
            },
            "categories": {
                "revenue": (
                    data.groupby("product_category")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
                "quantity": (
                    data.groupby("product_category")["quantity"]
                    .sum()
                    .sort_values(ascending=False)
                    .to_dict()
                ),
                "profit": (
                    data.groupby("product_category")["profit"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
            },
            "customers": {
                "revenue": (
                    data.groupby("customer_name")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .head(10)
                    .to_dict()
                ),
                "orders": (
                    data.groupby("customer_name")["order_id"]
                    .nunique()
                    .sort_values(ascending=False)
                    .head(10)
                    .to_dict()
                ),
                "segments": (
                    data.groupby("customer_segment")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
            },
            "geography": {
                "countries": (
                    data.groupby("country")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
                "regions": (
                    data.groupby("region")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
            },
            "time": {
                "year": (data.groupby("year")["total_sales"].sum().to_dict()),
                "month": (data.groupby("month")["total_sales"].sum().to_dict()),
                "weekday": (data.groupby("weekday")["total_sales"].sum().to_dict()),
            },
            "payments": {
                "methods": (
                    data.groupby("payment_method")["total_sales"]
                    .sum()
                    .sort_values(ascending=False)
                    .round(2)
                    .to_dict()
                ),
                "orders": (
                    data.groupby("payment_method")["order_id"]
                    .nunique()
                    .sort_values(ascending=False)
                    .to_dict()
                ),
            },
        }

        logger.info("Término da criação de métricas e KPIs.")

        return summary

    except (TypeError, ValueError, KeyError):
        logger.exception("Erro de validação ao criar resumo.")
        raise

    except Exception:
        logger.exception("Erro inesperado durante criação do resumo.")
        raise
