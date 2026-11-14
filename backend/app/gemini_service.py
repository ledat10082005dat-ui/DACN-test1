import json
import logging
import requests
import httpx
from typing import List, Dict, Any, AsyncIterator
from app.config import settings
from app.prompt_templates import build_system_prompt

logger = logging.getLogger(__name__)

# =========================================================================
# KHO TRI THỨC VỊ TRÍ CÔNG VIỆC, SKILL GAP & LỘ TRÌNH CHUYỂN NGÀNH (2026)
# =========================================================================
MOCK_JOB_ROLES_DATABASE = [
    {
        "target_field": "Phân tích dữ liệu (Data / BI Analyst)",
        "job_title": "Data Analyst / Business Intelligence (BI) Specialist",
        "base_fit": 92,
        "keywords": ["data", "phân tích", "số liệu", "kế toán", "excel", "sql", "toán", "thống kê", "ngân hàng"],
        "reason": "Phù hợp với người có tư duy phân tích định lượng, logic số liệu và mong muốn biến dữ liệu thô thành báo cáo hỗ trợ kinh doanh ra quyết định.",
        "transferable_skills": ["Tư duy logic số liệu", "Kỹ năng tổng hợp báo cáo", "Hiểu biết về nghiệp vụ kinh doanh/tài chính", "Sử dụng bảng tính"],
        "missing_skills": ["SQL truy vấn dữ liệu nâng cao", "Power BI / Tableau Dashboard", "Python xử lý dữ liệu (Pandas, Numpy)", "Data Modeling & ETL"],
        "roadmap_summary": "Tháng 1: Thành thạo SQL & Excel nâng cao -> Tháng 2: Xây dựng Dashboard Power BI thực tế -> Tháng 3: Hoàn thiện Portfolio 2 dự án phân tích dữ liệu bán hàng & tài chính.",
        "expected_salary": "10 – 16 triệu/tháng (Fresher/Junior) -> 18 – 28 triệu/tháng (sau 1.5 - 2 năm)",
        "suitable_companies": ["Fintech, Ngân hàng", "Sàn Thương mại điện tử", "Công ty Bán lẻ (Retail)", "Công ty Logistics & Supply Chain"]
    },
    {
        "target_field": "Kiểm thử phần mềm (Tester QA/QC)",
        "job_title": "Manual Tester (QA/QC Engineer) - Định hướng Automation",
        "base_fit": 94,
        "keywords": ["tester", "qa", "qc", "kiểm thử", "cẩn thận", "chi tiết", "văn phòng", "ngôn ngữ anh", "kế toán"],
        "reason": "Ngành có rào cản kỹ thuật vừa phải, cực kỳ chào đón người chuyển ngành có tính tỉ mỉ, kiên nhẫn và khả năng đọc hiểu quy trình nghiệp vụ.",
        "transferable_skills": ["Tính cách tỉ mỉ, kiên nhẫn", "Kỹ năng giao tiếp và mô tả lỗi rõ ràng", "Tư duy phản biện (Critical Thinking)", "Đọc hiểu tài liệu tiếng Anh"],
        "missing_skills": ["Kỹ thuật thiết kế Test Case (BVA, EP)", "Quy trình kiểm thử SDLC & STLC", "Công cụ quản lý lỗi Jira / Confluence", "Kiểm thử API cơ bản bằng Postman", "SQL kiểm tra dữ liệu database"],
        "roadmap_summary": "Tháng 1: Học lý thuyết kiểm thử & Viết Test Case -> Tháng 2: Thực hành bắt bug trên hệ thống Web/App thực tế & Postman API -> Tháng 3: Làm bộ Portfolio Test Case hoàn chỉnh nộp cùng CV.",
        "expected_salary": "9 – 14 triệu/tháng (Fresher) -> 16 – 22 triệu/tháng (khi biết thêm Automation/API)",
        "suitable_companies": ["Software Outsourcing (FPT Software, TMA, NashTech)", "Công ty Sản phẩm (Product Tech)", "Startups công nghệ"]
    },
    {
        "target_field": "Công nghệ thông tin (Lập trình Web/App)",
        "job_title": "Frontend Web Developer (ReactJS / VueJS)",
        "base_fit": 90,
        "keywords": ["lập trình", "web", "frontend", "developer", "cntt", "python", "javascript", "code", "html"],
        "reason": "Vị trí trực quan, sản phẩm hiển thị ngay trên trình duyệt giúp người chuyển ngành dễ học, dễ hình dung và dễ làm sản phẩm mẫu (Portfolio) để chứng minh năng lực.",
        "transferable_skills": ["Tư duy thuật toán và giải quyết vấn đề", "Tính kiên trì sửa lỗi (Debugging)", "Khả năng tự nghiên cứu tài liệu kỹ thuật", "Thẩm mỹ giao diện"],
        "missing_skills": ["HTML5, CSS3 hiện đại, Tailwind CSS", "JavaScript ES6+ chuyên sâu", "Thư viện ReactJS / Next.js", "Quản lý mã nguồn với Git/GitHub", "Gọi API RESTful & Xử lý bất đồng bộ"],
        "roadmap_summary": "Tháng 1: Làm chủ HTML, CSS, JavaScript cốt lõi -> Tháng 2: Xây dựng ứng dụng SPA với ReactJS & Tailwind -> Tháng 3: Hoàn thành 2 Web app có đăng nhập và kết nối API đưa lên GitHub & deploy Vercel.",
        "expected_salary": "10 – 17 triệu/tháng (Fresher) -> 20 – 35 triệu/tháng (sau 2 năm)",
        "suitable_companies": ["Software Outsourcing", "Tech Startups", "Agency truyền thông và phát triển Web", "Doanh nghiệp chuyển đổi số"]
    },
    {
        "target_field": "Chuyên viên phân tích nghiệp vụ (IT BA)",
        "job_title": "IT Business Analyst (Cầu nối Nghiệp vụ & Kỹ thuật)",
        "base_fit": 91,
        "keywords": ["ba", "business analyst", "nghiệp vụ", "tiếng anh", "giao tiếp", "tư vấn", "quản lý", "kinh doanh", "ngân hàng"],
        "reason": "Vị trí vàng cho người có thế mạnh tiếng Anh và kỹ năng giao tiếp hoặc có kinh nghiệm nghiệp vụ ngành ngân hàng, kế toán, logistics muốn nhảy sang mảng công nghệ.",
        "transferable_skills": ["Tiếng Anh giao tiếp và viết tài liệu tốt", "Kỹ năng đàm phán và thuyết trình", "Hiểu sâu về quy trình vận hành doanh nghiệp", "Kỹ năng lắng nghe và đặt câu hỏi"],
        "missing_skills": ["Vẽ sơ đồ luồng quy trình (BPMN, Flowchart)", "Kỹ thuật khơi gợi và thu thập yêu cầu (Elicitation)", "Viết tài liệu đặc tả BRD, SRS, User Stories", "Thiết kế Wireframe/Prototype trên Figma cơ bản"],
        "roadmap_summary": "Tháng 1: Nắm vững mô hình Agile/Scrum & Kỹ thuật viết User Story -> Tháng 2: Thực hành vẽ BPMN và làm Prototype Figma -> Tháng 3: Xây dựng bộ tài liệu dự án mẫu (SRS + Prototype) chuẩn chỉnh.",
        "expected_salary": "11 – 18 triệu/tháng (Fresher) -> 20 – 32 triệu/tháng (sau 2 năm)",
        "suitable_companies": ["Ngân hàng số, Bảo hiểm, Fintech", "Tập đoàn công nghệ đa quốc gia", "Doanh nghiệp tư vấn ERP/CRM"]
    },
    {
        "target_field": "Digital Marketing & Truyền thông",
        "job_title": "Performance & Content Marketing Specialist",
        "base_fit": 89,
        "keywords": ["marketing", "content", "quảng cáo", "ads", "seo", "viết lách", "sáng tạo", "bán hàng", "photoshop", "canva"],
        "reason": "Thích hợp cho người nhạy bén với xu hướng mạng xã hội, có năng khiếu viết lách, chụp ảnh, dựng video ngắn hoặc thích tối ưu hóa chiến dịch quảng cáo.",
        "transferable_skills": ["Năng lực sáng tạo nội dung", "Khả năng nắm bắt thị hiếu người tiêu dùng", "Kỹ năng sử dụng các công cụ chỉnh sửa hình ảnh/video", "Thấu hiểu hành vi khách hàng"],
        "missing_skills": ["Thiết lập và tối ưu chiến dịch Facebook Ads / TikTok Ads", "Tối ưu hóa công cụ tìm kiếm (SEO On-page/Off-page)", "Đọc hiểu số liệu Google Analytics 4 (GA4)", "Kỹ năng viết Copywriting thôi miên & A/B Testing"],
        "roadmap_summary": "Tháng 1: Học viết Content chuẩn SEO & Kịch bản video ngắn -> Tháng 2: Thực hành chạy chiến dịch Ads với ngân sách nhỏ & đo lường ROI -> Tháng 3: Tổng hợp Case study tăng trưởng vào Portfolio nộp ứng tuyển.",
        "expected_salary": "9 – 15 triệu/tháng (Khởi điểm) -> Hoa hồng doanh số / Dự án hấp dẫn",
        "suitable_companies": ["Digital Marketing Agency", "Doanh nghiệp Thương mại Điện tử", "Chuỗi bán lẻ F&B, Thời trang", "Startups"]
    },
    {
        "target_field": "Nhân sự & Tuyển dụng (IT Recruiter)",
        "job_title": "IT Recruiter / Talent Acquisition Specialist",
        "base_fit": 88,
        "keywords": ["nhân sự", "hr", "recruiter", "headhunt", "tuyển dụng", "giao tiếp", "tiếng anh", "con người"],
        "reason": "Phù hợp với người thích làm việc với con người, có thế mạnh ngoại ngữ và mong muốn gia nhập thị trường tuyển dụng công nghệ với mức hoa hồng cao.",
        "transferable_skills": ["Kỹ năng phỏng vấn và thấu hiểu ứng viên", "Xây dựng mối quan hệ cá nhân", "Kỹ năng thuyết phục và thương lượng", "Khả năng thích ứng nhanh"],
        "missing_skills": ["Đọc hiểu thuật ngữ công nghệ (Tech Stack: Java, Python, Cloud, DevOps...)", "Kỹ thuật Boolean Search trên LinkedIn & GitHub", "Quy trình sàng lọc CV & Phỏng vấn theo kỹ thuật STAR", "Quản lý nguồn ứng viên qua hệ thống ATS"],
        "roadmap_summary": "Tháng 1: Nắm bắt bức tranh tổng quan các vị trí IT & Thuật ngữ chuyên ngành -> Tháng 2: Thực hành Sourcing ứng viên trên LinkedIn -> Tháng 3: Tham gia thực tập tại Headhunt Agency để tích lũy dữ liệu.",
        "expected_salary": "8 – 14 triệu/tháng lương cứng + Thưởng hoa hồng tuyển dụng thành công",
        "suitable_companies": ["Công ty săn đầu người (Headhunter Agency: Navigos, Adecco, TopCV...)", "Doanh nghiệp IT quy mô lớn"]
    },
    {
        "target_field": "Chăm sóc khách hàng & Bán hàng B2B",
        "job_title": "Customer Success / B2B Sales Executive (Tech Solution)",
        "base_fit": 87,
        "keywords": ["bán hàng", "sales", "cskh", "telesales", "tư vấn", "giao tiếp", "khách hàng", "đàm phán"],
        "reason": "Cơ hội việc làm nhanh nhất, thu nhập không giới hạn dựa trên năng lực dành cho người có kỹ năng hoạt ngôn, kiên trì và chịu được áp lực doanh số.",
        "transferable_skills": ["Kỹ năng giao tiếp và xử lý từ chối của khách hàng", "Sự nhẫn nại và thấu cảm", "Kỹ năng gọi điện và mở rộng mạng lưới quan hệ", "Khả năng chịu áp lực chỉ tiêu (KPIs)"],
        "missing_skills": ["Quy trình bán hàng giải pháp B2B (Consultative Selling)", "Sử dụng phần mềm quản lý quan hệ khách hàng (HubSpot, Salesforce, Lark)", "Kỹ năng thuyết trình giải pháp kinh doanh trước hội đồng khách hàng doanh nghiệp"],
        "roadmap_summary": "Tháng 1: Học kịch bản telesales & Kỹ thuật xử lý từ chối -> Tháng 2: Thực hành demo giải pháp phần mềm/dịch vụ -> Tháng 3: Nộp đơn vào các công ty SaaS/B2B có chương trình đào tạo Fresher bài bản.",
        "expected_salary": "8 – 15 triệu/tháng cứng + Hoa hồng không giới hạn (tổng thu nhập 15 – 35+ triệu)",
        "suitable_companies": ["Công ty phần mềm SaaS (MISA, KiotViet, Haravan)", "Doanh nghiệp Viễn thông, Công nghệ giáo dục (EdTech)"]
    }
]

