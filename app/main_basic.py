
import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="Document Analysis Agent",
    page_icon="📚",
    layout="wide"
)

st.title("📚 Document Analysis Agent")
st.write(
    "Upload a PDF, ask questions about its content, "
    "or generate an AI summary."
)

# Initialize session state
if "processed" not in st.session_state:
    st.session_state.processed = False

if "filename" not in st.session_state:
    st.session_state.filename = ""

if "last_answer" not in st.session_state:
    st.session_state.last_answer = None

if "summary" not in st.session_state:
    st.session_state.summary = None


# Sidebar: Upload PDF
with st.sidebar:
    st.header("📂 Documents")

    uploaded_file = st.file_uploader(
        "Upload a PDF file",
        type=["pdf"],
        accept_multiple_files=False
    )

    if st.button("Process Document", type="primary"):
        if uploaded_file is None:
            st.warning("Please upload a PDF first.")

        else:
            payload = {
                "file": (
                    uploaded_file.name,
                    uploaded_file.getvalue(),
                    "application/pdf"
                )
            }

            try:
                with st.spinner("Processing your PDF..."):
                    response = requests.post(
                        f"{API_URL}/upload",
                        files=payload,
                        timeout=600
                    )

                if response.ok:
                    result = response.json()

                    st.session_state.processed = True
                    st.session_state.filename = result.get(
                        "filename", uploaded_file.name
                    )
                    st.session_state.last_answer = None
                    st.session_state.summary = None

                    st.success("PDF processed successfully!")

                    st.write(
                        f"Pages processed: "
                        f"{result.get('pages_processed', 0)}"
                    )
                    st.write(
                        f"Text chunks created: "
                        f"{result.get('chunks_created', 0)}"
                    )

                else:
                    st.error(
                        f"Upload failed: {response.text}"
                    )

            except requests.RequestException as error:
                st.error(
                    f"Could not connect to FastAPI: {error}"
                )

    if st.session_state.processed:
        st.divider()
        st.subheader("✅ Uploaded Document")
        st.write(f"📄 {st.session_state.filename}")


# Show features only after successful PDF processing
if not st.session_state.processed:
    st.info(
        "👈 Upload a PDF in the sidebar and click "
        "**Process Document** to get started."
    )

else:
    st.success(
        "Your document is ready! Choose what you want to do below."
    )

    feature = st.radio(
        "Choose a feature",
        ["Ask Questions", "Summarize Documents"],
        horizontal=True,
        key="selected_feature"
    )

    # Ask Questions
    if feature == "Ask Questions":
        st.subheader("💬 Ask Questions")

        question = st.text_area(
            "Enter your question about the PDF",
            placeholder="Example: What is Python used for?",
            key="question_input"
        )

        if st.button("Get Answer"):
            if not question.strip():
                st.warning("Please enter a question.")

            else:
                try:
                    with st.spinner("Finding your answer..."):
                        response = requests.post(
                            f"{API_URL}/ask",
                            json={"question": question.strip()},
                            timeout=300
                        )

                    if response.ok:
                        st.session_state.last_answer = (
                            response.json()
                        )
                    else:
                        st.error(response.text)

                except requests.RequestException as error:
                    st.error(
                        f"Could not connect to FastAPI: {error}"
                    )

        # Display answer and sources
        if st.session_state.last_answer:
            result = st.session_state.last_answer

            st.subheader("🧠 Answer")
            st.markdown(result["answer"])

            st.subheader("📚 Sources")

            for source in result.get("sources", []):
                st.write(
                    f"📄 {source['file']} — "
                    f"Page {source['page']}"
                )

    # Summarize Documents
    else:
        st.subheader("📝 Document Summary")

        if st.button("Generate Summary"):
            try:
                with st.spinner("Generating PDF summary..."):
                    response = requests.post(
                        f"{API_URL}/summarize",
                        timeout=600
                    )

                if response.ok:
                    st.session_state.summary = (
                        response.json()["summary"]
                    )
                else:
                    st.error(response.text)

            except requests.RequestException as error:
                st.error(
                    f"Could not connect to FastAPI: {error}"
                )

        if st.session_state.summary:
            st.markdown("---")
            st.subheader("📖 Generated Summary")
            st.markdown(st.session_state.summary)
