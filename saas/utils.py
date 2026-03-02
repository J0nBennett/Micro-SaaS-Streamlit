from dotenv import load_dotenv
import streamlit as st
import os
import stripe
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import requests
from urllib.parse import quote_plus
load_dotenv()


def get_config_value(key, default=None, required=False):
    value = os.getenv(key)
    if not value:
        try:
            value = st.secrets.get(key)
        except Exception:
            value = None
    if not value:
        value = default
    if required and not value:
        raise RuntimeError(f"Missing required config: {key}")
    return value

def resend_verification(email):
    # Call FastAPI email verification service
    verification_url = get_config_value("VERIFICATION_URL")
    if not verification_url:
        st.error("VERIFICATION_URL is not configured.")
        return
    data = {'email': email}
    response = requests.post(verification_url, json=data)
    if response.status_code != 200:
        st.error(f"Failed to resend verification email: {response.text}")
    else:
        st.success("Verification email resent successfully!")


def is_email_subscribed(email):
    # Initialize the Stripe API with the given key
    stripe.api_key = get_config_value("STRIPE_API_KEY")
    if not stripe.api_key:
        st.error("STRIPE_API_KEY is not configured.")
        return False

    # List customers with the given email address
    customers = stripe.Customer.list(email=email)

    for customer in customers:
        # For each customer, list their subscriptions
        subscriptions = stripe.Subscription.list(customer=customer.id)
        
        # If any active subscription is found, return True
        for subscription in subscriptions:
            if subscription['status'] == 'active':
                return True

    # If no active subscriptions found, return False
    print(f"No active subscriptions found for {email}")
    return False

def reset_password():
    if st.session_state['authentication_status']:
        try:
            if st.session_state['authenticator'].reset_password(st.session_state['username'], 'Reset password'):
                st.success('Password modified successfully')
        except Exception as e:
            st.error(e)

def send_email(subject, message, to_address):
    from_address = get_config_value("YOUR_EMAIL")
    password = get_config_value("YOUR_EMAIL_PASS")
    if not from_address or not password:
        raise RuntimeError("YOUR_EMAIL and YOUR_EMAIL_PASS must be configured to send email.")
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    server = smtplib.SMTP_SSL('mail.privateemail.com', 465)
    server.login(from_address, password)
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()


def forgot_username():
    try:
        username_forgot_username, email_forgot_username = st.session_state['authenticator'].forgot_username('Forgot username')
        if username_forgot_username:
            subject = 'Your SmartBids Username'
            message = f'Your SmartBids username is: {username_forgot_username}'
            send_email(subject, message, email_forgot_username)
            st.success('Username sent securely')
        else:
            st.error('Email not found. Register below.')
    except Exception as e:
        st.error(e)

def forgot_password():
    try:
        reset_email, reset_token, expires_at = st.session_state['authenticator'].forgot_password('Forgot password')
        if reset_email:
            app_base_url = get_config_value("APP_BASE_URL")
            if app_base_url:
                reset_link = (
                    f"{app_base_url}?reset_email={quote_plus(reset_email)}&reset_token={quote_plus(reset_token)}"
                )
                message = (
                    "We received a password reset request for your account.\n\n"
                    f"Use this reset link (expires at {expires_at.isoformat()} UTC):\n{reset_link}\n\n"
                    "If you did not request this change, you can ignore this email."
                )
            else:
                message = (
                    "We received a password reset request for your account.\n\n"
                    f"Open the app and use this token before {expires_at.isoformat()} UTC:\n"
                    f"Email: {reset_email}\nToken: {reset_token}\n\n"
                    "If you did not request this change, you can ignore this email."
                )

            send_email(
                "Password reset request",
                message,
                reset_email,
            )
            st.success('Password reset link sent securely')
        else:
            st.error('Email not found. Register below.')
    except Exception as e:
        st.error(e)


def register_new_user():
    try:
        if st.session_state['authenticator'].register_user('Register user', preauthorization=False):
            st.success('Great! Now please complete registration by confirming your email address. Then login above!')
    except Exception as e:
        st.error(e)


def render_reset_password_form():
    reset_email = st.query_params.get("reset_email")
    reset_token = st.query_params.get("reset_token")
    if not reset_email or not reset_token:
        return

    st.info("Password reset link detected. Set your new password below.")
    with st.form("Set new password"):
        new_password = st.text_input("New password", type="password")
        repeat_password = st.text_input("Repeat new password", type="password")
        submitted = st.form_submit_button("Set password")

    if submitted:
        try:
            if st.session_state["authenticator"].reset_password_with_token(
                reset_email,
                reset_token,
                new_password,
                repeat_password,
            ):
                st.success("Password updated successfully. You can now log in.")
                st.query_params.clear()
        except Exception as e:
            st.error(e)

