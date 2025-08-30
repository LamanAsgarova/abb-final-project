import streamlit as st
import os
import json
from datetime import datetime

from document_processing.text_extractor import extract_text
from document_processing.metadata_extractor import extract_metadata
from services.index_manager import add_document_to_index, remove_document_from_index
from services.indexing_service import process_and_embed_document
from .localization import get_text
from services.logger_service import setup_logger

logger = setup_logger()

UPLOAD_FOLDER = "data/raw_documents/"
PROCESSED_FOLDER = "data/processed_documents/"
METADATA_FOLDER = "data/metadata/"

def get_all_files():
    """Gets a list of all raw files from the data directory."""
    files_info = []
    file_types = ["pdf", "word", "excel", "pptx"]
    for file_type in file_types:
        folder_path = os.path.join(UPLOAD_FOLDER, file_type)
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    files_info.append({
                        'name': filename, 'type': file_type, 'path': file_path,
                        'size': os.path.getsize(file_path),
                        'modified': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
                    })
    return sorted(files_info, key=lambda x: x['modified'], reverse=True)

def delete_file(file_path, filename, lang):
    """Deletes a file and removes it from the metadata index, with logging."""
    admin_user = st.session_state.get("role", "Unknown Admin")
    try:
        os.remove(file_path)
        remove_document_from_index(filename)
        logger.warning(f"User '{admin_user}' DELETED file: '{filename}'.")
        st.success(f"'{filename}' " + get_text(lang, "delete_success"))
        return True
    except Exception as e:
        logger.error(f"Failed to delete file '{filename}' by user '{admin_user}'. Error: {e}")
        st.error(f"Error deleting '{filename}': {str(e)}")
        return False


def admin_upload_page(lang):
    # main entry point for the admin page
    tab1_title = get_text(lang, "upload_tab")
    tab2_title = get_text(lang, "manage_tab")
    tab3_title = get_text(lang, "bulk_ops_tab")
    
    tab1, tab2, tab3 = st.tabs([f"📤 {tab1_title}", f"📁 {tab2_title}", f"🔧 {tab3_title}"])
    
    with tab1:
        upload_section(lang)
    with tab2:
        view_documents_section(lang)
    with tab3:
        bulk_operations_section(lang)


def upload_section(lang):
    st.subheader(get_text(lang, "upload_header"))
    
    uploaded_files = st.file_uploader(
        get_text(lang, "uploader_label"), type=["pdf", "docx", "xlsx", "pptx"],
        accept_multiple_files=True
    )
    if uploaded_files:
        teams = ["Unassigned", "Data Tribe", "Mobile Application Tribe", "Risk Tribe", "Card Tribe"]
        assigned_team = st.selectbox(get_text(lang, "assign_team_label"), teams)
        tags_input = st.text_input(get_text(lang, "tags_label"), placeholder=get_text(lang, "tags_placeholder"))
        
        if st.button(get_text(lang, "upload_process_button"), type="primary", use_container_width=True):
            tags_list = [tag.strip() for tag in tags_input.split(',') if tag.strip()]
            admin_user = st.session_state.get("role", "Unknown Admin")
            
            total_success, total_error = 0, 0
            for uploaded_file in uploaded_files:
                with st.spinner(f"Processing '{uploaded_file.name}'..."):
                    try:
                        # standard processing steps:
                        file_type = uploaded_file.name.split('.')[-1].lower()
                        folder_map = {"pdf": "pdf", "docx": "word", "xlsx": "excel", "pptx": "pptx"}
                        folder = folder_map.get(file_type)
                        file_path = os.path.join(UPLOAD_FOLDER, folder, uploaded_file.name)
                        with open(file_path, "wb") as f: f.write(uploaded_file.getbuffer())
                        text_content = extract_text(file_path)
                        base_filename = os.path.splitext(uploaded_file.name)[0]
                        processed_file_path = os.path.join(PROCESSED_FOLDER, f"{base_filename}.txt")
                        with open(processed_file_path, "w", encoding="utf-8") as f: f.write(text_content)
                        metadata = extract_metadata(file_path)
                        metadata['team'], metadata['tags'] = assigned_team, tags_list
                        metadata_file_path = os.path.join(METADATA_FOLDER, f"{base_filename}.json")
                        with open(metadata_file_path, "w", encoding="utf-8") as f: json.dump(metadata, f, indent=4)
                        add_document_to_index(metadata)
                        logger.info(f"User '{admin_user}' UPLOADED file '{uploaded_file.name}'.")

                        # Automated Embedding with Detailed Feedback
                        success, message = process_and_embed_document(uploaded_file.name)
                        
                        if success:
                            st.write(f"✅ '{uploaded_file.name}' - " + get_text(lang, "index_success"))
                            total_success += 1
                        else:
                            st.error(f"'{uploaded_file.name}' - " + get_text(lang, "index_fail") + f": {message}")
                            total_error += 1
                        
                    except Exception as e:
                        logger.error(f"Critical error during upload of '{uploaded_file.name}': {e}")
                        st.error(f"Error processing {uploaded_file.name}: {e}")
                        total_error += 1
            
            st.divider()
            if total_success > 0: st.success(f"Finished processing. Successful: {total_success}, Failed: {total_error}.")
            else: st.error(f"Finished processing. All {total_error} file(s) failed.")


