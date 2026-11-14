# 🎓 HỆ THỐNG CHATBOT AI ĐỊNH HƯỚNG CHỌN NGÀNH ĐẠI HỌC (ĐỒ ÁN CHUYÊN NGÀNH)

Hệ thống Chatbot AI thông minh hỗ trợ học sinh, sinh viên định hướng nghề nghiệp, tra cứu điểm chuẩn trường đại học, dự báo thị trường việc làm và trải nghiệm thực tế công việc tương lai.

---

## 📌 CÁC TÍNH NĂNG CỐT LÕI

### 1. Bốn Mô Hình Định Hướng Cốt Lõi:
1. **Chatbot Trắc nghiệm & Phân tích Đa chiều (Tư vấn cá nhân hóa):**
   - Đánh giá đa yếu tố (Khối thi, học lực, sở thích môi trường, tính cách hướng nội/ngoại, ngân sách học phí, khu vực địa lý).
   - Tích hợp tư duy Holland RIASEC & MBTI qua đàm thoại tự nhiên.
   - Trả về **Top 3–5 ngành học phù hợp nhất**, tính toán **% độ tương thích** và lý do chi tiết.
2. **Chatbot Chi tiết Ngành & Trường:**
   - Tra cứu điểm chuẩn 3 năm gần nhất các trường ĐH tại Việt Nam.
   - Bản đồ chương trình học (môn học đại cương, chuyên ngành, môn thử thách nhất).
   - So sánh học phí và cơ sở vật chất giữa các trường có cùng ngành đào tạo.
3. **Chatbot Phân tích Xu hướng Thị trường & Việc làm:**
   - Dự báo nhu cầu tuyển dụng 3–5 năm tới, mức lương khởi điểm Fresher & lộ trình thăng tiến.
   - Góc nhìn thực tế (áp lực công việc, OT, sự cạnh tranh của trí tuệ nhân tạo).
   - Gợi ý kỹ năng mềm và chứng chỉ nên tích lũy ngay từ sớm.
4. **Chatbot Giả lập "Thử nghiệm 1 ngày làm nghề" (Roleplay):**
   - Đưa sinh viên vào tình huống thực tế của ngành (Ví dụ: Nghẽn mạng hệ thống IT, khủng hoảng truyền thông Marketing...).
   - Cho học sinh chọn phương án xử lý (A, B, C) và AI phân tích kết quả tư duy nghề nghiệp.

### 2. Thu thập Thông tin qua UI Form 4 Bước:
- **Bước 1:** Khối thi / Tổ hợp môn thế mạnh (A00, A01, D01, C00, Khác) & Học lực (Xuất sắc, Giỏi, Khá, Trung bình).
- **Bước 2:** Môi trường làm việc yêu thích & Slider mức độ Hướng nội/Hướng ngoại (1 - 5).
- **Bước 3:** Khu vực ưu tiên học tập (TP.HCM, Hà Nội, Đà Nẵng...) & Mức học phí/năm mong muốn.
- **Bước 4:** Kỳ vọng đầu ra (Dễ kiếm việc, Lương cao, Đam mê cá nhân, Đi onsite/nước ngoài).

### 3. Hai Tính Năng Mở Rộng:
- **Lưu lịch sử tư vấn & Xuất báo cáo PDF:** Học sinh có thể lưu lại kết quả và tải file PDF báo cáo định hướng cá nhân hóa.
- **Admin Dashboard:** Trang quản trị thống kê xu hướng chọn ngành, phân bổ khối thi, học lực và học phí của học sinh.

### 4. Hệ Thống Bảo Mật Guardrails Chống Lạc Đề:
- **Lớp 1 (Backend Filter):** Chặn các từ khóa lạc đề (bóng đá, game, code linh tinh, chính trị...) và phát hiện kỹ thuật Jailbreak/Prompt Injection.
- **Lớp 2 (System Prompt Constraint):** Chỉ thị hệ thống bắt buộc AI chỉ trả lời trong phạm vi tuyển sinh, hướng nghiệp đại học.

