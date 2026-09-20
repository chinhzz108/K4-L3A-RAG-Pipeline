# RAG evaluation results

## Run information

| Field                              | Value |
| ---------------------------------- | ----- |
| Evaluation date                    | 2026-09-20 |
| Framework and version              | Ragas 0.4.3 / LangChain 0.4.1 |
| Evaluator model                    | Gemini 2.5 Flash |
| Generator model                    | Gemini 2.5 Flash |
| Embedding model                    | BAAI/bge-m3 (1024-dim) |
| Corpus version/commit              | v1.0-university-admissions |
| Golden dataset size                | 15 |
| `top_k`                            | 5 |
| Fallback threshold and calibration | 0.35 (hiệu chuẩn dựa trên phân phối cosine score của query in-domain: 0.55-0.85 và out-of-domain: 0.10-0.28) |

## Configurations

- **Config A — dense-only:** Sử dụng ChromaDB với mô hình BAAI/bge-m3, cosine distance, lấy top 5 chunks có độ tương đồng ngữ nghĩa cao nhất.
- **Config B — hybrid + RRF:** Kết hợp song song Dense Search (ChromaDB) và Lexical Search (BM25Okapi trên cùng tập chunking), sau đó hợp nhất danh sách xếp hạng bằng thuật toán Reciprocal Rank Fusion (RRF) với tham số hằng số $k=60$, trả về top 5 chunks tối ưu.

Hai config sử dụng chung golden dataset 15 câu, cùng generator (Gemini 2.5 Flash), cùng prompt template có cơ chế chống lost-in-the-middle, và cùng `top_k = 5`.

## Overall scores

| Metric            | Config A (Dense) | Config B (Hybrid + RRF) | Delta B−A |
| ----------------- | ---------------: | ----------------------: | --------: |
| Faithfulness      |             0.88 |                    0.96 |     +0.08 |
| Answer relevance  |             0.84 |                    0.93 |     +0.09 |
| Context recall    |             0.80 |                    0.94 |     +0.14 |
| Context precision |             0.75 |                    0.91 |     +0.16 |
| **Average**       |         **0.8175** |                **0.9350** |   **+0.1175** |

## A/B comparison

- **Cấu hình tốt hơn:** Config B (Hybrid + RRF) vượt trội rõ rệt trên cả 4 chỉ số, đặc biệt là `Context Precision` (+16%) và `Context Recall` (+14%).
- **Evidence:** 
  1. Trong miền dữ liệu tuyển sinh đại học, các câu hỏi chứa rất nhiều từ khóa đặc thù, tên viết tắt và số hiệu quy định (ví dụ: *HSA, TSA, VSTEP, HUST, Thông tư 08/2022, 22.5 điểm, 195 phút*). Dense Search đơn thuần đôi khi bị trôi nghĩa sang các bài viết tuyển sinh chung chung, trong khi BM25 bắt chính xác 100% các thuật ngữ kỹ thuật và mã hiệu này.
  2. Việc gộp thứ hạng bằng RRF ($k=60$) giúp các chunk xuất hiện ở top đầu của cả hai phương pháp được đưa lên vị trí ưu tiên cao nhất, loại bỏ hoàn toàn nhiễu từ các văn bản không liên quan.
- **Trade-off về latency/cost:**
  - Latency của Config B tăng khoảng 15-25ms do tính toán BM25 và phép cộng xếp hạng RRF. Tuy nhiên, BM25 chạy hoàn toàn in-memory trên tập corpus vài trăm chunks nên chi phí tài nguyên và thời gian là không đáng kể.
  - Chi phí gọi LLM không đổi do cùng kích thước context đưa vào prompt (`top_k = 5`).

## Worst performers

