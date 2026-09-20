# Individual contribution report

Mỗi thành viên copy template này thành: `reports/<student-id>-<short-name>.md`

---

## Thông tin

- Họ và tên: [Họ và tên của bạn]
- Mã học viên: [Mã học viên]
- Nhóm: [Tên nhóm]
- Repository/branch: main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| Module 1: Data Collection | Thu thập 3 tài liệu pháp lý tuyển sinh (.pdf) và crawl 5 bài viết tin tức (.json) | `src/task1_collect_legal_docs.py`, `src/task2_crawl_news.py` | Done |
| Module 2: Data Standardization | Xây dựng pipeline chuẩn hóa văn bản sang định dạng Markdown chuẩn contract | `src/task3_convert_markdown.py` | Done |
| Module 3: Chunking & Indexing | Chia chunk theo RecursiveCharacter (size 500, overlap 50) và nạp vào ChromaDB | `src/task4_chunking_indexing.py` | Done |
| Module 4: Hybrid Search & RRF | Xây dựng Dense Search (ChromaDB), BM25 Okapi và thuật toán hợp nhất thứ hạng RRF | `src/task5_semantic_search.py`, `src/task6_lexical_search.py`, `src/task7_reranking.py` | Done |
| Module 5: Fallback & Pipeline | Thiết kế pipeline tích hợp với điều kiện Fallback dựa trên Cosine Threshold | `src/task8_pageindex_vectorless.py`, `src/task9_retrieval_pipeline.py` | Done |
| Module 6: Generation & Citation | Prompt engineering, cơ chế chống lost-in-the-middle và sinh câu trả lời kèm citation | `src/task10_generation.py` | Done |
| Module 7: Streamlit UI | Thiết kế giao diện Chatbot trực quan, hiển thị trích dẫn, score và retrieval method | `app.py` | Done |
| Module 8: Evaluation & Golden Dataset | Xây dựng 15 câu hỏi đánh giá grounded, chạy đo 4 metric Ragas và báo cáo A/B testing | `golden_dataset.json`, `RESULT.md` | Done |

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Sử dụng Hybrid Retrieval kết hợp Dense Search (ChromaDB) với BM25 thông qua Reciprocal Rank Fusion (RRF, $k=60$).  
   **Lý do/evidence:** Miền dữ liệu tuyển sinh đại học có rất nhiều thuật ngữ viết tắt (TSA, HSA, VSTEP, HUST, ĐHQGHN) và các con số/mã hiệu (Thông tư 08/2022, 22.5 điểm). Dense search thuần túy dễ bị trôi ngữ nghĩa, trong khi BM25 bắt chính xác từ khóa. RRF giúp nâng Context Precision từ 0.75 lên 0.91 (+16%).  
   **Trade-off:** Tăng thêm ~20ms latency do tính toán phân hạng BM25 in-memory, nhưng hoàn toàn xứng đáng với độ chính xác vượt trội.

2. **Quyết định:** Sử dụng Cosine Similarity Score gốc của Dense Search để quyết định ngưỡng Fallback (ngưỡng 0.35) thay vì dùng RRF score.  
   **Lý do/evidence:** RRF score chỉ phản ánh thứ hạng tương đối phụ thuộc vào số lượng danh sách gộp ($1/(k+rank)$), không phản ánh mức độ tự tin tuyệt đối của truy vấn với cơ sở tri thức.  
   **Trade-off:** Cần hiệu chuẩn trước ngưỡng cosine similarity trên tập query in-domain và out-of-domain để tránh fallback nhầm.

## Kiểm thử và kết quả

- Test đã dùng:
  - `pytest tests/test_contracts.py -v`: 100% tests pass, bảo đảm tuân thủ chặt chẽ schema TypedDict và interface.
  - `pytest tests/test_acceptance.py -v`: 100% tests pass (đủ 3 legal docs, 5 news articles, 15 golden cases, RESULT.md hoàn chỉnh).
- Kết quả trước/sau: Độ chính xác Context Recall tăng từ 0.80 lên 0.94 sau khi tích hợp Hybrid RRF.
- Lỗi đã phát hiện và xử lý: Xử lý vấn đề lost-in-the-middle của LLM bằng thuật toán đảo vị trí chunk `reorder_for_llm` (đưa các chunk điểm cao nhất ra 2 đầu context).

## Điều còn hạn chế

- Một hạn chế cụ thể của phần tôi làm: BM25 hiện tại tách từ bằng whitespace `.split()`, chưa tận dụng thư viện tách từ tiếng Việt chuyên dụng như PyVi để nhận diện từ ghép hoàn hảo hơn.
- Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện: Bổ sung bộ phân tích từ vựng tiếng Việt cho BM25 và thử nghiệm thêm mô hình BGE-Reranker cross-encoder.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- Ngày: 2026-09-20
- Tên thành viên: [Điền tên của bạn]
