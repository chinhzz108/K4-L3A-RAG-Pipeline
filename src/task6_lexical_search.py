"""
Task 6 — Lexical search bằng BM25.

Dùng cùng corpus chunks với Task 5. BM25 phù hợp với từ khóa chính xác, mã tài
liệu và tên riêng. Output phải theo SearchResult và sort score giảm dần.
"""

from rank_bm25 import BM25Okapi


CORPUS: list[dict] = []


def build_bm25_index(corpus: list[dict]) -> BM25Okapi:
    """Tạo BM25 index từ danh sách chunks."""
    tokenized = [item["content"].lower().split() for item in corpus]
    return BM25Okapi(tokenized)


def lexical_search(query: str, top_k: int = 10) -> list[dict]:
    """Trả về BM25 SearchResult theo score giảm dần."""
    global CORPUS
    if not CORPUS:
        try:
            from .task4_chunking_indexing import load_documents, chunk_documents
            docs = load_documents()
            CORPUS = chunk_documents(docs)
        except Exception:
            pass

    if not CORPUS:
        return []

    tokens = query.lower().split()
    if not tokens:
        return []

    bm25 = build_bm25_index(CORPUS)
    scores = bm25.get_scores(tokens)

    # Sort indices by score descending
    ranked_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]

    results = []
    for idx in ranked_indices:
        item = CORPUS[idx]
        results.append({
            "id": item["id"],
            "content": item["content"],
            "score": float(scores[idx]),
            "metadata": item["metadata"],
            "retrieval_method": "bm25",
        })
    return results


if __name__ == "__main__":
    for result in lexical_search("tuyen sinh", top_k=3):
        print(result["id"], f"Score: {result['score']:.4f}")
