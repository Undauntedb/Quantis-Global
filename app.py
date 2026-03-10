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
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .hero-title { text-align: center; font-size: 3.5rem; font-weight: 800; color: #58a6ff; margin-bottom: 0px; }
    .hero-sub { text-align: center; font-size: 1.2rem; color: #8b949e; margin-top: 0px; margin-bottom: 30px; }
    .stButton>button { background: linear-gradient(135deg, #238636 0%, #2ea043 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:12px; font-weight:bold; font-size: 16px; }
    .paywall-box { background-color: #21262d; border: 2px solid #58a6ff; border-radius: 12px; padding: 30px; text-align: center; margin-top: 20px; }
    .result-card { background-color: #161b22; padding: 25px; border-radius: 15px; border: 1px solid #30363d; margin-top: 15px; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BAĞLANTILAR (HATA GÖSTERİMİ AÇIK)
# ==========================================
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    # En stabil modeli kullanıyoruz
    model = genai.GenerativeModel('gemini-1.5-flash')
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
# 3. VİTRİN (GENİŞLETİLMİŞ KİTLE)
# ==========================================
def show_landing():
    st.markdown("<h1 class='hero-title'>⚡ Quantis</h1>", unsafe_allow_html=True)
    st.markdown("<p class='hero-sub'>Universal Math & Science Problem Solver.<br><i>From high school algebra to university physics. Get step-by-step solutions instantly.</i></p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("**Topics:** Math • Calculus • Algebra • Physics • Chemistry • Engineering")
        img_file = st.file_uploader("Upload your problem (Image)", type=['png','jpg','jpeg'])
        
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            
            if st.button("✨ Generate Solution"):
                with st.spinner("Analyzing..."):
                    try:
                        # GERÇEK HATAYI YAKALAMAK İÇİN
                        prompt = "Give ONLY the final numerical answer or short result for this problem. No steps."
                        response = model.generate_content([prompt, img])
                        
                        st.success("Analysis Complete!")
                        st.markdown(f"<div class='result-card'><h3>Answer: {response.text}</h3></div>", unsafe_allow_html=True)
                        
                        st.markdown("""
                        <div class='paywall-box'>
                            <h2>🔒 Step-by-Step Solution Locked</h2>
                            <p>Create a free account to see the full explanation and download reports.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button("🚀 Unlock Full Solution (Free)"):
                            st.session_state.page = "auth"
                            st.rerun()
                    except Exception as e:
                        # HATA ARTIK GİZLENMİYOR! Ekranda ne olduğunu göreceğiz.
                        st.error(f"❌ Yapay Zeka Hatası: {e}")

# ==========================================
# 4. GİRİŞ VE PANEL EKRANLARI
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

    st.title("My Workspace")
    if credits > 0:
        img_file = st.file_uploader("Upload problem", type=['png','jpg','jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
            if st.button("✨ Detailed Solution (1 Credit)"):
                with st.spinner("Processing..."):
                    try:
                        prompt = "Solve this problem step-by-step in extreme detail. Explain why you use certain formulas."
                        response = model.generate_content([prompt, img])
                        supabase.table("profiles").update({"credits": credits - 1}).eq("id", user.id).execute()
                        st.markdown(response.text)
                        st.download_button("📄 Download Report", data=response.text, file_name="quantis_solution.txt")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Hata: {e}")
    else:
        st.error("0 Credits Remaining. Please upgrade to Premium.")

if st.session_state.user is not None: show_dashboard()
elif st.session_state.page == "auth": show_auth()
else: show_landing()
