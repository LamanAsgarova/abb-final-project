import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import sys
import os
from collections.abc import Mapping

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from ui.admin_upload import admin_upload_page
from ui.user_dashboard import user_dashboard_page
from ui.localization import get_text
from services.logger_service import setup_logger

logger = setup_logger()

def _to_plain_dict(x):
    """Recursively convert Mapping/list/tuple from Streamlit Secrets to plain Python containers."""
    if isinstance(x, Mapping):
        return {k: _to_plain_dict(v) for k, v in x.items()}
    if isinstance(x, list):
        return [_to_plain_dict(v) for v in x]
    if isinstance(x, tuple):
        return tuple(_to_plain_dict(v) for v in x)
    return x

def main():
    if 'language' not in st.session_state:
        st.session_state.language = 'az'
    lang = st.session_state.language

    st.set_page_config(page_title=get_text(lang, "page_title"), page_icon="📚", layout="wide")

    # Load config from Streamlit secrets (preferred) or fallback to local YAML.
    try:
        raw_config = {
            "credentials": st.secrets["credentials"],
            "cookie": st.secrets["cookie"],
            "preauthorized": st.secrets.get("preauthorized", {}),
        }
        config = _to_plain_dict(raw_config)  # make it mutable for streamlit_authenticator
    except Exception as e:
        logger.warning("Falling back to config.yaml due to: %s", e)
        with open('config.yaml') as file:
            config = yaml.load(file, Loader=SafeLoader)

    # Build the authenticator using kwargs to avoid positional mixups.
    authenticator = stauth.Authenticate(
        credentials=config["credentials"],
        cookie_name=config.get("cookie", {}).get("name", "auth"),
        key=config.get("cookie", {}).get("key", "some_random_key"),
        cookie_expiry_days=config.get("cookie", {}).get("expiry_days", 30),
        preauthorized=config.get("preauthorized", {}).get("emails", []),
        auto_hash=False,  # set True only if you need to generate hashes locally
    )

    if st.session_state.get("authentication_status"):
        username = st.session_state['username']
        # Safely get the role; default to "User"
        user_role = config["credentials"]["usernames"].get(username, {}).get("role", "User")

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
        # Login screen
        st.markdown("""
            <style>
                div[data-testid="stForm"] {
                    background-color: #FFFFFF;
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

            # This will set st.session_state['authentication_status'] / ['username'] / ['name']
            authenticator.login(fields={'Form name': ''})

            if st.session_state.get("authentication_status") is False:
                st.error(get_text(lang, "invalid_credentials"))

if __name__ == "__main__":
    main()