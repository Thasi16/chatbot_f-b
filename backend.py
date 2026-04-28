import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# Khai báo đường dẫn để đảm bảo load đúng module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from agent.workflow import app as langgraph_app

# Khởi tạo FastAPI
app = FastAPI(title="F&B AI Advisor API")

# Ensure the frontend directory exists relative to this file
frontend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frontend")
if not os.path.exists(frontend_dir):
    os.makedirs(frontend_dir)

app.mount("/frontend", StaticFiles(directory=frontend_dir), name="frontend")

# Lớp định nghĩa Body Request
class ChatRequest(BaseModel):
    message: str
    thread_id: str = "web_session_darkmode_1"

@app.get("/", response_class=HTMLResponse)
async def read_index():
    index_path = os.path.join(frontend_dir, "index.html")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/images/{img_id}")
async def get_image(img_id: str):
    image_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "image")
    for ext in [".jpg", ".png", ".webp", ".jpeg"]:
        img_path = os.path.join(image_dir, f"{img_id}{ext}")
        if os.path.exists(img_path):
            from fastapi.responses import FileResponse
            return FileResponse(img_path)
    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Image not found")


@app.post("/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        # Bộ lọc từ ngữ thô tục (Profanity Filter) cơ bản
        bad_words = ["địt", "lồn", "cặc", "chó đẻ", "đụ", "ngu", "điếm", "đĩ", "mẹ mày", "cứt"]
        user_msg_lower = req.message.lower()
        if any(bad_word in user_msg_lower for bad_word in bad_words):
            return {
                "status": "success", 
                "reply": "Xin lỗi, ngôn từ của bạn chứa từ khóa không phù hợp. Vui lòng giữ lịch sự khi trò chuyện cùng tôi nhé!"
            }

        # Fast path cho câu hỏi gợi ý (không gọi mô hình)
        if user_msg_lower.strip() in [
            "nhà hàng có bao nhiêu chi nhánh?", "nhà hàng có bao nhiêu chi nhánh", 
            "chi nhánh", "các chi nhánh", "danh sách chi nhánh", "địa chỉ", 
            "địa chỉ nhà hàng", "nhà hàng ở đâu", "địa chỉ quán", "chi nhánh nhà hàng", 
            "hệ thống chi nhánh", "nhà hàng có mấy chi nhánh", "có bao nhiêu chi nhánh"
        ]:
            try:
                db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "mock_db.json")
                import json
                with open(db_path, "r", encoding="utf-8") as f:
                    db_data = json.load(f)
                    branches = db_data.get("branches", [])
                    reply_text = f"Hiện tại, chuỗi nhà hàng của chúng tôi có **{len(branches)} chi nhánh**:\n\n"
                    for b in branches:
                        addr = b.get('address', 'Chưa cập nhật địa chỉ')
                        reply_text += f"- **{b['name']}**\n  📍 Địa chỉ: {addr}\n  ⏰ Giờ hoạt động: {b.get('operating_hours', '')}\n\n"
                    reply_text += "Quý khách muốn đặt bàn ở chi nhánh nào ạ?"
                return {"status": "success", "reply": reply_text}
            except Exception as e:
                pass # Fallback to LLM if error

        if user_msg_lower.strip() in [
            "menu của nhà hàng", "menu của nhà hàng?", "thực đơn của nhà hàng",
            "menu", "thực đơn", "xem menu", "cho xin cái menu", "nhà hàng có món gì",
            "cho xem menu", "danh sách món", "menu quán", "thực đơn quán", 
            "có món gì ngon", "xin menu", "cho mình xem menu"
        ]:
            try:
                menu_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "menu_nhahang.md")
                with open(menu_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                
                reply_text = "Dưới đây là chi tiết toàn bộ Menu của nhà hàng:\n"
                reply_text += "![Menu](/images/D00)\n"
                current_item_name = ""
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if line.startswith("## 8.") or line.startswith("## 9."):
                        break # Skip rules and policies
                    if line.startswith("## "):
                        # Header
                        reply_text += f"\n**{line.replace('## ', '')}**\n"
                    elif line.startswith("**Món") or line.startswith("**Thức uống") or line.startswith("**Combo"):
                        # Extract name and strip asterisks
                        name = line.split(":", 1)[-1].replace("**", "").strip()
                        current_item_name = name
                    elif line.startswith("* **ID:**") or line.startswith("* **Giá:**"):
                        import re
                        id_match = re.search(r'\*\*ID:\*\*\s*(.*?)\s*(?:\||$)', line)
                        item_id = id_match.group(1).strip() if id_match else ""
                        
                        price_match = re.search(r'\*\*Giá:\*\*\s*(.*?)\s*(?:\||$)', line)
                        price = price_match.group(1).strip() if price_match else ""
                        
                        if current_item_name:
                            if item_id:
                                reply_text += f"\n**({item_id}) {current_item_name}**\n"
                            else:
                                reply_text += f"\n**{current_item_name}**\n"
                            current_item_name = ""
                            
                        if price:
                            reply_text += f"• **Giá:** {price}\n"
                    elif line.startswith("* **Thành phần:**"):
                        val = line.split("**", 2)[-1].lstrip(":").strip()
                        reply_text += f"• **Thành phần:** {val}\n"
                    elif line.startswith("* **Hương vị") or line.startswith("* **Đặc điểm"):
                        val = line.split("**", 2)[-1].lstrip(":").strip()
                        reply_text += f"• **Đặc điểm:** {val}\n"
                    elif line.startswith("* **Lưu ý"):
                        val = line.split("**", 2)[-1].lstrip(":").strip()
                        reply_text += f"• **Lưu ý:** {val}\n"
                    elif line.startswith("* **Gợi ý"):
                        val = line.split("**", 2)[-1].lstrip(":").strip()
                        reply_text += f"• **Gợi ý:** {val}\n"
                
                reply_text += "\nBạn có muốn tôi tư vấn thêm về món nào không?"
                return {"status": "success", "reply": reply_text}
            except Exception as e:
                pass # Fallback to LLM if error

        inputs = {"messages": [HumanMessage(content=req.message)]}
        config = {"configurable": {"thread_id": req.thread_id}}
        
        # Invoke "Não bộ" LangGraph
        result = langgraph_app.invoke(inputs, config=config)
        bot_reply = result["messages"][-1].content
        
        # Xử lý trường hợp mô hình Gemini trả về blocks/array thay vì chuỗi thuần túy
        if isinstance(bot_reply, list):
            texts = []
            for block in bot_reply:
                if isinstance(block, dict) and "text" in block:
                    texts.append(block["text"])
                elif isinstance(block, str):
                    texts.append(block)
            bot_reply = "\n".join(texts) if texts else str(bot_reply)
        elif not isinstance(bot_reply, str):
            bot_reply = str(bot_reply)
        
        return {"status": "success", "reply": bot_reply}
    except Exception as e:
        return {"status": "error", "reply": f"Lỗi hệ thống: {str(e)}"}

if __name__ == "__main__":
    print("Khởi chạy Giao diện Web: http://localhost:8000")
    uvicorn.run("backend:app", host="127.0.0.1", port=8000, reload=True)
