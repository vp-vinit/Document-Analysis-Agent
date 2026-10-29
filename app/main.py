import streamlit as st
import requests
from datetime import datetime
from html import escape
from uuid import uuid4

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Document Analysis Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Document Analysis Agent")
st.write(
    "Turn documents into knowledge with AI. Upload PDFs, ask questions, "
    "generate summaries, and review your file assessment history."
)

# --------------------------------------------------
# 1. SESSION STATE
# --------------------------------------------------

defaults = {
    "processed": False,
    "filename": "",
    "last_answer": None,
    "summary": None,
    "completed_action": None,
    "history": [],
    "current_history_id": None,
    "pages": 0,
    "chunks": 0,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


def current_history_entry():
    """Find the history entry belonging to the active PDF."""
    current_id = st.session_state.current_history_id
    for entry in st.session_state.history:
        if entry["id"] == current_id:
            return entry
    return None


def record_activity(task, question="", answer=""):
    """Save a task to the correct PDF's history entry."""
    entry = current_history_entry()
    if entry is not None:
        entry["activities"].append({
            "task": task,
            "question": question,
            "answer": answer,
            "time": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
            "status": "Completed",
        })


# --------------------------------------------------
# 2. WORKFLOW DIAGRAM
# --------------------------------------------------

def stage_card(number, title, description, completed=False):
    border_color = "#22c55e" if completed else "#64748b"
    status = "✅ Completed" if completed else "⏳ Waiting"

    st.markdown(
        f"""
        <div style="
            border: 1px solid {border_color};
            border-radius: 12px;
            padding: 15px 10px;
            text-align: center;
            min-height: 145px;
            background: rgba(100, 116, 139, 0.10);
            display: flex;
            flex-direction: column;
            justify-content: center;
        ">
            <div style="color: #60a5fa; font-size: 12px;">
                STAGE {number}
            </div>
            <div style="font-size: 17px; font-weight: bold; margin: 10px 0;">
                {title}
            </div>
            <div style="font-size: 13px;">{description}</div>
            <div style="font-size: 12px; margin-top: 10px;">{status}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


st.subheader("⚙️ How Document Analysis Agent Works")
st.caption("Follow the stages to understand how your PDF is processed.")

col1, arrow1, col2, arrow2, col3 = st.columns([3, 0.5, 3, 0.5, 3])

with col1:
    stage_card(1, "📄 Upload PDF", "Select a PDF document",
               st.session_state.processed)

with arrow1:
    st.markdown(
        "<div style='text-align:center;padding-top:48px;font-size:24px;'>➡️</div>",
        unsafe_allow_html=True,
    )

with col2:
    stage_card(2, "⚙️ Extract & Split", "Extract text and create chunks",
               st.session_state.processed)

with arrow2:
    st.markdown(
        "<div style='text-align:center;padding-top:48px;font-size:24px;'>➡️</div>",
        unsafe_allow_html=True,
    )

with col3:
    stage_card(3, "🗄️ FAISS Index", "Create a searchable vector index",
               st.session_state.processed)

st.markdown(
    "<div style='text-align:center;font-size:28px;margin:12px 0;'>⬇️</div>",
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    stage_card(4, "💬 Ask Questions",
               "Retrieve relevant text and generate an answer",
               st.session_state.completed_action == "ask")
with right:
    stage_card(5, "📝 Summarize PDF", "Generate a summary using Groq",
               st.session_state.completed_action == "summary")

st.divider()


# --------------------------------------------------
# 3. RESET ACTIVE DOCUMENT (BACKEND + FRONTEND)
# --------------------------------------------------

def reset_current_document():
    try:
        response = requests.post(f"{API_URL}/reset", timeout=30)
        if not response.ok:
            st.error(f"Backend reset failed: {response.text}")
            return False
    except requests.RequestException as error:
        st.error(f"Could not reset the backend: {error}")
        return False

    st.session_state.processed = False
    st.session_state.filename = ""
    st.session_state.last_answer = None
    st.session_state.summary = None
    st.session_state.completed_action = None
    st.session_state.pages = 0
    st.session_state.chunks = 0
    st.session_state.current_history_id = None
    st.session_state.pop("question_input", None)
    st.session_state.pop("pdf_uploader", None)
    return True


# --------------------------------------------------
# 4. SIDEBAR: UPLOAD AND RESET
# --------------------------------------------------

with st.sidebar:
    st.header("📂 Documents")

    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        accept_multiple_files=False,
        key="pdf_uploader",
    )

    if st.button("⚙️ Process Document", type="primary",
                 use_container_width=True):
        if uploaded_file is None:
            st.warning("Please upload a PDF first.")
        else:
            payload = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf",
                )
            }
            try:
                with st.spinner("Processing your PDF..."):
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=payload,
                        timeout=600,
                    )

                if response.ok:
                    result = response.json()
                    st.session_state.processed = True
                    st.session_state.filename = result.get(
                        "filename", uploaded_file.name
                    )
                    st.session_state.pages = result.get("pages_processed", 0)
                    st.session_state.chunks = result.get("chunks_created", 0)
                    st.session_state.last_answer = None
                    st.session_state.summary = None
                    st.session_state.completed_action = None

                    history_id = str(uuid4())
                    st.session_state.current_history_id = history_id
                    st.session_state.history.insert(0, {
                        "id": history_id,
                        "filename": st.session_state.filename,
                        "time": datetime.now().strftime("%d-%m-%Y %I:%M %p"),
                        "pages": st.session_state.pages,
                        "chunks": st.session_state.chunks,
                        "activities": [],
                    })

                    record_activity(
                        "Process PDF",
                        answer=(
                            f"Successfully processed {st.session_state.filename}. "
                            f"Pages: {st.session_state.pages}; "
                            f"text chunks: {st.session_state.chunks}."
                        ),
                    )
                    st.success("PDF processed successfully!")
                    st.rerun()
                else:
                    st.error(f"Upload failed: {response.text}")

            except requests.RequestException as error:
                st.error(f"Could not connect to FastAPI: {error}")

    if st.session_state.processed:
        st.divider()
        st.subheader("✅ Current Document")
        st.write(f"📄 {st.session_state.filename}")
        st.metric("Pages processed", st.session_state.pages)
        st.metric("Text chunks", st.session_state.chunks)

        if st.button("🔄 Reset Current Document", use_container_width=True):
            if reset_current_document():
                st.success("Current document reset. History has been kept.")
                st.rerun()


# --------------------------------------------------
# 5. FEATURE TABS
# --------------------------------------------------

tab_ask, tab_summary, tab_history = st.tabs([
    "💬 Ask Questions",
    "📝 Summarize Documents",
    "📜 File Assessment History",
])


# --------------------------------------------------
# 6. ASK QUESTIONS
# --------------------------------------------------

with tab_ask:
    st.subheader("💬 Ask Questions")

    if not st.session_state.processed:
        st.info("Upload and process a PDF from the sidebar first.")
    else:
        st.caption(f"Current document: {st.session_state.filename}")
        question = st.text_area(
            "Enter your question about the PDF",
            placeholder="Example: What is Python used for?",
            key="question_input",
        )

        if st.button("🔍 Get Answer", type="primary"):
            if not question.strip():
                st.warning("Please enter a question.")
            else:
                try:
                    with st.spinner("Finding your answer..."):
                        response = requests.post(
                            f"{API_URL}/ask",
                            json={"question": question.strip()},
                            timeout=300,
                        )

                    if response.ok:
                        result = response.json()
                        st.session_state.last_answer = result
                        st.session_state.completed_action = "ask"
                        record_activity(
                            "Ask Questions",
                            question=question.strip(),
                            answer=result.get("answer", ""),
                        )
                        st.rerun()
                    else:
                        st.error(f"Question failed: {response.text}")

                except requests.RequestException as error:
                    st.error(f"Could not connect to FastAPI: {error}")

        if st.session_state.last_answer:
            result = st.session_state.last_answer
            st.divider()
            st.subheader("🧠 Answer")
            st.markdown(result.get("answer", "No answer returned."))
            st.subheader("📚 Sources")

            sources = result.get("sources", [])
            if sources:
                for source in sources:
                    st.write(
                        f"📄 {source.get('file', 'Unknown')} — "
                        f"Page {source.get('page', 'Unknown')}"
                    )
            else:
                st.info("No sources were returned.")


# --------------------------------------------------
# 7. SUMMARIZE DOCUMENT
# --------------------------------------------------

with tab_summary:
    st.subheader("📝 Document Summary")

    if not st.session_state.processed:
        st.info("Upload and process a PDF from the sidebar first.")
    else:
        st.caption(f"Current document: {st.session_state.filename}")

        if st.button("✨ Generate Summary", type="primary"):
            try:
                with st.spinner("Generating PDF summary..."):
                    response = requests.post(
                        f"{API_URL}/summarize",
                        timeout=600,
                    )

                if response.ok:
                    result = response.json()
                    summary_text = result.get("summary", "No summary returned.")
                    st.session_state.summary = summary_text
                    st.session_state.completed_action = "summary"
                    record_activity(
                        "Generate Summary",
                        answer=summary_text,
                    )
                    st.rerun()
                else:
                    st.error(f"Summary failed: {response.text}")

            except requests.RequestException as error:
                st.error(f"Could not connect to FastAPI: {error}")

        if st.session_state.summary:
            st.divider()
            st.subheader("📖 Generated Summary")
            st.markdown(st.session_state.summary)


# --------------------------------------------------
# 8. FILE ASSESSMENT HISTORY
# --------------------------------------------------

with tab_history:
    st.subheader("📜 File Assessment History")
    st.write(
        "Click a filename to view the tasks performed, questions asked, "
        "answers, and generated summaries."
    )

    history = st.session_state.history

    if not history:
        st.info("No history available yet. Process a PDF to create an entry.")
    else:
        st.metric("Total processed entries", len(history))

        for index, item in enumerate(history, start=1):
            with st.expander(f"📄 {item['filename']} — {item['time']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Pages", item["pages"])
                with col2:
                    st.metric("Text chunks", item["chunks"])

                st.divider()
                st.markdown("### 📝 Tasks and Questions")
                activities = item.get("activities", [])

                if not activities:
                    st.info("No tasks have been recorded for this file yet.")
                else:
                    for task_number, activity in enumerate(activities, start=1):
                        st.markdown(
                            f"#### {task_number}. {activity['task']}"
                        )
                        st.caption(
                            f"Time: {activity['time']} | "
                            f"Status: {activity['status']}"
                        )

                        if activity.get("question"):
                            st.markdown("**Question asked:**")
                            st.write(activity["question"])

                        if activity.get("answer"):
                            label = (
                                "AI Answer:"
                                if activity["task"] == "Ask Questions"
                                else (
                                    "Generated Summary:"
                                    if activity["task"] == "Generate Summary"
                                    else "Details:"
                                )
                            )
                            st.markdown(f"**{label}**")
                            st.markdown(activity["answer"])

                        st.divider()

        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.success("File assessment history cleared.")
            st.rerun()
