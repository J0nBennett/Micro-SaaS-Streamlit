import streamlit as st
import yaml
from pymongo import MongoClient
from dotenv import load_dotenv
from mongo_auth import Authenticate
import os
import stripe
load_dotenv(".env")

st.set_page_config(page_title="UltraSaaS Account", page_icon="👤", layout="centered")

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

    /* Better contrast in inputs - DARK NUCLEAR VERSION */
    div[data-baseweb="input"], div[data-baseweb="input"] > div {
        background-color: #1b1b1b !important;
        color: white !important;
    }
    
    div[data-baseweb="input"] input {
        color: white !important;
        -webkit-text-fill-color: white !important;
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

st.title('Account Settings')
stripe.api_key = os.getenv("STRIPE_API_KEY")

def update_user_details():
    if authentication_status:
        try:
            if st.session_state['authenticator'].update_user_details(username, 'Update user details'):
                st.success('Entries updated successfully')
        except Exception as e:
            st.error(e)
def reset_password():
    if authentication_status:
        try:
            if st.session_state['authenticator'].reset_password(username, 'Reset password'):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)   

name, authentication_status, username = st.session_state['authenticator'].login('Login', 'main')

# Define function to cancel subscriptions based on email
def cancel_subscriptions(email):
    try:
        # List customers by email
        customers = stripe.Customer.list(email=email, limit=100)

        # If no customers found, return a message
        if len(customers.data) == 0:
            return "No customer found with this email."

        # Iterate over customers (though typically there should only be one)
        for customer in customers.data:
            # List all subscriptions for the customer ID
            subscriptions = stripe.Subscription.list(customer=customer.id, limit=100)

            # Cancel all subscriptions for the customer ID
            for subscription in subscriptions:
                stripe.Subscription.delete(subscription.id)
        
        return f"All subscriptions for {email} have been canceled."
    except Exception as e:
        return str(e)


# Initialize session state for account management
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None

if 'authenticator' not in st.session_state:
    try:
        from utils import get_config_value
        from mongo_auth.authenticate import Authenticate
        cookie_name = get_config_value("AUTH_COOKIE_NAME", required=True)
        cookie_key = get_config_value("AUTH_COOKIE_KEY", required=True)
        st.session_state['authenticator'] = Authenticate(cookie_name, cookie_key, 60)
    except Exception:
        st.warning("Authentication system not fully initialized. Please go to Home first.")
        st.stop()

if st.session_state["authentication_status"]:
    update_user_details()
    reset_password()
    if st.session_state['verified'] and st.session_state["authentication_status"]:
        st.session_state['authenticator'].logout('Logout', 'sidebar', key='123')
    if st.session_state.get('subscribed'):
        with st.expander('Manage subscription'):
            if st.button('Cancel subscription'):
                response = cancel_subscriptions(st.session_state.get('email'))
                st.success(response)


else:
    st.write('You are not logged in')
