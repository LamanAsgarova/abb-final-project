import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ui.admin_upload import admin_upload_page
from ui.user_dashboard import user_dashboard_page
from ui.localization import get_text
from services.logger_service import setup_logger

logger = setup_logger()

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'az'
    lang = st.session_state.language

    st.set_page_config(page_title=get_text(lang, "page_title"), page_icon="📚", layout="wide")

    try:
        config = {
            "credentials": st.secrets["credentials"],
            "cookie": st.secrets["cookie"]
        }
    except Exception:
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )

    if st.session_state.get("authentication_status"):
        username = st.session_state['username']
        user_role = config['credentials']['usernames'][username]['role']

        with st.sidebar:
            st.write(f"Welcome *{st.session_state['name']}*")
            authenticator.logout(get_text(lang, "logout_button"), 'sidebar')
            st.divider()
            
            selected_language = st.radio(
                label=get_text(lang, "language_select"),
                options=['az', 'en'],
                format_func=lambda x: "Azərbaycanca" if x == 'az' else "English",
                index=0 if lang == 'az' else 1,
                horizontal=True
            )
            if selected_language != st.session_state.language:
                st.session_state.language = selected_language
                st.rerun()

        if user_role == "Admin":
            st.title(get_text(lang, "admin_dashboard_title"))
            st.markdown(get_text(lang, "admin_dashboard_welcome"))
            admin_upload_page(lang)
        else:
            user_dashboard_page(user_role, lang)
    
    else:
        
        st.markdown("""
            <style>
                div[data-testid="stForm"] {
                    background-color: #FFFFFF;
                    /* --- THIS LINE IS CHANGED --- */
                    /* Top padding reduced from 2rem to 1.5rem */
                    padding: 1.5rem 3rem 2.5rem 3rem; 
                    border-radius: 10px;
                    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
                    border: 1px solid #E0E0E0;
                }
            </style>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 1.5, 1])
        with col2:
            st.markdown(f"<h1 style='text-align: center;'>{get_text(lang, 'login_header')}</h1>", unsafe_allow_html=True)
            
            authenticator.login(fields={'Form name': ''})

            if st.session_state.get("authentication_status") is False:
                st.error(get_text(lang, "invalid_credentials"))

if __name__ == "__main__":
    main()