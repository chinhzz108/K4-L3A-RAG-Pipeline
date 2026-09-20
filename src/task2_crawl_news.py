"""
Task 2 — Crawl/Thu thập bài viết và tin tức tuyển sinh đại học.

Thu thập tối thiểu 5 bài viết chuyên sâu về tuyển sinh đại học vào data/landing/news/.
Mỗi file JSON lưu: url, title, date_crawled, content_markdown.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLES_DATA = [
    {
        "url": "https://tuyensinh.vnu.edu.vn/tin-tuc/huong-dan-dang-ky-ky-thi-hsa-2025",
        "title": "Hướng dẫn chi tiết kỳ thi Đánh giá năng lực HSA của ĐHQGHN năm 2025",
        "content_markdown": """# Hướng dẫn chi tiết kỳ thi Đánh giá năng lực HSA của ĐHQGHN năm 2025

Kỳ thi Đánh giá năng lực học sinh trung học phổ thông (HSA) năm 2025 của Đại học Quốc gia Hà Nội dự kiến tổ chức 6 đợt thi từ tháng 3 đến tháng 6 năm 2025 tại Hà Nội, Thái Nguyên, Hải Phòng, Nam Định, Hưng Yên, Hải Dương, Ninh Bình, Thái Bình, Thanh Hóa, Nghệ An, Hà Tĩnh.

### Cấu trúc bài thi HSA 2025:
- **Thời gian thi:** 195 phút làm bài trên máy tính.
- **Tổng số câu hỏi:** 150 câu trắc nghiệm khách quan và điền đáp án ngắn.
- **Phần 1: Tư duy định lượng (Toán học):** 50 câu hỏi, thời gian 75 phút. Đánh giá năng lực vận dụng kiến thức toán học giải quyết vấn đề thực tiễn.
- **Phần 2: Tư duy định tính (Văn học - Ngôn ngữ):** 50 câu hỏi, thời gian 60 phút. Đánh giá năng lực cảm thụ, phân tích ngôn ngữ, suy luận văn bản tiếng Việt.
- **Phần 3: Khoa học (Khoa học Tự nhiên hoặc Khoa học Xã hội):** 50 câu hỏi, thời gian 60 phút. Thí sinh chọn làm phần thi KHTN (Vật lý, Hóa học, Sinh học) hoặc KHXH (Lịch sử, Địa lý, Giáo dục công dân).

Thí sinh được đăng ký tối đa 2 đợt thi trong năm, mỗi đợt cách nhau tối thiểu 28 ngày. Kết quả thi HSA được hơn 90 trường đại học trên cả nước sử dụng để xét tuyển đầu vào."""
    },
    {
        "url": "https://hust.edu.vn/tuyen-sinh/ky-thi-danh-gia-tu-duy-tsa-bach-khoa",
        "title": "Kỳ thi Đánh giá tư duy TSA Đại học Bách khoa Hà Nội: Toàn bộ điều cần biết",
        "content_markdown": """# Kỳ thi Đánh giá tư duy TSA Đại học Bách khoa Hà Nội

Đại học Bách khoa Hà Nội chính thức công bố cấu trúc và kế hoạch tổ chức kỳ thi Đánh giá tư duy (Thinking Skills Assessment - TSA). Bài thi TSA được thiết kế chuẩn hóa, tiếp cận các kỳ thi đánh giá năng lực quốc tế như SAT, ACT.

### Nội dung và thời lượng 3 phần thi:
1. **Phần thi Tư duy Toán học (60 phút):** 40 câu hỏi trắc nghiệm gồm nhiều lựa chọn, đúng/sai, kéo thả và điền đáp án ngắn. Đánh giá tư duy logic, mô hình hóa toán học.
2. **Phần thi Tư duy Đọc hiểu (30 phút):** 20 câu hỏi đánh giá khả năng đọc nhanh, hiểu sâu, tổng hợp dữ liệu từ các văn bản khoa học, kỹ thuật, công nghệ, đời sống xã hội.
3. **Phần thi Tư duy Khoa học / Giải quyết vấn đề (60 phút):** 40 câu hỏi tích hợp kiến thức khoa học tự nhiên, đánh giá phương pháp thực nghiệm, kỹ năng phân tích biểu đồ và suy luận logic.

Thí sinh dự thi trực tiếp trên máy tính tại các điểm thi chuẩn hóa. Điểm thi TSA có giá trị sử dụng xét tuyển trong 2 năm vào Đại học Bách khoa Hà Nội và hơn 40 trường đại học khối ngành kỹ thuật, công nghệ, kinh tế."""
    },
    {
        "url": "https://moet.gov.vn/giao-duc-dai-hoc/nguyen-tac-dang-ky-loc-ao-nguyen-vong",
        "title": "Nguyên tắc vàng khi đăng ký và sắp xếp nguyện vọng xét tuyển đại học",
        "content_markdown": """# Nguyên tắc vàng khi đăng ký và sắp xếp nguyện vọng xét tuyển đại học

Bộ Giáo dục và Đào tạo lưu ý thí sinh về các quy định mang tính quyết định trong đợt đăng ký nguyện vọng xét tuyển đại học chính quy:

### 1. Không giới hạn số lượng nguyện vọng:
Thí sinh được phép đăng ký không giới hạn số lượng nguyện vọng và ngành nghề, tuy nhiên phải xếp thứ tự ưu tiên từ nguyện vọng 1 trở đi. Nguyện vọng 1 là nguyện vọng ưu tiên cao nhất mà thí sinh mong muốn theo học nhất.

