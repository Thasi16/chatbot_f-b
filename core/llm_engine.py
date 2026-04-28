from langchain_google_genai import ChatGoogleGenerativeAI
from .config import GEMINI_API_KEY

def get_llm(temperature=0):
    """Khởi tạo mô hình Gemini."""
    return ChatGoogleGenerativeAI(
        model="models/gemini-2.5-flash", 
        google_api_key=GEMINI_API_KEY,
        temperature=temperature,
        max_retries=5 
    )
