from .index_manager import load_index

def get_accessible_documents(user_role: str) -> list:
    """
    Loads the document index and returns a list of documents
    accessible to the given user role.
    """
    all_documents = load_index()
    if not all_documents:
        return []

    user_documents = []
    # An Admin can see all documents
    if user_role == "Admin":
        return list(all_documents.values())
        
    # Regular users see documents for their team or unassigned ones
    for doc_key, doc_metadata in all_documents.items():
        if doc_metadata.get('team') == user_role or doc_metadata.get('team') == 'Unassigned':
            user_documents.append(doc_metadata)
            
    return user_documents