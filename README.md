# -Intelligent-Document-Q-A-with-Feedback
caw studios project

# 📄 Intelligent Document Q&A System

An end-to-end LangChain-based system for intelligent Q&A over documents using:

- 🔍 **Google Gemini** (via Generative AI)
- 📚 **LangChain** for RAG & Memory
- 📦 **FastAPI** backend
- 🌐 **Streamlit** frontend
- 🧠 **ChromaDB** vector store
- 📝 Feedback & Evaluation dashboard

---

## 🚀 Features

- Upload PDF, DOCX, or TXT files
- Ask questions with conversational memory
- Store Q&A history
- Rate & suggest improved answers
- Real-time analytics (avg rating, feedback count)
- Clean UI via Streamlit sidebar and rating system

---

## 🛠️ Technologies Used

- Python
- FastAPI
- Streamlit
- LangChain
- Google Generative AI (Gemini)
- ChromaDB
- PyMuPDF / python-docx / unstructured

---

## ⚙️ Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/langchain-doc-qa.git
cd langchain-doc-qa
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add `.env` file

```env
GOOGLE_API_KEY=your_google_generative_ai_api_key
```

### 4. Start FastAPI backend

```bash
uvicorn yourfilename:app --reload
```

### 5. Start Streamlit frontend

```bash
streamlit run your_streamlit_file.py
```

---

## 📊 Sample API Endpoints

- `POST /upload` - Upload & index documents
- `POST /ask` - Ask a question
- `POST /feedback` - Submit feedback
- `GET /history` - View question-answer history
- `GET /metrics` - Monitor stats

---

## 📬 Feedback

For improvements or issues, feel free to open a PR or issue.  
This project is open to contributions!

---

