import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import sympy as sp
from PIL import Image
import google.generativeai as genai
from fpdf import FPDF
import re

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

# -- PDF OLUŞTURUCU MOTOR (QUANTIS REPORT) --
def create_quantis_pdf(solution_text, lang_code):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="QUANTIS ENGINEERING REPORT", ln=True, align='C')
    pdf.set_font("Arial", size=10)
    pdf.ln(10)
    
    # Yazıdaki markdown (*) ve (#) işaretlerini temizliyoruz ki PDF şık dursun
    clean_text = solution_text.replace('*', '').replace('#', '')
    # fpdf latin-1 desteklediği için özel karakterleri dönüştürüyoruz
    clean_text = clean_text.encode('latin-1', 'replace').decode('latin-1')
    
    pdf.multi_cell(0, 8, txt=clean_text)
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="Generated automatically by Quantis Intelligence Engine.", ln=True, align='R')
    return pdf.output(dest='S').encode('latin-1', 'ignore')

# -- DEV KÜRESEL DİL SÖZLÜĞÜ --
T = {
    "English": {"sub": "Advanced Engineering Solutions", "tab1": "Manual Entry", "tab2": "Quantis Vision", "in": "Enter Equation:", "mode": "Mode:", "modes": ["Derivative", "Integral", "Solve Roots"], "btn": "Analyze", "up": "Upload Problem Photo", "info": "Upload the problem and let Quantis Engine handle the rest.", "solve_btn": "✨ Quantis Solve", "spin": "Quantis is processing...", "lang_code": "English", "dl_btn": "📄 Download Quantis Report (PDF)"},
    "Türkçe": {"sub": "İleri Mühendislik Çözümleri", "tab1": "Manuel Giriş", "tab2": "Quantis Vision", "in": "Denklemi Girin:", "mode": "İşlem:", "modes": ["Türev", "İntegral", "Kök Bulma"], "btn": "Analiz Et", "up": "Problem Fotoğrafı Yükle", "info": "Problemi yükleyin ve Quantis Motoru'na bırakın.", "solve_btn": "✨ Quantis Analiz", "spin": "Quantis işliyor...", "lang_code": "Turkish", "dl_btn": "📄 Quantis Raporunu İndir (PDF)"},
    "Deutsch": {"sub": "Fortgeschrittene Ingenieurlösungen", "tab1": "Manuelle Eingabe", "tab2": "Quantis Vision", "in": "Gleichung eingeben:", "mode": "Modus:", "modes": ["Ableitung", "Integral", "Wurzeln lösen"], "btn": "Analysieren", "up": "Problemfoto hochladen", "info": "Laden Sie das Problem hoch, Quantis übernimmt den Rest.", "solve_btn": "✨ Quantis Lösen", "spin": "Quantis verarbeitet...", "lang_code": "German", "dl_btn": "📄 Quantis-Bericht Herunterladen (PDF)"},
    "Español": {"sub": "Soluciones de Ingeniería Avanzada", "tab1": "Entrada Manual", "tab2": "Quantis Vision", "in": "Ingrese la ecuación:", "mode": "Modo:", "modes": ["Derivada", "Integral", "Resolver Raíces"], "btn": "Analizar", "up": "Subir Foto del Problema", "info": "Sube el problema y deja que Quantis Engine haga el resto.", "solve_btn": "✨ Resolver con Quantis", "spin": "Quantis está procesando...", "lang_code": "Spanish", "dl_btn": "📄 Descargar Informe Quantis (PDF)"}
}
# (Not: Kodu kısa tutmak için 4 dil bıraktım, sen istersen diğer dilleri de önceki koddan buraya ekleyebilirsin)

# -- YAN MENÜ --
with st.sidebar:
    st.title("🌐 Quantis Settings")
    lang_choice = st.selectbox("", list(T.keys()))
    current_T = T[lang_choice]

# -- UI STYLING --
st.markdown("""
<style>
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:10px; font-weight:bold; margin-top: 10px;}
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
                        prompt = f"You are the Quantis Engineering Engine. Solve the math/engineering problem in the image step by step. Provide a highly detailed and professional solution. YOU MUST WRITE THE ENTIRE RESPONSE IN {current_T['lang_code']}. State the final result clearly."
                        response = model.generate_content([prompt, img])
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # PDF İNDİRME BUTONU (YENİ EKLENDİ)
                        pdf_data = create_quantis_pdf(response.text, current_T['lang_code'])
                        st.download_button(
                            label=current_T["dl_btn"],
                            data=pdf_data,
                            file_name="Quantis_Report.pdf",
                            mime="application/pdf"
                        )
                        
                    except Exception as e:
                        st.error(f"Quantis Engine Error: {e}")
