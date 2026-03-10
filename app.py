import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image
import google.generativeai as genai

# -- SAYFA AYARLARI --
st.set_page_config(page_title="Quantis Global | Universal Engineering", page_icon="⚡", layout="wide")

# -- API VE OTOMATİK MODEL BULUCU --
# (Bu kısım 404 hatasını tamamen çözer. Tahmin etmez, API'ye sorar.)
model = None
try:
    if "GEMINI_API_KEY" in st.secrets:
        genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
        
        # API anahtarına tanımlı, çalışır durumdaki tüm modellerin listesini çekiyoruz
        available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
        
        # İçinde 'flash' geçen en güncel, fotoğraf okuyabilen modeli otomatik seçiyoruz
        target_model_name = 'models/gemini-1.5-flash' # Varsayılan güvenlik ağı
        for m_name in available_models:
            if 'flash' in m_name:
                target_model_name = m_name
                break
                
        model = genai.GenerativeModel(target_model_name)
    else:
        st.error("⚠️ API Key bulunamadı! Streamlit 'Manage app' > 'Settings' > 'Secrets' kısmını kontrol et.")
except Exception as e:
    st.error(f"⚠️ API Bağlantı Hatası: {e}")

# -- DİL SÖZLÜĞÜ --
T = {
    "English": {"sub": "Universal Engineering Solutions", "tab1": "Manual", "tab2": "Vision (AI)", "in": "Enter Equation:", "btn": "Analyze", "up": "Upload Problem Photo"},
    "Türkçe": {"sub": "Evrensel Mühendislik Çözümleri", "tab1": "Manuel", "tab2": "Görüntü (AI)", "in": "Denklemi Girin:", "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle"}
}

# -- YAN MENÜ --
with st.sidebar:
    st.title("🌐 Global Gateway")
    lang_choice = st.selectbox("Select Language / Dil Seçin", list(T.keys()))
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
        calc_mode = st.radio("Mode:", ["Derivative / Türev", "Integral / İntegral", "Solve / Kök Bulma"])
        solve_btn = st.button(current_T["btn"])
        
    if solve_btn:
        with col2:
            try:
                x_sym = sp.symbols('x')
                expr_sym = sp.sympify(u_expr)
                if "Derivative" in calc_mode: res = sp.diff(expr_sym, x_sym)
                elif "Integral" in calc_mode: res = sp.integrate(expr_sym, x_sym)
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
            except Exception as e:
                st.error("Matematiksel ifade okunamadı, lütfen doğru formatta girin.")

with tab2:
    st.info("Quantis Vision: Sadece problemi yükleyin ve arkanıza yaslanın.")
    img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Yüklenen Görsel", use_container_width=True)
        
        if st.button("✨ Magic Solve (AI)"):
            if model is None:
                st.error("Model yüklenemedi. Lütfen API Key ayarlarınızı kontrol edin.")
            else:
                with st.spinner("Quantis zekası problemi analiz ediyor..."):
                    try:
                        prompt = "Sen uzman bir matematik ve mühendislik asistanısın. Görseldeki soruyu adım adım, son derece detaylı ve anlaşılır bir Türkçe ile çöz. En son sonucu net bir şekilde belirt."
                        response = model.generate_content([prompt, img])
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"❌ Görsel Analiz Hatası: {e}")
