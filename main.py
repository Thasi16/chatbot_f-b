import os
import sys

# Đảm bảo python có thể đọc được các module thư mục con
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from langchain_core.messages import HumanMessage
from agent.workflow import app

def main():
    print("=" * 60)
    print("🤖 CHATBOT F&B ADVISOR - LangGraph + Gemini API")
    print("Gõ 'q' hoặc 'quit' để thoát.")
    print("=" * 60)
    
    # Cấu hình bộ nhớ checkpointer cho LangGraph
    # Sử dụng thread_id cố định để bot nhớ luồng tin nhắn (slot filling)
    config = {"configurable": {"thread_id": "session_1"}}
    
    while True:
        try:
            user_input = input(">> Bạn: ")
            if not user_input.strip():
                continue
                
            if user_input.lower() in ["q", "quit", "exit", "thoát"]:
                print("Tạm biệt!")
                break
                
            # Tạo message input
            inputs = {"messages": [HumanMessage(content=user_input)]}
            
            # Gọi graph App
            result = app.invoke(inputs, config=config)
            
            # Lấy câu trả lời cuối cùng
            bot_reply = result["messages"][-1].content
            print(f"\nBot: {bot_reply}\n")
            
        except KeyboardInterrupt:
            print("\nTạm biệt!")
            break
        except Exception as e:
            print(f"[Error]: {e}")

if __name__ == "__main__":
    main()
