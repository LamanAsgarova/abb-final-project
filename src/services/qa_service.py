import google.generativeai as genai
import json
from .google_client import configure_google_client
from services.logger_service import setup_logger

logger = setup_logger()

def get_answer_from_llm(query: str, context_chunks: list, chat_history: list) -> str:
    """
    Generates a structured JSON response containing a text answer and an optional
    chart suggestion based on the context and chat history.
    """
    configure_google_client()
    
    if not context_chunks:
        error_response = {"answer_text": "Sənədlərdə bu suala cavab vermək üçün uyğun məlumat tapılmadı.", "chart_info": None}
        return json.dumps(error_response)

    context_string = "\n\n---\n\n".join(context_chunks)
    history_string = "\n".join([f"{m['role']}: {m['content']}" for m in chat_history])

    prompt = f"""
    You are an expert data analyst. Your task is to answer the user's LATEST QUESTION based on the provided CONTEXT.
    You MUST respond with a single, valid JSON object with two keys: "answer_text" and "chart_info".

    1.  **"answer_text"**: - Write a helpful, synthesized text answer in the same language as the user's question. Cite the source document(s) at the end of the answer (e.g., "Mənbə: filename.pdf").
                           - **Detect the language of the "LATEST QUESTION" and ALWAYS respond in that same language.**
                           - If the question is in Azerbaijani, answer in Azerbaijani. If it's in English, answer in English.
    2.  **"chart_info"**:
        - If the context contains statistical data that can be visualized to help answer the question, create a dictionary for this key.
        - The dictionary MUST contain these FOUR keys:
            - "chart_type": Recommend the best chart type from this list: ["line", "bar", "pie"].
            - "x_column": The exact name of the column/header from the data for the x-axis.
            - "y_column": The exact name of the column/header from the data for the y-axis.
            - "title": A short, descriptive title for the chart based on the user's question and the data.
        - If the data is NOT suitable for a chart, the value for "chart_info" MUST be null.

    CHAT HISTORY:
    {history_string}

    CONTEXT DOCUMENTS:
    {context_string}

    LATEST QUESTION:
    {query}

    JSON RESPONSE:
    """
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
            response_mime_type="application/json"
        )
        response = model.generate_content(prompt, generation_config=generation_config)
        return response.text
    except Exception as e:
        logger.error(f"An error occurred while generating JSON answer: {e}")
        error_response = {"answer_text": f"An error occurred while generating the answer: {e}", "chart_info": None}
        return json.dumps(error_response)