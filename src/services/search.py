import json
import numpy as np
import faiss
import google.generativeai as genai
import os

from .access_control import get_accessible_documents
from .google_client import configure_google_client
from .index_manager import load_index as load_metadata_index

VECTOR_STORE_PATH = "data/vector_store.json"
FAISS_INDEX_PATH = "data/faiss_index.idx"
EMBEDDING_MODEL = "models/embedding-001"

# load resources
try:
    configure_google_client()
    index = faiss.read_index(FAISS_INDEX_PATH)
    with open(VECTOR_STORE_PATH, 'r', encoding='utf-8') as f:
        vector_store = json.load(f)
    metadata_index = load_metadata_index()
except (FileNotFoundError, IOError):
    print("WARNING: Search index files not found. Search will not work.")
    index, vector_store, metadata_index = None, None, None

def semantic_search(query: str, user_role: str, top_k: int = 5, temp_index=None, temp_vector_store=None) -> list:
    if temp_index and temp_vector_store:
        index_to_search=temp_index
        store_to_use=temp_vector_store
    else:
        if not all([index, vector_store, metadata_index]):
            return []
        index_to_search=index
        store_to_use=vector_store

    accessible_docs_metadata = get_accessible_documents(user_role)
    accessible_source_files = {os.path.splitext(doc['file_name'])[0] for doc in accessible_docs_metadata}
    
    # generate embedding for the user query
    query_embedding = genai.embed_content(
        model=EMBEDDING_MODEL,
        content=query,
        task_type="RETRIEVAL_QUERY"
    )['embedding']
    
    query_vector = np.array([query_embedding]).astype('float32')

    # search the FAISS index
    distances, indices = index.search(query_vector, k=top_k * 5)

    # format and filter results
    results = []
    seen_chunks = set()
    for i in range(len(indices[0])):
        original_index = indices[0][i]
        chunk_data = vector_store[original_index]
        base_filename = os.path.splitext(chunk_data['source_file'])[0]

        # RBAC check and duplicate chunk check
        if base_filename in accessible_source_files and chunk_data['chunk_text'] not in seen_chunks:

            original_metadata = metadata_index.get(base_filename, {})
            
            results.append({
                "chunk_text": chunk_data['chunk_text'],
                "original_filename": original_metadata.get('file_name', 'Unknown'),
                "original_filepath": original_metadata.get('file_path', ''),
                "title": original_metadata.get('title', base_filename)
            })
            seen_chunks.add(chunk_data['chunk_text'])
            if len(results) >= top_k:
                break
                
    return results