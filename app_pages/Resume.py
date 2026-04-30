from __future__ import annotations

from pathlib import Path

import streamlit as st

from src.ui import render_header, section, set_page_config


ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets"
RESUME_PDF = ASSETS_DIR / "resume.pdf"


def main() -> None:
    set_page_config(page_title="Resume", page_icon="📄")
    render_header("Resume", "Interactive snapshot + downloadable resume.")

    section("Summary")
    st.write(
        "Replace this content with your real resume highlights: domains, impact metrics, and core tools."
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("### Core skills")
        st.markdown("- Python\n- SQL\n- dbt / Airflow\n- Spark\n- Streamlit\n- ML basics")
    with c2:
        st.markdown("### Focus areas")
        st.markdown("- Analytics engineering\n- Data pipelines\n- Experimentation\n- Model serving (API)")
    with c3:
        st.markdown("### Links")
        st.markdown("- GitHub: `https://github.com/<username>`\n- LinkedIn: `https://linkedin.com/in/<username>`")

    st.divider()

    section("Experience (example)")
    st.markdown(
        "- **Data Engineer** — Built ELT pipelines and data quality checks (2024–2026)\n"
        "- **Data Analyst** — Delivered dashboards and cohort analysis (2022–2024)\n"
        "- **Projects** — Stable diffusion playground, forecasting, churn modeling"
    )

    st.divider()

    section("Download resume PDF")
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    if RESUME_PDF.exists():
        st.download_button(
            "Download resume.pdf",
            data=RESUME_PDF.read_bytes(),
            file_name="resume.pdf",
            mime="application/pdf",
            type="primary",
        )
    else:
        st.info("Add your PDF at `assets/resume.pdf` to enable downloads.")


# if __name__ == "__main__":
#     main()

