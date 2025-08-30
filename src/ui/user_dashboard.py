import streamlit as st
from streamlit.components.v1 import html
import os
import re
import json

from services.search import semantic_search
from services.qa_service import get_answer_from_llm
from services.insight_service import extract_insights
from services.access_control import get_accessible_documents
from services.charting_service import create_chart
from .localization import get_text

def user_dashboard_page(user_role, lang):
    st.sidebar.title(get_text(lang, "nav_header"))
    
    # navigation with 3 options
    page_options = { 
        "az": ("🤖 Söhbət", "📚 Fayl Kitabxanası", "🔬 Fayl Analizi"), 
        "en": ("🤖 Chatbot", "📚 Document Library", "🔬 Document Analysis") 
    }
    
    if st.session_state.get("navigate_to_library"):
        st.session_state.page_selection = page_options[lang][1]
        del st.session_state.navigate_to_library
    
    page = st.sidebar.radio(get_text(lang, "nav_header"), page_options[lang], key="page_selection", label_visibility="collapsed")

    # routing to the selected page
    if page == page_options[lang][0]:
        if st.sidebar.button(get_text(lang, "new_chat_button")):
            st.session_state.messages = []
            st.rerun()
        chatbot_page(user_role, lang)
    elif page == page_options[lang][1]:
        library_page(user_role, lang)
    elif page == page_options[lang][2]:
        analysis_page(lang)

def auto_scroll():
    html("""<script>window.scrollTo(0, document.body.scrollHeight);</script>""", height=0)


def chatbot_page(user_role, lang):
    """The final chatbot interface with all features integrated."""
    st.markdown(f"<h1 style='text-align: center;'>{get_text(lang, 'chatbot_welcome_message')}</h1>", unsafe_allow_html=True)
    st.divider()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    # display chat history
    for idx, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.markdown(message["content"])
                continue

            assistant_content = message.get("content", {})
            answer_text = assistant_content.get("answer_text", "")
            chart_info = assistant_content.get("chart_info")
            source_filepath = assistant_content.get("source_filepath")

            st.markdown(answer_text)
            
            # display visualize button if a chart is possible
            if chart_info and source_filepath:
                if st.button("📊 Vizualizasiya et", key=f"viz_{idx}"):
                    # Call the corrected function with 3 arguments
                    fig = create_chart(source_filepath, chart_info, lang)
                    if fig:
                        st.session_state.messages[idx]["chart_figure"] = fig
                    else:
                        st.session_state.messages[idx]["chart_figure"] = "error"
                    st.rerun()

            # display the generated chart or an error
            if message.get("chart_figure") and message.get("chart_figure") != "error":
                st.plotly_chart(message["chart_figure"], use_container_width=True)
            elif message.get("chart_figure") == "error":
                st.error("Qrafik qurmaq üçün sənəddəki məlumatda problem yarandı.")
    
    # user input and response generation
    if prompt := st.chat_input(get_text(lang, "search_placeholder")):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
        last_prompt = st.session_state.messages[-1]["content"]
        with st.chat_message("assistant", avatar="🤖"):
            with st.spinner(get_text(lang, "generating_answer_spinner")):
                search_results = semantic_search(query=last_prompt, user_role=user_role, top_k=1)
                source_filepath_for_llm = search_results[0]['original_filepath'] if search_results else None
                context_with_sources = [f"[Source: {item['original_filename']}]\n{item['chunk_text']}" for item in search_results] if search_results else []
                json_response_str = get_answer_from_llm(query=last_prompt, context_chunks=context_with_sources, chat_history=[])
                
                try:
                    response_data = json.loads(json_response_str)
                    response_data["source_filepath"] = source_filepath_for_llm
                    st.session_state.messages.append({"role": "assistant", "content": response_data})
                except json.JSONDecodeError:
                    err_msg = {"answer_text": "AI returned an invalid format.", "chart_info": None}
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
                st.rerun()

    if st.session_state.messages: auto_scroll()


def library_page(user_role, lang):
    """The document library with a search bar and consolidated action buttons."""
    st.subheader(get_text(lang, "library_header"))
    all_user_documents = get_accessible_documents(user_role)

    # hand search term passed from chat or entered by user
    search_term_key = "search_term_from_library"
    if "search_from_chat" in st.session_state:
        st.session_state[search_term_key] = st.session_state.search_from_chat
        del st.session_state.search_from_chat
    
    search_term = st.text_input(get_text(lang, "search_files_label"), key=search_term_key)

    if search_term:
        filtered_documents = [doc for doc in all_user_documents if search_term.lower() in doc.get('file_name', '').lower()]
    else:
        filtered_documents = all_user_documents

    if not filtered_documents:
        st.info(get_text(lang, "no_docs_uploaded"))
        return

    # Initialize session state for displaying insights
    if 'active_doc_info' not in st.session_state:
        st.session_state.active_doc_info = None

    for doc in filtered_documents:
        with st.container(border=True):
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                st.markdown(f"**📄 {doc.get('title', doc.get('file_name'))}**")
                st.caption(f"Team: {doc.get('team', 'N/A')} | Category: {doc.get('auto_category', 'N/A')}")
            
            filepath = doc.get('file_path')
            if os.path.exists(filepath):
                with col2:
                    with open(filepath, "rb") as file:
                        st.download_button("📥 Endir", file, doc.get('file_name'), key=f"dl_{doc.get('file_name')}")
                with col3:
                    if st.button("💡 Çıxarış Et", key=f"ins_{doc.get('file_name')}"):
                        with st.spinner("Mühüm məlumatlar çıxarılır..."):
                            insights = extract_insights(filepath, lang)
                            st.session_state.active_doc_info = {
                                "file": doc.get('file_name'),
                                "content": insights
                            }
                        st.rerun()

            if st.session_state.active_doc_info and st.session_state.active_doc_info["file"] == doc.get('file_name'):
                info_content = st.session_state.active_doc_info["content"]
                st.success("Mühüm Çıxarışlar:")
                if "Error:" in info_content:
                    st.error(info_content)
                else:
                    st.info(info_content)



def analysis_page(lang):
    """A dedicated page for one-time analysis of a user-uploaded document."""
    st.subheader(get_text(lang, "analysis_header"))
    st.info(get_text(lang, "analysis_info"))

    TEMP_DIR = "data/temp"
    os.makedirs(TEMP_DIR, exist_ok=True)

    uploaded_file = st.file_uploader(
        get_text(lang, "uploader_label"),
        type=["pdf", "docx", "xlsx", "pptx"]
    )

    analysis_result = None
    if uploaded_file:
        temp_path = os.path.join(TEMP_DIR, uploaded_file.name)
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        st.markdown("---")
        
        if st.button("💡 " + get_text(lang, "insights_button")):
            with st.spinner("Mühüm məlumatlar çıxarılır..."):
                analysis_result = extract_insights(temp_path, lang)
        
        if os.path.exists(temp_path):
            os.remove(temp_path)
    
    if analysis_result:
        st.markdown("---")
        st.subheader(get_text(lang, "analysis_result_header"))
        if "Error:" in analysis_result:
            st.error(analysis_result)
        else:
            st.success(analysis_result)