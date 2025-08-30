# GenAI Document Navigator for ABB

This project is a sophisticated, AI-powered web application designed to serve as an intelligent interface for internal corporate documents. It transforms a static library of files (PDFs, Word documents, Excel sheets, PPTX files) into an interactive, conversational knowledge base, enabling employees to find information, extract insights, and get answers to their questions in seconds.

This system was developed as a final project for the ABB Data Science Internship program.

## 🎯 The Problem This Solves

Large organizations like banks manage a vast amount of information scattered across numerous documents. This creates several challenges:

- **Time Inefficiency**: Employees spend significant time manually searching through long documents to find specific information.

- **Compliance & Accuracy Risks**: It's difficult to ensure that decisions are based on the most up-to-date policy or report, leading to potential compliance issues.

- **Information Silos**: Knowledge remains locked within documents specific to certain teams, hindering cross-departmental collaboration and analysis.

The GenAI Document Navigator solves these problems by creating a single, secure, and intelligent gateway to all internal documents.

## ✨ Key Features

- **Conversational Q&A**: Ask questions about the document library in natural language and receive synthesized, accurate answers.

- **Secure Role-Based Access Control (RBAC)**: A robust authentication system ensures that users can only view and query documents relevant to their specific role or team (e.g., Data Tribe, Risk Tribe).

- **Automated Insights & Visualization**:
  - Instantly generate summaries and extract key insights (financial metrics, policy changes, important dates) from any document in the library.
  - The AI can suggest and render data visualizations (e.g., bar, line charts) from statistical data found in Excel files.

- **Temporary "Chat with your Doc" Mode**: Users can securely upload a private document for a temporary, one-on-one chat session. The document is processed in-memory and is never saved to the main library, ensuring privacy.

- **Full Admin Panel**: A dedicated interface for administrators to upload new documents, manage the library, and view analytics on document distribution and storage.

- **Persistent Sessions**: Uses a secure cookie-based system, so users remain logged in even after refreshing the page.

## 🛠️ Tech Stack

- **Backend**: Python
- **Frontend**: Streamlit
- **AI & Language Models**: Google Gemini API (Embedding & Generative Models)
- **Vector Search**: Facebook AI Similarity Search (FAISS)
- **Data Processing**: Pandas, NumPy
- **Document Parsing**: pdfplumber, python-docx, openpyxl
- **Authentication**: streamlit-authenticator

## 📂 Project Structure

The project is organized into a modular structure for clarity and scalability:

```
├── data/              # Stores raw documents, processed text, metadata, and indexes
├── scripts/           # Utility scripts for setup (e.g., hashing passwords)
├── src/               # Main source code for the application
│   ├── document_processing/
│   ├── services/      # Backend logic (search, QA, database, etc.)
│   └── ui/            # Streamlit UI components
├── .streamlit/        # Streamlit configuration (e.g., custom theme)
├── assets/            # Static assets like logos
├── logs/              # Application log files
├── main_app.py        # Main entry point to run the application
└── config.yaml        # User credentials and app configuration
```

## 🚀 Getting Started

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.9+
- A Google Gemini API Key. You can get one from [Google AI Studio](https://makersuite.google.com/).

### 2. Installation

Clone the repository.

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Install the required libraries:

```bash
pip install -r requirements.txt
```

### 3. Configuration

**Set up the Google API Key:**

1. Create a file named `.env` in the root directory.
2. Add your Gemini API key to this file:

```env
GOOGLE_API_KEY="api_key_here"
```

**Configure Users and Passwords:**

1. Open the `scripts/hash_passwords.py` file and replace the example passwords with your desired passwords.
2. Run the script to generate secure password hashes:

```bash
python scripts/hash_passwords.py
```

3. Open the `config.yaml` file. Paste the generated hashes into the password field for each user. Also, change the key under the cookie section to your own unique secret string.

### 4. Running the Application

**Generate the Initial Search Index:**

1. Place your initial documents into the `data/raw_documents/` subfolders (pdf, word, etc.).
2. Run the embedding script to process these documents. This only needs to be done once initially.

```bash
python scripts/generate_embeddings.py
```

**Launch the Streamlit App:**

```bash
streamlit run main_app.py
```

The application should now be running in your web browser!

## 📜 Usage Guide

### For Regular Users (e.g., Data Tribe)

- **Login**: Use the credentials you configured (e.g., username `data_user`).
- **Chatbot**: The main interface for asking questions. You can ask about the main document library or use the expander at the top to have a temporary, private chat with a document you upload.
- **Document Library**: Browse, search, and download all documents accessible to your role. Use the "💡 Extract Insights" button for an AI-generated summary and analysis.

### For Admins

- **Login**: Use the admin credentials.
- **Upload Tab**: Upload new documents, assign them to a team, and add tags. The system will automatically index them for searching.
- **View & Manage Tab**: View the entire document library, with options to delete files.
- **Bulk Operations Tab**: Securely delete all documents from the system.
- **Analytics Tab**: View interactive charts showing the distribution and storage usage of documents.

---

*Developed as part of the ABB Data Science Internship program*