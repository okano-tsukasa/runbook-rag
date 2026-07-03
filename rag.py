"""検索 + 生成。

設計上のポイント:
- 参考手順に無いことは答えさせない（ハルシネーション抑制）
- 回答に必ず出典ファイル名を付ける
- temperature=0 で再現性を確保
"""
import re

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate

import config

SYSTEM_PROMPT = """あなたは運用・保守手順を案内するアシスタントです。
以下の【参考手順】だけを根拠に、日本語で簡潔に回答してください。
- 参考手順に書かれていないことは推測せず「手順書には記載がありません」と答える。
- 回答の最後に、根拠にした手順のファイル名を [出典: ...] の形で必ず示す。
"""

PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        ("human", "【参考手順】\n{context}\n\n【質問】\n{question}"),
    ]
)


def get_retriever(k: int = config.TOP_K, persist_dir: str = str(config.CHROMA_DIR)):
    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL, base_url=config.OLLAMA_BASE_URL)
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    return vectordb.as_retriever(search_kwargs={"k": k})


def answer(question: str, k: int = config.TOP_K):
    retriever = get_retriever(k=k)
    docs = retriever.invoke(question)
    context = "\n\n---\n\n".join(
        f"({d.metadata.get('source', '?')}) {d.page_content}" for d in docs
    )
    llm = ChatOllama(
        model=config.CHAT_MODEL,
        base_url=config.OLLAMA_BASE_URL,
        temperature=0,
        num_ctx=config.NUM_CTX,  # Ollama 既定の 2048 だと参考手順が黙って切り捨てられるため明示
    )
    chain = PROMPT | llm
    resp = chain.invoke({"context": context, "question": question})
    # Qwen3 系は思考過程を <think>...</think> で出力することがあるため除去する
    content = re.sub(r"<think>.*?</think>", "", resp.content, flags=re.DOTALL).strip()
    sources = [d.metadata.get("source", "?") for d in docs]
    return content, sources, docs


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "CloudWatchアラートが鳴ったらまず何をする？"
    ans, sources, _ = answer(q)
    print(ans)
    print("\nretrieved sources:", sources)
