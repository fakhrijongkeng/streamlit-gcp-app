from __future__ import annotations

from datetime import date

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from src.tt_oop import fetch_tiktok_content_cached, fetch_tiktok_profile_cached 
from src.ui import render_header, section, set_page_config


def main() -> None:
    set_page_config(page_title="Tiktok Scrapper", page_icon="📊")
    render_header("TikTok Scrapper", "Upload CSV and explore TikTok clip performance.")

    section("TikTok Scrapper", "Get your Tiktok public data")

    col1, col2 = st.columns(2)
    with col1:
            username = st.text_input("Enter TikTok username", placeholder="Enter TikTok username")
    with col2:
        category = st.selectbox("Select category", ["content", "profile"], placeholder="Select category", index=None)

    if st.button("Scrape"):
        if not username and not category:
            st.warning("Please enter a username and select a category")
            return
        
        with st.spinner(f"Scraping {category}for {username}..."):
            if category == "content":
                df_content = fetch_tiktok_content_cached(username)
                st.dataframe(df_content)
            elif category == "profile":
                df_profile = fetch_tiktok_profile_cached(username)
                st.dataframe(df_profile)

def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" or _running_in_streamlit():
    main()

