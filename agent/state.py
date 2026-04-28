from typing import TypedDict, Annotated, List, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class GraphState(TypedDict):
    # Sử dụng add_messages để LangGraph tự động append thay vì override mảng
    messages: Annotated[List[BaseMessage], add_messages]
    
    # Intend/Phân loại luồng ("menu_lookup", "reservation", "clarification")
    intent: Optional[str]
    
    # --- Slot Filling cho Book bàn ---
    branch_id: Optional[str]    # ID chi nhánh
    time: Optional[str]         # Khung giờ (VD: 19:00)
    guests: Optional[int]       # Số lượng người
    
    # Kết quả RAG hoặc query từ DB
    context: Optional[str]
