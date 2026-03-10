import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from fpdf import FPDF
from PIL import Image
import google.generativeai as genai

# Sayfa Ayarları
st.set_page_config(page_title="Quantis Global | Universal Engineering", page_icon="🌐", layout="wide")

# Secrets'tan API Key Al
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    st.error("API Key not found in Secrets!")

# -- DEV KÜRESEL DİL SÖZLÜĞÜ --
T = {
    "English": {"sub": "Universal Engineering Solutions", "tab1": "Manual", "tab2": "Vision (AI)", "in": "Enter Equation:", "btn": "Analyze", "up": "Upload Problem Photo"},
    "Türkçe": {"sub": "Evrensel Mühendislik Çözümleri", "tab1": "Manuel", "tab2": "Görüntü (AI)", "in": "Denklemi Girin:", "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle"}
}

with st.sidebar:
    st.title("🌐 Global Gateway")
    lang_choice = st.selectbox("Select Language", list(T.keys()))
    current_T = T[lang_choice]

# -- UI STYLING --
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%); color: white; border-radius: 8px; width: 100%; }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Quantis")
st.caption(current_T["sub"])

tab1, tab2 = st.tabs([current_T["tab1"], current_T["tab2"]])

with tab1:
    # (Önceki manuel giriş kodları burada devam eder...)
    u_expr = st.text_input(current_T["in"], "x**2 + 5*x + 6")
    if st.button(current_T["btn"]):
        st.write("Analiz ediliyor...") # Basitleştirilmiş örnek

with tab2:
    st.info("Quantis Vision: Just upload a photo of the math problem.")
    img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Problem Image", use_container_width=True)
        
        if st.button("✨ Solve with AI / Yapay Zeka ile Çöz"):
            with st.spinner("Quantis is thinking..."):
                prompt = "Analyze this math/engineering problem. Solve it step by step. Provide the final mathematical expression clearly."
                response = model.generate_content([prompt, img])
                
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.markdown(response.text)
                st.markdown("</div>", unsafe_allow_html=True)

