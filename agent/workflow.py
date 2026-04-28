from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from agent.state import GraphState
from agent.nodes import assistant_node, tools_list
from langgraph.checkpoint.memory import MemorySaver

def build_workflow() -> StateGraph:
    workflow = StateGraph(GraphState)
    
    # Tool Node tích hợp sẵn từ langgraph sẽ thực thi hàm Python
    tool_node = ToolNode(tools_list)
    
    # Khai báo các Node
    workflow.add_node("assistant", assistant_node)
    workflow.add_node("tools", tool_node)
            
    # Bắt đầu tại Assistant
    workflow.add_edge(START, "assistant")
    
    # Nếu assistant chọn gọi Tool, langgraph tự rẽ nhánh sang Tool Node
    # Nếu assistant chọn trả lời thông thường (không gọi tool), langgraph rẽ về END
    workflow.add_conditional_edges(
        "assistant",
        tools_condition
    )
    
    # Sau khi chạy Tool Node xong, kết quả trả ngược về lại cho Assistant để xử lý bước tiếp theo
    workflow.add_edge("tools", "assistant")
    
    return workflow

# Biên dịch state graph với checkpointer
memory = MemorySaver()
workflow = build_workflow()
app = workflow.compile(checkpointer=memory)
