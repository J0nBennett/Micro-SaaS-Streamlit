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
)
import openai

# Set Streamlit page configuration
st.set_page_config(page_title="SaaS", page_icon=":house", layout="centered", initial_sidebar_state="auto", menu_items=None)

# Load environment variables

# Display the main title
st.markdown('# Your SaaS App')

# Initialize the authenticator
if 'authenticator' not in st.session_state:
    try:
        cookie_name = get_config_value("AUTH_COOKIE_NAME", required=True)
        cookie_key = get_config_value("AUTH_COOKIE_KEY", required=True)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    st.session_state['authenticator'] = Authenticate(cookie_name, cookie_key, 60)

# Set default session state values if not already set
if 'authentication_status' not in st.session_state:
    st.session_state['authentication_status'] = None
if 'verified' not in st.session_state:
    st.session_state['verified'] = None

# Handle login if not authenticated and not verified
if not st.session_state['authentication_status'] and not st.session_state['verified']:
    st.session_state['authenticator'].login('Login', 'main')
if 'summarized_text' not in st.session_state:
    st.session_state['summarized_text'] = ''
if 'translation' not in st.session_state:
    st.session_state['translation'] = ''
# Handle actions for verified and authenticated users
if st.session_state['verified'] and st.session_state["authentication_status"]:
    st.session_state['authenticator'].logout('Logout', 'sidebar', key='123')

    try:
        client = openai.Client(api_key=get_config_value("OPENAI_API_KEY", required=True))
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()
    # Check if the user's email is subscribed
    st.session_state['subscribed'] = is_email_subscribed(st.session_state['email'])
    
    # Display subscription status
    if st.session_state.get('subscribed'):
        st.write('You are subscribed!')
    else:
        st.write('You are not subscribed!')

    # Free Tool
    st.write('This tool is free to use!')
    input1 = st.text_area('Enter your text to summarize here:')
    if st.button('Summarize') and input1 and input1 != '':
        response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
                {'role': 'system', 'content': f'You are a helpful assistant.'},
            {"role": "user", "content": f"Provide a summary of the following content: \n ```{input1}```"}
        ],
        temperature=0.0)
        st.session_state['summarized_text'] = response.choices[0].message.content
        
    st.write(st.session_state['summarized_text'])
    # Subscription-only Tool
    st.write('Subscription Only Tool')

    st.write('Special tool only subscribers can use!')
    input2 = st.text_area('Enter your text to translate here:')
    language = st.text_input('Enter the language you want to translate to:')
    if st.button('Translate') and input2 and language and input2 != '' and language != '':
        if not st.session_state.get('subscribed'):
            st.error('Please subscribe to use this tool!')
            try:
                st.link_button('Subscribe', get_config_value('STRIPE_PAYMENT_URL', required=True))
            except RuntimeError as exc:
                st.error(str(exc))
        else:
            response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                    {'role': 'system', 'content': f'You are a helpful assistant.'},
                {"role": "user", "content": f"Translate the text below to the language {language}: \n INPUT: ```{input2}```"}
            ],
            temperature=0.0)
            st.write(response)
            st.session_state['translation'] = response.choices[0].message.content
    
    st.write(st.session_state['translation'])

# Handle actions for users with correct password but unverified email
elif st.session_state["authentication_status"] == True:
    st.error('Your password was correct, but your email has not been not verified. Check your email for a verification link. After you verify your email, refresh this page to login.')
    
    # Add a button to resend the email verification
    if st.session_state.get('email'):
        if st.button(f"Resend Email Verification to {st.session_state['email']}"):
            resend_verification(st.session_state['email'])

# Handle actions for users with incorrect login credentials
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect or does not exist. Reset login credential or register below.')
    render_reset_password_form()
    forgot_password()
    register_new_user()

# Handle actions for new users or users with no authentication status
elif st.session_state["authentication_status"] == None:
    st.warning('New to SaaS app? Register below.')
    render_reset_password_form()
    register_new_user()
