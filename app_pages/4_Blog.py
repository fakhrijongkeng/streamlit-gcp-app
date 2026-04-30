from __future__ import annotations

from pathlib import Path
from typing import NamedTuple

import streamlit as st

from src.ui import render_header, section, set_page_config


POSTS_DIR = Path(__file__).resolve().parents[1] / "posts"


class Post(NamedTuple):
    path: Path
    title: str


def _extract_title(md_text: str, fallback: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip() or fallback
    return fallback


def _list_posts() -> list[Post]:
    POSTS_DIR.mkdir(parents=True, exist_ok=True)
    posts: list[Post] = []
    for p in sorted(POSTS_DIR.glob("*.md")):
        text = p.read_text(encoding="utf-8")
        title = _extract_title(text, fallback=p.stem.replace("_", " ").title())
        posts.append(Post(path=p, title=title))
    return posts


def main() -> None:
    set_page_config(page_title="Blog", page_icon="✍️")
    render_header("Blog", "Markdown-based technical writing and storytelling.")

    posts = _list_posts()
    if not posts:
        st.info("No posts yet. Add markdown files to the `posts/` folder.")
        return

    titles = [p.title for p in posts]
    selected = st.selectbox("Select a post", options=titles, index=None, placeholder="Select a post")
    
    if selected:
        post = next(p for p in posts if p.title == selected)

        section(post.title)
        st.markdown(post.path.read_text(encoding="utf-8"))
    else:
        st.info("No post selected.")


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" or _running_in_streamlit():
    main()

