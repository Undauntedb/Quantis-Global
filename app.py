import streamlit as st
from PIL import Image
import google.generativeai as genai
from supabase import create_client, Client

# -- 1. GÖRSEL TEMİZLİK (WHITE LABEL) --
st.set_page_config(page_title="Quantis Global | Engineering Engine", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stApp { background-color: #0d1117; color: #c9d1d9; }
    .stButton>button { background: linear-gradient(135deg, #58a6ff 0%, #1f6feb 100%); color: white; border-radius: 8px; width: 100%; border:none; padding:12px; font-weight:bold; }
    .paywall-card { background: linear-gradient(180deg, rgba(22,27,34,1) 0%, rgba(13,17,23,1) 100%); padding: 40px; border-radius: 20px; border: 1px solid #30363d; text-align: center; margin-top: 20px; }
    .blur-text { filter: blur(8px); user-select: none; opacity: 0.5; pointer-events: none; }
    </style>
""", unsafe_allow_html=True)

# -- 2. BAĞLANTILAR --
try:
    supabase: Client = create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash-latest')
except:
    st.error("Connection Error.")

if 'user' not in st.session_state: st.session_state.user = None

# -- 3. YARDIMCI FONKSİYONLAR --
def get_user_credits(user_id):
    res = supabase.table("profiles").select("credits").eq("id", user_id).execute()
    if len(res.data) == 0:
        supabase.table("profiles").insert({"id": user_id, "email": st.session_state.user.email, "credits": 3}).execute()
        return 3
    return res.data[0]["credits"]

# -- 4. LANDING & PREVIEW (GİRİŞSİZ EKRAN) --
def landing_page():
    st.markdown("<h1 style='text-align: center; color: #58a6ff;'>⚡ Quantis</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Universal Engineering Problem Solver</h3>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #8b949e;'>Calculus • Physics • Mechanics • Linear Algebra</p>", unsafe_allow_html=True)
    
    st.write("---")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        img_file = st.file_uploader("Try it now: Upload your problem", type=['jpg','png','jpeg'])
        if img_file:
            img = Image.open(img_file)
            st.image(img, use_container_width=True)
    
    with col2:
        if img_file:
            if st.button("✨ Solve with Quantis Engine"):
                with st.spinner("Analyzing..."):
                    # PREVIEW PROMPT: Sadece sonucu ver, adımları gizle.
                    prompt = "Give ONLY the final numerical answer or result of the problem in the image. Do not show steps."
                    response = model.generate_content([prompt, img])
                    
                    st.success("Analysis Complete!")
                    st.markdown(f"### Result: **{response.text}**")
                    
                    st.markdown("<div class='blur-text'>Step 1: Apply the formula... Step 2: Integrate over the volume... Step 3: Solve for the unknown...</div>", unsafe_allow_html=True)
                    
                    st.markdown("""
                        <div class='paywall-card'>
                            <h4>🔒 Full Solution Locked</h4>
                            <p>Sign up to see step-by-step explanations and download the PDF report.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button("🚀 Create Free Account"):
                        st.session_state.show_auth = True
                        st.rerun()
        else:
            st.info("Upload an image on the left to see the magic.")

# -- 5. AUTH EKRANI --
def auth_screen():
    if st.button("← Back"):
        st.session_state.show_auth = False
        st.rerun()
    
    choice = st.radio("Action:", ["Login", "Sign Up"])
    email = st.text_input("Email:")
    password = st.text_input("Password:", type="password")
    
    if st.button("Confirm"):
        try:
            if choice == "Sign Up":
                supabase.auth.sign_up({"email": email, "password": password})
                st.success("Done! Check your email.")
            else:
                res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                st.session_state.user = res.user
                st.session_state.show_auth = False
                st.rerun()
        except Exception as e: st.error(f"Error: {e}")

# -- 6. MAIN APP (GİRİŞ YAPILDIĞINDA) --
def main_app():
    user = st.session_state.user
    credits = get_user_credits(user.id)
    
    with st.sidebar:
        st.title("🌐 Quantis PRO")
        st.write(f"👤 {user.email}")
        st.metric("Credits", f"{credits} ⚡")
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()

    st.title("🚀 Quantis Pro Engine")
    img_file = st.file_uploader("Upload Problem", type=['jpg','png','jpeg'])
    
    if img_file:
        img = Image.open(img_file)
        if st.button("✨ Full Detailed Analysis (1 Credit)"):
            if credits > 0:
                with st.spinner("Detailed Engine Processing..."):
                    response = model.generate_content(["Solve this engineering problem step by step with full explanations.", img])
                    supabase.table("profiles").update({"credits": credits - 1}).eq("id", user.id).execute()
                    st.markdown(response.text)
                    st.rerun()
            else:
                st.error("Out of credits! Upgrade to Pro.")

# -- AKIŞ KONTROLÜ --
if st.session_state.user:
    main_app()
elif st.session_state.get('show_auth'):
    auth_screen()
else:
    landing_page()
