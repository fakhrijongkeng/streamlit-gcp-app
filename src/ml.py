from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class PredictionResult:
    label: str
    probability: float


def _make_training_data(seed: int = 42, n: int = 1200) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    experience_years = rng.uniform(0, 10, size=n)
    projects = rng.integers(0, 15, size=n)
    role = rng.choice(["Analyst", "Engineer", "Scientist"], size=n, p=[0.4, 0.3, 0.3])
    hours_per_week = rng.uniform(5, 50, size=n)

    signal = (
        0.55 * experience_years
        + 0.25 * projects
        + 0.06 * hours_per_week
        + (role == "Engineer") * 1.2
        + (role == "Scientist") * 1.0
        + rng.normal(0, 1.8, size=n)
    )
    p = 1 / (1 + np.exp(-(signal - 6.5)))
    label = rng.binomial(1, p, size=n)

    return pd.DataFrame(
        {
            "experience_years": experience_years,
            "projects": projects,
            "role": role,
            "hours_per_week": hours_per_week,
            "target": label,
        }
    )


@st.cache_resource(show_spinner=False)
def load_model() -> Pipeline:
    df = _make_training_data()

    X = df.drop(columns=["target"])
    y = df["target"].astype(int)

    categorical = ["role"]
    numeric = ["experience_years", "projects", "hours_per_week"]

    pre = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical),
            ("num", Pipeline([("scaler", StandardScaler())]), numeric),
        ],
        remainder="drop",
    )

    model = LogisticRegression(max_iter=500)
    pipe = Pipeline([("pre", pre), ("model", model)])
    pipe.fit(X, y)
    return pipe


def predict_success_probability(
    experience_years: float,
    projects: int,
    role: str,
    hours_per_week: float,
) -> PredictionResult:
    pipe = load_model()
    X = pd.DataFrame(
        [
            {
                "experience_years": experience_years,
                "projects": projects,
                "role": role,
                "hours_per_week": hours_per_week,
            }
        ]
    )

    proba = float(pipe.predict_proba(X)[0, 1])
    label = "Likely" if proba >= 0.5 else "Unlikely"
    return PredictionResult(label=label, probability=proba)