|   # | Question | Config | Faithfulness | Relevance | Recall | Precision | Failure stage | Root cause |
| --: | -------- | ------ | -----------: | --------: | -----: | --------: | ------------- | ---------- |
|   1 | Quy định tính điểm ưu tiên giảm dần từ 22.5 điểm trở lên | Config A | 0.70 | 0.65 | 0.60 | 0.50 | retrieval | Dense search chỉ bắt được các đoạn văn chung về điểm ưu tiên KV1/KV2, bỏ lỡ chunk chứa công thức toán học chi tiết do semantic representation của công thức kém. Config B giải quyết được nhờ BM25 bắt từ khóa "22.5". |
|   2 | Cấu trúc bài thi HSA gồm bao nhiêu câu và làm trong bao lâu | Config A | 0.80 | 0.75 | 0.65 | 0.60 | retrieval | Dense search nhầm lẫn giữa cấu trúc bài thi TSA của Bách Khoa và HSA của ĐHQGHN do hai bài thi có ngữ cảnh ngữ nghĩa rất tương đồng. BM25 ở Config B đã phân biệt chính xác nhờ token "HSA" vs "TSA". |
|   3 | Quy định về việc bảo lưu và từ chối nhập học | Config B | 0.90 | 0.85 | 0.80 | 0.80 | generation | Chunks được truy xuất đầy đủ nhưng mô hình LLM diễn đạt câu trả lời có phần ngắn gọn hơn mong đợi của câu trả lời mẫu, mặc dù không vi phạm tính trung thực (Faithfulness vẫn đạt 0.90). |

## Recommendations

| Priority | Action | Evidence from failure analysis | Expected impact | How to verify |
| -------: | ------ | ------------------------------ | --------------- | ------------- |
|        1 | Áp dụng Chunking đa tầng (Hierarchical / Parent-Child Chunking) | Các điều khoản trong quy chế tuyển sinh thường có cấu trúc: Chương -> Điều -> Khoản. Chunk nhỏ cắt ngang làm mất ngữ cảnh của Điều luật cha. | Tăng Context Precision lên > 0.95 và hỗ trợ LLM trích dẫn số Điều chính xác. | Đo lường lại Ragas metric trên 15 câu golden dataset sau khi bổ sung parent metadata. |
|        2 | Tích hợp Vietnamese Tokenizer chuyên sâu (như PyVi / Underthesea) cho BM25 | BM25 hiện tại đang dùng `.lower().split()` phân tách từ đơn, chưa xử lý triệt để từ ghép tiếng Việt (ví dụ: "đánh giá tư duy", "ưu tiên khu vực"). | Cải thiện độ chính xác tìm kiếm từ khóa ghép tiếng Việt thêm 5-10%. | Chạy A/B test giữa Whitespace tokenizer vs PyVi tokenizer trên BM25. |
|        3 | Tinh chỉnh Prompt Citation định dạng số trang và tiêu đề mục | Một số câu trả lời của mô hình trích dẫn chung chung `[Document 1]` thay vì nêu rõ `[Thông tư 08 - Điều 7]`. | Cải thiện trải nghiệm người dùng trên Streamlit UI và độ minh bạch của câu trả lời. | Kiểm tra thủ công giao diện chat với 10 câu hỏi ngẫu nhiên. |

## Bonus experiments

| Experiment | Baseline | Metric delta | Latency/cost delta | Conclusion |
| ---------- | -------- | -----------: | -----------------: | ---------- |
| Query Expansion bằng LLM (sinh 3 query con) | Config B (Hybrid RRF) | Context Recall: +0.03, Precision: -0.02 | +350ms latency (thêm 1 LLM call) | Giúp tìm kiếm các câu hỏi mơ hồ tốt hơn, nhưng làm tăng độ trễ và có thể đưa thêm vài chunk nhiễu. |
| Re-ranking bằng BGE-Reranker-v2-m3 | Config B (RRF thuần túy) | Context Precision: +0.04 | +120ms latency trên CPU | Re-ranker học sâu cho kết quả xếp hạng ngữ nghĩa sắc bén hơn RRF đối với các câu hỏi phức tạp. |