# =========================================================================
# BỘ MÁY TÍNH TOÁN SKILL GAP VÀ ĐỀ XUẤT NGHỀ NGHIỆP THỰC CHIẾN
# =========================================================================
def calculate_rule_based_analysis(profile_data: dict) -> dict:
    """
    Phân tích hồ sơ người dùng 4 bước mới:
    - user_group: Nhóm đối tượng (Sinh viên năm cuối, Thất nghiệp, Career Switcher)
    - current_education_major: Trình độ & Chuyên ngành hiện tại
    - known_skills: Kỹ năng đã có
    - experience_years: Số năm kinh nghiệm
    - target_career: Hướng đi quan tâm
    - expected_salary: Mức lương mong muốn
    - learning_time: Thời gian học (1-3 tháng, 3-6 tháng...)
    - primary_goal: Việc làm ngay vs Lộ trình long-term
    """
    step1 = profile_data.get("step1_target", {})
    step2 = profile_data.get("step2_skillset", {})
    step3 = profile_data.get("step3_expectations", {})
    step4 = profile_data.get("step4_priority", {})

    user_group = step1.get("user_group", "Người muốn chuyển sang ngành mới (Career Switcher)")
    current_major = step1.get("current_education_major", "Ngành hiện tại")
    
    known_skills = step2.get("known_skills", [])
    if isinstance(known_skills, str):
        known_skills = [s.strip() for s in known_skills.split(",") if s.strip()]
    custom_skills = step2.get("custom_skills", "")
    if custom_skills:
        known_skills.append(custom_skills.strip())
        
    exp_years = step2.get("experience_years", "Dưới 1 năm")
    target_career = step3.get("target_career", "Công nghệ thông tin")
    expected_salary = step3.get("expected_salary", "8 - 12 triệu")
    learning_time = step3.get("learning_time", "Học cấp tốc 1-3 tháng")
    primary_goal = step4.get("primary_goal", "Cần việc làm có thu nhập ngay lập tức")

    # Tính toán điểm số tương thích cho từng công việc
    scored_roles = []
    user_skills_text = " ".join(known_skills).lower() + " " + current_major.lower() + " " + target_career.lower()

    for role in MOCK_JOB_ROLES_DATABASE:
        score = role["base_fit"]
        
        # Nếu trùng đúng hướng đi quan tâm -> cộng điểm mạnh
        if any(w in role["target_field"].lower() for w in target_career.lower().split()):
            score += 5
        elif target_career.lower() in role["job_title"].lower():
            score += 4

        # Đối chiếu kỹ năng đã có với từ khóa của vị trí
        matched_kw_count = 0
        for kw in role["keywords"]:
            if kw in user_skills_text:
                matched_kw_count += 1
        score += min(matched_kw_count * 2, 6)

        # Điều chỉnh theo thời gian học & mục tiêu
        if "cấp tốc" in learning_time.lower() and "tester" in role["job_title"].lower():
            score += 2
        if "thu nhập ngay" in primary_goal.lower() and ("sales" in role["job_title"].lower() or "tester" in role["job_title"].lower()):
            score += 2

        score = min(score, 98)

        # Lọc ra kỹ năng chuyển đổi cụ thể theo hồ sơ người dùng
        user_transferable = []
        for ts in role["transferable_skills"]:
            user_transferable.append(ts)
        
        scored_roles.append({
            "job_title": role["job_title"],
            "match_percentage": score,
            "reason": role["reason"],
            "transferable_skills": user_transferable,
            "missing_skills": role["missing_skills"],
            "roadmap_summary": role["roadmap_summary"],
            "expected_salary": role["expected_salary"],
            "suitable_companies": role["suitable_companies"]
        })

    # Sắp xếp theo độ tương thích giảm dần
    scored_roles.sort(key=lambda x: x["match_percentage"], reverse=True)
    top_roles = scored_roles[:3]

    skills_str = ", ".join(known_skills) if known_skills else "kỹ năng giao tiếp và tin học văn phòng cơ bản"
    overview_text = (
        f"Dựa trên hồ sơ của bạn (**{user_group}**, nền tảng **{current_major}**, kinh nghiệm **{exp_years}**), "
        f"với các kỹ năng sẵn có gồm **{skills_str}** và định hướng chuyển sang **{target_career}** trong thời gian **{learning_time}**, "
        f"hệ thống AI đã phân tích bản đồ khoảng trống kỹ năng (Skill Gap) và đối chiếu với dữ liệu tuyển dụng 2026. "
        f"Dưới đây là **Top 3 Vị trí công việc thực chiến phù hợp nhất** giúp bạn tối ưu hóa thế mạnh sẵn có và rút ngắn thời gian có việc làm:"
    )

    return {
        "overview_text": overview_text,
        "job_roles": top_roles,
        "top_majors": top_roles # tương thích với UI
    }


