from __future__ import annotations

import streamlit as st

from src.ml import predict_success_probability
from src.ui import render_header, section, set_page_config


def main() -> None:
    set_page_config(page_title="ML Predictor", page_icon="🤖")
    render_header("ML Predictor", "Lightweight, CPU-friendly prediction demo.")

    section(
        "What is this?",
        "A small classification model trained on synthetic data. Replace with your real model when ready.",
    )

    st.markdown("### Input")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        experience_years = st.number_input("Experience (years)", min_value=0.0, max_value=20.0, value=3.0, step=0.5)
    with col2:
        projects = st.number_input("Projects shipped", min_value=0, max_value=50, value=5, step=1)
    with col3:
        role = st.selectbox("Role focus", options=["Analyst", "Engineer", "Scientist"], index=1)
    with col4:
        hours_per_week = st.number_input("Study hours / week", min_value=0.0, max_value=80.0, value=12.0, step=1.0)

    if st.button("Predict", type="primary", use_container_width=False):
        res = predict_success_probability(
            experience_years=float(experience_years),
            projects=int(projects),
            role=str(role),
            hours_per_week=float(hours_per_week),
        )
        st.success(f"Prediction: **{res.label}**")
        st.metric("Probability", f"{res.probability:.2%}")

        st.caption(
            "Tip: In a real portfolio, document features, training data, metrics (AUC/F1), and limitations."
        )


# if __name__ == "__main__":
#     main()

