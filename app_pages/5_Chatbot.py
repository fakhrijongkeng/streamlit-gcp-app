from __future__ import annotations

import streamlit as st

from src.ui import render_header, section, set_page_config

try:
    from google import genai
except ImportError:  # pragma: no cover - optional dependency
    genai = None


def _running_in_streamlit() -> bool:
    try:
        from streamlit.runtime.scriptrunner import get_script_run_ctx

        return get_script_run_ctx() is not None
    except Exception:
        return False


def _init_chat(api_key: str):
    if "client" not in st.session_state or st.session_state.get("api_key") != api_key:
        st.session_state.client = genai.Client(api_key=api_key)
        st.session_state.chat = st.session_state.client.chats.create(model="gemini-2.5-flash")
        st.session_state.api_key = api_key

    if "chat" not in st.session_state:
        st.session_state.chat = st.session_state.client.chats.create(model="gemini-2.5-flash")

    return st.session_state.chat


def main() -> None:
    set_page_config(page_title="Gemini Chatbot", page_icon="💬")
    render_header("Personal Chatbot", "Chat with Google Gemini directly from this Streamlit app.")

    section("Chatbot", "Chat dengan Gemini menggunakan token dari Streamlit secrets.")

    col1, col2 = st.columns([3, 1])
    with col1:
        st.caption("Percakapan tersimpan di sesi browser ini.")
    with col2:
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.pop("chat", None)
            st.session_state.pop("client", None)
            st.session_state.pop("api_key", None)
            st.rerun()

    if genai is None:
        st.error("Paket google-genai belum terinstal. Jalankan `pip install google-genai`.")
        return

    api_key = st.secrets.get("GEMINI_TOKEN_KEY")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if not api_key:
        st.warning("GEMINI_TOKEN_KEY belum tersedia di Streamlit secrets.")
        return

    chat = _init_chat(api_key)

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["text"])

    if user_input := st.chat_input("Tanya sesuatu ke Gemini..."):
        with st.chat_message("user"):
            st.markdown(user_input)
        st.session_state.messages.append({"role": "user", "text": user_input})

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                response = chat.send_message_stream(user_input)
                for chunk in response:
                    full_response += getattr(chunk, "text", "")
                    message_placeholder.markdown(full_response + "▌")

                message_placeholder.markdown(full_response)
                st.session_state.messages.append({"role": "assistant", "text": full_response})
            except Exception as exc:  # pragma: no cover - runtime safeguard
                st.error(f"Terjadi kesalahan: {exc}")


if __name__ == "__main__" or _running_in_streamlit():
    main()