# =========================================================================
# BỘ MÁY TRI THỨC TRẢ LỜI ĐÚNG TRỌNG TÂM CÁC CÂU HỎI CHUYỂN NGÀNH
# =========================================================================
def generate_smart_fallback_response(query: str, mode: str, profile_data: dict) -> str:
    """
    Xử lý câu trả lời CỰC KỲ ĐÚNG TRỌNG TÂM về Sinh Viên Ra Trường, Chuyển Ngành, Học Cấp Tốc, Sửa CV, Skill Gap, Lương & Phỏng vấn
    khi chưa có Gemini API Key.
    """
    q = query.lower()

    # 0. NẾU NGƯỜI DÙNG NÓI: "TÔI LÀ SINH VIÊN", "KHÔNG PHẢI CHUYỂN NGÀNH", "MỚI RA TRƯỜNG"
    if any(k in q for k in ["sinh viên", "sinh vien", "không phải người chuyển ngành", "khong phai nguoi chuyen nganh", "mới ra trường", "moi ra truong", "năm cuối", "nam cuoi", "chưa ra trường"]):
        return (
            f"🎓 **CHIẾN LƯỢC DÀNH RIÊNG CHO SINH VIÊN NĂM CUỐI / MỚI TỐT NGHIỆP RA TRƯỜNG:**\n\n"
            f"Chào bạn! Rất cảm ơn bạn đã làm rõ. Với tư cách là **sinh viên chuẩn bị ra trường / mới tốt nghiệp**, bạn có lợi thế rất lớn về sức trẻ, thời gian linh hoạt và kiến thức nền tảng mới mẻ. Dưới đây là chiến lược thực chiến giúp bạn có việc làm Fresher/Intern ngay khi nhận bằng:\n\n"
            f"1. **Biến đồ án môn học / Đồ án tốt nghiệp thành dự án thực chiến (Portfolio):**\n"
            f"   - Thay vì chỉ nộp đồ án lấy điểm ở trường, hãy chau chuốt lại mã nguồn, đưa lên **GitHub** và viết file `README.md` mô tả rõ tính năng, công nghệ sử dụng và các màn hình demo.\n"
            f"   - Nếu bạn học ngành khác muốn xin việc IT/Data, hãy đưa link demo thực tế (deploy trên Vercel hoặc link Dashboard Power BI) vào CV.\n\n"
            f"2. **Cách viết CV cho sinh viên chưa có kinh nghiệm thực tế:**\n"
            f"   - **Đưa mục DỰ ÁN & ĐỒ ÁN (Projects) lên trên cùng**, ngay dưới thông tin cá nhân.\n"
            f"   - Nêu rõ các môn chuyên ngành có điểm số cao (GPA), các giải thưởng NCKH, học bổng hoặc hoạt động ngoại khóa có đóng góp kỹ năng làm việc nhóm.\n\n"
            f"3. **Tận dụng các chương trình tuyển dụng Fresher / OJT doanh nghiệp lớn:**\n"
            f"   - Ứng tuyển vào các chương trình đào tạo Fresher có lương (như FPT Software Academy, TMA Solutions, VNG Fresher, Viettel Digital Talent...).\n"
            f"   - Doanh nghiệp không kỳ vọng bạn biết hết mọi thứ, họ tìm kiếm **tư duy nền tảng vững, tính chủ động và thái độ ham học hỏi**!\n\n"
            f"Bạn muốn tôi tư vấn cụ thể về: **cách sửa CV sinh viên**, **câu hỏi phỏng vấn Fresher**, hay **lộ trình chuẩn bị trong 1-3 tháng tới**?"
        )

    # 1. HỎI VỀ HỌC PHÍ / TIỀN HỌC / HỌC TRƯỜNG ĐẠI HỌC (Ví dụ HUTECH, Bách Khoa, FPT...)
    if any(k in q for k in ["hutech", "bách khoa", "fpt", "ueh", "học phí", "hoc phi", "tốn bao nhiêu tiền", "ton bao nhieu tien"]):
        if "hutech" in q:
            return (
                f"🎓 **CHI TIẾT HỌC PHÍ VÀ LỘ TRÌNH ĐÀO TẠO ĐẠI HỌC HUTECH (CẬP NHẬT 2026)**\n\n"
                f"1. **Tổng học phí trọn khóa (đến khi tốt nghiệp):**\n"
                f"   👉 Dao động từ **180.000.000 – 210.000.000 VNĐ** cho toàn khóa học 3.5 – 4 năm (khoảng 140 tín chỉ chương trình chuẩn).\n"
                f"   - Nếu học chương trình Chuẩn Nhật Bản hoặc Chuẩn Quốc tế: Khoảng 240 – 275 triệu VNĐ trọn khóa.\n\n"
                f"2. **Học phí trung bình theo năm học:**\n"
                f"   - Khoảng **48.000.000 – 58.000.000 VNĐ / năm** (HUTECH học 3 học kỳ/năm).\n"
                f"   - Đơn giá: ~1.400.000 – 1.600.000 VNĐ / tín chỉ.\n\n"
                f"3. **Tỷ lệ có việc làm ngành Công nghệ thông tin:** Đạt khoảng **95% – 97%** sau 1 năm tốt nghiệp nhờ trường có mạng lưới liên kết với hơn 1000+ doanh nghiệp (FPT, TMA, VNG, DXC...).\n\n"
                f"💡 *Góc nhìn chuyển ngành:* Nếu bạn đã có bằng đại học khác và muốn học IT, thay vì học lại 4 năm đại học tốn 200 triệu, bạn có thể cân nhắc các khóa **Bootcamp lập trình cấp tốc 3-6 tháng** (học phí khoảng 20-35 triệu) để đi làm sớm hơn rất nhiều!"
            )
        elif "fpt" in q:
            return (
                f"🎓 **HỌC PHÍ ĐẠI HỌC FPT TRỌN KHÓA ĐẾN TỐT NGHIỆP:**\n\n"
                f"- **Học phí chuyên ngành:** Khoảng **31 – 35 triệu VNĐ / học kỳ** (1 năm có 3 học kỳ).\n"
                f"- **Tổng học phí trọn khóa (9 học kỳ chuyên ngành):** Khoảng **280 – 315 triệu VNĐ** (chưa tính giai đoạn tiếng Anh dự bị nếu chưa có IELTS 6.0).\n"
                f"- **Điểm sáng:** 100% sinh viên được thực tập doanh nghiệp (OJT) có lương tại Tập đoàn FPT và cơ hội đi onsite nước ngoài."
            )

    # 2. HỎI VỀ TỶ LỆ CÓ VIỆC LÀM / XÁC SUẤT XIN ĐƯỢC VIỆC KHI ĐỔI NGÀNH
    if any(k in q for k in ["tỷ lệ", "ty le", "việc làm", "viec lam", "có việc", "co viec", "xin việc", "xin viec", "phần trăm", "phan tram", "%", "có dễ xin việc", "co de xin viec", "thất nghiệp", "that nghiep", "ra trường", "ra truong", "cơ hội việc làm"]):
        return (
            f"📊 **THỰC TẾ TỶ LỆ CÓ VIỆC LÀM CỦA NGƯỜI CHUYỂN NGÀNH (CAREER SWITCHER 2026):**\n\n"
            f"1. **Tỷ lệ thành công theo từng ngành nghề chuyển đổi:**\n"
            f"   - **Manual Tester (QA/QC):** Đạt **80% - 85%** có việc làm sau 2-4 tháng học nghiêm túc. Đây là ngành có rào cản kỹ thuật thấp nhất và chào đón người trái ngành nhất.\n"
            f"   - **Data Analyst / BI:** Đạt **70% - 75%** nếu bạn biết kết hợp nghiệp vụ cũ (kế toán, kinh tế, ngân hàng) với kỹ năng SQL và Power BI.\n"
            f"   - **Frontend Developer (ReactJS):** Đạt **65% - 70%**. Cạnh tranh cao hơn, bắt buộc phải có **Portfolio ít nhất 2 dự án thực tế chạy mượt mà trên Vercel/GitHub** thay vì chỉ chứng chỉ lý thuyết.\n"
            f"   - **Digital Marketing / Sales B2B:** Đạt **85% - 90%** vì thị trường luôn có nhu cầu tuyển dụng liên tục.\n\n"
            f"2. **3 Yếu tố giúp bạn lọt vào nhóm 20% ứng viên trái ngành có việc ngay:**\n"
            f"   - **Portfolio thực chiến:** Chứng minh năng lực bằng sản phẩm thật, không nói suông.\n"
            f"   - **Làm nổi bật Transferable Skills:** Ví dụ Kế toán nhấn mạnh tư duy số liệu khi phỏng vấn Data; Ngôn ngữ Anh nhấn mạnh khả năng đọc tài liệu kỹ thuật.\n"
            f"   - **Chấp nhận mức lương xuất phát điểm Fresher** trong 6 tháng đầu để tích lũy kinh nghiệm thực tế."
        )

    # 3. HỎI VỀ MỨC LƯƠNG KHỞI ĐIỂM (FRESHER / CHUYỂN NGÀNH)
    if any(k in q for k in ["mức lương", "muc luong", "lương bao nhiêu", "luong bao nhieu", "lương", "luong", "thu nhập", "thu nhap", "bao nhiêu tiền 1 tháng", "kiem duoc bao nhieu"]):
        return (
            f"💰 **BẢNG MỨC LƯƠNG THỰC TẾ CHO NGƯỜI CHUYỂN NGÀNH TẠI VIỆT NAM (2026):**\n\n"
            f"| Vị trí công việc | Mức lương Fresher / Mới chuyển | Lương sau 1 - 2 năm kinh nghiệm |\n"
            f"| :--- | :--- | :--- |\n"
            f"| **Manual Tester (QA/QC)** | 8.5 – 13 triệu/tháng | 15 – 22 triệu/tháng |\n"
            f"| **Data Analyst (SQL, BI)** | 10 – 15 triệu/tháng | 18 – 28 triệu/tháng |\n"
            f"| **Frontend Developer (Web)** | 9 – 15 triệu/tháng | 18 – 32 triệu/tháng |\n"
            f"| **IT Business Analyst (BA)** | 11 – 17 triệu/tháng | 20 – 30 triệu/tháng |\n"
            f"| **Digital Marketing Specialist** | 8 – 13 triệu + Thưởng KPI | 16 – 25 triệu/tháng |\n"
            f"| **B2B Tech Sales / CSKH** | 8 – 12 triệu cứng + Thưởng DS | 20 – 40+ triệu/tháng |\n\n"
            f"💡 *Lời khuyên chiến lược:* Khi đi phỏng vấn trái ngành, đừng đặt nặng mức lương 6 tháng đầu. Hãy ưu tiên vào công ty có môi trường làm việc tốt và người hướng dẫn (Mentor) giỏi để bứt phá thu nhập sau năm thứ hai!"
        )

    # 4. HỎI VỀ LỘ TRÌNH HỌC CẤP TỐC (1-3 THÁNG HOẶC 3-6 THÁNG)
    if any(k in q for k in ["lộ trình", "lo trinh", "roadmap", "cấp tốc", "cap toc", "1-3 tháng", "3-6 tháng", "học cái gì", "hoc cai gi", "học gì", "hoc gi", "môn gì", "mon gi", "bắt đầu từ đâu", "bat dau tu dau", "học như thế nào", "hoc nhu the nao"]):
        return (
            f"🚀 **LỘ TRÌNH CHUYỂN NGÀNH CẤP TỐC 3 THÁNG (BẢO ĐẢM TÍNH THỰC CHIẾN):**\n\n"
            f"**Tháng 1: Xây nền tảng kỹ năng cốt lõi (Core Hard Skills)**\n"
            f"- Dành 3-4 tiếng/ngày học công cụ trọng tâm nhất (Ví dụ: Chuyển IT Web -> Học chắc HTML/CSS/JavaScript; Chuyển Data -> Học SQL và Excel nâng cao; Chuyển Tester -> Học thiết kế Test Case & Jira).\n"
            f"- Đọc hiểu các thuật ngữ chuyên môn phổ biến trong ngành.\n\n"
            f"**Tháng 2: Làm dự án thực tế mô phỏng doanh nghiệp (Hands-on Project)**\n"
            f"- Không học lý thuyết lan man, bắt tay ngay vào làm 2 đồ án mẫu:\n"
            f"  + Với Data: Phân tích doanh số bán hàng từ dataset Kaggle và dựng Dashboard Power BI.\n"
            f"  + Với Tester: Lập kế hoạch kiểm thử và viết bộ 50+ Test Case cho ứng dụng E-commerce.\n"
            f"  + Với Web: Xây dựng trang Web bán hàng kết nối API, có giỏ hàng và thanh toán.\n\n"
            f"**Tháng 3: Chuẩn hóa Portfolio, Viết lại CV & Rải đơn phỏng vấn**\n"
            f"- Đưa toàn bộ dự án lên GitHub / Notion / Web cá nhân để làm bằng chứng năng lực.\n"
            f"- Sửa CV tập trung vào kỹ năng và sản phẩm đã làm, loại bỏ các chi tiết không liên quan của ngành cũ.\n"
            f"- Luyện trả lời các câu hỏi phỏng vấn hóc búa dành cho ứng viên trái ngành."
        )

    # 5. HỎI VỀ CÁCH SỬA CV / VIẾT CV KHI CHUYỂN NGÀNH
    if any(k in q for k in ["cv", "resume", "portfolio", "hồ sơ", "ho so", "sửa cv", "sua cv", "viết cv", "viet cv", "làm cv", "lam cv"]):
        return (
            f"📄 **BÍ QUYẾT TỐI ƯU CV DÀNH RIÊNG CHO NGƯỜI CHUYỂN NGÀNH (ĐẢM BẢO QUA VÒNG LỌC HR):**\n\n"
            f"1. **Thay đổi cấu trúc CV sang dạng Functional Resume (Tập trung vào Kỹ năng):**\n"
            f"   - Đừng liệt kê theo dòng thời gian ngành cũ lên đầu. Hãy đưa mục **KỸ NĂNG CHUYÊN MÔN (TECHNICAL SKILLS)** và **DỰ ÁN ĐÃ LÀM (PROJECTS)** lên ngay dưới thông tin cá nhân.\n\n"
            f"2. **Viết phần Tóm tắt bản thân (Career Summary) thật ấn tượng:**\n"
            f"   - *Ví dụ mẫu:* 'Cử nhân Kế toán với 2 năm kinh nghiệm phân tích số liệu tài chính, đã hoàn thành đào tạo chuyên sâu về SQL & Power BI với 2 dự án phân tích dữ liệu kinh doanh. Mong muốn ứng tuyển vị trí Junior Data Analyst để vận dụng tư duy logic số liệu giải quyết bài toán tăng trưởng của doanh nghiệp.'\n\n"
            f"3. **Luôn đính kèm đường link Portfolio trực tuyến:**\n"
            f"   - Đặt link GitHub, Notion Portfolio hoặc link Dashboard công khai ngay đầu CV. HR sẽ tin tưởng gấp 5 lần khi thấy sản phẩm thực tế bạn tự tay làm ra!"
        )

    # 6. HỎI VỀ MÔ PHỎNG PHỎNG VẤN HOẶC TÌNH HUỐNG (ROLEPLAY)
    if any(k in q for k in ["phỏng vấn", "phong van", "tại sao chuyển ngành", "tai sao chuyen nganh", "hỏi thử", "hoi thu", "roleplay", "tình huống", "tinh huong", "câu hỏi", "cau hoi"]):
        return (
            f"🎭 **CÂU HỎI PHỎNG VẤN KINH ĐIỂN: 'TẠI SAO BẠN LẠI BỎ NGÀNH CŨ ĐỂ CHUYỂN SANG ĐÂY?'**\n\n"
            f"Đây là câu hỏi 100% nhà tuyển dụng sẽ hỏi bạn. Dưới đây là công thức trả lời điểm 10:\n\n"
            f"❌ **Cách trả lời sai (Nên tránh):** 'Dạ do ngành cũ lương thấp / chán quá / không tìm được việc nên em chuyển sang IT/Marketing kiếm nhiều tiền hơn.' (HR đánh giá bạn thiếu kiên định và dễ từ bỏ).\n\n"
            f"✅ **Công thức chuẩn 3 bước:**\n"
            f"1. **Ghi nhận giá trị ngành cũ:** 'Trong thời gian học và làm ngành cũ, em đã tích lũy được tư duy số liệu / tính tỉ mỉ / kỹ năng giao tiếp rất tốt.'\n"
            f"2. **Điểm chạm chuyển đổi (Trigger):** 'Tuy nhiên, khi có cơ hội tiếp xúc với việc phân tích dữ liệu / công nghệ, em nhận thấy đây mới thực sự là đam mê và thế mạnh dài hạn của mình.'\n"
            f"3. **Hành động chứng minh nghiêm túc:** 'Em không chuyển ngành theo phong trào mà đã dành 4 tháng nghiêm túc học tập, hoàn thành 2 dự án thực tế (em có đính kèm trong CV) và sẵn sàng cống hiến từ vị trí Fresher.'\n\n"
            f"👉 Bạn muốn tôi phỏng vấn thử câu nào tiếp theo không? (Ví dụ: Hỏi về điểm yếu của bạn, hoặc câu hỏi tình huống chuyên môn?)"
        )

    # 7. MẶC ĐỊNH CHO CÁC CÂU HỎI TƯ VẤN KHÁC
    return (
        f"Chào bạn! Về câu hỏi của bạn: *'{query}'*:\n\n"
        f"Đối với lộ trình chuyển ngành và tìm kiếm việc làm thực chiến 2026, chiến lược tối ưu nhất là:\n"
        f"1. **Tập trung vào kỹ năng cốt lõi (Skill Gap):** Học đúng những công cụ thị trường đang tuyển dụng nhiều nhất (SQL, Power BI, Test Case, ReactJS, Ads...).\n"
        f"2. **Chứng minh bằng Portfolio:** Làm ra ít nhất 1-2 sản phẩm thực tế để bù đắp điểm yếu trái ngành khi nộp CV.\n"
        f"3. **Tận dụng kỹ năng cũ:** Liên kết kinh nghiệm hoặc ngành học trước đây thành lợi thế cạnh tranh riêng biệt.\n\n"
        f"Bạn có thể bấm vào các gợi ý bên dưới hoặc hỏi cụ thể về lộ trình học cấp tốc, mức lương từng vị trí, hay cách viết CV nhé!"
    )