def view_documents_section(lang):
    """UI for viewing, filtering, and managing existing documents."""
    st.subheader(get_text(lang, "library_header"))
    files = get_all_files()
    if not files:
        st.info(get_text(lang, "no_docs_uploaded"))
        return
    
    col1, col2 = st.columns(2)
    with col1:
        search_term = st.text_input(get_text(lang, "search_files_label"))
    with col2:
        all_option = get_text(lang, "all_files_option")
        file_types = [all_option] + sorted(list(set([f['type'] for f in files])))
        selected_type = st.selectbox(get_text(lang, "filter_type_label"), file_types)
        
    if selected_type != all_option: files = [f for f in files if f['type'] == selected_type]
    if search_term: files = [f for f in files if search_term.lower() in f['name'].lower()]

    st.write(f"{len(files)} {get_text(lang, 'found_docs_text')}")
    st.divider()

    for i, file_info in enumerate(files):
        col1, col2, col3, col4, col5 = st.columns([4, 1, 2, 1, 1.2])
        with col1:
            icon = {"pdf": "📄", "word": "📝", "excel": "📊", "pptx": "📋"}.get(file_info['type'], "📄")
            st.write(f"{icon} **{file_info['name']}**")
        with col2: st.write(file_info['type'].upper())
        with col3: st.caption(file_info['modified'])
        with col4:
            size_mb = file_info['size'] / (1024 * 1024)
            st.caption(f"{size_mb:.2f} MB")
        with col5:
            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                with open(file_info['path'], "rb") as file_data:
                    st.download_button(label="⬇️", data=file_data, file_name=file_info['name'], key=f"dl_{i}")
            with btn_col2:
                if st.button("🗑️", key=f"del_{i}", help="Delete file"):
                    st.session_state.confirm_delete_file = file_info['name']
                    st.rerun()

        if st.session_state.get('confirm_delete_file') == file_info['name']:
            with st.container():
                st.warning(f"**{get_text(lang, 'delete_button_confirm')}** `{file_info['name']}`")
                c1, c2, _ = st.columns([1, 1, 4]) 
                with c1:
                    if st.button(get_text(lang, "confirm_delete_single_button"), key=f"confirm_del_{i}", type="primary"):
                        if delete_file(file_info['path'], file_info['name'], lang):
                            del st.session_state.confirm_delete_file
                            st.rerun()
                with c2:
                    if st.button(get_text(lang, "cancel_button"), key=f"cancel_del_{i}"):
                        del st.session_state.confirm_delete_file
                        st.rerun()
        st.divider()

def bulk_operations_section(lang):
    """UI for performing bulk actions."""
    st.subheader(get_text(lang, "bulk_ops_header"))
    files = get_all_files()
    if not files:
        st.info(get_text(lang, "no_docs_for_bulk"))
        return
    
    col1, col2 = st.columns(2)
    with col1:
        st.error(get_text(lang, "danger_zone"))
        if st.button(get_text(lang, "delete_all_button")):
            st.session_state.confirm_delete_all = True
            if 'confirm_delete_file' in st.session_state:
                del st.session_state.confirm_delete_file
            st.rerun()
            
        if st.session_state.get('confirm_delete_all', False):
            st.warning(get_text(lang, "delete_button_confirm"))
            c1, c2, _ = st.columns([2, 2, 2.5])
            with c1:
                if st.button(get_text(lang, "confirm_delete_all_button"), type="primary"):
                    admin_user = st.session_state.get("role", "Unknown Admin")
                    logger.critical(f"User '{admin_user}' initiated DELETE ALL DOCUMENTS operation.")
                    with st.spinner("Deleting all documents..."):
                        for file_info in files: 
                            delete_file(file_info['path'], file_info['name'], lang)
                    del st.session_state.confirm_delete_all
                    st.rerun()
            with c2:
                if st.button(get_text(lang, "cancel_button")):
                    del st.session_state.confirm_delete_all
                    st.rerun()
    with col2:
        st.info(get_text(lang, "storage_statistics"))
        total_docs = len(files)
        total_size_mb = sum(f['size'] for f in files) / (1024 * 1024)
        st.metric(label=get_text(lang, "total_documents"), value=total_docs)
        st.metric(label=get_text(lang, "total_storage_used"), value=f"{total_size_mb:.2f} MB")