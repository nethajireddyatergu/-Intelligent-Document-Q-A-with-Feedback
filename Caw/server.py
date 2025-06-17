
from fastapi import FastAPI, UploadFile, File
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from uuid import uuid4
import os
import shutil
from pydantic import BaseModel

from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

from dotenv import load_dotenv
load_dotenv()  # Load .env variables

import os
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Setup API
app = FastAPI()
UPLOAD_DIR = "uploaded_docs"
os.makedirs(UPLOAD_DIR, exist_ok=True)


embedding = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
llm = ChatGoogleGenerativeAI(model="models/gemini-1.5-flash-8b", convert_system_message_to_human=True)
#llm = ChatGoogleGenerativeAI(model="models/chat-bison-001", convert_system_message_to_human=True)


# Memory & VectorDB
memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
vectorstore = None
qa_chain = None

# ----------- PHASE 1: DOCUMENT INGESTION AND INDEXING ------------ #

def get_loader(file_path):
    if file_path.endswith(".pdf"):
        return PyPDFLoader(file_path)
    elif file_path.endswith(".docx"):
        return Docx2txtLoader(file_path)
    elif file_path.endswith(".txt"):
        return TextLoader(file_path)
    else:
        raise ValueError("Unsupported file format")

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    file_id = str(uuid4())
    file_path = os.path.join(UPLOAD_DIR, file_id + "_" + file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    loader = get_loader(file_path)
    docs = loader.load()

    # Semantic chunking
    splitter = RecursiveCharacterTextSplitter(chunk_size=512, chunk_overlap=128)
    chunks = splitter.split_documents(docs)

    global vectorstore, qa_chain
    vectorstore = Chroma.from_documents(chunks, embedding=embedding, persist_directory=".chromadb")
    vectorstore.persist()

    # Setup RAG chain with memory
    retriever = vectorstore.as_retriever(search_type="mmr")
    qa_chain = ConversationalRetrievalChain.from_llm(llm=llm, retriever=retriever, memory=memory)

    return {"message": f"Uploaded and indexed {len(chunks)} chunks."}

# ----------- PHASE 2: Q&A WITH MEMORY ------------ #

class AskRequest(BaseModel):
    query: str

qa_history = []

@app.post("/ask")
async def ask_question(request: AskRequest):
    if qa_chain is None:
        return {"error": "No documents uploaded yet."}
    result = qa_chain.invoke(request.query)

    # If it's a dict with 'answer', extract it
    answer_str = result['answer'] if isinstance(result, dict) and 'answer' in result else str(result)

    qa_history.append({"question": request.query, "answer": answer_str})
    return {"answer": answer_str}

@app.get("/history")
async def get_history():
    return {"history": qa_history}

# ----------- PHASE 3: FEEDBACK & LEARNING ------------ #

class Feedback(BaseModel):
    question: str
    answer: str
    rating: int
    correction: str = ""

feedback_store = []

@app.post("/feedback")
async def give_feedback(feedback: Feedback):  # Use Pydantic model
    feedback_store.append({
        "question": feedback.question,
        "answer": feedback.answer,
        "rating": feedback.rating,
        "correction": feedback.correction
    })
    return {"message": "Feedback recorded."}

# ----------- PHASE 4: EVALUATION & MONITORING ------------ #

@app.get("/metrics")
def get_metrics():
    avg_rating = sum(f["rating"] for f in feedback_store) / max(len(feedback_store), 1)
    return {
        "uploaded_docs": len(os.listdir(UPLOAD_DIR)),
        "feedback_count": len(feedback_store),
        "average_rating": round(avg_rating, 2),
        "memory_summary": memory.buffer if hasattr(memory, "buffer") else "N/A"
    }

