import streamlit as st
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client

# ==========================================
# 1. TEMEL AYARLAR VE GÖRSEL TEMİZLİK (WHITE-LABEL)
# ==========================================
st.set_page_config(page_title="Quantis | Engineering Solver", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    /* Streamlit izlerini tamamen yok etme */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    div[data-testid="stStatusWidget"] {display: none !important;}
    .viewerBadge_container__1QSob {display: none !important;}
    
    /* Premium UI Tasarımı */
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .hero-title { text-align: center; font-size: 3.5rem; font-weight: 800; color: #58a6ff; margin-bottom: 0px; }
    .hero-sub { text-align: center; font-size: 1.2rem; color: #8b949e; margin-top: 0px; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:12px; font-weight:bold; font-size: 16px; }
    .blur-box { filter: blur(6px); user-select: none; opacity: 0.6; pointer-events: none; background: #161b22; padding: 20px; border-radius: 10px; margin-top: 10px; }
    .paywall-box { background-color: #21262d; border: 2px solid #58a6ff; border-radius: 12px; padding: 30px; text-align: center; margin-top: -30px; position: relative; z-index: 10; box-shadow: 0px -15px 20px rgba(13,17,23,0.9); }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VERİTABANI VE YAPAY ZEKA BAĞLANTILARI
# ==========================================
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("⚠️ System Configuration Error. Please check Streamlit Secrets.")

if 'user' not in st.session_state: st.session_state.user = None
if 'page' not in st.session_state: st.session_state.page = "landing"

def get_credits(user_id):
    res = supabase.table("profiles").select("credits").eq("id", user_id).execute()
    if len(res.data) == 0:
        supabase.table("profiles").insert({"id": user_id, "email": st.session_state.user.email, "credits": 3}).execute()
        return 3
    return res.data[0]["credits"]

def use_credit(user_id, current_credits):
    supabase.table("profiles").update({"credits": current_credits - 1}).eq("id", user_id).execute()

# ==========================================
# 3. LANDING PAGE (VİTRİN VE PAZARLAMA)
# ==========================================
def show_landing():
    st.markdown("<h1 class='hero-title'>⚡ Quantis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Solve engineering & calculus problems instantly.<br><i>Used by top engineering students worldwide to finish homework faster.</i></p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("**Supported Topics:** Calculus • Linear Algebra • Differential Equations • Physics")
        img_file = st.file_uploader("Upload your problem (Image)", type=['png','jpg','jpeg'])
        
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            
            if st.button("✨ Generate Solution"):
                with st.spinner("Quantis Engine is calculating..."):
                    try:
                        # PREVIEW: Sadece Sonucu Al
                        response = model.generate_content(["What is the final numerical answer or short result for this problem? Give ONLY the final answer, no steps.", img])
                        
                        st.success("Analysis Complete!")
                        st.markdown(f"<div class='result-card'><h3>Answer: {response.text}</h3></div>", unsafe_allow_html=True)
                        
                        # SAHTE BLUR EFEKTİ
                        st.markdown("<div class='blur-box'>Step 1: First, we set up the integral based on the boundaries.<br><br>Step 2: Applying the chain rule, we derive the following equation...<br><br>Step 3: Simplifying the terms gives us the final variable state.<br><br>Step 4: Substituting the values yields the final result.</div>", unsafe_allow_html=True)
                        
                        # ÖDEME / KAYIT DUVARI
                        st.markdown("""
                        <div class='paywall-box'>
                            <h2>🔒 Full Solution Locked</h2>
                            <p>You need an account to see the step-by-step explanation and download the report.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 Unlock Step-by-Step Solution (Free)"):
                            st.session_state.page = "auth"
                            st.rerun()
                    except Exception as e:
                        st.error("Error reading the image. Try another one.")

# ==========================================
# 4. GİRİŞ VE KAYIT EKRANI
# ==========================================
def show_auth():
    st.markdown("<h2 style='text-align:center;'>Welcome to Quantis</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("← Back to Home"):
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
                st.error("Authentication failed. Please check your credentials.")

# ==========================================
# 5. KULLANICI PANELİ (DASHBOARD - GERÇEK MOTOR)
# ==========================================
def show_dashboard():
    user = st.session_state.user
    credits = get_credits(user.id)
    
    with st.sidebar:
        st.title("⚡ Quantis PRO")
        st.write(f"👤 {user.email}")
        st.metric("Available Credits", f"{credits}")
        if st.button("Logout"):
            st.session_state.user = None
            st.session_state.page = "landing"
            st.rerun()

    st.title("Engineering Workspace")
    
    if credits > 0:
        img_file = st.file_uploader("Upload your homework/problem", type=['png','jpg','jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            
            if st.button("✨ Generate Detailed Solution (Uses 1 Credit)"):
                with st.spinner("Processing deep analysis..."):
                    try:
                        # GERÇEK DETAYLI ÇÖZÜM
                        prompt = "Act as an expert engineering and math tutor. Solve this problem step-by-step in extreme detail. Explain why you use certain formulas. Make it look like a professional homework report."
                        response = model.generate_content([prompt, img])
                        
                        use_credit(user.id, credits)
                        
                        st.markdown("<div class='result-card'>", unsafe_allow_html=True)
                        st.markdown(response.text)
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # RAPOR İNDİRME BUTONU (PDF Hissi verir)
                        st.download_button(
                            label="📄 Download Report",
                            data=response.text,
                            file_name="quantis_solution_report.txt",
                            mime="text/plain"
                        )
                        st.success("1 Credit used.")
                    except Exception as e:
                        st.error("Error during processing.")
    else:
        st.markdown("""
        <div class='paywall-box' style='margin-top:50px;'>
            <h1 style='color:#ff7b72;'>0 Credits Remaining</h1>
            <h3>Your free trial has ended.</h3>
            <p>Upgrade to Quantis Premium for unlimited solves, PDF reports, and Tutor Mode.</p>
            <button style='background-color:#58a6ff; color:black; padding:15px; width:100%; border-radius:10px; font-weight:bold; font-size:18px; border:none; margin-top:20px;'>
                Upgrade to Premium ($9.99/mo)
            </button>
        </div>
        """, unsafe_allow_html=True)

# ==========================================
# YÖNLENDİRİCİ (ROUTER)
# ==========================================
if st.session_state.user is not None:
    show_dashboard()
elif st.session_state.page == "auth":
    show_auth()
else:
    show_landing()
