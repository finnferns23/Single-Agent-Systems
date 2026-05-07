
# Legal Document Review Application with LangChain & Chroma

## Overview

This project is a **Legal Document Review Application** built with **LangChain**, **Chroma**, and **Streamlit**.
It allows users to upload legal documents (PDF, DOCX, TXT), extract and process text, and receive:

* **Concise summaries** of documents
* **Context-aware answers** to specific legal questions
* **Crucial contract information** (key dates, obligations, payment terms, confidentiality clauses)

The app leverages **Retrieval-Augmented Generation (RAG)** pipelines with modern language models to simplify legal review tasks.

---

## Problem Statement

Legal professionals often spend significant time manually reviewing lengthy contracts to identify key clauses, obligations, and risks.
This process is **time-consuming, error-prone, and costly**.

The application automates this workflow by:

* Extracting and processing text from legal documents
* Summarizing contracts into actionable insights
* Providing answers to specific legal questions based on document context
* Extracting structured, crucial contract information

---

## Objectives

* Enable PDF, DOCX, and TXT uploads through a web interface
* Extract, chunk, and embed text for semantic search
* Implement a **RAG pipeline** for document-specific Q\&A
* Generate clear, structured document summaries
* Securely handle API keys via `.env`
* Provide error handling for unsupported/invalid files
* Enable download of results in **CSV, JSON, or PDF**

---

## Features

* Upload and preview legal documents
* Automated **text extraction & chunking**
* **Semantic search** and context-aware Q\&A
* AI-generated **document summaries**
* **Crucial contract info extraction** (start/end dates, payment terms, non-negotiables, confidentiality)
* Download results in multiple formats: CSV, JSON, PDF
* Session memory with **Chroma vector database** for embeddings
* Clear UI guidance for unsupported formats

---

## Tech Stack

* **LangChain** – text processing, prompts, and chains
* **Chroma** – vector database for semantic retrieval
* **Streamlit** – frontend for file upload, Q\&A, and downloads
* **OpenAI GPT models** – embeddings and natural language understanding
* **PyPDF2 / Docx2txt** – document loading
* **dotenv** – API key management

---

## Setup Instructions

1. **Create and activate a virtual environment**

```bash
python -m venv venv
source venv/bin/activate   # macOS/Linux
venv\Scripts\activate      # Windows
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Set up your OpenAI API key**
   Create a `.env` file in the project root and add:

```bash
OPENAI_API_KEY=your_openai_api_key
```

4. **Run the application**

```bash
streamlit run app.py
```

---

## File Structure

```plaintext
├── app.py               # Main Streamlit app
├── .env                 # API key (not committed)
├── requirements.txt     # Python dependencies
├── chroma_store/        # Chroma vector DB files
└── README.md            # Project documentation
```

---

## LangChain Concepts Used

* **Document Loading** – PyPDFLoader, Docx2txtLoader, TextLoader
* **Text Splitting** – RecursiveCharacterTextSplitter
* **Embeddings** – OpenAI Embeddings
* **Vector DB** – Chroma for semantic search
* **RAG Pipeline** – Retrieval + Q\&A + Summarization + Crucial Info Extraction
* **Chains** – For structured summarization, question answering, and info extraction

---

## Example Prompts

* Upload a service agreement → “What are the termination terms?”
* Upload an NDA → “What is the confidentiality period?”
* Upload a licensing contract → “Summarize obligations, payment terms, and crucial clauses.”

---

## Ideal For

* Lawyers and legal teams
* Compliance & contract management professionals
* AI demos for legal tech solutions
* Academic projects on **LangChain + RAG pipelines**

---

This application demonstrates how AI can transform **manual contract review** into a **faster, more accurate, and scalable process**.
