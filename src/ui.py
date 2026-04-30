from __future__ import annotations

import streamlit as st


def set_page_config(page_title: str, page_icon: str = "📊") -> None:
    st.set_page_config(
        page_title=page_title,
        page_icon=page_icon,
        layout="wide",
        initial_sidebar_state="expanded",
    )


def render_header(title: str, subtitle: str | None = None) -> None:
    st.title(title)
    if subtitle:
        st.caption(subtitle)


def info_card(label: str, value: str, help_text: str | None = None) -> None:
    st.metric(label=label, value=value, help=help_text)


def section(title: str, body: str | None = None) -> None:
    st.subheader(title)
    if body:
        st.write(body)
