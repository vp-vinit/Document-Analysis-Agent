# 📚 Document Analysis Agent

An AI agent designed to analyze PDF documents using artificial intelligence. It supports document question answering, automatic summarization, and file assessment history.

## 🚀 Features

- **PDF Upload:** Upload and process PDF documents.
- **Text Extraction:** Extract readable text from PDF pages using PyPDF.
- **Text Chunking:** Split extracted text into manageable chunks using LangChain.
- **Vector Search:** Generate embeddings using Sentence Transformers and store them in FAISS.
- **AI Question Answering:** Ask questions about the uploaded PDF using Retrieval-Augmented Generation (RAG).
- **Document Summarization:** Generate clear summaries of PDF content using the Groq language model.
- **Source References:** Display source file names and page numbers for retrieved passages.
- **Assessment History:** Review questions, answers, summaries, and processing activities.
- **Document Reset:** Clear the active document and start a new analysis.

## 🛠️ Technology Stack

- Python
- Streamlit
- FastAPI
- LangChain
- Groq API
- Sentence Transformers
- FAISS Vector Database
- PyPDF
- Requests
- Python-dotenv

## 📂 Project Structure

```text
DOCUMENT_ANALYSIS_GROQ/
├── app.py
├── api.py
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

`app.py` is the Streamlit frontend. You can rename your existing `main(1).py` file to `app.py`.

`api.py` contains the FastAPI backend and AI document-processing logic.

## ⚙️ Installation

### 1. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure the Groq API key

Create a `.env` file at the location expected by `api.py`:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your actual API key. Never upload this file to GitHub.

## ▶️ Run the Project

**Terminal 1 — Start the FastAPI backend**

```bash
uvicorn api:app --reload --port 8000
```

API documentation: http://127.0.0.1:8000/docs

**Terminal 2 — Start the Streamlit frontend**

```bash
streamlit run app.py
```

Keep both terminals running while using the application.

## 🔌 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | API welcome message |
| GET | `/status` | Active document status |
| POST | `/upload` | Upload and process a PDF |
| POST | `/ask` | Ask questions about the PDF |
| POST | `/summarize` | Generate a document summary |
| POST | `/reset` | Reset the active document |
| GET | `/docs` | Interactive API documentation |

## 🔄 Workflow

1. Upload a PDF document.
2. Extract its readable text.
3. Split the text into chunks.
4. Generate embeddings and create a FAISS index.
5. Retrieve relevant document passages for a question.
6. Generate a context-based answer using the Groq model.
7. Generate a summary when requested.
8. Review the recorded document assessment history.

## ⚠️ Current Limitations

- Only one active PDF is stored in backend memory at a time.
- Scanned PDFs require OCR, which is not currently implemented.
- Assessment history is stored in Streamlit session state.
- Document data and the vector index are not persistently stored.
- The frontend is configured for local development.

## 🔒 Security

- Never commit `.env` or API keys to GitHub.
- Add `.env`, `.venv/`, and Python cache files to `.gitignore`.
- Configure authentication and security before public deployment.

## 🔮 Future Improvements

- Add OCR support for scanned PDFs.
- Support multiple documents.
- Store assessment history in a database.
- Add user authentication.
- Export summaries and answers as PDF or Word files.
- Deploy the agent with production security settings.

## 👨‍💻 Project Summary

The Document Analysis Agent uses retrieval-augmented generation, semantic search, and a language model to help users understand PDF documents, obtain context-based answers, and generate summaries.

It combines a Streamlit interface with a FastAPI backend to deliver AI-powered document analysis.
