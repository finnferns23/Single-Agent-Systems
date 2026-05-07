# Import necessary libraries
import os
import re
import shutil
import streamlit as st
import pandas as pd
import json
from io import BytesIO
from fpdf import FPDF
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnableMap

# Environment Setup
load_dotenv()

# Configure OpenAI API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    st.error("❌ Please set your OPENAI_API_KEY in a .env file")
    st.stop()

# Model Setup
llm = ChatOpenAI(
    model="gpt-3.5-turbo",
    temperature=0.2,
    openai_api_key=OPENAI_API_KEY
)

# Embedding model
embedding_model = OpenAIEmbeddings(
    model="text-embedding-3-large",
    openai_api_key=OPENAI_API_KEY
)

# Vector Store Setup
VECTOR_STORE_DIR = "chroma_store"
os.makedirs(VECTOR_STORE_DIR, exist_ok=True)

vectorstore = Chroma(
    persist_directory=VECTOR_STORE_DIR,
    embedding_function=embedding_model
)

# Extract text from uploaded files
def extract_text_from_file(file):
    temp_file_path = f"temp_{file.name}"
    with open(temp_file_path, "wb") as f:
        f.write(file.getbuffer())

    file_extension = os.path.splitext(file.name)[1].lower()
    try:
        if file_extension == ".pdf":
            loader = PyPDFLoader(temp_file_path)
        elif file_extension == ".docx":
            loader = Docx2txtLoader(temp_file_path)
        elif file_extension == ".txt":
            loader = TextLoader(temp_file_path)
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")

        documents = loader.load()
        text = " ".join([doc.page_content for doc in documents])
        return text, documents
    finally:
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)

# Text splitting
def split_text(docs):
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    return splitter.split_documents(docs)

# Store legal document in vector store
def store_legal_document(docs, doc_id):
    chunks = split_text(docs)
    vectorstore.add_documents(
        chunks,
        ids=[f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    )
    vectorstore.persist()

# RAG Functions
def answer_question(question):
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
    retrieved_docs = retriever.get_relevant_documents(question)
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    prompt_template = PromptTemplate(
        input_variables=["context", "question"],
        template="""
        You are a legal assistant. Use the provided context to answer the question.

        Context:
        {context}

        Question:
        {question}

        Answer clearly and concisely. If unsure, say so.
        """
    )

    chain = (
        RunnableMap({
            "context": lambda x: x["context"],
            "question": lambda x: x["question"]
        })
        | prompt_template
        | llm
        | StrOutputParser()
    )
    return chain.invoke({"context": context, "question": question})

# Summarization of Legal Documents
def summarize_document():
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    retrieved_docs = retriever.get_relevant_documents("Summarize this legal document")
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="""
        You are a legal assistant. Provide a **clear and structured summary overview** 
        of the legal document. Highlight key clauses, obligations, risks, payment terms, 
        and any unusual provisions. Summarize in a way that gives a decision-maker a 
        quick but reliable understanding of the document.

        Context:
        {context}

        Summary:
        """
    )
    chain = prompt_template | llm | StrOutputParser()
    return chain.invoke({"context": context})

# Retrieve Crucial Info
def retrieve_crucial_info():
    retriever = vectorstore.as_retriever(search_kwargs={"k": 8})
    retrieved_docs = retriever.get_relevant_documents(
        "Retrieve crucial contract information and key clauses"
    )
    context = "\n".join([doc.page_content for doc in retrieved_docs])

    prompt_template = PromptTemplate(
        input_variables=["context"],
        template="""
        You are a legal assistant. Retrieve **crucial structured contract information** in one line each:

        - Start Date
        - Expiration Date
        - Non-Negotiables
        - Payment Terms (amounts, due dates, penalties)
        - Confidential Details (confidentiality clauses, fine print, private data)

        If something is missing, explicitly say: "Not applicable".

        Context:
        {context}

        Crucial Contract Information:
        """
    )
    chain = prompt_template | llm | StrOutputParser()
    raw_output = chain.invoke({"context": context})

    results = {
        "start_date": re.search(r"Start Date[:\-]?\s*(.*)", raw_output, flags=re.IGNORECASE),
        "expiration_date": re.search(r"(Expiration Date|End Date)[:\-]?\s*(.*)", raw_output, flags=re.IGNORECASE),
        "non_negotiables": re.search(r"Non[- ]?Negotiables[:\-]?\s*(.*)", raw_output, flags=re.IGNORECASE),
        "payments": re.search(r"Payment Terms[:\-]?\s*(.*)", raw_output, flags=re.IGNORECASE),
        "confidential": re.search(r"Confidential Details[:\-]?\s*(.*)", raw_output, flags=re.IGNORECASE),
    }

    structured = {
        "Start Date": results["start_date"].group(1).strip() if results["start_date"] else "Not applicable",
        "Expiration Date": results["expiration_date"].group(2).strip() if results["expiration_date"] else "Not applicable",
        "Non-Negotiables": results["non_negotiables"].group(1).strip() if results["non_negotiables"] else "Not applicable",
        "Payment Terms": results["payments"].group(1).strip() if results["payments"] else "Not applicable",
        "Confidential Details": results["confidential"].group(1).strip() if results["confidential"] else "Not applicable",
    }
    return structured

