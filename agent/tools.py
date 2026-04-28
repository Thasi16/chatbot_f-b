from langchain_core.tools import tool
import json
import os

# Đường dẫn tới Mock DB
MOCK_DB_PATH = os.path.join(os.path.dirname(__file__), "../data/mock_db.json")

# Đường dẫn DB Menu
MENU_PATH = os.path.join(os.path.dirname(__file__), "../data/menu_nhahang.md")

def load_mock_db():
    if not os.path.exists(MOCK_DB_PATH):
        return {"branches": []}
    with open(MOCK_DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def save_mock_db(db):
    with open(MOCK_DB_PATH, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

@tool
def check_branch_availability(branch_id: str, date: str, time: str, guests: int) -> str:
    """Hàm này CỰC KỲ QUAN TRỌNG. Bạn CHỈ gọi hàm này khi khách hàng cung cấp đủ 4 thông tin: ID Chi Nhánh, Ngày (YYYY-MM-DD), Khung giờ đón, và Số lượng người. Nó sẽ trả về trạng thái còn bàn hay hết bàn từ hệ thống."""
    db = load_mock_db()
    for branch in db["branches"]:
        if str(branch["id"]) == str(branch_id):
            avail_by_date = branch.get("availability", {})
            avail_by_time = avail_by_date.get(date, {})
            
            if time in avail_by_time:
                slot_info = avail_by_time[time]
                tables_left = slot_info["total_tables"] - slot_info["booked"]
                # Cứ 4 khách = 1 bàn (giả lập)
                tables_needed = (int(guests) + 3) // 4
                
                if tables_left >= tables_needed:
                    return f"Trạng thái: CÒN BÀN. Chi nhánh '{branch['name']}' còn chỗ lúc {time} ngày {date} cho {guests} người."
                else:
                    return f"Trạng thái: HẾT BÀN. Chi nhánh '{branch['name']}' đã đầy chỗ lúc {time} ngày {date}."
            else:
                return f"Chi nhánh '{branch['name']}' không có thông tin giờ {time} ngày {date}."
                
    return "Không tìm thấy chi nhánh với ID được cung cấp."

import random

@tool
def book_table(branch_id: str, name: str, phone: str, date: str, time: str, guests: int) -> str:
    """Gọi hàm này ĐỂ CHỐT ĐẶT BÀN LƯU VÀO CƠ SỞ DỮ LIỆU sau khi khách đã đồng ý chốt đơn với đủ các thông tin Tên, Số điện thoại, branch_id, Ngày, Giờ, Số người."""
    db = load_mock_db()
    for branch in db["branches"]:
        if str(branch["id"]) == str(branch_id):
            avail_by_date = branch.get("availability", {})
            avail_by_time = avail_by_date.get(date, {})
            
            if time in avail_by_time:
                slot_info = avail_by_time[time]
                tables_left = slot_info["total_tables"] - slot_info["booked"]
                tables_needed = (int(guests) + 3) // 4
                
                if tables_left >= tables_needed:
                    slot_info["booked"] += tables_needed
                    
                    if "reservations" not in db:
                        db["reservations"] = []
                        
                    booking_id = f"RES-{random.randint(1000, 9999)}"
                    db["reservations"].append({
                        "booking_id": booking_id,
                        "branch_id": branch_id,
                        "branch_name": branch["name"],
                        "name": name,
                        "phone": phone,
                        "date": date,
                        "time": time,
                        "guests": guests,
                        "tables_booked": tables_needed
                    })
                    
                    save_mock_db(db)
                    return f"Đặt bàn THÀNH CÔNG! Mã xác nhận của khách là #{booking_id}. Thông tin đã được lưu."
                else:
                    return f"Đặt bàn thất bại: Chi nhánh '{branch['name']}' không còn đủ bàn lúc {time} ngày {date}."
            else:
                return f"Đặt bàn thất bại: Không có ca phục vụ nào vào lúc {time} ngày {date}."
                
    return "Đặt bàn thất bại: Không tìm thấy chi nhánh với ID được cung cấp."


def get_menu_context() -> str:
    """Đọc file markdown thay thế cho RAG truy vấn vector database"""
    if not os.path.exists(MENU_PATH):
        return "Không có thông tin menu hiện tại."
    with open(MENU_PATH, "r", encoding="utf-8") as f:
        return f.read()

@tool
def get_branches_info() -> str:
    """Gọi hàm này khi bạn cần lấy danh sách các chi nhánh gồm Tên, ID, Đặc điểm nổi bật, Bãi đỗ xe và Dịch vụ Giao hàng để tư vấn cho khách."""
    db = load_mock_db()
    info = "Danh sách chi nhánh:\n"
    for branch in db["branches"]:
        features = ", ".join(branch.get("features", []))
        parking = branch.get("parking", "Không có thông tin đỗ xe")
        
        delivery = branch.get("delivery_service", {})
        deliv_status = delivery.get("current_status", "Không rõ") if delivery.get("is_active") else "Không giao hàng"
        
        info += f"- Tên: {branch['name']} (ID: {branch['id']}), Giờ mở cửa: {branch['operating_hours']}, Đặc điểm: {features}\n"
        info += f"  + Bãi đỗ xe: {parking}\n"
        info += f"  + Giao hàng: {deliv_status}\n"
    return info

import requests
import urllib.parse

@tool
def calculate_delivery_distance(user_address: str, branch_name: str) -> str:
    """Gọi hàm này khi bạn cần đo khoảng cách (km) thực tế từ địa chỉ khách hàng đến Chi nhánh để kiểm tra khả năng giao hàng và phí ship."""
    try:
        headers = {'User-Agent': 'FB_Chatbot_Agent_1.0'}
        # 1. Geocode user address
        user_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(user_address)}&format=json&limit=1"
        user_resp = requests.get(user_url, headers=headers, timeout=5)
        user_data = user_resp.json()
        if not user_data:
            return f"Không thể định vị được địa chỉ khách hàng: '{user_address}'. Vui lòng xin khách địa chỉ chi tiết hơn (Ví dụ thêm Quận, Thành phố)."
        user_lat, user_lon = float(user_data[0]['lat']), float(user_data[0]['lon'])

        # 2. Geocode branch
        branch_address = f"{branch_name}, Hà Nội"
        branch_url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(branch_address)}&format=json&limit=1"
        branch_resp = requests.get(branch_url, headers=headers, timeout=5)
        branch_data = branch_resp.json()
        if not branch_data:
            return f"Lỗi hệ thống: Không thể định vị được địa chỉ chi nhánh '{branch_name}'."
        branch_lat, branch_lon = float(branch_data[0]['lat']), float(branch_data[0]['lon'])

        # 3. OSRM Routing for driving distance
        osrm_url = f"http://router.project-osrm.org/route/v1/driving/{user_lon},{user_lat};{branch_lon},{branch_lat}?overview=false"
        osrm_resp = requests.get(osrm_url, timeout=5)
        osrm_data = osrm_resp.json()
        
        if osrm_data.get("code") == "Ok" and osrm_data.get("routes"):
            distance_meters = osrm_data["routes"][0]["distance"]
            distance_km = round(distance_meters / 1000, 1)
            return f"Khoảng cách lái xe thực tế từ '{user_address}' đến '{branch_name}' là: {distance_km} km. Hãy dùng số km này đối chiếu với luật Giao hàng để tính phí ship hoặc từ chối giao."
        else:
            return "Lỗi: Không thể tìm thấy tuyến đường giao thông giữa 2 địa điểm."
            
    except Exception as e:
        return f"Lỗi kết nối đến máy chủ Bản đồ: {str(e)}"