---

## 🛠️ KIẾN TRÚC BACKEND (PYTHON FASTAPI)

```
DACN/
└── backend/
    ├── app/
    │   ├── main.py                  # Entrypoint FastAPI & CORS & Mount Routers
    │   ├── config.py                # Cấu hình biến môi trường
    │   ├── database.py              # Kết nối SQLite & SQLAlchemy Engine
    │   ├── models.py                # Bảng CSDL (User, Profile, Session, Chat, Major)
    │   ├── schemas.py               # Pydantic Schemas validate Form & Payload
    │   ├── guardrails.py            # Bộ lọc Guardrails chặn câu hỏi lạc đề
    │   ├── prompt_templates.py      # System Prompts cho 4 chế độ định hướng
    │   ├── gemini_service.py        # Tích hợp Google Gemini API & Fallback Engine
    │   ├── pdf_generator.py         # Module xuất file PDF báo cáo
    │   └── routers/
    │       ├── auth.py              # Đăng ký / Đăng nhập học sinh & Admin
    │       ├── profile.py           # Tiếp nhận Form 4 bước & Trả phân tích ban đầu
    │       ├── chat.py              # Hội thoại đa lượt, kiểm duyệt và 4 chế độ
    │       ├── history.py           # Xem lịch sử tư vấn & Download PDF
    │       └── admin.py             # Thống kê số liệu cho Admin Dashboard
    ├── requirements.txt             # Danh sách thư viện Python cần thiết
    ├── .env.example                 # Mẫu file cấu hình API Key
    └── run.py                       # Script khởi chạy Server
```

---

## 🚀 HƯỚNG DẪN CÀI ĐẶT & CHẠY BACKEND

### 1. Chuẩn bị môi trường Python:
Nếu máy bạn chưa có Python, hãy tải và cài đặt [Python 3.11 hoặc 3.12](https://www.python.org/downloads/) (Lưu ý tích chọn **"Add Python to PATH"** khi cài đặt).

### 2. Tạo môi trường ảo & Cài đặt thư viện:
Mở PowerShell hoặc Command Prompt tại thư mục `DACN/backend`:

```powershell
# Tạo môi trường ảo venv
python -m venv venv

# Kích hoạt môi trường ảo (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# Cài đặt toàn bộ thư viện cần thiết
pip install -r requirements.txt
```

### 3. Cấu hình file `.env`:
Tạo một file `.env` từ file `.env.example`:
```powershell
copy .env.example .env
```
Mở file `.env` và điền `GEMINI_API_KEY` của bạn (Lấy miễn phí tại [Google AI Studio](https://aistudio.google.com/)).
*(Lưu ý: Hệ thống đã tích hợp sẵn cơ chế **Fallback Engine thông minh**, nên kể cả khi bạn chưa điền API Key, hệ thống vẫn phản hồi và demo mượt mà các chức năng!)*

### 4. Khởi chạy Server:
```powershell
python run.py
```
Server sẽ chạy tại địa chỉ: **http://localhost:8000**

---

## 📖 TÀI LIỆU API & KIỂM THỬ TRỰC TIẾP (SWAGGER UI)

Truy cập: **http://localhost:8000/docs** trên trình duyệt để kiểm thử toàn bộ API:
- `POST /api/auth/register`: Đăng ký tài khoản học sinh / admin
- `POST /api/auth/login`: Đăng nhập nhận JWT Token
- `POST /api/profile/submit`: Nộp Form 4 bước, nhận Top 3 ngành & % Match
- `POST /api/chat/message`: Gửi tin nhắn hội thoại Chatbot (tự động kích hoạt Guardrails & 4 Mode)
- `GET /api/history`: Xem lịch sử các lần tư vấn
- `GET /api/history/{id}/export-pdf`: Tải xuống file PDF báo cáo hướng nghiệp
- `GET /api/admin/dashboard`: Lấy dữ liệu biểu đồ thống kê cho Admin
