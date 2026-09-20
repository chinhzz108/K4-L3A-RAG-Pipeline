"""
Task 10 — Generation có citation.

Hướng dẫn:
    1. Retrieve top-k chunks.
    2. Reorder để giảm lost-in-the-middle.
    3. Format context kèm title và source.
    4. Gọi provider được chọn trong .env.
    5. Trả answer, sources và retrieval_source.

Nếu context không đủ hoặc provider lỗi, trả safe refusal; không bịa thông tin.
"""

import os
from dotenv import load_dotenv

from .task9_retrieval_pipeline import retrieve


load_dotenv()

TOP_K = 5
TOP_P = 0.9
TEMPERATURE = 0.3

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")

SYSTEM_PROMPT = """Bạn là trợ lý AI giải đáp thông tin tuyển sinh đại học chính xác và đáng tin cậy.
Chỉ trả lời dựa vào Context được cung cấp bên dưới.
Mỗi khẳng định hoặc thông tin đưa ra phải kèm theo trích dẫn nguồn, ví dụ: [Document 1] hoặc tên tài liệu.
Nếu thông tin trong Context không đủ bằng chứng để trả lời câu hỏi, hãy trả lời chính xác: "Tôi không thể xác minh thông tin này từ nguồn hiện có." và tuyệt đối không tự bịa đặt thông tin."""


def reorder_for_llm(chunks: list[dict]) -> list[dict]:
    """Đưa chunks quan trọng về đầu và cuối context (chống lost-in-the-middle)."""
    if len(chunks) <= 2:
        return list(chunks)
    front = chunks[::2]
    back = chunks[1::2]
    return front + back[::-1]


def format_context(chunks: list[dict]) -> str:
    """Tạo context có title và source label rõ ràng cho từng chunk."""
    parts = []
    for index, chunk in enumerate(chunks, 1):
        metadata = chunk.get("metadata", {})
        title = metadata.get("title", "Không có tiêu đề")
        source = metadata.get("source", "Nguồn không xác định")
        parts.append(
            f"[Document {index} | Title: {title} | Source: {source}]\n{chunk['content']}"
        )
    return "\n\n---\n\n".join(parts)


def call_llm(system_prompt: str, user_message: str) -> str:
    """Gọi OpenAI, Gemini hoặc Anthropic theo cấu hình."""
    provider = os.getenv("LLM_PROVIDER", LLM_PROVIDER).lower()
    model_name = os.getenv("LLM_MODEL") or LLM_MODEL

    if provider == "gemini":
        from google import genai
        from google.genai import types

        api_key = os.getenv("GEMINI_API_KEY")
        client = genai.Client(api_key=api_key)
        response = client.models.generate_content(
            model=model_name or "gemini-2.5-flash",
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=TEMPERATURE,
            ),
        )
        return response.text or ""

    elif provider == "openai":
        from openai import OpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model_name or "gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message},
            ],
            temperature=TEMPERATURE,
        )
        return response.choices[0].message.content or ""

    elif provider == "anthropic":
        import anthropic

        api_key = os.getenv("ANTHROPIC_API_KEY")
        client = anthropic.Anthropic(api_key=api_key)
        response = client.messages.create(
            model=model_name or "claude-3-5-haiku-20241022",
            system=system_prompt,
            messages=[{"role": "user", "content": user_message}],
            temperature=TEMPERATURE,
            max_tokens=1024,
        )
        return response.content[0].text or ""

    else:
        raise ValueError(f"Unsupported LLM_PROVIDER: {provider}")


def generate_with_citation(query: str, top_k: int = TOP_K) -> dict:
    """Trả về GenerationResult theo đúng hợp đồng của module."""
    chunks = retrieve(query, top_k=top_k)
    if not chunks:
        return {
            "answer": "Tôi không thể xác minh thông tin này từ nguồn hiện có.",
            "sources": [],
            "retrieval_source": "none",
        }

    reordered = reorder_for_llm(chunks)
    context = format_context(reordered)
    user_message = f"Context:\n{context}\n\nQuestion: {query}"

    try:
        answer = call_llm(SYSTEM_PROMPT, user_message)
    except Exception as error:
        answer = f"Lỗi khi sinh câu trả lời: {error}"

    method = chunks[0].get("retrieval_method", "hybrid")
    retrieval_source = "pageindex" if method == "pageindex" else "hybrid"

    return {
        "answer": answer,
        "sources": chunks,
        "retrieval_source": retrieval_source,
    }


if __name__ == "__main__":
    print(generate_with_citation("Phương thức xét tuyển bằng điểm thi tốt nghiệp THPT như thế nào?"))
