import json
import os

METADATA_INDEX_PATH = "data/document_index.json"

def load_index():
    """Load the document metadata index"""
    if not os.path.exists(METADATA_INDEX_PATH):
        return {}
    try:
        with open(METADATA_INDEX_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading index: {e}")
        return {}

def save_index(index_data):
    """Save the document metadata index"""
    os.makedirs(os.path.dirname(METADATA_INDEX_PATH), exist_ok=True)
    with open(METADATA_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)

def add_document_to_index(metadata):
    """Add a document to the metadata index"""
    if not metadata.get('file_name'):
        print("Warning: Cannot add document without filename")
        return
    
    index = load_index()
    key = os.path.splitext(metadata.get('file_name', ''))[0]
    index[key] = metadata
    save_index(index)
    print(f"Added {metadata.get('file_name')} to index")

def remove_document_from_index(filename):
    """Remove a document from the metadata index"""
    index = load_index()
    key = os.path.splitext(filename)[0]
    if key in index:
        del index[key]
        save_index(index)
        print(f"Removed {filename} from index")
    else:
        print(f"Document {filename} not found in index")

def get_document_metadata(filename):
    """Get metadata for a specific document"""
    index = load_index()
    key = os.path.splitext(filename)[0]
    return index.get(key, {})

def update_document_metadata(filename, updates):
    """Update specific fields in document metadata"""
    index = load_index()
    key = os.path.splitext(filename)[0]
    if key in index:
        index[key].update(updates)
        save_index(index)
        return True
    return False