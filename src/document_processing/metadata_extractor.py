import os
from datetime import datetime
import pdfplumber
import docx
import openpyxl
from pptx import Presentation
import pptx

def _get_common_metadata(file_path):
    """Gets metadata common to all file types from the file system."""
    try:
        stat = os.stat(file_path)
        
        return {
            "file_name": os.path.basename(file_path),
            "file_path": file_path,
            "file_size_bytes": stat.st_size,
            "last_modified_date": datetime.fromtimestamp(stat.st_mtime).isoformat(),
            "creation_date": datetime.fromtimestamp(stat.st_ctime).isoformat()
        }
    except FileNotFoundError:
        return {}


def extract_metadata(file_path):
    """
    Extracts metadata from a file by detecting its type.
    This function combines general file info with document-specific properties.
    """
    metadata = _get_common_metadata(file_path)
    
    # Get the file extension to determine the file type
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    try:
        if file_extension == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                doc_properties = pdf.metadata
            metadata['title'] = doc_properties.get('Title', 'N/A')
            metadata['author'] = doc_properties.get('Author', 'N/A')
            metadata['subject'] = doc_properties.get('Subject', 'N/A')
            metadata['creator'] = doc_properties.get('Creator', 'N/A')

        elif file_extension == '.docx':
            doc_properties = docx.Document(file_path).core_properties
            metadata['title'] = getattr(doc_properties, 'title', 'N/A')
            metadata['author'] = getattr(doc_properties, 'author', 'N/A')
            metadata['subject'] = getattr(doc_properties, 'subject', 'N/A')
            metadata['last_modified_by'] = getattr(doc_properties, 'last_modified_by', 'N/A')
            modified_date = getattr(doc_properties, 'modified', None)
            if modified_date:
                metadata['document_modified_date'] = modified_date.isoformat()

        elif file_extension == '.xlsx':
            doc_properties = openpyxl.load_workbook(file_path).properties
            metadata['title'] = getattr(doc_properties, 'title', 'N/A')
            metadata['author'] = getattr(doc_properties, 'creator', 'N/A')
            metadata['subject'] = getattr(doc_properties, 'subject', 'N/A')
            metadata['last_modified_by'] = getattr(doc_properties, 'lastModifiedBy', 'N/A')
            modified_date = getattr(doc_properties, 'modified', None)
            if modified_date:
                metadata['document_modified_date'] = modified_date.isoformat()

        elif file_extension == '.pptx':
            doc_properties = Presentation(file_path).core_properties
            metadata['title'] = getattr(doc_properties, 'title', 'N/A')
            metadata['author'] = getattr(doc_properties, 'author', 'N/A')
            metadata['subject'] = getattr(doc_properties, 'subject', 'N/A')
            metadata['last_modified_by'] = getattr(doc_properties, 'last_modified_by', 'N/A')
            modified_date = getattr(doc_properties, 'modified', None)
            if modified_date:
                metadata['document_modified_date'] = modified_date.isoformat()
            
    except Exception as e:
        print(f"Could not extract specific metadata for {metadata.get('file_name')}: {e}")
        # default keys exist even if extraction fails
        metadata.setdefault('title', 'Extraction Error')
        metadata.setdefault('author', 'Extraction Error')

    return metadata