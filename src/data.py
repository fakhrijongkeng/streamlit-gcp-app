from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class DatasetInfo:
    path: Path
    name: str


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
DEFAULT_DATASET = DatasetInfo(path=DATA_DIR / "sample_sales.csv", name="Sample sales")


@st.cache_data(show_spinner=False)
def load_sales_dataset(path: str | Path = DEFAULT_DATASET.path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["date"] = pd.to_datetime(df["date"]).dt.date
    return df


def filter_sales_dataset(
    df: pd.DataFrame,
    regions: list[str] | None = None,
    categories: list[str] | None = None,
    date_range: tuple[date, date] | None = None,
) -> pd.DataFrame:
    out = df.copy()

    if regions:
        out = out[out["region"].isin(regions)]
    if categories:
        out = out[out["category"].isin(categories)]
    if date_range:
        start, end = date_range
        out = out[(out["date"] >= start) & (out["date"] <= end)]

    return out


def ensure_sample_data_exists() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    path = DEFAULT_DATASET.path
    if path.exists():
        return

    rng = np.random.default_rng(7)
    start = datetime(2025, 1, 1)
    days = 180
    dates = [start.date() for start in pd.date_range(start, periods=days, freq="D")]

    regions = ["APAC", "EMEA", "AMER"]
    categories = ["Analytics", "AI", "Data Engineering"]

    rows: list[dict] = []
    for d in dates:
        for _ in range(rng.integers(8, 14)):
            region = rng.choice(regions)
            category = rng.choice(categories)
            units = int(rng.integers(1, 20))
            price = float(rng.normal(120, 30))
            price = float(max(25, min(price, 260)))
            revenue = units * price
            rows.append(
                {
                    "date": d.isoformat(),
                    "region": region,
                    "category": category,
                    "units": units,
                    "unit_price": round(price, 2),
                    "revenue": round(revenue, 2),
                }
            )

    pd.DataFrame(rows).to_csv(path, index=False)
