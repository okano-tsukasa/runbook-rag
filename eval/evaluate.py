"""検索精度を測る。

判定は「チャンク単位」:
  正しい出典ファイル由来で、かつ答えの根拠となる文言（answer_keyword）を
  含むチャンクが top_k に入って初めてヒットとみなす。
※ ファイル単位の判定にすると、文書が少ないうちは常にほぼ満点になり
   chunk_size の違いが測れないため、あえてチャンク単位にしている。

- hit-rate@k: 正解チャンクが top_k 内に入った割合
- hit-rate@1: 正解チャンクが 1 位に来た割合（@k が飽和したときの比較用）
- MRR: 正解チャンクの順位の逆数の平均

chunk設定を変えて before/after を比較できる（README の表を埋める用）。
"""
import json
import shutil
import sys
import tempfile
from pathlib import Path

# eval/ から実行しても、プロジェクト直下の config.py / ingest.py を読めるようにする
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

import config
from ingest import build_index

EVAL_PATH = Path(__file__).parent / "eval_set.json"


def load_eval():
    return json.loads(EVAL_PATH.read_text(encoding="utf-8"))


def evaluate(persist_dir: str, k: int = config.TOP_K) -> dict:
    eval_set = load_eval()
    embeddings = OllamaEmbeddings(model=config.EMBED_MODEL, base_url=config.OLLAMA_BASE_URL)
    vectordb = Chroma(persist_directory=persist_dir, embedding_function=embeddings)
    retriever = vectordb.as_retriever(search_kwargs={"k": k})

    hits, hits_at_1, rr_total = 0, 0, 0.0
    for item in eval_set:
        docs = retriever.invoke(item["question"])
        expected = item["expected_source"]
        keyword = item["answer_keyword"]
        rank = next(
            (
                i + 1
                for i, d in enumerate(docs)
                if d.metadata.get("source") == expected and keyword in d.page_content
            ),
            None,
        )
        if rank is not None:
            hits += 1
            rr_total += 1.0 / rank
            if rank == 1:
                hits_at_1 += 1
    n = len(eval_set)
    return {
        "hit_rate@k": hits / n,
        "hit_rate@1": hits_at_1 / n,
        "MRR": rr_total / n,
        "n": n,
        "k": k,
    }


def compare_chunk_sizes(configs):
    """configs = [(chunk_size, overlap), ...] を順に試して比較表を出す。"""
    results = []
    for cs, ov in configs:
        tmp = tempfile.mkdtemp(prefix=f"chroma_{cs}_")
        build_index(chunk_size=cs, chunk_overlap=ov, persist_dir=tmp)
        metrics = evaluate(persist_dir=tmp)
        metrics.update({"chunk_size": cs, "overlap": ov})
        results.append(metrics)
        shutil.rmtree(tmp, ignore_errors=True)

    print(f"\n{'chunk':>6} {'overlap':>8} {'hit@k':>7} {'hit@1':>7} {'MRR':>6}")
    for r in results:
        print(
            f"{r['chunk_size']:>6} {r['overlap']:>8} {r['hit_rate@k']:>7.2f}"
            f" {r['hit_rate@1']:>7.2f} {r['MRR']:>6.2f}"
        )
    return results


if __name__ == "__main__":
    compare_chunk_sizes([(300, 50), (600, 100), (1000, 150)])
