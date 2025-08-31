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
    
    if not metadata:
        return {}
    
    # Get the file extension to determine the file type
    _, file_extension = os.path.splitext(file_path)
    file_extension = file_extension.lower()
    
    # Create meaningful defaults from filename
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    default_title = base_name.replace('_', ' ').replace('-', ' ').title()
    
    # Set initial defaults
    metadata['title'] = default_title
    metadata['author'] = 'Unknown'
    metadata['subject'] = 'Document'
    metadata['creator'] = 'Unknown'
    metadata['last_modified_by'] = 'Unknown'
    metadata['auto_category'] = 'General'  # Add default category
    
    try:
        if file_extension == '.pdf':
            with pdfplumber.open(file_path) as pdf:
                doc_properties = pdf.metadata or {}
            
            # Only override defaults if we have actual values
            if doc_properties.get('Title') and doc_properties['Title'].strip():
                metadata['title'] = doc_properties['Title'].strip()
            if doc_properties.get('Author') and doc_properties['Author'].strip():
                metadata['author'] = doc_properties['Author'].strip()
            if doc_properties.get('Subject') and doc_properties['Subject'].strip():
                metadata['subject'] = doc_properties['Subject'].strip()
            if doc_properties.get('Creator') and doc_properties['Creator'].strip():
                metadata['creator'] = doc_properties['Creator'].strip()

        elif file_extension == '.docx':
            try:
                doc = docx.Document(file_path)
                doc_properties = doc.core_properties
                
                if hasattr(doc_properties, 'title') and doc_properties.title and doc_properties.title.strip():
                    metadata['title'] = doc_properties.title.strip()
                if hasattr(doc_properties, 'author') and doc_properties.author and doc_properties.author.strip():
                    metadata['author'] = doc_properties.author.strip()
                if hasattr(doc_properties, 'subject') and doc_properties.subject and doc_properties.subject.strip():
                    metadata['subject'] = doc_properties.subject.strip()
                if hasattr(doc_properties, 'last_modified_by') and doc_properties.last_modified_by and doc_properties.last_modified_by.strip():
                    metadata['last_modified_by'] = doc_properties.last_modified_by.strip()
                
                if hasattr(doc_properties, 'modified') and doc_properties.modified:
                    metadata['document_modified_date'] = doc_properties.modified.isoformat()
                    
            except Exception as e:
                print(f"Error extracting DOCX properties: {e}")

        elif file_extension == '.xlsx':
            try:
                wb = openpyxl.load_workbook(file_path)
                doc_properties = wb.properties
                
                if hasattr(doc_properties, 'title') and doc_properties.title and doc_properties.title.strip():
                    metadata['title'] = doc_properties.title.strip()
                if hasattr(doc_properties, 'creator') and doc_properties.creator and doc_properties.creator.strip():
                    metadata['author'] = doc_properties.creator.strip()
                if hasattr(doc_properties, 'subject') and doc_properties.subject and doc_properties.subject.strip():
                    metadata['subject'] = doc_properties.subject.strip()
                if hasattr(doc_properties, 'lastModifiedBy') and doc_properties.lastModifiedBy and doc_properties.lastModifiedBy.strip():
                    metadata['last_modified_by'] = doc_properties.lastModifiedBy.strip()
                
                if hasattr(doc_properties, 'modified') and doc_properties.modified:
                    metadata['document_modified_date'] = doc_properties.modified.isoformat()
                    
            except Exception as e:
                print(f"Error extracting XLSX properties: {e}")

        elif file_extension == '.pptx':
            try:
                prs = Presentation(file_path)
                doc_properties = prs.core_properties
                
                if hasattr(doc_properties, 'title') and doc_properties.title and doc_properties.title.strip():
                    metadata['title'] = doc_properties.title.strip()
                if hasattr(doc_properties, 'author') and doc_properties.author and doc_properties.author.strip():
                    metadata['author'] = doc_properties.author.strip()
                if hasattr(doc_properties, 'subject') and doc_properties.subject and doc_properties.subject.strip():
                    metadata['subject'] = doc_properties.subject.strip()
                if hasattr(doc_properties, 'last_modified_by') and doc_properties.last_modified_by and doc_properties.last_modified_by.strip():
                    metadata['last_modified_by'] = doc_properties.last_modified_by.strip()
                
                if hasattr(doc_properties, 'modified') and doc_properties.modified:
                    metadata['document_modified_date'] = doc_properties.modified.isoformat()
                    
            except Exception as e:
                print(f"Error extracting PPTX properties: {e}")
            
    except Exception as e:
        print(f"Could not extract specific metadata for {metadata.get('file_name')}: {e}")
        # Keep the meaningful defaults we set earlier
    
    # Auto-categorize based on filename or content
    filename_lower = base_name.lower()
    if any(word in filename_lower for word in ['report', 'hesabat', 'annual']):
        metadata['auto_category'] = 'Report'
    elif any(word in filename_lower for word in ['policy', 'siyasət', 'prosedur']):
        metadata['auto_category'] = 'Policy'
    elif any(word in filename_lower for word in ['manual', 'guide', 'təlimat']):
        metadata['auto_category'] = 'Manual'
    elif file_extension == '.xlsx':
        metadata['auto_category'] = 'Spreadsheet'
    elif file_extension == '.pptx':
        metadata['auto_category'] = 'Presentation'

    return metadata