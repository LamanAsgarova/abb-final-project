import google.generativeai as genai
from .google_client import configure_google_client
from document_processing.text_extractor import extract_text
from services.logger_service import setup_logger

logger = setup_logger()

def extract_insights(file_path: str, lang: str):
    """
    Extracts key insights (key points, metrics, dates) from a document.
    Returns a markdown-formatted string on success or an error message on failure.
    """
    try:
        configure_google_client()
        
        full_text = extract_text(file_path)
        if not full_text or not full_text.strip():
            return "Error: Document is empty or text could not be extracted."

        # Use a large portion of the text for analysis
        truncated_text = full_text[:20000]

        if lang == 'az':
            prompt = f"""
            Sən peşəkar bir biznes analitiksən. Sənin vəzifən aşağıdakı sənədin mətnini təhlil etmək və ondan ən vacib məlumatları strukturlaşdırılmış şəkildə çıxarmaqdır.

            Aşağıdakı formatda cavab ver:
            - **Əsas Məqamlar və Dəyişikliklər:** (Ən vacib 3-5 məqamı və ya siyasət dəyişikliyini qeyd et)
            - **Əsas Rəqəmlər və Metrikalar:** (Mətndəki vacib rəqəmləri, faizləri və ya maliyyə göstəricilərini qeyd et)
            - **Vacib Tarixlər:** (Mətndə qeyd olunan son müraciət, qüvvəyə minmə və ya hesabat tarixlərini qeyd et)

            Cavabı Azərbaycan dilində, aydın və qısa şəkildə təqdim et.

            SƏNƏDİN MƏZMUNU:
            ---
            {truncated_text}
            ---
            """
        else:
            prompt = f"""
            You are a professional business analyst. Your task is to analyze the document content below and extract the most critical insights in a structured format.

            Respond in the following markdown format:
            - **Key Points & Changes:** (List the 3-5 most important takeaways or policy changes)
            - **Key Metrics & Numbers:** (List any significant numbers, percentages, or financial figures)
            - **Important Dates:** (List any deadlines, effective dates, or reporting dates mentioned)

            Provide the answer in English, clearly and concisely.

            DOCUMENT CONTENT:
            ---
            {truncated_text}
            ---
            """
        
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        
        return response.text

    except Exception as e:
        logger.error(f"Error during insights extraction for {file_path}: {e}")
        return f"An error occurred while extracting insights: {str(e)}"