import streamlit as st
import requests
from src.config import Config, logger

st.title("Register")


def show_terms_and_conditions():
    terms_content = """
    # Terms and Conditions
    
    ## Data Protection and Privacy Policy
    
    **1. Data Collection**
    
    We collect personal information including email, username, and encrypted passwords for the purpose of account management and service provision.
    
    **2. Data Processing**
    
    Your data is processed according to GDPR requirements, ensuring lawful, fair, and transparent data handling.
    
    **3. User Rights**
    
    Users have the right to:
    - Access their personal data
    - Request correction of inaccurate data
    - Request deletion of their data
    - Object to processing of their data
    - Data portability
    
    **4. Data Security**
    
    We implement appropriate security measures to protect against unauthorized access, alteration, disclosure, or destruction of your personal information.
    
    **5. Cookies and Tracking**
    
    Our application may use cookies for session management and improving user experience.
    
    **6. Contact Information**
    
    For privacy concerns or data requests, contact us at insia.resistance@gmail.com.
    """
    return terms_content


terms_container = st.empty()


def register(email: str, username: str, password: str):
    payload = {"username": username, "password": password, "email": email}
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    response = requests.post(
        f"{Config.BACKEND_URL}/users", data=payload, headers=headers
    )
    if response.status_code == 200:
        logger.debug(f"response : {response.json()}")
        # reroute to login pages
        st.success("Registration successful!")
        st.rerun()
    else:
        st.error("Registration failed!")
        return None


with st.form("register_form"):
    email = st.text_input("Email")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    col1, col2 = st.columns([1, 10])
    with col1:
        terms_accepted = st.checkbox("", key="terms_checkbox")
    with col2:
        terms_link = st.markdown("I accept the [Terms and Conditions](#)")
        if st.session_state.get("show_terms", False):
            terms_container.markdown(show_terms_and_conditions())

    # Make the terms link clickable
    if terms_link:
        st.session_state["show_terms"] = not st.session_state.get("show_terms", False)

    submitted = st.form_submit_button("Register")

    if submitted:
        if not terms_accepted:
            st.error("You must accept the Terms and Conditions to register.")
        else:
            register(email, username, password)

if st.button("View Terms and Conditions"):
    st.session_state["show_terms"] = True
    terms_container.markdown(show_terms_and_conditions())
# link to login pages if already have an account
st.write("Already have an account? [Login](content/0_login.py)")
if st.session_state.get("show_terms", False) and st.button("Close Terms"):
    st.session_state["show_terms"] = False
    terms_container.empty()
