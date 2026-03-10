import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from fpdf import FPDF
from PIL import Image

# Sayfa Ayarları
st.set_page_config(page_title="Quantis Global | Universal Engineering", page_icon="🌐", layout="wide")

# -- DEV KÜRESEL DİL SÖZLÜĞÜ --
T = {
    "English": {"sub": "Universal Engineering Solutions", "tab1": "Manual", "tab2": "Vision (AI)", "in": "Enter Equation:", "btn": "Analyze", "up": "Upload Problem Photo"},
    "Türkçe": {"sub": "Evrensel Mühendislik Çözümleri", "tab1": "Manuel", "tab2": "Görüntü (AI)", "in": "Denklemi Girin:", "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle"},
    "Deutsch": {"sub": "Universelle Ingenieurlösungen", "tab1": "Manuell", "tab2": "Vision (KI)", "in": "Gleichung eingeben:", "btn": "Analysieren", "up": "Problemfoto hochladen"},
    "Español": {"sub": "Soluciones Universales de Ingeniería", "tab1": "Manual", "tab2": "Visión (IA)", "in": "Ingresa la ecuación:", "btn": "Analizar", "up": "Subir foto del problema"},
    "Français": {"sub": "Solutions d'Ingénierie Universelles", "tab1": "Manuel", "tab2": "Vision (IA)", "in": "Entrez l'équation:", "btn": "Analyser", "up": "Télécharger la photo"},
    "Português": {"sub": "Soluções Universais de Engenharia", "tab1": "Manual", "tab2": "Visão (IA)", "in": "Digite a equação:", "btn": "Analisar", "up": "Enviar foto do problema"},
    "Русский": {"sub": "Универсальные инженерные решения", "tab1": "Вручную", "tab2": "Зрение (ИИ)", "in": "Введите уравнение:", "btn": "Анализировать", "up": "Загрузить фото"},
    "中文": {"sub": "通用工程解决方案", "tab1": "手动输入", "tab2": "视觉识别 (AI)", "in": "输入方程式:", "btn": "开始分析", "up": "上传题目照片"},
    "हिन्दी": {"sub": "सार्वभौमिक इंजीनियरिंग समाधान", "tab1": "मैनुअल", "tab2": "विजन (AI)", "in": "समीकरण दर्ज करें:", "btn": "विश्लेषण करें", "up": "फोटो अपलोड करें"},
    "日本語": {"sub": "ユニバーサルエンジニアリングソリューション", "tab1": "手動入力", "tab2": "ビジョン (AI)", "in": "方程式を入力:", "btn": "解析する", "up": "写真をアップロード"},
    "العربية": {"sub": "حلول هندسية عالمية", "tab1": "يدوي", "tab2": "الرؤية (AI)", "in": "أدخل المعادلة:", "btn": "تحليل", "up": "تحميل صورة المسألة"}
}

# Sidebar - Dil Seçici
with st.sidebar:
    st.title("🌐 Global Gateway")
    lang_choice = st.selectbox("Select Language / Dil Seçin", list(T.keys()))
    current_T = T[lang_choice]
    st.markdown("---")
    st.write("Quantis v2.5 - Enterprise")

# -- UI STYLING --
st.markdown(f"""
<style>
    .stApp {{ background-color: #0d1117; color: #c9d1d9; }}
    .stButton>button {{ background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%); color: white; border: none; padding: 12px; font-weight: bold; border-radius: 8px; width: 100%; }}
    .result-card {{ background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
</style>
""", unsafe_allow_html=True)

st.title("⚡ Quantis")
st.caption(current_T["sub"])

# Ana Sekmeler
tab1, tab2 = st.tabs([current_T["tab1"], current_T["tab2"]])

with tab1:
    col1, col2 = st.columns([1, 2])
    with col1:
        u_expr = st.text_input(current_T["in"], "x**2 + 5*x + 6")
        mode = st.radio("Mode:", ["Derivative", "Integral", "Solve"])
        if st.button(current_T["btn"], key="solve_m"):
            with col2:
                try:
                    x_sym = sp.symbols('x')
                    expr_sym = sp.sympify(u_expr)
                    if mode == "Derivative": res = sp.diff(expr_sym, x_sym)
                    elif mode == "Integral": res = sp.integrate(expr_sym, x_sym)
                    else: res = sp.solve(expr_sym, x_sym)
                    
                    st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                    st.latex(sp.latex(res))
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Grafik Çizimi
                    f_func = sp.lambdify(x_sym, expr_sym, "numpy")
                    x_axis = np.linspace(-10, 10, 200)
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots()
                    ax.plot(x_axis, f_func(x_axis), color='#58a6ff', linewidth=2)
                    ax.grid(alpha=0.2)
                    st.pyplot(fig)
                except Exception as e: st.error(f"Error: {e}")

with tab2:
    st.info("Quantis Vision Engine: Just upload and solve.")
    img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
    if img_file:
        st.image(Image.open(img_file), use_container_width=True)
        st.button("✨ Magic Solve (AI)")