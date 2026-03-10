import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image
import google.generativeai as genai

# -- SAYFA AYARLARI --
st.set_page_config(page_title="Quantis Global | Universal Engineering", page_icon="⚡", layout="wide")

# -- API VE OTOMATİK MODEL BULUCU --
model = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        target_model_name = 'models/gemini-1.5-flash'
        for m_name in available_models:
            if 'flash' in m_name:
                target_model_name = m_name
                break
        model = genai.GenerativeModel(target_model_name)
    else:
        st.error("⚠️ API Key bulunamadı!")
except Exception as e:
    st.error(f"⚠️ API Bağlantı Hatası: {e}")

# -- %100 GENİŞLETİLMİŞ DİL SÖZLÜĞÜ --
T = {
    "English": {
        "sub": "Universal Engineering Solutions", "tab1": "Manual Entry", "tab2": "Vision (AI)",
        "in": "Enter Equation:", "mode": "Select Mode:", "modes": ["Derivative", "Integral", "Solve Roots"],
        "btn": "Analyze", "up": "Upload Problem Photo", 
        "info": "Quantis Vision: Just upload the problem photo and sit back.",
        "cap": "Uploaded Image", "solve_btn": "✨ Magic Solve (AI)",
        "spin": "Quantis intelligence is analyzing the problem...",
        "prompt": "You are an expert math and engineering assistant. Solve the problem in the image step by step, highly detailed, and in clear English. State the final result clearly at the end.",
        "err_math": "Could not read mathematical expression, please enter in correct format.",
        "err_api": "Model could not be loaded. Please check your API Key settings.",
        "err_vis": "❌ Vision Analysis Error:"
    },
    "Türkçe": {
        "sub": "Evrensel Mühendislik Çözümleri", "tab1": "Manuel Giriş", "tab2": "Görüntü (AI)",
        "in": "Denklemi Girin:", "mode": "İşlem Seçin:", "modes": ["Türev", "İntegral", "Kök Bulma"],
        "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle", 
        "info": "Quantis Vision: Sadece problem fotoğrafını yükleyin ve arkanıza yaslanın.",
        "cap": "Yüklenen Görsel", "solve_btn": "✨ Yapay Zeka ile Çöz",
        "spin": "Quantis zekası problemi analiz ediyor...",
        "prompt": "Sen uzman bir matematik ve mühendislik asistanısın. Görseldeki soruyu adım adım, son derece detaylı ve anlaşılır bir Türkçe ile çöz. En son sonucu net bir şekilde belirt.",
        "err_math": "Matematiksel ifade okunamadı, lütfen doğru formatta girin.",
        "err_api": "Model yüklenemedi. Lütfen API Key ayarlarınızı kontrol edin.",
        "err_vis": "❌ Görsel Analiz Hatası:"
    }
}

# -- YAN MENÜ --
with st.sidebar:
    st.title("🌐 Global Gateway")
    lang_choice = st.selectbox("Language / Dil", list(T.keys()))
    current_T = T[lang_choice]

# -- UI STYLING --
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:10px; font-weight:bold; }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-top: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("⚡ Quantis")
st.caption(current_T["sub"])

# -- SEKMELER --
tab1, tab2 = st.tabs([current_T["tab1"], current_T["tab2"]])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        u_expr = st.text_input(current_T["in"], "x**2 + 5*x + 6")
        calc_mode = st.radio(current_T["mode"], current_T["modes"])
        solve_btn = st.button(current_T["btn"])
        
    if solve_btn:
        with col2:
            try:
                x_sym = sp.symbols('x')
                expr_sym = sp.sympify(u_expr)
                if current_T["modes"][0] in calc_mode: res = sp.diff(expr_sym, x_sym)
                elif current_T["modes"][1] in calc_mode: res = sp.integrate(expr_sym, x_sym)
                else: res = sp.solve(expr_sym, x_sym)
                
                st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                st.latex(sp.latex(res))
                st.markdown("</div>", unsafe_allow_html=True)
                
                f_func = sp.lambdify(x_sym, expr_sym, "numpy")
                x_axis = np.linspace(-10, 10, 200)
                plt.style.use('dark_background')
                fig, ax = plt.subplots()
                ax.plot(x_axis, f_func(x_axis), color='#58a6ff', linewidth=2)
                ax.grid(alpha=0.2)
                st.pyplot(fig)
            except:
                st.error(current_T["err_math"])

with tab2:
    st.info(current_T["info"])
    img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption=current_T["cap"], use_container_width=True)
        
        if st.button(current_T["solve_btn"]):
            if model is None:
                st.error(current_T["err_api"])
            else:
                with st.spinner(current_T["spin"]):
                    try:
                        # Yapay zekaya verilecek emir, seçilen dile göre dinamik olarak çekiliyor
                        response = model.generate_content([current_T["prompt"], img])
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"{current_T['err_vis']} {e}")
