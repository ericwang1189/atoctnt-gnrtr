import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
import os
import json
import requests
import random

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

# Generate random image function
def get_random_car_image():
    """Tạo URL hình ảnh ngẫu nhiên từ các nguồn ổn định"""
    sources = [
        f"https://picsum.photos/600/400?random={random.randint(1, 1000)}",
        f"https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Car+Content",
        f"https://dummyimage.com/600x400/ff6b6b/ffffff&text=Auto+Content",
        f"https://picsum.photos/600/400?random={random.randint(1001, 2000)}"
    ]
    return random.choice(sources)

# Generate Button
if st.button("Tạo Nội Dung"):
    with st.spinner("Đang tạo nội dung, vui lòng chờ..."):
        # Generate random image URL
        random_image = get_random_car_image()
        
        prompt = f"""
        You are an AI content generator specialized in car-related humor and infotainment.
        Create a piece of content in the following structure (JSON format):
        {{
          "title": "...",
          "content": "...",
          "hashtag": "#car #fun",
          "image_url": "{random_image}"
        }}
        Topic context: Related to either real cars or 1:64 scale model cars.
        User-selected style: {content_style}
        Language: Vietnamese
        Tone: Witty, engaging, internet-friendly
        Length: Max 300 words
        Ensure the output is valid JSON. Use the provided image_url exactly as given.
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
                try:
                    content_data = json.loads(json_string)
                except json.JSONDecodeError:
                    # Fallback if JSON parsing fails
                    content_data = {
                        "title": "Nội dung được tạo",
                        "content": text_response,
                        "hashtag": "#car #fun #auto",
                        "image_url": random_image
                    }
                
                # Display content
                st.subheader(content_data.get("title", "Tiêu đề không có"))
                st.write(content_data.get("content", "Nội dung không có"))
                st.write(f"**Hashtags:** {content_data.get('hashtag', '')}")
                
                # Display image with better error handling
                image_url = content_data.get("image_url", random_image)
                if image_url:
                    try:
                        # Check if image URL is accessible
                        response_img = requests.head(image_url, timeout=5)
                        if response_img.status_code == 200:
                            st.image(image_url, caption="Ảnh minh họa", use_container_width=True)
                        else:
                            # Fallback to a simple placeholder
                            st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Car+Content", 
                                   caption="Ảnh minh họa", use_container_width=True)
                    except:
                        # If all else fails, show a placeholder
                        st.image("https://via.placeholder.com/600x400/4CAF50/FFFFFF?text=Car+Content", 
                               caption="Ảnh minh họa", use_container_width=True)
                else:
                    st.info("Không có URL hình ảnh được cung cấp.")
                    
            else:
                st.error("Không thể phân tích phản hồi từ Gemini thành định dạng JSON. Vui lòng thử lại.")
                st.write("Phản hồi gốc:", text_response)
                
        except Exception as e:
            st.error(f"Đã xảy ra lỗi khi tạo nội dung: {e}")
            st.info("Vui lòng thử lại hoặc kiểm tra API Key và kết nối mạng của bạn.")

# Add some stats or info
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Phong cách", content_style)
with col2:
    st.metric("Ngôn ngữ", "Tiếng Việt")
with col3:
    st.metric("AI Model", "Gemini 1.5 Flash")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Google Gemini AI")
st.markdown("📧 Feedback: [GitHub Issues](https://github.com/ericwang1189/autocontent-generator/issues)")