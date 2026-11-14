import re
from typing import Tuple

# Danh sách các từ khóa liên quan đến chuyển ngành, kỹ năng, việc làm, hướng nghiệp (Whitelisted Domain Keywords)
CAREER_DOMAIN_KEYWORDS = [
    # Chuyển ngành & Việc làm
    "chuyển ngành", "chuyen nganh", "đổi ngành", "doi nganh", "trái ngành", "trai nganh", "thất nghiệp", "that nghiep",
    "tìm việc", "tim viec", "xin việc", "phỏng vấn", "phong van", "cv", "resume", "portfolio", "skill gap", "khoảng trống kỹ năng",
    "kỹ năng", "ky nang", "kinh nghiệm", "kinh nghiem", "lộ trình", "roadmap", "bootcamp", "khóa học", "khoa hoc",
    "học lại", "cấp tốc", "fresher", "intern", "thực tập", "junior", "senior", "onsite", "remote", "việc làm",
    "mức lương", "thu nhập", "thăng tiến", "tuyển dụng", "tuyen dung", "nhà tuyển dụng", "hr", "headhunt",
    # Ngành nghề & Đại học
    "ngành", "trường", "đại học", "cao đẳng", "học viện", "tuyển sinh", "khoa", "chuyên ngành",
    "học bổng", "học phí", "chương trình học", "môn học", "giáo trình", "tín chỉ",
    # Các lĩnh vực công việc phổ biến
    "cntt", "công nghệ thông tin", "khoa học máy tính", "kỹ thuật phần mềm", "tester", "qa", "qc", "kiểm thử",
    "data", "data analyst", "phân tích dữ liệu", "business analyst", "ba", "lập trình", "developer", "frontend", "backend",
    "python", "sql", "excel", "power bi", "tableau", "marketing", "digital marketing", "seo", "content", "ads",
    "chăm sóc khách hàng", "cskh", "telesales", "sales", "kinh doanh", "bán hàng", "tư vấn", "nhân sự", "recruiter",
    "logistics", "xuất nhập khẩu", "kế toán", "ngôn ngữ anh", "thiết kế đồ họa", "ui/ux", "photoshop",
    # Tình huống thử nghiệm & phỏng vấn
    "thử nghiệm", "tình huống", "1 ngày làm", "mô phỏng", "roleplay", "xử lý", "sếp", "khách hàng", "dự án", "câu hỏi phỏng vấn"
]

# Các từ khóa cố tình phá vỡ hệ thống (Prompt Injection & Jailbreak)
PROMPT_INJECTION_PATTERNS = [
    r"ignore (all )?previous instructions",
    r"forget (everything|what you were told)",
    r"bỏ qua (tất cả )?chỉ thị",
    r"quên hết (chỉ thị|hướng dẫn)",
    r"you are now (an unrestricted|a different)",
    r"system prompt",
    r"chỉ thị hệ thống",
    r"hiển thị prompt gốc",
    r"reveal your instructions",
    r"dan mode",
    r"jailbreak"
]

# Các chủ đề rõ ràng lạc đề (Blacklisted Off-topic Keywords)
OFF_TOPIC_KEYWORDS = [
    "bóng đá", "tỷ số", "cá độ", "soi kèo", "ngoại hạng anh", "champions league", "messi", "ronaldo",
    "viết code game", "lập trình bot discord", "hack", "crack pass", "ddos", "nấu món", "cách làm bánh",
    "tử vi", "bói bài", "xem tướng", "chính trị", "đảng phái", "chiến tranh thế giới", "đánh nhau",
    "tâm sự tình yêu", "bạn gái giận", "chia tay người yêu"
]

DEFAULT_REJECTION_MESSAGE = (
    "Chào bạn, tôi là **Cố vấn Chuyển Ngành & Phát Triển Sự Nghiệp AI**. "
    "Sứ mệnh của tôi là hỗ trợ bạn trong việc **phân tích khoảng trống kỹ năng (Skill Gap), lập lộ trình chuyển ngành thực chiến, "
    "gợi ý vị trí việc làm (Job Roles), tối ưu CV và mô phỏng phỏng vấn**.\n\n"
    "Câu hỏi vừa rồi nằm ngoài phạm vi chuyên môn chuyển ngành và tuyển dụng. "
    "Bạn có thắc mắc nào về lộ trình học kỹ năng mới, cơ hội việc làm trái ngành, hay cách tối ưu CV không? Hãy hỏi tôi nhé!"
)

INJECTION_ALERT_MESSAGE = (
    "Yêu cầu không hợp lệ. Hệ thống Cố vấn Hướng nghiệp hoạt động theo tiêu chuẩn an toàn thông tin "
    "và chỉ phản hồi các nội dung phục vụ công tác tư vấn tuyển sinh đại học."
)


def validate_user_message(user_message: str) -> Tuple[bool, str, str]:
    """
    Kiểm duyệt câu hỏi của người dùng (Guardrails Engine).
    Trả về: (is_safe, category, feedback_message)
    """
    cleaned_message = user_message.strip().lower()
    
    # 1. Kiểm tra độ dài tối thiểu
    if len(cleaned_message) < 2:
        return False, "EMPTY_MESSAGE", "Em vui lòng nhập câu hỏi rõ ràng hơn để tôi có thể hỗ trợ em nhé!"
    
    # 2. Kiểm tra Prompt Injection / Phá rào
    for pattern in PROMPT_INJECTION_PATTERNS:
        if re.search(pattern, cleaned_message):
            return False, "PROMPT_INJECTION", INJECTION_ALERT_MESSAGE

    # 3. Kiểm tra các từ khóa lạc đề tiêu biểu
    for bad_kw in OFF_TOPIC_KEYWORDS:
        if bad_kw in cleaned_message:
            return False, "OFF_TOPIC", DEFAULT_REJECTION_MESSAGE

    # 4. Kiểm tra câu ngắn nếu không chứa bất kỳ từ khóa chuyên môn nào
    # Với các câu ngắn dưới 25 ký tự, nếu hỏi vu vơ ("alo", "chào bạn", "hello") thì vẫn cho qua để chào hỏi
    greeting_words = ["chào", "hello", "hi", "alo", "ơi", "bạn ơi", "thầy ơi", "cô ơi"]
    if any(g in cleaned_message for g in greeting_words) and len(cleaned_message) < 20:
        return True, "GREETING", ""

    # Nếu câu dài hơn mà không có bất kỳ liên hệ nào tới trường lớp, nghề nghiệp, điểm số, kỹ năng, lương...
    # Ta đánh dấu cẩn trọng nhưng cho phép AI kết hợp cùng System Prompt từ chối mềm.
    # Tuy nhiên, nếu câu chứa ít nhất 1 từ khóa chuyên môn, xem như Safe 100%.
    has_domain_keyword = any(kw in cleaned_message for kw in CAREER_DOMAIN_KEYWORDS)
    
    if not has_domain_keyword and len(cleaned_message) > 40:
        # Kiểm tra xem có phải câu hỏi toán/code/chuyện phiếm không liên quan không
        unrelated_signals = ["nấu ăn", "quân sự", "phim ảnh", "ca sĩ", "nhạc kịch", "truyện tranh", "mua sắm quần áo"]
        if any(sig in cleaned_message for sig in unrelated_signals):
            return False, "OFF_TOPIC", DEFAULT_REJECTION_MESSAGE

    return True, "PASSED", ""
