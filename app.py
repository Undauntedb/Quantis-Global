import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image
import google.generativeai as genai

# -- SAYFA AYARLARI --
st.set_page_config(page_title="Quantis Global | Engineering Hub", page_icon="⚡", layout="wide")

# -- API VE MOTOR AYARLARI --
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
        st.error("⚠️ API Key is missing in Secrets.")
except Exception as e:
    st.error(f"⚠️ Connection Error: {e}")

# -- DEV KÜRESEL DİL SÖZLÜĞÜ (10 DİL) --
T = {
    "English": {"sub": "Advanced Engineering Solutions", "tab1": "Manual Entry", "tab2": "Quantis Vision", "in": "Enter Equation:", "mode": "Mode:", "modes": ["Derivative", "Integral", "Solve Roots"], "btn": "Analyze", "up": "Upload Problem Photo", "info": "Upload the problem and let Quantis Engine handle the rest.", "solve_btn": "✨ Quantis Solve", "spin": "Quantis is processing...", "lang_code": "English"},
    "Türkçe": {"sub": "İleri Mühendislik Çözümleri", "tab1": "Manuel Giriş", "tab2": "Quantis Vision", "in": "Denklemi Girin:", "mode": "İşlem:", "modes": ["Türev", "İntegral", "Kök Bulma"], "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle", "info": "Problemi yükleyin ve Quantis Motoru'na bırakın.", "solve_btn": "✨ Quantis Analiz", "spin": "Quantis işliyor...", "lang_code": "Turkish"},
    "Deutsch": {"sub": "Fortgeschrittene Ingenieurlösungen", "tab1": "Manuelle Eingabe", "tab2": "Quantis Vision", "in": "Gleichung eingeben:", "mode": "Modus:", "modes": ["Ableitung", "Integral", "Wurzeln lösen"], "btn": "Analysieren", "up": "Problemfoto hochladen", "info": "Laden Sie das Problem hoch, Quantis übernimmt den Rest.", "solve_btn": "✨ Quantis Lösen", "spin": "Quantis verarbeitet...", "lang_code": "German"},
    "Español": {"sub": "Soluciones de Ingeniería Avanzada", "tab1": "Entrada Manual", "tab2": "Quantis Vision", "in": "Ingrese la ecuación:", "mode": "Modo:", "modes": ["Derivada", "Integral", "Resolver Raíces"], "btn": "Analizar", "up": "Subir Foto del Problema", "info": "Sube el problema y deja que Quantis Engine haga el resto.", "solve_btn": "✨ Resolver con Quantis", "spin": "Quantis está procesando...", "lang_code": "Spanish"},
    "Français": {"sub": "Solutions d'Ingénierie Avancées", "tab1": "Entrée Manuelle", "tab2": "Quantis Vision", "in": "Entrez l'équation:", "mode": "Mode:", "modes": ["Dérivée", "Intégrale", "Résoudre les Racines"], "btn": "Analyser", "up": "Télécharger la Photo", "info": "Téléchargez le problème, Quantis s'occupe du reste.", "solve_btn": "✨ Résoudre avec Quantis", "spin": "Quantis traite en cours...", "lang_code": "French"},
    "Português": {"sub": "Soluções de Engenharia Avançada", "tab1": "Entrada Manual", "tab2": "Quantis Vision", "in": "Digite a Equação:", "mode": "Modo:", "modes": ["Derivada", "Integral", "Encontrar Raízes"], "btn": "Analisar", "up": "Enviar Foto do Problema", "info": "Envie o problema e deixe o Quantis Engine resolver.", "solve_btn": "✨ Resolver com Quantis", "spin": "Quantis está processando...", "lang_code": "Portuguese"},
    "Русский": {"sub": "Передовые Инженерные Решения", "tab1": "Ручной Ввод", "tab2": "Quantis Vision", "in": "Введите уравнение:", "mode": "Режим:", "modes": ["Производная", "Интеграл", "Найти Корни"], "btn": "Анализ", "up": "Загрузить Фото Проблемы", "info": "Загрузите проблему, Quantis сделает остальное.", "solve_btn": "✨ Решить с Quantis", "spin": "Quantis обрабатывает...", "lang_code": "Russian"},
    "中文": {"sub": "高级工程解决方案", "tab1": "手动输入", "tab2": "Quantis Vision", "in": "输入方程式:", "mode": "模式:", "modes": ["导数", "积分", "求根"], "btn": "分析", "up": "上传问题照片", "info": "上传问题，让 Quantis 引擎来处理。", "solve_btn": "✨ Quantis 解析", "spin": "Quantis 正在处理...", "lang_code": "Chinese"},
    "日本語": {"sub": "高度なエンジニアリングソリューション", "tab1": "手動入力", "tab2": "Quantis Vision", "in": "方程式を入力:", "mode": "モード:", "modes": ["導関数", "積分", "根を求める"], "btn": "解析する", "up": "問題の写真をアップロード", "info": "問題をアップロードして、Quantisエンジンにお任せください。", "solve_btn": "✨ Quantis 解決", "spin": "Quantisが処理中...", "lang_code": "Japanese"},
    "العربية": {"sub": "حلول هندسية متقدمة", "tab1": "إدخال يدوي", "tab2": "Quantis Vision", "in": "أدخل المعادلة:", "mode": "الوضع:", "modes": ["مشتق", "تكامل", "حل الجذور"], "btn": "تحليل", "up": "رفع صورة المسألة", "info": "قم برفع المسألة ودع محرك Quantis يتولى الباقي.", "solve_btn": "✨ حل عبر Quantis", "spin": "Quantis يقوم بالمعالجة...", "lang_code": "Arabic"}
}

# -- YAN MENÜ --
with st.sidebar:
    st.title("🌐 Quantis Settings")
    lang_choice = st.selectbox("", list(T.keys()))
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
                st.error("Error evaluating expression.")

with tab2:
    st.info(current_T["info"])
    img_file = st.file_uploader(current_T["up"], type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, caption="Quantis Upload", use_container_width=True)
        
        if st.button(current_T["solve_btn"]):
            if model is None:
                st.error("Engine offline. Check API Key.")
            else:
                with st.spinner(current_T["spin"]):
                    try:
                        # DİNAMİK YAPAY ZEKA EMRİ: Seçilen dile göre cevap verir.
                        prompt = f"You are the Quantis Engineering Engine. Solve the math/engineering problem in the image step by step. Provide a highly detailed and professional solution. YOU MUST WRITE THE ENTIRE RESPONSE IN {current_T['lang_code']}. State the final result clearly."
                        response = model.generate_content([prompt, img])
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Quantis Engine Error: {e}")