async def generate_initial_analysis(profile_data: dict) -> dict:
    """Sinh kết quả phân tích ban đầu (hỗ trợ gọi Gemini hoặc fallback thông minh)"""
    return calculate_rule_based_analysis(profile_data)


def call_gemini_via_rest(api_key: str, model_name: str, system_instruction: str, formatted_contents: list) -> str:
    """Gọi trực tiếp Google Gemini REST API bảo đảm 100% không phụ thuộc SDK"""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_instruction}]
        },
        "contents": formatted_contents,
        # Grounding Google Search: dữ liệu học phí/tỷ lệ việc làm lấy theo thời điểm thực
        **GROUNDING_TOOL,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=25)
    if resp.status_code != 200:
        raise Exception(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


# Grounding Google Search: dữ liệu học phí/tỷ lệ việc làm lấy theo thời điểm thực
GROUNDING_TOOL = {"tools": [{"google_search": {}}]}


async def _ollama_stream(targeted_instruction: str, formatted_contents: list):
    """Stream phản hồi từ Ollama local (/api/chat, NDJSON). Yield từng đoạn text."""
    payload = {
        "model": settings.OLLAMA_MODEL,
        "messages": [{"role": "system", "content": targeted_instruction}] + formatted_contents,
        "stream": True,
        "options": {"num_ctx": 8192},
    }
    async with httpx.AsyncClient(timeout=300) as client:
        async with client.stream("POST", f"{settings.OLLAMA_BASE_URL}/api/chat", json=payload) as resp:
            if resp.status_code != 200:
                raise Exception(f"HTTP {resp.status_code}: {await resp.aread()}")
            async for line in resp.aiter_lines():
                if not line.strip():
                    continue
                chunk = json.loads(line)
                text = chunk.get("message", {}).get("content", "")
                if text:
                    yield text


def _build_chat_instruction(messages: List[Dict[str, str]], profile_data: dict, mode: str):
    """System prompt + contents chung cho cả bản đầy đủ và bản stream."""
    system_instruction = build_system_prompt(profile_data, current_mode=mode)
    targeted_instruction = (
        f"{system_instruction}\n\n"
        f"QUY TẮC BẮT BUỘC KHI TRẢ LỜI:\n"
        f"- Phải trả lời TRỰC DIỆN VÀO TRỌNG TÂM câu hỏi của người dùng (Ví dụ: Hỏi học phí -> trả lời số tiền; "
        f"Hỏi tỷ lệ việc làm -> trả lời số % và phân tích; Hỏi cách đổi ngành -> chỉ rõ kỹ năng và lộ trình; Hỏi câu phỏng vấn -> đưa ra câu trả lời chuẩn).\n"
        f"- TUYỆT ĐỐI KHÔNG dùng câu trả lời chung chung né tránh."
    )
    formatted_contents = []
    for msg in messages:
        role = "user" if msg["role"] == "user" else "model"
        formatted_contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    return targeted_instruction, formatted_contents


async def stream_chat_response(messages: List[Dict[str, str]], profile_data: dict, mode: str, custom_api_key: str = None):
    """Stream phản hồi Gemini qua REST SSE (streamGenerateContent?alt=sse), yield từng đoạn text.

    Không có API key hoặc mọi model lỗi -> yield nguyên 1 đoạn từ Bộ máy Tri thức.
    Nếu stream đứt giữa chừng sau khi đã yield text, dừng mà không nhét thêm fallback
    (tránh nhân đôi nội dung người dùng đã đọc)."""
    last_user_msg = messages[-1]["content"] if messages else ""

    # Ưu tiên AI local (Ollama) khi bật — không tốn chi phí, chạy offline
    if settings.OLLAMA_ENABLED:
        try:
            instruction, contents = _build_chat_instruction(messages, profile_data, mode)
            print(f"🦙 [Ollama]: Đang stream bằng {settings.OLLAMA_MODEL}...")
            async for text in _ollama_stream(instruction, contents):
                yield text
            print(f"✅ [Ollama]: Stream thành công từ {settings.OLLAMA_MODEL}!")
            return
        except Exception as e:
            print(f"⚠️ [Lỗi Ollama {settings.OLLAMA_MODEL}]: {e}")

    api_key = custom_api_key or settings.GEMINI_API_KEY

    if not api_key or api_key == "your_gemini_api_key_here":
        print(f"💡 [Tri Thức Chuyển Ngành]: Trả lời câu hỏi '{last_user_msg}'")
        yield generate_smart_fallback_response(last_user_msg, mode, profile_data)
        return

    targeted_instruction, formatted_contents = _build_chat_instruction(messages, profile_data, mode)

    # Thử gọi Gemini REST API. Danh sách cập nhật 11/2026: gemini-1.5-* đã shut down
    # 5/2025, gemini-2.0-* shut down 6/2026, gemini-2.5-flash auto-route từ 12/2026.
    async with httpx.AsyncClient(timeout=60) as client:
        for model_candidate in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash-lite"]:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_candidate}:streamGenerateContent?alt=sse&key={api_key}"
            payload = {
                "systemInstruction": {"parts": [{"text": targeted_instruction}]},
                "contents": formatted_contents,
                **GROUNDING_TOOL,
            }
            try:
                print(f"🤖 [Gemini AI]: Đang stream câu hỏi bằng {model_candidate}...")
                yielded = False
                async with client.stream("POST", url, headers={"Content-Type": "application/json"}, json=payload) as resp:
                    if resp.status_code != 200:
                        raise Exception(f"HTTP {resp.status_code}: {await resp.aread()}")
                    async for line in resp.aiter_lines():
                        if not line.startswith("data: "):
                            continue
                        chunk = json.loads(line[len("data: "):])
                        for part in chunk.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                            text = part.get("text")
                            if text:
                                yielded = True
                                yield text
                if yielded:
                    print(f"✅ [Gemini AI]: Stream thành công từ {model_candidate}!")
                    return
            except Exception as e:
                print(f"⚠️ [Lỗi {model_candidate}]: {e}")
                if yielded:
                    return

    print("⚠️ Tất cả model Gemini gặp sự cố, chuyển sang Bộ máy Tri thức Chuyên sâu.")
    yield generate_smart_fallback_response(last_user_msg, mode, profile_data)


async def generate_chat_response(messages: List[Dict[str, str]], profile_data: dict, mode: str, custom_api_key: str = None) -> str:
    """
    Tạo phản hồi hội thoại:
    - Nếu bật Ollama local -> gọi model local trước (mặc định gemma3:4b cho GPU 4GB)
    - Nếu có API key (từ config hoặc do người dùng nhập trên web) -> Gọi Gemini
    - Nếu chưa có API key hoặc lỗi -> Gọi Bộ máy Tri thức Chuyển Ngành Trực Tiếp cực kỳ đúng trọng tâm
    """
    last_user_msg = messages[-1]["content"] if messages else ""

    # Ưu tiên AI local (Ollama) khi bật
    if settings.OLLAMA_ENABLED:
        try:
            instruction, contents = _build_chat_instruction(messages, profile_data, mode)
            print(f"🦙 [Ollama]: Đang xử lý bằng {settings.OLLAMA_MODEL}...")
            parts = [text async for text in _ollama_stream(instruction, contents)]
            if parts:
                print(f"✅ [Ollama]: Phản hồi thành công từ {settings.OLLAMA_MODEL}!")
                return "".join(parts)
        except Exception as e:
            print(f"⚠️ [Lỗi Ollama {settings.OLLAMA_MODEL}]: {e}")

    api_key = custom_api_key or settings.GEMINI_API_KEY

    if not api_key or api_key == "your_gemini_api_key_here":
        print(f"💡 [Tri Thức Chuyển Ngành]: Trả lời câu hỏi '{last_user_msg}'")
        return generate_smart_fallback_response(last_user_msg, mode, profile_data)

    targeted_instruction, formatted_contents = _build_chat_instruction(messages, profile_data, mode)

    # Thử gọi Gemini REST API. Danh sách cập nhật 11/2026: gemini-1.5-* đã shut down
    # 5/2025, gemini-2.0-* shut down 6/2026, gemini-2.5-flash auto-route từ 12/2026.
    for model_candidate in ["gemini-2.5-flash-lite", "gemini-2.5-flash", "gemini-3.5-flash-lite"]:
        try:
            print(f"🤖 [Gemini AI]: Đang xử lý câu hỏi bằng {model_candidate}...")
            ai_text = call_gemini_via_rest(api_key, model_candidate, targeted_instruction, formatted_contents)
            print(f"✅ [Gemini AI]: Phản hồi thành công từ {model_candidate}!")
            return ai_text
        except Exception as e:
            print(f"⚠️ [Lỗi {model_candidate}]: {e}")

    print("⚠️ Tất cả model Gemini gặp sự cố, chuyển sang Bộ máy Tri thức Chuyên sâu.")
    return generate_smart_fallback_response(last_user_msg, mode, profile_data)
