import os
import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation
from src.task9_retrieval_pipeline import retrieve


load_dotenv()

st.set_page_config(
    page_title="Hệ thống Tư vấn Tuyển sinh Đại học - RAG Pipeline",
    page_icon="🎓",
    layout="wide",
)

# Custom CSS for enhanced aesthetics
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .source-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 10px 14px;
        margin-bottom: 8px;
        border-radius: 4px;
        font-size: 0.9rem;
    }
    .method-badge {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 12px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        margin-right: 6px;
    }
    .badge-hybrid { background-color: #DBEAFE; color: #1E40AF; }
    .badge-dense { background-color: #DCFCE7; color: #166534; }
    .badge-bm25 { background-color: #FEF3C7; color: #92400E; }
    .badge-pageindex { background-color: #F3E8FF; color: #6B21A8; }
</style>
""", unsafe_allow_html=True)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar
with st.sidebar:
    st.header("⚙️ Cấu hình Hệ thống")
    st.caption("Chủ đề: **Tuyển sinh đại học**")
    
    top_k = st.slider("Số lượng Chunks (Top-K)", min_value=1, max_value=10, value=5)
    
    st.divider()
    st.subheader("💡 Câu hỏi mẫu")
    sample_queries = [
        "Quy định cộng điểm ưu tiên theo Thông tư của Bộ GD&ĐT như thế nào?",
        "Các phương thức xét tuyển chính vào Đại học Bách Khoa Hà Nội?",
        "Thời gian và nguyên tắc đăng ký nguyện vọng xét tuyển đại học?",
        "Quy định xét tuyển sớm của các trường đại học?",
        "Học phí đại học có những quy định chính sách hỗ trợ gì?",
    ]
    for sq in sample_queries:
        if st.button(sq, key=f"btn_{sq}", use_container_width=True):
            st.session_state.preset_query = sq

    st.divider()
    if st.button("🗑️ Xoá lịch sử hội thoại", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Header
st.markdown('<div class="main-title">🎓 Trợ Lý Tuyển Sinh Đại Học AI</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Hệ thống RAG Pipeline (Hybrid Search + RRF + Citation) tra cứu quy chế tuyển sinh, chỉ tiêu và phương thức xét tuyển.</div>', unsafe_allow_html=True)

def render_sources(sources: list, retrieval_source: str):
    if not sources:
        return
    with st.expander(f"📚 Xem {len(sources)} nguồn tài liệu trích dẫn (Nguồn: {retrieval_source.upper()})"):
        for idx, src in enumerate(sources, 1):
            meta = src.get("metadata", {})
            title = meta.get("title", "Tài liệu")
            source = meta.get("source", "Nguồn")
            doc_type = meta.get("doc_type", "Chính sách")
            score = src.get("score", 0.0)
            method = src.get("retrieval_method", "hybrid")
            badge_class = f"badge-{method}"

            st.markdown(
                f"""
                <div class="source-card">
                    <b>[{idx}] {title}</b> ({source})<br>
                    <span class="method-badge {badge_class}">{method}</span>
                    <small><b>Điểm tương đồng:</b> {score:.4f} | <b>Loại:</b> {doc_type}</small>
                    <p style="margin-top:6px; color:#374151;">{src.get('content', '')}</p>
                </div>
                """,
                unsafe_allow_html=True
            )

# Render chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            render_sources(message["sources"], message.get("retrieval_source", "hybrid"))

# Check for preset query from buttons
input_query = st.chat_input("Nhập thắc mắc về tuyển sinh đại học...")
if getattr(st.session_state, "preset_query", None):
    input_query = st.session_state.preset_query
    del st.session_state.preset_query

if input_query:
    st.session_state.messages.append({"role": "user", "content": input_query})
    with st.chat_message("user"):
        st.markdown(input_query)

    with st.chat_message("assistant"):
        with st.spinner("Đang tra cứu cơ sở dữ liệu quy chế tuyển sinh..."):
            result = generate_with_citation(input_query, top_k=top_k)
            answer = result["answer"]
            sources = result.get("sources", [])
            retrieval_source = result.get("retrieval_source", "none")

            st.markdown(answer)
            if sources:
                render_sources(sources, retrieval_source)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": sources,
        "retrieval_source": retrieval_source,
    })
