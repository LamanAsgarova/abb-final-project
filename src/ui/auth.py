import streamlit as st
from .localization import get_text
from services.database_service import verify_user
from services.logger_service import setup_logger

logger = setup_logger()

def login(username, role):
    st.session_state.logged_in = True
    st.session_state.role = role
    st.rerun()

def login_page(lang):
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1>🔐 {get_text(lang, "login_header")}</h1>
            <p>{get_text(lang, "login_subheader")}</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    username = st.text_input(get_text(lang, "username_label"))
    password = st.text_input(get_text(lang, "password_label"), type="password")
    
    if st.button(get_text(lang, "login_button"), type="primary", use_container_width=True):
        logger.info(f"Login attempt for user: '{username}'")
        user_role = verify_user(username, password)
        if user_role:
            logger.info(f"User '{username}' logged in successfully as role '{user_role}'.")
            login(username, user_role)
        else:
            logger.warning(f"Failed login attempt for user: '{username}'.")
            st.error(get_text(lang, "invalid_credentials"))