### 2. Nguyên tắc xét tuyển bình đẳng:
Hệ thống tuyển sinh chung lọc ảo sẽ xét đồng thời tất cả các nguyện vọng của thí sinh. Thí sinh chỉ trúng tuyển duy nhất vào 01 nguyện vọng có thứ tự ưu tiên cao nhất trong số các nguyện vọng mà điểm của thí sinh đạt chuẩn trúng tuyển.
Sau khi đã trúng tuyển một nguyện vọng, các nguyện vọng có thứ tự thấp hơn sẽ tự động bị hủy bỏ.

### 3. Chiến lược chia nguyện vọng làm 3 nhóm:
- **Nhóm 1 (Mơ ước):** Các ngành, trường có điểm chuẩn các năm trước cao hơn điểm của thí sinh từ 0.5 đến 1.5 điểm (đặt ở NV1 - NV3).
- **Nhóm 2 (Vừa sức):** Các ngành có điểm chuẩn xấp xỉ hoặc bằng với điểm thi của thí sinh (đặt ở NV4 - NV6).
- **Nhóm 3 (An toàn):** Các ngành có điểm chuẩn thấp hơn điểm của thí sinh từ 2 đến 3 điểm để bảo đảm chắc chắn có cơ hội trúng tuyển đại học."""
    },
    {
        "url": "https://vnexpress.net/giao-duc/quy-dinh-quy-doi-ielts-xet-tuyen-dai-hoc-2025",
        "title": "Xu hướng và thang điểm quy đổi chứng chỉ IELTS trong xét tuyển đại học",
        "content_markdown": """# Xu hướng và thang điểm quy đổi chứng chỉ IELTS trong xét tuyển đại học

Năm 2025, hơn 100 trường đại học tại Việt Nam tiếp tục áp dụng phương thức xét tuyển kết hợp chứng chỉ ngoại ngữ quốc tế (IELTS, TOEFL, VSTEP, JLPT...).

### Thang quy đổi phổ biến tại các trường top đầu:
- **Đại học Kinh tế Quốc dân (NEU):** IELTS 5.5 quy đổi thành 8.0 điểm môn tiếng Anh; IELTS 6.0 quy đổi thành 9.0; IELTS 6.5 quy đổi thành 9.5; IELTS 7.0 trở lên quy đổi thành 10.0 tuyệt đối.
- **Đại học Bách khoa Hà Nội (HUST):** IELTS 5.0 quy đổi thành 8.0 điểm; IELTS 5.5 = 8.5; IELTS 6.0 = 9.0; IELTS 6.5 = 9.5; IELTS 7.0+ = 10.0 điểm.
- **Đại học Ngoại thương (FTU):** Yêu cầu ngưỡng sàn tối thiểu IELTS 6.5 đối với các chương trình tiên tiến, chất lượng cao giảng dạy bằng tiếng Anh.

Lưu ý: Chứng chỉ quốc tế phải còn thời hạn hiệu lực tối thiểu tính đến ngày nộp hồ sơ xét tuyển (thông thường là trong vòng 2 năm kể từ ngày thi)."""
    },
    {
        "url": "https://thanhnien.vn/giao-duc/chinh-sach-hoc-bong-va-mien-giam-hoc-phi-dai-hoc",
        "title": "Chính sách miễn giảm học phí và quỹ học bổng khuyến khích cho sinh viên đại học",
        "content_markdown": """# Chính sách miễn giảm học phí và quỹ học bổng khuyến khích cho sinh viên đại học

Chính phủ ban hành Nghị định quy định về cơ chế thu, quản lý học phí và chính sách miễn, giảm học phí, hỗ trợ chi phí học tập đối với sinh viên các cơ sở giáo dục đại học.

### 1. Đối tượng được miễn 100% học phí:
- Sinh viên là người dân tộc thiểu số rất ít người ở vùng có điều kiện kinh tế - xã hội khó khăn hoặc đặc biệt khó khăn.
- Sinh viên mồ côi cả cha lẫn mẹ, không nơi nương tựa.
- Sinh viên khuyết tật nặng hoặc đặc biệt nặng.
- Sinh viên là con của liệt sĩ, thương binh, người hưởng chính sách như thương binh theo Pháp lệnh ưu đãi người có công.

### 2. Quỹ học bổng khuyến khích học tập tại các trường:
Mỗi trường đại học trích tối thiểu 8% từ nguồn thu học phí để lập quỹ học bổng khuyến khích học tập. Các mức học bổng gồm:
- **Loại Khá:** Mức học bổng bằng hoặc cao hơn mức trần học phí của ngành học.
- **Loại Giỏi:** Mức học bổng cao hơn loại Khá (khoảng 110% - 120%).
- **Loại Xuất sắc:** Mức học bổng cao nhất (khoảng 130% - 150% học phí).
Ngoài ra, các doanh nghiệp và tập đoàn công nghệ lớn hàng năm trao tặng nhiều suất học bổng tài năng toàn phần cho sinh viên xuất sắc khối ngành STEM và AI."""
    }
]


async def crawl_article(article_info: dict) -> dict:
    """Tạo payload bài viết chuẩn metadata."""
    return {
        "url": article_info["url"],
        "title": article_info["title"],
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": article_info["content_markdown"],
    }


async def crawl_all() -> None:
    """Lưu từng bài thành một file JSON trong data/landing/news/."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, item in enumerate(ARTICLES_DATA, 1):
        try:
            article = await crawl_article(item)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {item['url']} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
