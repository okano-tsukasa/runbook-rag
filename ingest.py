"""docs/ 以下の Markdown を読み込み、チャンク分割して Chroma に格納する。

見出し（## / ###）を優先セパレータにしているのは、手順書が見出し単位で
意味的にまとまっているため。chunk_size は eval/evaluate.py で決める。
"""
import shutil
from pathlib import Path

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

import config


def load_documents(docs_dir: Path) -> list[Document]:
    docs = []
    for path in sorted(docs_dir.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        docs.append(Document(page_content=text, metadata={"source": path.name}))
    return docs


def build_index(
    chunk_size: int = config.CHUNK_SIZE,
    chunk_overlap: int = config.CHUNK_OVERLAP,
    persist_dir: str = str(config.CHROMA_DIR),
):
    # 追記ではなく毎回作り直す（同じ persist_dir に足すと古いチャンクが残り検索結果に混ざるため）
    shutil.rmtree(persist_dir, ignore_errors=True)

    docs = load_documents(config.DOCS_DIR)
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", "。", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL, base_url=config.OLLAMA_BASE_URL)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=persist_dir,
    )
    print(f"Indexed {len(chunks)} chunks from {len(docs)} documents -> {persist_dir}")
    return vectordb


if __name__ == "__main__":
    build_index()
