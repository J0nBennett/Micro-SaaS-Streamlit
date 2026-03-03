import streamlit as st
from dotenv import load_dotenv
load_dotenv('.env')
from mongo_auth import Authenticate
from utils import (
    forgot_password,
    get_config_value,
    is_email_subscribed,
    register_new_user,
    render_reset_password_form,
    resend_verification,
    save_activity,
    get_recent_activity,
)
import openai

# Set Streamlit page configuration
st.set_page_config(page_title="UltraSaaS", page_icon="✨", layout="centered")

# Initialize session state immediately
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'verified' not in st.session_state:
    st.session_state['verified'] = None
if 'summarized_text' not in st.session_state:
    st.session_state['summarized_text'] = ''
if 'translation' not in st.session_state:
    st.session_state['translation'] = ''
if 'name' not in st.session_state:
    st.session_state['name'] = None
if 'email' not in st.session_state:
    st.session_state['email'] = None

# Custom CSS for Premium Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap');

    html, body, [class*="st-"] {
        font-family: 'Inter', sans-serif;
        color: white;
    }

    /* Background Gradient */
    .stApp {
        background: radial-gradient(circle at top right, #1a1a2e, #16213e, #0f3460);
    }

    /* Premium Header */
    .hero-container {
        padding: 4rem 2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }

    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        background: linear-gradient(90deg, #e94560, #a033ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #ffffff;
        opacity: 0.8;
        margin-bottom: 2rem;
    }

    /* Button Styling */
    .stButton>button {
        background: linear-gradient(90deg, #e94560, #a033ff) !important;
        color: white !important;
        border: none !important;
        padding: 0.75rem 2rem !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        transition: transform 0.2s, box-shadow 0.2s !important;
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(233, 69, 96, 0.3);
    }

    /* Tool Card Styling */
    .tool-card {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(5px);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin-bottom: 2rem;
    }

    .tool-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #e94560;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(233, 69, 96, 0.3);
        padding-bottom: 0.5rem;
    }

    /* Better contrast in inputs - DARK NUCLEAR VERSION */
    div[data-baseweb="input"], div[data-baseweb="input"] > div {
        background-color: #1b1b1b !important;
        color: white !important;
    }
    
    div[data-baseweb="input"] input {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    .stTextArea textarea {
        background-color: #1b1b1b !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
    }

    /* Primary Button Styling - ABSOLUTE NUCLEAR */
    .stButton button, button[data-testid*="stBaseButton"], button[kind="primary"], button[kind="secondary"] {
        background-color: #e94560 !important;
        background-image: linear-gradient(90deg, #e94560, #a033ff) !important;
        color: #ffffff !important;
        border: none !important;
        font-weight: 700 !important;
        min-height: 45px !important;
    }
    
    .stButton button *, button[data-testid*="stBaseButton"] *, button[kind="primary"] *, button[kind="secondary"] * {
        color: #ffffff !important;
    }

    /* Labels visibility */
    label p {
        color: #ffffff !important;
        font-weight: 600 !important;
    }

    /* Sidebar Nuclear Fix */
    [data-testid="stSidebar"] {
        background-color: #000000 !important;
    }

    [data-testid="stSidebarNav"] {
        background-color: transparent !important;
    }

    [data-testid="stSidebarNav"] ul li a {
        color: #ffffff !important;
        background-color: transparent !important;
    }
    
    [data-testid="stSidebarNav"] ul li a[aria-current="page"] {
        background: linear-gradient(90deg, rgba(233, 69, 96, 0.6), rgba(160, 51, 255, 0.6)) !important;
        border-left: 5px solid #e94560 !important;
    }

    [data-testid="stSidebarNav"] ul li a span {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize the authenticator if needed
if 'authenticator' not in st.session_state:
    try:
        from utils import get_config_value
        from mongo_auth.authenticate import Authenticate
        cookie_name = get_config_value("AUTH_COOKIE_NAME", required=True)
        cookie_key = get_config_value("AUTH_COOKIE_KEY", required=True)
        st.session_state['authenticator'] = Authenticate(cookie_name, cookie_key, 60)
    except Exception as exc:
        st.error(f"Configuration error: {exc}")
        st.stop()

# MAIN NAVIGATION LOGIC
if not st.session_state.get('authentication_status'):
    # --- LANDING PAGE / LOGIN ---
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">UltraSaaS Intelligence</div>
        <div class="hero-subtitle">The ultimate AI-powered productivity suite for modern creators. Summarize, translate, and automate with style.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Toggle between Login and Register
    auth_mode = st.radio("Choose action:", ["Login", "Register"], horizontal=True, label_visibility="collapsed")
    
    if auth_mode == "Login":
        st.session_state['authenticator'].login('Login', 'main')
    else:
        from utils import register_new_user
        register_new_user()

    # Handle error states from Authenticate
    if st.session_state["authentication_status"] == False:
        st.error('Username/password is incorrect.')
        from utils import forgot_password
        forgot_password()
    elif st.session_state["authentication_status"] == True and not st.session_state.get('verified'):
         st.error('Please verify your email correctly.')
         from utils import resend_verification
         if st.session_state.get('email'):
             if st.button(f"Resend Verification to {st.session_state['email']}"):
                 resend_verification(st.session_state['email'])

else:
    # --- DASHBOARD (LOGGED IN) ---
    st.markdown('### 🚀 Dashboard')
    
    # --- USER STATUS & TIER ---
    st.sidebar.markdown('---')
    st.sidebar.markdown('### 💎 Current Tier')
    if st.session_state.get('subscribed'):
        st.sidebar.success('🌟 PREMIUM SUBSCRIBER')
    elif st.session_state.get('verified'):
        st.sidebar.info('✅ VERIFIED MEMBER')
    else:
        st.sidebar.warning('🆓 FREE TIER')

    st.session_state['authenticator'].logout('Sign Out', 'sidebar')
    st.sidebar.markdown('---')

    try:
        client = openai.Client(api_key=get_config_value("OPENAI_API_KEY", required=True))
    except (RuntimeError, Exception) as exc:
        st.error(f"OpenAI Initialization Error: {exc}")
        st.stop()
    
    # Check subscription
    st.session_state['subscribed'] = is_email_subscribed(st.session_state['email'])

    # --- SUMMARIZER TOOL ---
    st.markdown('<div class="tool-card"><div class="tool-header">✨ AI Text Summarizer</div>', unsafe_allow_html=True)
    st.write('Distill any content into its core essence instantly.')
    input1 = st.text_area('Input text:', height=150, placeholder="Paste your article or notes here...", key="sum_in")
    if st.button('Generate Summary') and input1:
        with st.spinner('Summarizing...'):
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {'role': 'system', 'content': 'You are a professional editor.'},
                    {"role": "user", "content": f"Provide a brief summary: \n ```{input1}```"}
                ],
                temperature=0.0)
            st.session_state['summarized_text'] = response.choices[0].message.content
            save_activity(st.session_state['email'], 'Summarization', input1, st.session_state['summarized_text'])
    
    if st.session_state['summarized_text']:
        st.info(st.session_state['summarized_text'])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- TRANSLATOR TOOL ---
    st.markdown('<div class="tool-card"><div class="tool-header">🌐 Global Translator</div>', unsafe_allow_html=True)
    st.write('Professional-grade translation for any language duo.')
    
    col1, col2 = st.columns(2)
    with col1:
        input2 = st.text_area('Text to translate:', height=150, key="trans_in")
    with col2:
        language = st.text_input('Target Language:', placeholder="e.g. Spanish, Japanese", key="lang_in")
    
    if st.button('Start Translation') and input2 and language:
        if not st.session_state.get('subscribed'):
            st.error('This is a Premium feature. Please subscribe to unlock.')
            try:
                st.link_button('Upgrade to Premium', get_config_value('STRIPE_PAYMENT_URL', required=True))
            except Exception as exc:
                st.error(f"Link error: {exc}")
        else:
            with st.spinner('Translating...'):
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {'role': 'system', 'content': 'You are a professional translator.'},
                        {"role": "user", "content": f"Translate to {language}: \n ```{input2}```"}
                    ],
                    temperature=0.0)
                st.session_state['translation'] = response.choices[0].message.content
                save_activity(st.session_state['email'], f'Translation ({language})', input2, st.session_state['translation'])
    
    if st.session_state['translation']:
        st.success(st.session_state['translation'])
    st.markdown('</div>', unsafe_allow_html=True)

    # --- RECENT ACTIVITY ---
    st.markdown('### 🕒 Recent Activity')
    history = get_recent_activity(st.session_state['email'])
    if not history:
        st.write('Your latest generations will appear here.')
    for act in history:
        with st.expander(f"{act['type']} - {act['timestamp'].strftime('%Y-%m-%d %H:%M')}"):
            st.write(f"**Input:** {act['input']}")
            st.write(f"**Result:** {act['output']}")
