from __future__ import annotations

from datetime import date

import altair as alt
import pandas as pd
import plotly.express as px
import streamlit as st

from src.db import TikTokClip, list_tiktok_clips, replace_all_tiktok_clips
from src.ui import render_header, section, set_page_config


def _use_db() -> bool:
    try:
        v = st.secrets.get("USE_DB")
        if v is None:
            return False
        if isinstance(v, bool):
            return v
        return str(v).strip().lower() in {"1", "true", "yes", "y", "on"}
    except Exception:
        return False


def _normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out.columns = [str(c).strip().lower().replace(" ", "_") for c in out.columns]
    return out


def _coerce_int(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce").fillna(0).astype(int)


def _load_tiktok_from_csv_bytes(b: bytes) -> pd.DataFrame:
    df = pd.read_csv(pd.io.common.BytesIO(b))
    df = _normalize_columns(df)

    # minimal expected columns
    required = {"clip_date", "views", "likes", "comments", "shares", "saves"}
    missing = sorted([c for c in required if c not in df.columns])
    if missing:
        raise ValueError(f"Missing columns: {', '.join(missing)}")

    # optional columns
    for col in ["creator", "topic", "caption", "url"]:
        if col not in df.columns:
            df[col] = None

    df["clip_date"] = pd.to_datetime(df["clip_date"], errors="coerce").dt.date
    df["views"] = _coerce_int(df["views"])
    df["likes"] = _coerce_int(df["likes"])
    df["comments"] = _coerce_int(df["comments"])
    df["shares"] = _coerce_int(df["shares"])
    df["saves"] = _coerce_int(df["saves"])

    df = df.dropna(subset=["clip_date"])
    return df


def main() -> None:
    set_page_config(page_title="Dashboard", page_icon="📊")
    render_header("TikTok Dashboard", "Upload CSV and explore TikTok clip performance.")

    section("TikTok clips", "Upload your TikTok snippet dataset (CSV) and explore performance.")

    using_db = _use_db()
    st.caption("Storage: SQLite database" if using_db else "Storage: in-memory (upload each session)")

    left, right = st.columns([2, 1])
    with left:
        up = st.file_uploader("Upload CSV", type=["csv"])
    with right:
        load_sample = st.button("Load sample dataset", use_container_width=True)

    df_tk: pd.DataFrame | None = None

    if using_db:
        rows = list_tiktok_clips()
        if rows:
            df_tk = pd.DataFrame(rows)
            df_tk["clip_date"] = pd.to_datetime(df_tk["clip_date"], errors="coerce").dt.date

    if load_sample:
        sample_path = "data/sample_tiktok_clips.csv"
        df_tk = _normalize_columns(pd.read_csv(sample_path))
        df_tk["clip_date"] = pd.to_datetime(df_tk["clip_date"], errors="coerce").dt.date
        for m in ["views", "likes", "comments", "shares", "saves"]:
            df_tk[m] = _coerce_int(df_tk[m])

        if using_db:
            clips = [
                TikTokClip(
                    clip_date=str(r["clip_date"]),
                    creator=str(r.get("creator")) if pd.notna(r.get("creator")) else None,
                    topic=str(r.get("topic")) if pd.notna(r.get("topic")) else None,
                    caption=str(r.get("caption")) if pd.notna(r.get("caption")) else None,
                    url=str(r.get("url")) if pd.notna(r.get("url")) else None,
                    views=int(r.get("views", 0)),
                    likes=int(r.get("likes", 0)),
                    comments=int(r.get("comments", 0)),
                    shares=int(r.get("shares", 0)),
                    saves=int(r.get("saves", 0)),
                )
                for r in df_tk.to_dict(orient="records")
            ]
            replace_all_tiktok_clips(clips)
            st.toast("Saved sample dataset to DB.", icon="✅")

    if up is not None:
        try:
            df_tk = _load_tiktok_from_csv_bytes(up.getvalue())
        except Exception as e:
            st.error(f"Failed to parse CSV. {e}")
            st.info(
                "Expected columns: clip_date, creator, topic, caption, url, views, likes, comments, shares, saves"
            )
            df_tk = None

        if df_tk is not None and using_db:
            clips = [
                TikTokClip(
                    clip_date=str(r["clip_date"]),
                    creator=str(r.get("creator")) if pd.notna(r.get("creator")) else None,
                    topic=str(r.get("topic")) if pd.notna(r.get("topic")) else None,
                    caption=str(r.get("caption")) if pd.notna(r.get("caption")) else None,
                    url=str(r.get("url")) if pd.notna(r.get("url")) else None,
                    views=int(r.get("views", 0)),
                    likes=int(r.get("likes", 0)),
                    comments=int(r.get("comments", 0)),
                    shares=int(r.get("shares", 0)),
                    saves=int(r.get("saves", 0)),
                )
                for r in df_tk.to_dict(orient="records")
            ]
            replace_all_tiktok_clips(clips)
            st.toast("Saved uploaded dataset to DB.", icon="✅")

    if df_tk is None or df_tk.empty:
        st.info("Upload a CSV or click “Load sample dataset” to start.")
        return

    with st.sidebar:
        st.markdown("## TikTok filters")
        creators = sorted([c for c in df_tk["creator"].dropna().unique().tolist() if str(c).strip()])
        topics = sorted([c for c in df_tk["topic"].dropna().unique().tolist() if str(c).strip()])

        sel_creators = st.multiselect("Creator", options=creators, default=creators) if creators else []
        sel_topics = st.multiselect("Topic", options=topics, default=topics) if topics else []

        min_d = df_tk["clip_date"].min()
        max_d = df_tk["clip_date"].max()
        sel_dates = st.date_input("Date range", value=(min_d, max_d), min_value=min_d, max_value=max_d)
        if isinstance(sel_dates, tuple) and len(sel_dates) == 2:
            date_range_tk: tuple[date, date] | None = (sel_dates[0], sel_dates[1])
        else:
            date_range_tk = None

    f = df_tk.copy()
    if sel_creators:
        f = f[f["creator"].isin(sel_creators)]
    if sel_topics:
        f = f[f["topic"].isin(sel_topics)]
    if date_range_tk:
        start, end = date_range_tk
        f = f[(f["clip_date"] >= start) & (f["clip_date"] <= end)]

    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Clips", f"{len(f):,}")
    k2.metric("Views", f"{int(f['views'].sum()):,}")
    k3.metric("Likes", f"{int(f['likes'].sum()):,}")
    k4.metric("Comments", f"{int(f['comments'].sum()):,}")
    k5.metric("Share rate", f"{(f['shares'].sum() / max(1, f['views'].sum())):.2%}")

    st.divider()

    section("Views over time")
    ts = f.groupby("clip_date", as_index=False)["views"].sum().sort_values("clip_date")
    fig = px.line(ts, x="clip_date", y="views", markers=True)
    fig.update_layout(height=340, margin=dict(l=10, r=10, t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        section("Top topics by views")
        by_topic = f.groupby("topic", as_index=False)["views"].sum().sort_values("views", ascending=False).head(12)
        chart = (
            alt.Chart(by_topic)
            .mark_bar()
            .encode(
                x=alt.X("views:Q", title="Views"),
                y=alt.Y("topic:N", sort="-x", title="Topic"),
                tooltip=["topic", "views"],
            )
            .properties(height=280)
        )
        st.altair_chart(chart, use_container_width=True)

    with c2:
        section("Engagement (likes vs views)")
        scatter = px.scatter(
            f,
            x="views",
            y="likes",
            color="topic" if "topic" in f.columns else None,
            hover_data=["creator", "clip_date", "url"],
        )
        scatter.update_layout(height=280, margin=dict(l=10, r=10, t=10, b=10))
        st.plotly_chart(scatter, use_container_width=True)

    with st.expander("See TikTok data"):
        st.dataframe(f, use_container_width=True, hide_index=True)


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" or _running_in_streamlit():
    main()

