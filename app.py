from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from src.data import ensure_sample_data_exists
from src.ui import render_header, section, set_page_config


def home() -> None:
    set_page_config(page_title="Data & AI Portfolio", page_icon="📈")

    render_header(
        "Data & AI Portfolio",
        "Interactive Streamlit portfolio: analytics dashboard, ML demo, data pipeline, and AI playground.",
    )

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("### About")
        st.write(
            "This site is designed as a technical portfolio for Data Engineer / Analyst / Scientist roles."
        )
        st.markdown(
            "- Interactive analytics\n- Lightweight ML predictor demo\n- Pipeline architecture + ETL metadata\n- Hugging Face AI Playground"
        )
    with col_b:
        st.markdown("### Quick links")
        st.link_button("Open Dashboard", "Dashboard")
        st.link_button("Open Data Pipeline", "Data Pipeline")
    with col_c:
        st.markdown("### Profiles")
        st.write("Add your links here once ready:")
        st.markdown("- GitHub: `https://github.com/<username>`\n- LinkedIn: `https://linkedin.com/in/<username>`")

    st.divider()

    section("How to run locally")
    st.code("pip install -r requirements.txt\nstreamlit run app.py", language="bash")

    section("Deployment")
    st.write(
        "Deploy on Streamlit Community Cloud by pushing this project to GitHub and setting secrets in the app settings."
    )

    st.divider()
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    st.caption(f"Last build: {ts}")


if __name__ == "__main__":
    # Make sure sample datasets exist before any page tries to load them.
    ensure_sample_data_exists()

    nav = st.navigation(
        [
            st.Page(home, title="Home", icon="🏠", default=True),
            st.Page("app_pages/1_Dashboard.py", title="Dashboard", icon="📊"),
            st.Page("app_pages/2_Scrapper.py", title="Scrapper", icon="🕷️"),
            st.Page("app_pages/3_Data_Pipeline.py", title="Data Pipeline", icon="🧱"),
            st.Page("app_pages/4_Blog.py", title="Blog", icon="📝"), 
            st.Page("app_pages/5_Chatbot.py", title="Chatbot", icon="💬"),
        ]    
    )
    nav.run()

