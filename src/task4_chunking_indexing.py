"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

import os
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    env_file = Path(__file__).resolve().parent.parent / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                os.environ.setdefault(key.strip(), val.strip())

STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "sentence_transformers")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-m3")
EMBEDDING_DIM = 1024

COLLECTION_NAME = "rag_documents"

_ST_MODEL = None


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Tạo embedding cho danh sách văn bản dựa theo cấu hình provider."""
    global _ST_MODEL
    provider = os.getenv("EMBEDDING_PROVIDER", EMBEDDING_PROVIDER)

    if provider == "gemini":
        from google import genai
        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        model = os.getenv("EMBEDDING_MODEL") or "gemini-embedding-001"
        vectors = []
        batch_size = 20
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            res = client.models.embed_content(model=model, contents=batch)
            if hasattr(res, "embeddings") and res.embeddings:
                for e in res.embeddings:
                    vectors.append(list(e.values))
            elif hasattr(res, "embedding") and res.embedding:
                vectors.append(list(res.embedding.values))
        return vectors

    elif provider == "openai":
        from openai import OpenAI
        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        response = client.embeddings.create(
            input=texts,
            model=model,
        )
        return [item.embedding for item in response.data]

    else:
        # Default: sentence_transformers
        from sentence_transformers import SentenceTransformer
        if _ST_MODEL is None:
            _ST_MODEL = SentenceTransformer(EMBEDDING_MODEL)
        embeddings = _ST_MODEL.encode(texts)
        return embeddings.tolist()


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    if not STANDARDIZED_DIR.exists():
        return documents

    for path in sorted(STANDARDIZED_DIR.rglob("*.md")):
        doc_type = "legal" if "legal" in path.parts else "news"
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            continue
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": content,
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        splits = splitter.split_text(document["content"])
        for index, text in enumerate(splits):
            clean_text = text.strip()
            if not clean_text:
                continue
            chunks.append({
                "id": f"{document['id']}::chunk-{index}",
                "content": clean_text,
                "metadata": {
                    **document["metadata"],
                    "chunk_index": index,
                },
            })
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    if not chunks:
        return []
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    if not chunks:
        return
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    print(f"Loaded {len(documents)} documents.")
    chunks = chunk_documents(documents)
    print(f"Created {len(chunks)} chunks.")
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks to ChromaDB.")


if __name__ == "__main__":
    run_pipeline()
