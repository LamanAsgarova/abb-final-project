import os
import json
import time
import numpy as np
import faiss
import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from src.document_processing.chunker import chunk_text
from services.logger_service import setup_logger
from .index_manager import load_index as load_metadata_index

logger = setup_logger()

VECTOR_STORE_PATH = "data/vector_store.json"
FAISS_INDEX_PATH = "data/faiss_index.idx"
PROCESSED_TEXT_DIR = "data/processed_documents/"
EMBEDDING_MODEL = "models/embedding-001"
BATCH_SIZE = 50

def update_vector_store(new_data):
    if os.path.exists(VECTOR_STORE_PATH) and os.path.getsize(VECTOR_STORE_PATH) > 0:
        with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
            vector_store = json.load(f)
    else:
        vector_store = []
    vector_store.extend(new_data)
    with open(VECTOR_STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(vector_store, f)

def update_faiss_index(new_embeddings):
    new_embeddings_np = np.array(new_embeddings).astype('float32')
    d = new_embeddings_np.shape[1]
    if os.path.exists(FAISS_INDEX_PATH):
        index = faiss.read_index(FAISS_INDEX_PATH)
    else:
        index = faiss.IndexFlatL2(d)
    index.add(new_embeddings_np)
    faiss.write_index(index, FAISS_INDEX_PATH)

def process_and_embed_document(source_filename):
    logger.info(f"Starting automated, context-rich indexing for {source_filename}...")
    
    text_filename = os.path.splitext(source_filename)[0] + ".txt"
    text_file_path = os.path.join(PROCESSED_TEXT_DIR, text_filename)
    
    if not os.path.exists(text_file_path):
        msg = f"Processed text file not found at {text_file_path}"
        return (False, msg)

    # load metadata to get the title
    metadata_index = load_metadata_index()
    base_filename = os.path.splitext(source_filename)[0]
    doc_title = metadata_index.get(base_filename, {}).get('title', base_filename.replace('_', ' '))

    with open(text_file_path, 'r', encoding='utf-8') as f:
        text = f.read()

    chunks = chunk_text(text)
    if not chunks:
        return (True, "No chunks to process.")

    # context enrichment
    chunks_with_context = [f"Sənədin adı: {doc_title}\n\nMəzmun: {chunk}" for chunk in chunks]

    new_vector_data, all_new_embeddings = [], []
    try:
        for i in range(0, len(chunks), BATCH_SIZE):
            batch_to_embed = chunks_with_context[i:i + BATCH_SIZE]
            original_chunks_batch = chunks[i:i + BATCH_SIZE]

            response = genai.embed_content(
                model=EMBEDDING_MODEL,
                content=batch_to_embed,
                task_type="RETRIEVAL_DOCUMENT"
            )
            embeddings = response['embedding']
            all_new_embeddings.extend(embeddings)
            
            for j, chunk in enumerate(original_chunks_batch):
                new_vector_data.append({
                    "source_file": text_filename, "chunk_text": chunk, "embedding": embeddings[j]
                })
            time.sleep(1)
    except Exception as e:
        msg = f"Gemini API Error: {e}"
        return (False, msg)
            
    if new_vector_data:
        update_vector_store(new_vector_data)
        update_faiss_index(all_new_embeddings)
        msg = f"Successfully indexed {len(chunks)} context-rich chunks from {source_filename}."
        logger.info(msg)
        return (True, msg)
    
    return (True, "No new data to index.")