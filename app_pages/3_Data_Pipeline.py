from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from src.db import EtlMetadata, get_latest_etl_metadata, upsert_latest_etl_metadata
from src.ui import render_header, section, set_page_config


DATA_DIR = Path(__file__).resolve().parents[1] / "data"
METADATA_PATH = DATA_DIR / "metadata.json"


def _use_db() -> bool:
    """
    Enable DB persistence for ETL metadata.
    - secrets: USE_DB = true/false
    - fallback: false (JSON file mode)
    """
    try:
        v = st.secrets.get("USE_DB")
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}
    except Exception:
        return False


def _load_metadata() -> dict:
    if _use_db():
        latest = get_latest_etl_metadata()
        if latest:
            return {
                "last_sync_utc": latest.last_sync_utc,
                "rows_processed": latest.rows_processed,
                "status": latest.status,
                "sources": latest.sources,
            }
        return {
            "last_sync_utc": None,
            "rows_processed": 0,
            "status": "unknown",
            "sources": [],
        }

    if not METADATA_PATH.exists():
        return {
            "last_sync_utc": None,
            "rows_processed": 0,
            "status": "unknown",
            "sources": [],
        }
    return json.loads(METADATA_PATH.read_text(encoding="utf-8"))


def _refresh_metadata(existing: dict) -> dict:
    out = dict(existing)
    out["last_sync_utc"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    out["rows_processed"] = int(out.get("rows_processed", 0)) + 500 + int(datetime.now().timestamp()) % 500
    out["status"] = "healthy"

    if _use_db():
        upsert_latest_etl_metadata(
            EtlMetadata(
                last_sync_utc=out.get("last_sync_utc"),
                rows_processed=int(out.get("rows_processed", 0)),
                status=str(out.get("status", "unknown")),
                sources=list(out.get("sources") or []),
            )
        )
    else:
        METADATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        METADATA_PATH.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def main() -> None:
    set_page_config(page_title="Data Pipeline", page_icon="🧱")
    render_header("Data Pipeline", "Architecture overview + ETL metadata (lightweight, Streamlit Cloud-safe).")

    section("Pipeline architecture")
    st.markdown(
        """
```mermaid
flowchart LR
  sources[Sources] --> ingest[Ingest]
  ingest --> transform[Transform]
  transform --> warehouse[Warehouse]
  warehouse --> bi[BI_Dashboard]
  warehouse --> ml[ML_Features]
```
        """.strip()
    )

    st.divider()

    section("ETL metadata")
    meta = _load_metadata()
    if _use_db():
        st.caption("Storage: SQLite database (`data/app.db` by default).")
    else:
        st.caption("Storage: JSON file (`data/metadata.json`).")

    c1, c2, c3 = st.columns(3)
    c1.metric("Status", str(meta.get("status", "unknown")).upper())
    c2.metric("Rows processed", f"{int(meta.get('rows_processed', 0)):,}")
    c3.metric("Last sync (UTC)", str(meta.get("last_sync_utc") or "—"))

    if st.button("Refresh metadata", type="primary"):
        meta = _refresh_metadata(meta)
        st.toast("Metadata refreshed.", icon="✅")

    sources = meta.get("sources") or []
    if sources:
        st.markdown("### Sources")
        st.dataframe(sources, use_container_width=True, hide_index=True)
    else:
        st.info("No sources configured yet. Replace `data/metadata.json` with your pipeline metadata.")


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" or _running_in_streamlit():
    main()

