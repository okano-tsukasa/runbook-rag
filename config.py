"""プロジェクト共通の設定。モデル名やチャンク・検索パラメータをここに集約する。"""
from pathlib import Path

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "docs"
CHROMA_DIR = BASE_DIR / ".chroma"

# Ollama モデル（事前に取得: `ollama pull qwen3:8b` / `ollama pull bge-m3`）
CHAT_MODEL = "qwen3:8b"
EMBED_MODEL = "bge-m3"
OLLAMA_BASE_URL = "http://localhost:11434"

# チャンク分割（eval/evaluate.py の比較で 300/50 が hit@1・MRR とも最良だったため採用）
CHUNK_SIZE = 300
CHUNK_OVERLAP = 50

# 検索
TOP_K = 4

# LLM に渡すコンテキスト長（Ollama デフォルトの 2048 は RAG には短すぎるため明示）
NUM_CTX = 8192
