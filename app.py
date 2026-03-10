import streamlit as st
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client
import PyPDF2

# ==========================================
# 1. TEMEL AYARLAR VE TASARIM
# ==========================================
st.set_page_config(page_title="Quantis AI | Olympiad Level Solver", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
    <style>
    /* HATA BURADAYDI: header etiketini gizlediğim için menü butonu yok oluyordu. Onu sildim! */
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;} 
    .viewerBadge_container__1QSob {display: none !important;}
    
    .stApp { background-color: #0d1117; color: #c9d1d9; font-family: 'Inter', sans-serif; }
    .hero-title { text-align: center; font-size: 3.2rem; font-weight: 800; color: #58a6ff; margin-bottom: 0px; margin-top: 10px; }
    .hero-sub { text-align: center; font-size: 1.1rem; color: #8b949e; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:12px; font-weight:bold; }
    .paywall-box { background-color: #21262d; border: 2px solid #58a6ff; border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px; }
    .blur-box { filter: blur(6px); opacity: 0.4; background-color: #161b22; padding: 20px; border-radius: 10px; margin-top: 15px; user-select: none; pointer-events: none; }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. GLOBAL DİL SÖZLÜĞÜ (12 DİL)
# ==========================================
T = {
    "English": {"lang": "English", "hero": "Solve Engineering Problems with Olympiad-Level Reasoning.", "sub": "Built by a Top #135 YKS Ranker & TÜBİTAK Math Olympiad Bronze Medalist.<br><i>Your ultimate academic weapon.</i>", "up": "Upload problem (Image)", "btn1": "✨ Solve Problem (Free Preview)", "lock": "🔒 Pro Features Locked", "lock_sub": "Create a free account to unlock step-by-step reasoning, PDF Exam Predictor, and Mentorship.", "btn2": "🚀 Create Free Account", "dash": "My Workspace"},
    "Türkçe": {"lang": "Turkish", "hero": "Mühendislik Sorularını Olimpiyat Seviyesinde Çözün.", "sub": "Türkiye 135.si ve TÜBİTAK Matematik Olimpiyatı Madalyalısı tarafından geliştirildi.<br><i>En güçlü akademik asistanınız.</i>", "up": "Soru yükle (Görsel)", "btn1": "✨ Soruyu Çöz (Ücretsiz Önizleme)", "lock": "🔒 Pro Özellikler Kilitli", "lock_sub": "Adım adım çözümleri, PDF Sınav Tahmincisini ve Mentorluğu açmak için ücretsiz kayıt ol.", "btn2": "🚀 Ücretsiz Hesap Oluştur", "dash": "Çalışma Alanım"},
    "Español": {"lang": "Spanish", "hero": "Resuelve Problemas de Ingeniería con Razonamiento de Nivel Olímpico.", "sub": "Creado por un Medallista de Bronce en la Olimpiada de Matemáticas.<br><i>Tu arma académica definitiva.</i>", "up": "Sube tu problema (Imagen)", "btn1": "✨ Resolver Problema (Vista Previa)", "lock": "🔒 Funciones Pro Bloqueadas", "lock_sub": "Crea una cuenta gratuita para desbloquear el razonamiento paso a paso, el predictor de exámenes PDF y la mentoría.", "btn2": "🚀 Crear Cuenta Gratis", "dash": "Mi Espacio"},
    "Deutsch": {"lang": "German", "hero": "Lösen Sie Ingenieurprobleme mit Argumentation auf Olympiade-Niveau.", "sub": "Entwickelt von einem Bronzemedaillengewinner der Mathematik-Olympiade.<br><i>Ihre ultimative akademische Waffe.</i>", "up": "Problem hochladen (Bild)", "btn1": "✨ Problem lösen (Kostenlose Vorschau)", "lock": "🔒 Pro-Funktionen Gesperrt", "lock_sub": "Erstellen Sie ein kostenloses Konto, um schrittweise Erklärungen, PDF-Prüfungsvorhersagen und Mentoring freizuschalten.", "btn2": "🚀 Kostenloses Konto Erstellen", "dash": "Mein Arbeitsbereich"},
    "Français": {"lang": "French", "hero": "Résolvez des Problèmes d'Ingénierie avec un Raisonnement de Niveau Olympique.", "sub": "Créé par un Médaillé de Bronze aux Olympiades de Mathématiques.<br><i>Votre arme académique ultime.</i>", "up": "Téléchargez le problème (Image)", "btn1": "✨ Résoudre le Problème (Aperçu)", "lock": "🔒 Fonctionnalités Pro Verrouillées", "lock_sub": "Créez un compte gratuit pour débloquer les étapes, le prédicteur d'examen PDF et le mentorat.", "btn2": "🚀 Créer un Compte Gratuit", "dash": "Mon Espace"},
    "中文": {"lang": "Chinese", "hero": "以奥林匹克级别的推理解决工程问题。", "sub": "由数学奥林匹克铜牌得主打造。<br><i>你的终极学术武器。</i>", "up": "上传问题（图片）", "btn1": "✨ 解决问题（免费预览）", "lock": "🔒 专业功能已锁定", "lock_sub": "创建一个免费账户即可解锁详细步骤、PDF考试预测和导师辅导。", "btn2": "🚀 创建免费账户", "dash": "我的工作区"},
    "Русский": {"lang": "Russian", "hero": "Решайте Инженерные Задачи с Логикой Олимпиадного Уровня.", "sub": "Создано бронзовым призером Олимпиады по математике.<br><i>Ваше главное академическое оружие.</i>", "up": "Загрузите задачу (Изображение)", "btn1": "✨ Решить Задачу (Бесплатный предпросмотр)", "lock": "🔒 Pro-функции Заблокированы", "lock_sub": "Создайте бесплатный аккаунт, чтобы получить пошаговые решения, PDF-прогнозы экзаменов и наставничество.", "btn2": "🚀 Создать Бесплатный Аккаунт", "dash": "Моя Рабочая Область"},
    "Português": {"lang": "Portuguese", "hero": "Resolva Problemas de Engenharia com Raciocínio de Nível Olímpico.", "sub": "Criado por um Medalhista de Bronze na Olimpíada de Matemática.<br><i>Sua arma acadêmica definitiva.</i>", "up": "Envie o problema (Imagem)", "btn1": "✨ Resolver Problema (Prévia)", "lock": "🔒 Recursos Pro Bloqueados", "lock_sub": "Crie uma conta gratuita para desbloquear soluções passo a passo, o Previsor de Exames PDF e a Mentoria.", "btn2": "🚀 Criar Conta Grátis", "dash": "Meu Espaço"},
    "العربية": {"lang": "Arabic", "hero": "حل المشاكل الهندسية بتفكير على مستوى الأولمبياد.", "sub": "تم بناؤه بواسطة حائز على الميدالية البرونزية في أولمبياد الرياضيات.<br><i>سلاحك الأكاديمي النهائي.</i>", "up": "ارفع المشكلة (صورة)", "btn1": "✨ حل المشكلة (معاينة مجانية)", "lock": "🔒 الميزات الاحترافية مقفلة", "lock_sub": "قم بإنشاء حساب مجاني لفتح الحلول خطوة بخطوة، وتوقع امتحانات PDF، والإرشاد.", "btn2": "🚀 إنشاء حساب مجاني", "dash": "مساحة العمل الخاصة بي"},
    "日本語": {"lang": "Japanese", "hero": "オリンピックレベルの推論で工学の問題を解決します。", "sub": "数学オリンピックの銅メダリストによって構築されました。<br><i>究極の学術兵器。</i>", "up": "問題をアップロード (画像)", "btn1": "✨ 問題を解決 (無料プレビュー)", "lock": "🔒 プロ機能がロックされています", "lock_sub": "無料アカウントを作成して、ステップバイステップの解説、PDF試験予測、メンターシップのロックを解除してください。", "btn2": "🚀 無料アカウントを作成", "dash": "マイワークスペース"},
    "हिन्दी": {"lang": "Hindi", "hero": "ओलंपियाड स्तर के तर्क के साथ इंजीनियरिंग समस्याओं को हल करें।", "sub": "गणित ओलंपियाड के कांस्य पदक विजेता द्वारा निर्मित।<br><i>आपका अंतिम शैक्षणिक हथियार।</i>", "up": "समस्या अपलोड करें (छवि)", "btn1": "✨ समस्या हल करें (मुफ्त पूर्वावलोकन)", "lock": "🔒 प्रो सुविधाएँ लॉक हैं", "lock_sub": "चरण-दर-चरण स्पष्टीकरण, पीडीएफ परीक्षा भविष्यवक्ता और मेंटरशिप को अनलॉक करने के लिए एक निःशुल्क खाता बनाएं।", "btn2": "🚀 मुफ़्त खाता बनाएँ", "dash": "मेरा कार्यक्षेत्र"},
    "Italiano": {"lang": "Italian", "hero": "Risolvi Problemi di Ingegneria con un Ragionamento di Livello Olimpico.", "sub": "Creato da una Medaglia di Bronzo alle Olimpiadi della Matematica.<br><i>La tua arma accademica definitiva.</i>", "up": "Carica il problema (Immagine)", "btn1": "✨ Risolvi Problema (Anteprima)", "lock": "🔒 Funzionalità Pro Bloccate", "lock_sub": "Crea un account gratuito per sbloccare i passaggi, il previsore di esami PDF e il tutoraggio.", "btn2": "🚀 Crea Account Gratuito", "dash": "Il mio spazio di lavoro"}
}

# ==========================================
# 3. SOL MENÜ (SİDEBAR) VE DİL SEÇİMİ
# ==========================================
with st.sidebar:
    st.markdown("### 🌐 Settings / Ayarlar")
    lang_choice = st.selectbox("Language / Dil", list(T.keys()))
    curr = T[lang_choice]
    st.divider()

# ==========================================
# 4. SİSTEM BAĞLANTILARI
# ==========================================
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model_name = 'models/gemini-1.5-flash'
    for m_name in available_models:
        if 'flash' in m_name:
            target_model_name = m_name
            break
    model = genai.GenerativeModel(target_model_name)
except Exception as e:
    st.error(f"API Error: {e}")

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "landing"

def get_credits(user_id):
    res = supabase.table("profiles").select("credits").eq("id", user_id).execute()
    if len(res.data) == 0:
        supabase.table("profiles").insert({"id": user_id, "email": st.session_state.user.email, "credits": 3}).execute()
        return 3
    return res.data[0]["credits"]

def extract_pdf_text(pdf_file):
    reader = PyPDF2.PdfReader(pdf_file)
    return "".join([page.extract_text() for page in reader.pages])

# ==========================================
# EĞER GİRİŞ YAPILDIYSA SOL MENÜYE KULLANICI BİLGİLERİNİ EKLE
# ==========================================
if st.session_state.user:
    with st.sidebar:
        user_credits = get_credits(st.session_state.user.id)
        st.write(f"👤 **{st.session_state.user.email}**")
        st.metric("Credits Left", f"{user_credits} ⚡")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "landing"
            st.rerun()

# ==========================================
# 5. VİTRİN (LANDING PAGE)
# ==========================================
def show_landing():
    st.markdown(f"<h1 class='hero-title'>⚡ Quantis AI</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-sub'><b>{curr['hero']}</b><br>{curr['sub']}</p>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["📸 Photo Solver", "📄 PDF Exam AI", "🏆 1-on-1 Mentorship"])
    
    with tab1:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            img_file = st.file_uploader(curr["up"], type=['png','jpg','jpeg'], key="landing_img")
            if img_file:
                st.image(Image.open(img_file), use_container_width=True)
                if st.button(curr["btn1"]):
                    with st.spinner("Analyzing with Olympiad Reasoning..."):
                        try:
                            prompt = f"Give ONLY the final numerical answer or short result. Language: {curr['lang']}."
                            res = model.generate_content([prompt, Image.open(img_file)])
                            st.success("Analysis Complete!")
                            st.markdown(f"<div class='result-card'><h3>Answer: {res.text}</h3></div>", unsafe_allow_html=True)
                            st.markdown("""
                                <div class='blur-box'>
                                    <p><b>Step 1:</b> Defining variables and applying the foundational theorem...</p>
                                    <p><b>Step 2:</b> Integrating over the given boundaries yields the matrix.</p>
                                </div>
                            """, unsafe_allow_html=True)
                            st.markdown(f"<div class='paywall-box'><h2>{curr['lock']}</h2><p>{curr['lock_sub']}</p></div>", unsafe_allow_html=True)
                            if st.button(curr["btn2"], key="btn_signup_1"):
                                st.session_state.page = "auth"
                                st.rerun()
                        except Exception as e:
                            st.error(f"❌ AI Error: {e}")

    with tab2:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.info("Upload your lecture notes. AI will extract key formulas, predict exam questions, and generate a mini-test.")
            pdf_file = st.file_uploader("Upload PDF Notes", type=['pdf'], key="landing_pdf")
            if pdf_file:
                st.success("PDF Loaded! Ready for analysis.")
                if st.button("🧠 Analyze PDF & Predict Exam"):
                    st.markdown("""
                        <div class='blur-box'>
                            <p><b>Summary:</b> The core concept of this chapter relies on thermodynamics...</p>
                            <p><b>Predicted Question 1:</b> Calculate the entropy change when...</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"<div class='paywall-box'><h2>{curr['lock']}</h2><p>{curr['lock_sub']}</p></div>", unsafe_allow_html=True)
                    if st.button(curr["btn2"], key="btn_signup_2"):
                        st.session_state.page = "auth"
                        st.rerun()

    with tab3:
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("""
            ### Learn from the Best
            Your instructor, **Burak**, is a **Top 135 YKS Ranker** and a **TUBITAK Math Olympiad Bronze Medalist**.
            
            Get exclusive access to:
            * Advanced Problem Solving Techniques
            * Custom Exam Strategy
            * 1-on-1 Live Sessions
            """)
            st.markdown(f"<div class='paywall-box'><h2>{curr['lock']}</h2><p>{curr['lock_sub']}</p></div>", unsafe_allow_html=True)
            if st.button(curr["btn2"], key="btn_signup_3"):
                st.session_state.page = "auth"
                st.rerun()

# ==========================================
# 6. GİRİŞ VE KAYIT EKRANI
# ==========================================
def show_auth():
    st.markdown("<h2 style='text-align:center;'>Welcome to Quantis</h2>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← Back"):
            st.session_state.page = "landing"
            st.rerun()
        auth_mode = st.radio("Select:", ["Sign Up", "Login"], horizontal=True)
        email = st.text_input("Email:")
        password = st.text_input("Password:", type="password")
        if st.button("Confirm"):
            try:
                if auth_mode == "Sign Up":
                    supabase.auth.sign_up({"email": email, "password": password})
                    st.success("Account created! You can now log in.")
                else:
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    st.session_state.user = res.user
                    st.session_state.page = "dashboard"
                    st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")

# ==========================================
# 7. ÇALIŞMA ALANI (DASHBOARD)
# ==========================================
def show_dashboard():
    st.markdown(f"<h1 class='hero-title'>{curr['dash']}</h1>", unsafe_allow_html=True)
    
    user_credits = get_credits(st.session_state.user.id)
    
    if user_credits <= 0:
        st.error("0 Credits Remaining.")
        st.markdown("""
            <div class='paywall-box'>
                <h2>🚀 Upgrade to Quantis PRO</h2>
                <p>• 5 Credits: $2 <br>• 10 Credits: $5 <br>• Unlimited + PDF Tools: $10/mo</p>
                <a href='https://lemonsqueezy.com' target='_blank'><button style='background-color:#58a6ff; border:none; padding:10px 20px; border-radius:5px; color:black; font-weight:bold; cursor:pointer;'>Purchase Credits</button></a>
            </div>
        """, unsafe_allow_html=True)
        return

    tab1, tab2, tab3 = st.tabs(["📸 Photo Solver", "📄 PDF Exam AI", "🏆 Pro Tutoring"])
    
    with tab1:
        st.subheader("Step-by-Step Solver")
        img = st.file_uploader("Upload Problem", type=['png','jpg','jpeg'], key="img_dash")
        if img and st.button("✨ Solve & Explain (1 Credit)"):
            with st.spinner("Processing..."):
                prompt = f"Solve this step-by-step as an expert tutor. Language: {curr['lang']}."
                response = model.generate_content([prompt, Image.open(img)])
                supabase.table("profiles").update({"credits": user_credits - 1}).eq("id", st.session_state.user.id).execute()
                st.markdown(f"<div class='result-card'>{response.text}</div>", unsafe_allow_html=True)
                st.download_button("📄 Download PDF Report", response.text, "quantis_report.txt")
                st.rerun()
                
    with tab2:
        st.subheader("AI Exam Predictor")
        st.info("Upload your lecture notes. AI will extract key formulas, predict exam questions, and generate a mini-test.")
        pdf = st.file_uploader("Upload PDF Notes", type=['pdf'], key="pdf_dash")
        if pdf and st.button("🧠 Analyze PDF (1 Credit)"):
            with st.spinner("Reading document and generating predictions..."):
                text = extract_pdf_text(pdf)
                prompt = f"Act as a university professor. Based on this text, generate: 1. Key Formulas/Summary. 2. Three Highly Probable Exam Questions. 3. A Mini-Test (Flashcard style). Language: {curr['lang']}.\n\nText: {text[:8000]}"
                response = model.generate_content(prompt)
                supabase.table("profiles").update({"credits": user_credits - 1}).eq("id", st.session_state.user.id).execute()
                st.markdown(f"<div class='result-card'>{response.text}</div>", unsafe_allow_html=True)
                st.rerun()

    with tab3:
        st.subheader("Elite 1-on-1 Mentorship")
        st.markdown("""
        **Learn from the Best.**
        Your instructor, Burak, is a **Top 135 YKS Ranker** and a **TUBITAK Math Olympiad Bronze Medalist**.
        
        Get exclusive access to:
        * Advanced Problem Solving Techniques
        * Custom Exam Strategy
        """)
        st.button("Book a Session (Contact Support)")

# ==========================================
# AKIŞ KONTROLÜ
# ==========================================
if st.session_state.user: show_dashboard()
elif st.session_state.page == "auth": show_auth()
else: show_landing()
