import streamlit as st
import requests

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="📄 Gemini Document Q&A", layout="wide")
st.title("📄 Intelligent Document Q&A with Feedback")

# ---------- Session State Initialization ----------
if 'uploaded' not in st.session_state:
    st.session_state.uploaded = False
if 'last_query' not in st.session_state:
    st.session_state.last_query = None
if 'last_answer' not in st.session_state:
    st.session_state.last_answer = None

# ---------- Sidebar: Q&A History ----------
with st.sidebar:
    st.header("📜 Q&A History")
    try:
        history_res = requests.get(f"{API_BASE}/history")
        if history_res.status_code == 200:
            history = history_res.json().get("history", [])
            if history:
                for i, item in enumerate(reversed(history[-10:]), 1):
                    st.markdown(f"**{i}. {item['question']}**\n\n→ {item['answer']}")
            else:
                st.info("No Q&A history yet.")
        else:
            st.error("❌ Failed to load history.")
    except Exception as e:
        st.error(f"Error: {e}")

# ---------- Phase 1: File Upload ----------
st.header("1. Upload a Document")

if not st.session_state.uploaded:
    uploaded_file = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
    if uploaded_file:
        with st.spinner("Uploading and processing..."):
            files = {'file': (uploaded_file.name, uploaded_file, uploaded_file.type)}
            res = requests.post(f"{API_BASE}/upload", files=files)
            if res.status_code == 200:
                st.success(res.json().get("message", "Upload successful!"))
                st.session_state.uploaded = True
            else:
                st.error(f"Upload failed: {res.text}")
else:
    st.success("✅ Document already uploaded.")
    if st.button("🔁 Upload New Document"):
        st.session_state.uploaded = False
        st.experimental_rerun()

# ---------- Phase 2: Ask Questions ----------
if st.session_state.uploaded:
    st.header("2. Ask a Question")
    query = st.text_input("💬 Enter your question:")
    
    if st.button("🔎 Ask") and query:
        with st.spinner("Thinking..."):
            res = requests.post(f"{API_BASE}/ask", json={"query": query})
            if res.status_code == 200:
                answer = res.json().get("answer", "No answer returned.")
                st.session_state.last_query = query
                st.session_state.last_answer = answer
            else:
                st.error("❌ Failed to get answer.")
                st.session_state.last_query = None
                st.session_state.last_answer = None

    # ---------- Display Answer Immediately ----------
    if st.session_state.last_answer:
        st.markdown("### 🧠 Answer:")
        st.markdown(f"**{st.session_state.last_answer}**")

        # ---------- Phase 3: Feedback ----------
        st.subheader("3. Provide Feedback")
        col1, col2 = st.columns(2)
        with col1:
            rating = st.slider("⭐ Rate the answer (1 = Bad, 5 = Excellent)", 1, 5, 3)
        with col2:
            correction = st.text_area("✍️ Suggest a better answer (optional)")

        if st.button("📤 Submit Feedback"):
            fb_payload = {
                "question": st.session_state.last_query,
                "answer": st.session_state.last_answer,
                "rating": int(rating),  # Ensure int
                "correction": correction or ""  # Ensure string
            }

            fb_res = requests.post(f"{API_BASE}/feedback", json=fb_payload)

            if fb_res.status_code == 200:
                st.success("✅ Feedback submitted! Thank you 🙌")
                st.session_state.last_query = None
                st.session_state.last_answer = None
            else:
                st.error(f"❌ Failed to submit feedback: {fb_res.text}")

