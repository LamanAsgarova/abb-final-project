import re

def chunk_text(text: str) -> list[str]:
    """
    Splits text into chunks based on paragraphs.
    """
    if not isinstance(text, str) or not text.strip():
        return []

    # Split the text by two or more newlines (which signifies a paragraph break)
    paragraphs = re.split(r'\n{2,}', text)
    
    # Filter out any resulting paragraphs that are empty or just whitespace
    chunks = [p.strip() for p in paragraphs if p.strip()]
    
    return chunks