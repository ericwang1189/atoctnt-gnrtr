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

# Custom Prompt Input
st.subheader("🎯 Tùy chỉnh Prompt")
default_prompt = "You are an expert in automobiles and scale model cars, with extensive knowledge and professional-level insight across both industries."
custom_prompt = st.text_area(
    "Nhập prompt tùy chỉnh của bạn:",
    value=default_prompt,
    height=100,
    help="Đây là phần mô tả vai trò của AI. Bạn có thể thay đổi để tạo ra nội dung theo ý muốn.",
    placeholder="Ví dụ: You are a professional car reviewer with 20 years of experience..."
)

# Tone Selection
st.subheader("🎨 Chọn Tone")
tone_options = {
    "Gần gũi": "Casual, funny, relatable",
    "Thông minh": "Smart, upbeat, shareable",
    "Dứt khoát": "Bold, sharp, confident",
    "Mạnh mẽ": "Direct, raw, unapologetic"
}
selected_tone = st.selectbox(
    "Chọn tone cho nội dung:",
    options=list(tone_options.keys()),
    help="Tone này sẽ ảnh hưởng đến cách viết và cảm xúc của nội dung"
)
tone_description = tone_options[selected_tone]

# Generate random image function
def get_random_car_image():
    """Tạo URL hình ảnh ngẫu nhiên từ các nguồn ổn định"""
    # Sử dụng Unsplash API để lấy hình ảnh xe hơi thực tế
    car_keywords = ["sports-car", "luxury-car", "vintage-car", "racing-car", "electric-car", "suv", "sedan", "convertible"]
    selected_keyword = random.choice(car_keywords)
    
    sources = [
        f"https://source.unsplash.com/600x400/?car,{selected_keyword}",
        f"https://source.unsplash.com/600x400/?automobile,{selected_keyword}",
        f"https://source.unsplash.com/600x400/?vehicle,{selected_keyword}",
        f"https://source.unsplash.com/600x400/?automotive,{selected_keyword}",
        # Backup options
        f"https://picsum.photos/600/400?random={random.randint(1, 1000)}",
        f"https://via.placeholder.com/600x400/2C3E50/FFFFFF?text=🚗+Car+Content"
    ]
    return random.choice(sources)

# Generate Button
if st.button("Tạo Nội Dung"):
    with st.spinner("Đang tạo nội dung, vui lòng chờ..."):
        # Generate random image URL
        random_image = get_random_car_image()
        
        # Sử dụng custom prompt và tone thay vì prompt cố định
        prompt = f"""
        {custom_prompt}
        Create a piece of content in the following structure (JSON format):
        {{
          "title": "...",
          "content": "...",
          "hashtag": "#car #fun",
          "image_url": "{random_image}"
        }}
        Topic context: Related to either real cars or 1:64 scale model cars.
        User-selected style: {content_style}
        User-selected tone: {selected_tone} ({tone_description})
        Language: Vietnamese
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
                        # Sử dụng st.image với xử lý lỗi tốt hơn
                        st.image(image_url, caption="Ảnh minh họa", use_container_width=True)
                    except Exception as img_error:
                        st.warning(f"Không thể tải ảnh từ URL: {image_url}")
                        # Fallback với placeholder tốt hơn
                        fallback_url = "https://via.placeholder.com/600x400/2C3E50/FFFFFF?text=🚗+Car+Content"
                        try:
                            st.image(fallback_url, caption="Ảnh minh họa (dự phòng)", use_container_width=True)
                        except:
                            st.info("Không thể hiển thị hình ảnh. Vui lòng thử lại.")
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
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Phong cách", content_style)
with col2:
    st.metric("Tone", selected_tone)
with col3:
    st.metric("Ngôn ngữ", "Tiếng Việt")
with col4:
    st.metric("AI Model", "Gemini 1.5 Flash")

# Footer
st.markdown("---")
st.markdown("Made with ❤️ using Streamlit and Google Gemini AI")
st.markdown("📧 Feedback: [GitHub Issues](https://github.com/ericwang1189/autocontent-generator/issues)")