# Generate download files
def generate_download_files(question, answer, summary, structured):
    # CSV
    csv_buffer = BytesIO()
    rows = [
        ["Question", question],
        ["Answer", answer],
        ["Summary", summary]
    ]
    for key, val in structured.items():
        rows.append([key, val])
    df_csv = pd.DataFrame(rows, columns=["Field", "Details"])
    df_csv.to_csv(csv_buffer, index=False)
    csv_bytes = csv_buffer.getvalue()

    # JSON
    json_data = {
        "Question": question,
        "Answer": answer,
        "Summary": summary,
        "Crucial Info": structured
    }
    json_bytes = json.dumps(json_data, indent=4).encode('utf-8')

    # PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 7, f"Question: {question}\n\nAnswer: {answer}\n\nSummary:\n{summary}\n\nCrucial Info:\n")
    for key, val in structured.items():
        pdf.multi_cell(0, 7, f"{key}: {val}")

    # Corrected PDF output to bytes
    pdf_bytes = pdf.output(dest='S').encode('latin1')

    return csv_bytes, json_bytes, pdf_bytes

# Streamlit UI
def main():
    st.set_page_config(page_title="Legal Document Review App", layout="wide")
    st.title("📑 Legal Document Review with OpenAI + Chroma")

    col1, col2 = st.columns(2)
    with col1:
        st.header("Upload Legal Document")
        uploaded_file = st.file_uploader("Upload a document", type=["pdf", "docx", "txt"])

    with col2:
        st.header("Ask a Question")
        question = st.text_input("Enter your question about the document")

    answer, summary, structured = "", "", {}

    if uploaded_file:
        with st.spinner("Processing document..."):
            text, documents = extract_text_from_file(uploaded_file)
            with st.expander("📄 View Extracted Text"):
                st.text(text[:3000])
            doc_id = os.path.splitext(uploaded_file.name)[0]
            store_legal_document(documents, doc_id)
            st.success("✅ Document stored in vector database.")

    if question:
        with st.spinner("Answering your question..."):
            answer = answer_question(question)
            st.header("💡 AI Answer")
            st.markdown(answer)

    if st.button("Summarize Document"):
        with st.spinner("Generating summary..."):
            summary = summarize_document()
            with st.expander("📋 Document Summary", expanded=False):
                st.markdown(summary)

    if st.button("Retrieve Crucial Info"):
        with st.spinner("Extracting crucial contract info..."):
            structured = retrieve_crucial_info()
            st.header("📊 Crucial Contract Information")

            table_data = []
            for key, value in structured.items():
                if value == "Not applicable":
                    table_data.append([key, "⚠️ Not applicable"])
                else:
                    table_data.append([key, f"✅ {value}"])
            df = pd.DataFrame(table_data, columns=["Field", "Details"])

            def highlight_row(row):
                if "⚠️" in row["Details"]:
                    return ["background-color: #fff3cd"] * len(row)
                elif "✅" in row["Details"]:
                    return ["background-color: #d4edda"] * len(row)
                return [""] * len(row)

            st.dataframe(df.style.apply(highlight_row, axis=1), use_container_width=True)

    # Download Section
    if answer or summary or structured:
        st.subheader("💾 Download All Results")
        file_type = st.selectbox("Select file type", ["CSV", "JSON", "PDF"])
        csv_bytes, json_bytes, pdf_bytes = generate_download_files(question, answer, summary, structured)

        if file_type == "CSV":
            st.download_button("Download CSV", data=csv_bytes, file_name="legal_review.csv", mime="text/csv")
        elif file_type == "JSON":
            st.download_button("Download JSON", data=json_bytes, file_name="legal_review.json", mime="application/json")
        else:
            st.download_button("Download PDF", data=pdf_bytes, file_name="legal_review.pdf", mime="application/pdf")

# Run App
if __name__ == "__main__":
    main()
