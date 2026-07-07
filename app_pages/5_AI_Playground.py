from __future__ import annotations

import streamlit as st

from src.hf_inference import DEFAULT_MODEL, HFInferenceError, generate_image_via_hf
from src.ui import render_header, section, set_page_config


def _get_hf_token() -> str | None:
    try:
        token = st.secrets.get("HF_TOKEN")
        if token:
            return str(token)
    except Exception:
        return None
    return None


def main() -> None:
    set_page_config(page_title="AI Playground", page_icon="🎨")
    render_header("AI Playground", "Stable Diffusion via Hugging Face Inference API (no local GPU needed).")

    token = _get_hf_token()
    if not token:
        st.warning(
            "HF token is not configured. Add `HF_TOKEN` in Streamlit Cloud Secrets (or local `.streamlit/secrets.toml`)."
        )

    section("Generate an image")
    col1, col2 = st.columns([2, 1])
    with col1:
        prompt = st.text_area(
            "Prompt",
            placeholder="e.g., A minimal futuristic data dashboard on a glass screen, cyberpunk lighting",
            height=120,
            max_chars=400,
        )
    with col2:
        model = st.text_input("Model", value=DEFAULT_MODEL)
        timeout_s = st.slider("Timeout (seconds)", min_value=15, max_value=120, value=60, step=5)

    disabled = not bool(token)
    if st.button("Generate", type="primary", disabled=disabled):
        with st.spinner("Calling Hugging Face..."):
            try:
                resp = generate_image_via_hf(
                    token=token or "",
                    prompt=prompt,
                    model=model.strip() or DEFAULT_MODEL,
                    timeout_s=int(timeout_s),
                )
            except HFInferenceError as e:
                st.error(str(e))
                if getattr(e, "status_code", None) == 503:
                    st.info("If the model is cold-starting, retry after a short wait.")
                elif getattr(e, "status_code", None) in {401, 403}:
                    st.info("Check that your Hugging Face token is valid and has access to the selected model.")
                else:
                    st.info("If this keeps happening, try again in a few minutes or switch to a different model.")
                return

        st.image(resp.image_bytes, caption="Generated image", use_container_width=True)

    section("Notes")
    st.markdown(
        "- Streamlit Cloud free tier is CPU-only, so generation must be offloaded via API.\n"
        "- Keep prompts short and avoid excessive retries to stay within rate limits.\n"
        "- If generation fails with a network error, your network or DNS may be blocking access to Hugging Face."
    )

def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


if __name__ == "__main__" or _running_in_streamlit():
    main()

