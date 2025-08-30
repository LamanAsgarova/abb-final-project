import os
import sys
import json
import time
import numpy as np
import faiss

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions
from src.document_processing.chunker import chunk_text
from src.services.google_client import configure_google_client
from src.services.logger_service import setup_logger

logger = setup_logger()

# Configuration
PROCESSED_TEXT_DIR = "data/processed_documents/"
VECTOR_STORE_PATH = "data/vector_store.json"
FAISS_INDEX_PATH = "data/faiss_index.idx"
EMBEDDING_MODEL = "models/embedding-001"
BATCH_SIZE = 50

def generate_and_store_embeddings():
    """
    Processes all text files with a robust retry mechanism for API rate limits.
    """
    configure_google_client()
    print("Starting embedding and indexing process...")
    vector_store = []
    
    files_to_process = [f for f in os.listdir(PROCESSED_TEXT_DIR) if f.endswith('.txt')]

    # The outer loop for iterating through files now uses 'file_index'
    for file_index, filename in enumerate(files_to_process):
        print(f"Processing file {file_index + 1}/{len(files_to_process)}: {filename}...")
        
        file_path = os.path.join(PROCESSED_TEXT_DIR, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            text = f.read()
            
        chunks = chunk_text(text)
        if not chunks:
            print(f"  - Skipping {filename} as it has no content.")
            continue
            
        print(f"  - Generated {len(chunks)} chunks. Processing in batches of {BATCH_SIZE}...")
        
        # robust retry logic
        # The inner loop for batches now uses 'batch_start_index'
        for batch_start_index in range(0, len(chunks), BATCH_SIZE):
            batch_chunks = chunks[batch_start_index : batch_start_index + BATCH_SIZE]
            max_retries = 5
            retry_delay = 10 

            for attempt in range(max_retries):
                try:
                    print(f"    - Processing batch {batch_start_index//BATCH_SIZE + 1} (Attempt {attempt + 1})...")
                    response = genai.embed_content(
                        model=EMBEDDING_MODEL, content=batch_chunks, task_type="RETRIEVAL_DOCUMENT"
                    )
                    embeddings = response['embedding']
                    
                    for j, chunk in enumerate(batch_chunks):
                        vector_store.append({
                            "source_file": filename, "chunk_text": chunk, "embedding": embeddings[j]
                        })
                    
                    print(f"    - Batch {batch_start_index//BATCH_SIZE + 1} successful.")
                    time.sleep(1)
                    break 

                except google_exceptions.ResourceExhausted as e:
                    print(f"    - Rate limit hit. Waiting for {retry_delay} seconds before retrying...")
                    logger.warning(f"Rate limit hit for {filename}. Retrying in {retry_delay}s.")
                    time.sleep(retry_delay)
                    retry_delay *= 2 
                    
                    if attempt == max_retries - 1:
                        logger.error(f"Failed to process {filename} after {max_retries} retries.")
                        break 
                except Exception as e:
                    logger.error(f"An unexpected error occurred for {filename}: {e}")
                    break 
    
    print(f"\nSaving vector store with {len(vector_store)} entries...")
    with open(VECTOR_STORE_PATH, 'w', encoding='utf-8') as f:
        json.dump(vector_store, f)
    print("Vector store saved.")
    
    if not vector_store:
        print("No embeddings were generated. FAISS index will not be created.")
        return

    print("\nBuilding FAISS index...")
    embeddings = [entry['embedding'] for entry in vector_store]
    embedding_matrix = np.array(embeddings).astype('float32')
    d = embedding_matrix.shape[1]
    index = faiss.IndexFlatL2(d)
    index.add(embedding_matrix)
    faiss.write_index(index, FAISS_INDEX_PATH)
    print(f"FAISS index with {index.ntotal} vectors saved.")
    print("Embedding and indexing process complete!")

if __name__ == "__main__":
    generate_and_store_embeddings()