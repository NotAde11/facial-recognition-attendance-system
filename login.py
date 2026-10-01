import streamlit as st
import json
import bcrypt
import time
import os

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="PresenceID", page_icon="logo_icon.png", layout="wide")

# --- 2. DATABASE HELPERS ---
def load_users():
    if not os.path.exists("users.json"):
        with open("users.json", "w") as f:
            json.dump({}, f)
    with open("users.json", "r") as f:
        return json.load(f)

def save_user(username, password):
    users = load_users()
    if username in users:
        return False
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users[username] = hashed
    with open("users.json", "w") as f:
        json.dump(users, f, indent=4)
    return True

def verify_login(username, password):
    users = load_users()
    if username in users:
        stored_hashed_password = users[username].encode('utf-8')
        if bcrypt.checkpw(password.encode('utf-8'), stored_hashed_password):
            return True
    return False

# --- 3. ALL CSS STYLING ---
st.markdown("""
    <style>
    /* Force Wide Layout & Kill Scroll */
    .block-container {
        max-width: 98% !important;
        padding-top: 3rem !important;
        padding-bottom: 0rem !important;
        height: 100vh;
        overflow: hidden !important;
    }
    
    [data-testid="stAppViewContainer"] {
        overflow: hidden !important;
    }

    /* Black Container Box */
    [data-testid="stVerticalBlock"] > div:has(div.stForm) {
        background-color: #000000 !important;
        padding: 50px !important;
        border-radius: 20px;
        border: 2px solid #4A90E2;
    }

    /* PresenceID Title Styling */
    .title-text {
        font-family: 'Algerian', 'Stencil', 'Fantasy', serif !important;
        background: linear-gradient(45deg, #4A90E2, #FFFFFF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 68px !important;
        font-weight: 700 !important;
        text-align: center;
        white-space: nowrap;
        text-shadow: 2px 2px 8px rgba(0,0,0,0.2);
    }

    /* Input Styling */
    input {
        font-family: 'Inter', sans-serif !important;
    }

    .faint-footer {
        text-align: center;
        color: rgba(74, 144, 226, 0.4); /* Faint blue using RGBA */
        font-size: 13px;
        letter-spacing: 1px;
        margin-top: 20px;
    }

    /* Hide Sidebar Nav */
    [data-testid="stSidebarNav"] { display: none; }
    </style>
""", unsafe_allow_html=True)

# --- 4. APP LOGIC & LAYOUT ---
if 'auth_mode' not in st.session_state:
    st.session_state.auth_mode = 'login'

# Main split: 65% for Form, 35% for Branding
left_col, right_col = st.columns([65, 35], gap="large")

with left_col:
    if st.session_state.auth_mode == 'login':
        st.markdown("<h3 style='text-align: center; color: white;'>Admin Login</h3>", unsafe_allow_html=True)
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Sign In", width='stretch')

            if submit:
                if verify_login(username, password):
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success("Login Successful!")
                    time.sleep(1)
                    st.switch_page("pages/dashboard.py")
                else:
                    st.error("Invalid username or password.")
        
        if st.button("New here? Create an account", width='stretch'):
            st.session_state.auth_mode = 'signup'
            st.rerun()

    else:
        st.subheader("Create Account")
        with st.form("signup_form"):
            new_user = st.text_input("Choose Username")
            new_pass = st.text_input("Password", type="password")
            conf_pass = st.text_input("Confirm Password", type="password")
            submit_signup = st.form_submit_button("Sign Up", width='stretch')

            if submit_signup:
                if not new_user or not new_pass:
                    st.warning("Please fill all fields.")
                elif new_pass != conf_pass:
                    st.error("Passwords do not match.")
                else:
                    if save_user(new_user, new_pass):
                        st.success("Account created!")
                        time.sleep(1.5)
                        st.session_state.auth_mode = 'login'
                        st.rerun()
                    else:
                        st.error("Username already exists.")

        if st.button("Already have an account? Login", width='stretch'):
            st.session_state.auth_mode = 'login'
            st.rerun()

with right_col:
    # Branding
    st.markdown('<br><br><p class="title-text">PresenceID</p>', unsafe_allow_html=True)
        
    col1, col2, col3 = st.columns([1, 2, 1]) # Adjust ratios as needed

    with col2:
        st.image("logo_icon.png", width=200)

# Footer
st.markdown('<p class="faint-footer">CIS Final Year Project - 2026</p>', unsafe_allow_html=True)