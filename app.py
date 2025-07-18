import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import requests

# Load API key from Streamlit secrets or .env file
try:
    # Khi deploy lên Streamlit Cloud, sử dụng secrets
    GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
except:
    # Khi chạy local, sử dụng .env file
    load_dotenv()
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    st.error("GEMINI_API_KEY not found. Please set it up in Streamlit secrets or .env file.")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize the Generative Model
model = genai.GenerativeModel('gemini-1.5-flash')

# Streamlit App Title
st.title("🚗 AutoContent Generator 🏎️")
st.write("Tạo nội dung độc đáo về xe hơi (hoặc mô hình xe) với Gemini AI!")

# User Input for Content Style
content_style = st.selectbox(
    "Chọn phong cách nội dung bạn muốn:",
    ("Short Joke", "Fact", "Fun", "Dark joke")
)

# Generate Button
if st.button("Tạo Nội Dung"):
    with st.spinner("Đang tạo nội dung, vui lòng chờ..."):
        prompt = f"""
        You are an AI content generator specialized in car-related humor and infotainment.
        Create a piece of content in the following structure (JSON format):
        {{
          "title": "...",
          "content": "...",
          "hashtag": "#car #fun",
          "image_url": "https://..."
        }}
        Topic context: Related to either real cars or 1:64 scale model cars.
        User-selected style: {content_style}
        Language: Vietnamese
        Tone: Witty, engaging, internet-friendly
        Length: Max 300 words
        Ensure the output is valid JSON. For 'image_url', use a URL from Unsplash (e.g., https://source.unsplash.com/600x400/?car,humor) or placeholder.com that relates to the content.
        """
        
        try:
            response = model.generate_content(prompt)
            # Attempt to parse the JSON output from the model
            text_response = response.text
            
            # Find the first and last curly braces to extract the JSON part
            start_json = text_response.find('{')
            end_json = text_response.rfind('}') + 1
            
            if start_json != -1 and end_json != -1:
                json_string = text_response[start_json:end_json]
                content_data = json.loads(json_string)
                
                st.subheader(content_data.get("title", "Tiêu đề không có"))
                st.write(content_data.get("content", "Nội dung không có"))
                st.write(f"**Hashtags:** {content_data.get('hashtag', '')}")
                
                image_url = content_data.get("image_url")
                if image_url:
                    try:
                        st.image(image_url, caption="Ảnh minh họa", use_container_width=True)
                    except:
                        st.info("Không thể tải hình ảnh từ URL được cung cấp.")
                else:
                    st.info("Không có URL hình ảnh được cung cấp.")
            else:
                st.error("Không thể phân tích phản hồi từ Gemini thành định dạng JSON. Vui lòng thử lại.")
                st.write("Phản hồi gốc:", text_response)
                
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo nội dung: {e}")
            st.info("Vui lòng thử lại hoặc kiểm tra API Key và kết nối mạng của bạn.")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Google Gemini AI")