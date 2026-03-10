import streamlit as st
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. AYARLAR VE TASARIM
# ==========================================
st.set_page_config(page_title="Quantis | Universal Solver", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* UI ve Branding Gizleme */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .hero-title { text-align: center; font-size: 3.5rem; font-weight: 800; color: #58a6ff; margin-bottom: 0px; }
    .hero-sub { text-align: center; font-size: 1.2rem; color: #8b949e; margin-top: 0px; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:12px; font-weight:bold; font-size: 16px; }
    .paywall-box { background-color: #21262d; border: 2px solid #58a6ff; border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px; }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. KÜRESEL DİL SÖZLÜĞÜ (10 DİL)
# ==========================================
T = {
    "English": {"lang": "English", "hero": "Universal Math & Science Solver", "sub": "Get step-by-step solutions instantly.", "up": "Upload your problem", "btn1": "✨ Generate Solution", "lock": "🔒 Full Solution Locked", "lock_sub": "Create a free account to see the explanation.", "btn2": "🚀 Unlock Full Solution (Free)", "dash": "My Workspace", "btn3": "✨ Detailed Solution (1 Credit)", "err": "0 Credits. Upgrade to Premium.", "dl": "📄 Download Report", "ans": "Answer:"},
    "Türkçe": {"lang": "Turkish", "hero": "Evrensel Matematik ve Bilim Çözücü", "sub": "Anında adım adım çözüm alın.", "up": "Probleminizi yükleyin", "btn1": "✨ Çözüm Üret", "lock": "🔒 Tam Çözüm Kilitli", "lock_sub": "Açıklamayı görmek için ücretsiz hesap oluşturun.", "btn2": "🚀 Tam Çözümü Aç (Ücretsiz)", "dash": "Çalışma Alanım", "btn3": "✨ Detaylı Çözüm (1 Kredi)", "err": "0 Kredi. Lütfen Premium'a geçin.", "dl": "📄 Raporu İndir", "ans": "Cevap:"},
    "Español": {"lang": "Spanish", "hero": "Solucionador Universal de Matemáticas", "sub": "Obtén soluciones paso a paso al instante.", "up": "Sube tu problema", "btn1": "✨ Generar Solución", "lock": "🔒 Solución Completa Bloqueada", "lock_sub": "Crea una cuenta gratis para ver la explicación.", "btn2": "🚀 Desbloquear Solución (Gratis)", "dash": "Mi Espacio", "btn3": "✨ Solución Detallada (1 Crédito)", "err": "0 Créditos. Mejora a Premium.", "dl": "📄 Descargar Reporte", "ans": "Respuesta:"},
    "Deutsch": {"lang": "German", "hero": "Universeller Mathe- & Wissenschaftslöser", "sub": "Erhalten Sie sofort Schritt-für-Schritt-Lösungen.", "up": "Laden Sie Ihr Problem hoch", "btn1": "✨ Lösung Generieren", "lock": "🔒 Vollständige Lösung Gesperrt", "lock_sub": "Konto erstellen, um die Erklärung zu sehen.", "btn2": "🚀 Lösung Entsperren (Kostenlos)", "dash": "Mein Arbeitsbereich", "btn3": "✨ Detaillierte Lösung (1 Credit)", "err": "0 Credits. Bitte auf Premium upgraden.", "dl": "📄 Bericht Herunterladen", "ans": "Antwort:"},
    "中文": {"lang": "Chinese", "hero": "通用数学与科学求解器", "sub": "立即获取逐步解答。", "up": "上传您的问题", "btn1": "✨ 生成解答", "lock": "🔒 完整解答已锁定", "lock_sub": "创建一个免费账户以查看详细说明。", "btn2": "🚀 解锁完整解答 (免费)", "dash": "我的工作区", "btn3": "✨ 详细解答 (1 积分)", "err": "积分不足，请升级至高级版。", "dl": "📄 下载报告", "ans": "答案:"},
    "Français": {"lang": "French", "hero": "Solveur Universel de Mathématiques", "sub": "Obtenez des solutions étape par étape instantanément.", "up": "Téléchargez votre problème", "btn1": "✨ Générer la Solution", "lock": "🔒 Solution Complète Verrouillée", "lock_sub": "Créez un compte gratuit pour voir l'explication.", "btn2": "🚀 Débloquer la Solution (Gratuit)", "dash": "Mon Espace", "btn3": "✨ Solution Détaillée (1 Crédit)", "err": "0 Crédits. Passez à Premium.", "dl": "📄 Télécharger le Rapport", "ans": "Réponse:"},
    "Русский": {"lang": "Russian", "hero": "Универсальный Решатель Задач", "sub": "Получите пошаговые решения мгновенно.", "up": "Загрузите вашу задачу", "btn1": "✨ Сгенерировать Решение", "lock": "🔒 Полное Решение Заблокировано", "lock_sub": "Создайте бесплатный аккаунт, чтобы увидеть объяснение.", "btn2": "🚀 Разблокировать Решение (Бесплатно)", "dash": "Моя Рабочая Область", "btn3": "✨ Подробное Решение (1 Кредит)", "err": "0 Кредитов. Перейдите на Premium.", "dl": "📄 Скачать Отчет", "ans": "Ответ:"},
    "Português": {"lang": "Portuguese", "hero": "Solucionador Universal de Matemática", "sub": "Obtenha soluções passo a passo instantaneamente.", "up": "Envie seu problema", "btn1": "✨ Gerar Solução", "lock": "🔒 Solução Completa Bloqueada", "lock_sub": "Crie uma conta grátis para ver a explicação.", "btn2": "🚀 Desbloquear Solução (Grátis)", "dash": "Meu Espaço", "btn3": "✨ Solução Detalhada (1 Crédito)", "err": "0 Créditos. Mude para Premium.", "dl": "📄 Baixar Relatório", "ans": "Resposta:"},
    "日本語": {"lang": "Japanese", "hero": "汎用数学・科学ソルバー", "sub": "ステップバイステップの解答を瞬時に取得します。", "up": "問題をアップロード", "btn1": "✨ 解答を生成", "lock": "🔒 完全な解答はロックされています", "lock_sub": "解説を見るには無料アカウントを作成してください。", "btn2": "🚀 完全な解答をロック解除 (無料)", "dash": "マイワークスペース", "btn3": "✨ 詳細な解答 (1 クレジット)", "err": "クレジットがありません。Premiumにアップグレードしてください。", "dl": "📄 レポートをダウンロード", "ans": "答え:"},
    "العربية": {"lang": "Arabic", "hero": "الحلال العالمي للرياضيات والعلوم", "sub": "احصل على حلول خطوة بخطوة على الفور.", "up": "قم برفع مسألتك", "btn1": "✨ توليد الحل", "lock": "🔒 الحل الكامل مقفل", "lock_sub": "قم بإنشاء حساب مجاني لرؤية الشرح.", "btn2": "🚀 فتح الحل الكامل (مجاني)", "dash": "مساحة العمل الخاصة بي", "btn3": "✨ حل مفصل (1 رصيد)", "err": "0 رصيد. يرجى الترقية إلى Premium.", "dl": "📄 تحميل التقرير", "ans": "الإجابة:"}
}

# ==========================================
# 3. YAN MENÜ VE BAĞLANTILAR (GARANTİLİ MODEL BULUCU EKLENDİ)
# ==========================================
with st.sidebar:
    st.title("🌐 Global Gateway")
    lang_choice = st.selectbox("Select Language", list(T.keys()))
    curr = T[lang_choice]

try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    
    # 404 HATASINI ÇÖZEN OTOMATİK SİSTEM
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    target_model_name = 'models/gemini-1.5-flash'
    for m_name in available_models:
        if 'flash' in m_name:
            target_model_name = m_name
            break
    model = genai.GenerativeModel(target_model_name)
    
except Exception as e:
    st.error(f"⚠️ Kritik Bağlantı Hatası: {e}")

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "landing"

def get_credits(user_id):
    res = supabase.table("profiles").select("credits").eq("id", user_id).execute()
    if len(res.data) == 0:
        supabase.table("profiles").insert({"id": user_id, "email": st.session_state.user.email, "credits": 3}).execute()
        return 3
    return res.data[0]["credits"]

# ==========================================
# 4. VİTRİN (LANDING PAGE)
# ==========================================
def show_landing():
    st.markdown("<h1 class='hero-title'>⚡ Quantis</h1>", unsafe_allow_html=True)
    st.markdown(f"<p class='hero-sub'>{curr['hero']}<br><i>{curr['sub']}</i></p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        img_file = st.file_uploader(curr["up"], type=['png','jpg','jpeg'])
        
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            
            if st.button(curr["btn1"]):
                with st.spinner("Analyzing..."):
                    try:
                        prompt = f"Give ONLY the final numerical answer or short result for this problem. No steps. YOU MUST WRITE THE ANSWER IN {curr['lang']} LANGUAGE."
                        response = model.generate_content([prompt, img])
                        
                        st.success("Complete!")
                        st.markdown(f"<div class='result-card'><h3>{curr['ans']} {response.text}</h3></div>", unsafe_allow_html=True)
                        
                        st.markdown(f"""
                        <div class='paywall-box'>
                            <h2>{curr['lock']}</h2>
                            <p>{curr['lock_sub']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(curr["btn2"]):
                            st.session_state.page = "auth"
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ AI Error: {e}")

# ==========================================
# 5. GİRİŞ VE PANEL EKRANLARI
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
                st.error(f"Auth Error: {e}")

def show_dashboard():
    user = st.session_state.user
    credits = get_credits(user.id)
    
    with st.sidebar:
        st.title("⚡ Quantis PRO")
        st.write(f"👤 {user.email}")
        st.metric("Credits", f"{credits}")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "landing"
            st.rerun()

    st.title(curr["dash"])
    if credits > 0:
        img_file = st.file_uploader(curr["up"], type=['png','jpg','jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            if st.button(curr["btn3"]):
                with st.spinner("Processing..."):
                    try:
                        prompt = f"Act as an expert math and science tutor. Solve this problem step-by-step in extreme detail. YOU MUST WRITE THE ENTIRE EXPLANATION IN {curr['lang']} LANGUAGE."
                        response = model.generate_content([prompt, img])
                        
                        supabase.table("profiles").update({"credits": credits - 1}).eq("id", user.id).execute()
                        st.markdown(response.text)
                        st.download_button(curr["dl"], data=response.text, file_name="quantis_solution.txt")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error: {e}")
    else:
        st.error(curr["err"])

# ==========================================
# AKIŞ KONTROLÜ
# ==========================================
if st.session_state.user is not None: show_dashboard()
elif st.session_state.page == "auth": show_auth()
else: show_landing()
