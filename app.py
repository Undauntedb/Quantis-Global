import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client

# -- SAYFA AYARLARI --
st.set_page_config(page_title="Quantis Global | Engineering Hub", page_icon="⚡", layout="wide")

# -- 1. SUPABASE VE API BAĞLANTILARI --
try:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
    
    # Gemini Engine Bağlantısı
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error(f"System Configuration Error: {e}")

# -- 2. DİL SÖZLÜĞÜ (Ana Ekran İçin) --
T = {
    "English": {"sub": "Advanced Engineering Solutions", "tab1": "Manual Entry", "tab2": "Quantis Vision", "up": "Upload Problem", "solve_btn": "✨ Quantis Solve", "lang_code": "English"},
    "Türkçe": {"sub": "İleri Mühendislik Çözümleri", "tab1": "Manuel Giriş", "tab2": "Quantis Vision", "up": "Problem Fotoğrafı Yükle", "solve_btn": "✨ Quantis Analiz", "lang_code": "Turkish"}
}

# -- 3. OTURUM YÖNETİMİ (Session State) --
if 'user' not in st.session_state:
    st.session_state.user = None

# -- 4. GİRİŞ / KAYIT EKRANI (AUTH) --
def auth_screen():
    st.title("⚡ Quantis Platform")
    st.markdown("### Welcome to the future of engineering.")
    
    choice = st.radio("Action:", ["Login", "Sign Up"])
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    
    if choice == "Sign Up":
        if st.button("Create Account"):
            try:
                res = supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Please check your email for confirmation.")
            except Exception as e:
                st.error(f"Error: {e}")
    else:
        if st.button("Login"):
            try:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
            except Exception as e:
                st.error("Invalid email or password.")

# -- 5. ANA UYGULAMA (Giriş Yapıldıysa Çalışır) --
def main_app():
    with st.sidebar:
        st.title("🌐 Quantis")
        st.write(f"👤 {st.session_state.user.email}")
        lang_choice = st.selectbox("Language / Dil", list(T.keys()))
        current_T = T[lang_choice]
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    st.title("⚡ Quantis Engine")
    st.caption(current_T["sub"])

    tab1, tab2 = st.tabs([current_T["tab1"], current_T["tab2"]])

    with tab1:
        st.write("Manual entry system online.")
        # Buraya önceki manuel giriş kodlarını ekleyebilirsin.

    with tab2:
        img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            if st.button(current_T["solve_btn"]):
                with st.spinner("Processing..."):
                    prompt = f"Solve this problem step by step in {current_T['lang_code']}."
                    response = model.generate_content([prompt, img])
                    st.markdown(f"<div style='background-color:#161b22; padding:20px; border-radius:10px;'>{response.text}</div>", unsafe_allow_html=True)

# -- AKIŞ KONTROLÜ --
if st.session_state.user is None:
    auth_screen()
else:
    main_app()
