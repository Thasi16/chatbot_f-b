# 🤖 AI F&B Advisor - Trợ lý Ẩm thực Thông minh

Dự án này là một hệ thống Chatbot Trợ lý Ảo chuyên nghiệp dành cho lĩnh vực F&B (Nhà hàng, Quán ăn), được xây dựng trên nền tảng **LangGraph**, **Gemini API** và **FastAPI**. 

Chatbot không chỉ trả lời theo kịch bản tĩnh mà còn có "não bộ" có khả năng suy luận, gọi các công cụ (Tool Calling) để thao tác với cơ sở dữ liệu thực tế: Kiểm tra bàn trống, Xác nhận đặt bàn, Đo khoảng cách giao hàng thực tế và Tự động tư vấn Cross-sell thông minh.

## ✨ Các Tính Năng Nổi Bật

* **🧠 Kiến trúc Agentic với LangGraph**: Quản lý luồng hội thoại trạng thái (Stateful) tự nhiên, tự động nội suy khi nào cần gọi Tool.
* **🍽️ Quản lý Menu (RAG-like)**: Đọc hiểu toàn bộ Menu, hương vị, thành phần, cảnh báo y tế (dị ứng) từ tệp `menu_nhahang.md`.
* **📅 Hệ thống Đặt bàn Tự động (Booking System)**: 
  * Kiểm tra tính khả dụng của bàn (Availability Check) tại các chi nhánh theo thời gian thực.
  * Tương tác thu thập Tên, Số điện thoại và tự động **Lưu đơn đặt bàn** vào cơ sở dữ liệu `mock_db.json`.
* **🛵 Tính phí Giao hàng & Đo khoảng cách**: Tích hợp OpenStreetMap (OSRM) để đo khoảng cách thực tế từ nhà khách đến chi nhánh gần nhất và quyết định có giao hàng hay không.
* **💡 Tự động Cross-sell**: AI tự động theo dõi món khách vừa gọi và chủ động mời thêm đồ uống/đồ ăn kèm phù hợp (Ví dụ: Ăn lẩu -> mời uống trà tắc giải ngấy).
* **🖼️ Trích xuất Hình ảnh Tự động**: Tự động chèn hình ảnh minh họa chân thực cho từng món ăn, thức uống hoặc combo trực tiếp vào khung chat.
* **🌐 Giao diện Web Trực quan (Web UI)**: Cung cấp giao diện Chat hiện đại, hỗ trợ Dark/Light mode, Markdown Parsing.

---

## 🛠️ Công Nghệ Sử Dụng

* **Core AI**: Google Gemini API, LangChain, LangGraph.
* **Backend**: FastAPI, Uvicorn, Python 3.10+
* **Frontend**: Vanilla JavaScript, HTML5, CSS3.
* **Database**: JSON (`mock_db.json`), Markdown (`menu_nhahang.md`).

---

## 🚀 Hướng Dẫn Cài Đặt (Installation)

### Bước 1: Clone Repository
```bash
git clone https://github.com/your-username/chatbot-fb-advisor.git
cd chatbot-fb-advisor
```

### Bước 2: Thiết lập Môi trường Ảo (Virtual Environment)
Khuyến nghị sử dụng môi trường ảo để tránh xung đột thư viện:
```bash
# Tạo môi trường ảo
python -m venv venv

# Kích hoạt môi trường ảo
# Trên Windows:
venv\Scripts\activate
# Trên macOS/Linux:
source venv/bin/activate
```

### Bước 3: Cài đặt Thư viện
```bash
pip install -r requirements.txt
```

### Bước 4: Thiết lập API Key
Tạo một file `.env` ở thư mục gốc của dự án (`fb_advisor_agent/`) và điền API Key của Google Gemini vào:
```env
GOOGLE_API_KEY=your_gemini_api_key_here
```
---

## 💻 Hướng Dẫn Sử Dụng (Usage)

Dự án cung cấp 2 phương thức giao tiếp: Giao diện Web (khuyên dùng) và Giao diện Console CLI.

### 1. Khởi chạy Giao diện Web (FastAPI)
Chạy lệnh sau tại thư mục gốc:
```bash
python backend.py
```
* Hệ thống sẽ khởi động máy chủ tại địa chỉ: `http://localhost:8000`
* Mở trình duyệt và truy cập vào link trên để bắt đầu trò chuyện với Chatbot.

### 2. Khởi chạy Giao diện Console (CLI)
Nếu bạn chỉ muốn test nhanh logic nội bộ trên Terminal:
```bash
python main.py
```
Gõ `q` hoặc `quit` để thoát khỏi phiên chat.

---

## 📂 Cấu Trúc Thư Mục (Project Structure)

```text
fb_advisor_agent/
│
├── agent/                   # Xử lý Logic của LangGraph AI
│   ├── nodes.py             # System Prompt và khai báo các node
│   ├── tools.py             # Các Tools (Booking, Map, Menu)
│   ├── state.py             # Cấu trúc GraphState
│   └── workflow.py          # Khởi tạo sơ đồ LangGraph
│
├── core/                    # Khởi tạo mô hình ngôn ngữ (LLM Engine)
│
├── data/                    # Nơi lưu trữ Cơ sở dữ liệu
│   ├── image/               # Thư mục chứa ảnh món ăn (F01, D01...)
│   ├── menu_nhahang.md      # Data Menu và quy tắc phục vụ
│   └── mock_db.json         # Data chi nhánh và lịch sử Đặt bàn
│
├── frontend/                # Giao diện Web
│   ├── app.js               # Xử lý Fetch API & Markdown UI
│   ├── index.html           # Khung giao diện
│   └── style.css            # Trình bày giao diện (Dark/Light Mode)
│
├── backend.py               # Chạy Server FastAPI (Cổng giao tiếp chính)
├── main.py                  # Chạy giao tiếp CLI
├── requirements.txt         # Danh sách thư viện
└── .env                     # Chứa các API Keys (Ignored by Git)
```

---

## 📝 Một số Kịch bản Test Tiêu biểu

Để thấy được sức mạnh của hệ thống, bạn có thể thử copy/paste các câu hỏi sau vào Web UI:

1. **Hiển thị Menu & Ảnh:** *"Cho mình xem menu của nhà hàng"*
2. **Gợi ý Cross-sell:** *"Tư vấn cho mình một món chính ngon nhé, ví dụ món Lẩu"* (Chatbot sẽ tư vấn Lẩu, hiện ảnh lẩu và tự động mời bạn mua thêm Trà tắc hoặc đồ ăn kèm).
3. **Đo khoảng cách Giao hàng:** *"Mình ở Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội. Nhà hàng giao cho mình 1 suất Phở bò nhé"*
4. **Luồng Đặt bàn (Booking Flow):** *"Mình muốn đặt bàn cho 4 người vào lúc 19:00 ngày mai ở cơ sở Hoàn Kiếm"* -> Sau đó Chatbot sẽ xin Tên và SĐT -> Cấp mã `#RES-1025` và lưu thẳng vào file DB.

---


