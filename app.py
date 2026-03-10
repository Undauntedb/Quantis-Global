import streamlit as st
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client

# -- AYARLAR --
st.set_page_config(page_title="Quantis Global", page_icon="⚡", layout="wide")

# -- API VE SUPABASE BAĞLANTISI --
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except Exception as e:
    st.error("System Error: Check API Keys.")

# -- OTURUM DURUMU --
if 'user' not in st.session_state: st.session_state.user = None

# -- FONKSİYON: KREDİ SİSTEMİ --
def get_user_credits(user_id):
    res = supabase.table("profiles").select("credits").eq("id", user_id).execute()
    if len(res.data) == 0:
        # Profil yoksa oluştur (3 kredi ile)
        supabase.table("profiles").insert({"id": user_id, "email": st.session_state.user.email, "credits": 3}).execute()
        return 3
    return res.data[0]["credits"]

def decrease_credit(user_id, current_credits):
    supabase.table("profiles").update({"credits": current_credits - 1}).eq("id", user_id).execute()

# -- EKRAN 1: GİRİŞ / KAYIT --
def auth_screen():
    st.title("⚡ Quantis Engineering Platform")
    choice = st.radio("Action:", ["Login", "Sign Up"])
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    
    if st.button("Confirm"):
        try:
            if choice == "Sign Up":
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Account created! Check email if confirmation is needed.")
            else:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# -- EKRAN 2: ANA UYGULAMA --
def main_app():
    user = st.session_state.user
    credits = get_user_credits(user.id)

    with st.sidebar:
        st.title("🌐 Quantis")
        st.write(f"👤 {user.email}")
        st.metric("Available Credits", f"{credits} ⚡")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    st.title("✨ Quantis Engine")
    st.info("Engineering Problem Solver (Calculus, Physics, Mechanics)")

    img_file = st.file_uploader("Upload Problem Photo", type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        st.image(img, use_container_width=True)
        
        if credits > 0:
            if st.button("✨ Quantis Solve (Uses 1 Credit)"):
                with st.spinner("Analyzing..."):
                    try:
                        prompt = "Solve this engineering problem step by step. Use clear formatting and formulas."
                        response = model.generate_content([prompt, img])
                        
                        # Çözüm Başarılı: Krediyi düşür
                        decrease_credit(user.id, credits)
                        
                        st.markdown(f"<div style='background-color:#161b22; padding:20px; border-radius:10px; border:1px solid #30363d;'>{response.text}</div>", unsafe_allow_html=True)
                        st.rerun() # Krediyi güncellemek için
                    except Exception as e: st.error(f"API Error: {e}")
        else:
            # PAYWALL (Ödeme Duvarı)
            st.error("🚫 Out of Credits / Krediniz Bitti")
            st.markdown("""
                <div style='background-color:#21262d; padding:30px; border-radius:15px; text-align:center; border: 2px solid #58a6ff;'>
                    <h3>🚀 Upgrade to Quantis Pro</h3>
                    <p>Get unlimited solves, PDF reports, and priority engine speed.</p>
                    <button style='background-color:#238636; color:white; padding:15px 30px; border:none; border-radius:8px; font-weight:bold; cursor:pointer;'>
                        Unlock Unlimited for $9.99/mo
                    </button>
                </div>
            """, unsafe_allow_html=True)

# AKIŞ KONTROLÜ
if st.session_state.user is None: auth_screen()
else: main_app()
