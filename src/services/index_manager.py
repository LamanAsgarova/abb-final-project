import json
import os
from datetime import datetime

METADATA_DIR = "data/metadata/"
INDEX_FILE_PATH = os.path.join(METADATA_DIR, "document_index.json")

def load_index():
    # load the doc indexes from the JSON file
    if os.path.exists(INDEX_FILE_PATH):
        with open(INDEX_FILE_PATH, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}
    return {}

def save_index(index_data):
    # save the doc indexes to the JSON file
    os.makedirs(METADATA_DIR, exist_ok=True)
    with open(INDEX_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=4)

def add_document_to_index(metadata):
    # add or update a doc's entry in the master index
    base_filename = os.path.splitext(metadata['file_name'])[0]
    index = load_index()
    index[base_filename] = metadata
    save_index(index)
    print(f"Updated metadata index for '{base_filename}'.")

def remove_document_from_index(source_filename: str):
    # remove a doc's entry from the master index
    base_filename = os.path.splitext(source_filename)[0]
    index = load_index()
    
    if base_filename in index:
        del index[base_filename]
        save_index(index)
        print(f"Removed '{base_filename}' from metadata index.")
        return True
    else:
        print(f"Warning: '{base_filename}' not found in metadata index.")
        return False