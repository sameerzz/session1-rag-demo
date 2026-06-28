from __future__ import annotations

import os
import uuid
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import json

import streamlit as st


DEFAULT_API_BASE = os.getenv("RAG_API_BASE_URL", "http://35.232.150.97")


def call_chat_api(api_base: str, message: str, session_id: str, max_words_memory: int) -> dict:
    payload = {
        "message": message,
        "session_id": session_id,
        "max_words_memory": max_words_memory,
    }
    body = json.dumps(payload).encode("utf-8")
    req = Request(
        f"{api_base.rstrip('/')}/chat",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req, timeout=60) as response:
        return json.loads(response.read().decode("utf-8"))


st.set_page_config(page_title="Session 1 RAG Chat", page_icon="💬", layout="centered")

if "messages" not in st.session_state:
    st.session_state.messages = []

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

st.title("Session 1 RAG Chat")
st.caption("Streamlit client for the deployed FastAPI RAG service.")

with st.sidebar:
    st.subheader("Connection")
    api_base = st.text_input("API Base URL", value=DEFAULT_API_BASE)
    max_words_memory = st.slider("Memory limit", min_value=500, max_value=8000, value=5000, step=500)
    session_id = st.text_input("Session ID", value=st.session_state.session_id)

    col1, col2 = st.columns(2)
    with col1:
        if st.button("New Session", use_container_width=True):
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()
    with col2:
        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

st.session_state.session_id = session_id

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Ask something about your indexed data")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                data = call_chat_api(
                    api_base=api_base,
                    message=prompt,
                    session_id=st.session_state.session_id,
                    max_words_memory=max_words_memory,
                )
                answer = data.get("answer", "No answer returned.")
                st.session_state.session_id = data.get("session_id", st.session_state.session_id)
                st.markdown(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            except HTTPError as exc:
                error_body = exc.read().decode("utf-8", errors="ignore")
                st.error(f"API error {exc.code}: {error_body or exc.reason}")
            except URLError as exc:
                st.error(f"Connection failed: {exc.reason}")
            except Exception as exc:
                st.error(f"Unexpected error: {exc}")
