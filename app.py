"""Streamlit UI。回答に加えて、参照したチャンクを出典付きで展開表示する。"""
import streamlit as st

import config
from rag import answer

st.set_page_config(page_title="Runbook RAG", page_icon="📘")
st.title("📘 Runbook RAG — 運用・保守手順QA")
st.caption(
    f"chat: {config.CHAT_MODEL} / embed: {config.EMBED_MODEL} / top_k={config.TOP_K}"
)

q = st.text_input("質問を入力", placeholder="例: EC2のディスク使用率アラートの初動対応は？")

if st.button("質問する") and q:
    with st.spinner("検索して回答を生成中..."):
        ans, sources, docs = answer(q)
    st.markdown(ans)
    with st.expander(f"参照した手順チャンク（{len(docs)}件）"):
        for d in docs:
            st.markdown(f"**出典: {d.metadata.get('source', '?')}**")
            st.text(d.page_content)
            st.divider()
