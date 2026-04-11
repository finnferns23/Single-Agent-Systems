# 📈 Stock Market RAG Agent (2024)

This project implements an intelligent **Retrieval-Augmented Generation (RAG) Agent** designed to answer questions related to **Stock Market Performance in 2024**.  
The system loads a PDF report, processes it into vector embeddings, and uses a **LangGraph-driven multi-step agent loop** to reason, retrieve, and respond with accurate, citation-backed information.

---

## 🚀 Key Features

### 🔍 Retrieval-Augmented Generation  
- PDF ingestion and parsing using **PyPDFLoader**  
- Automated chunking using **RecursiveCharacterTextSplitter**  
- Embedding via **text-embedding-3-small**  
- Vectorstore persistence with **ChromaDB**

### 🤖 LangGraph-Based Agent  
- Conditional looping between LLM and tool execution  
- Tool-enabled reasoning  
- Smart detection of when retrieval is needed  
- Reliable, low-hallucination LLM configuration (`temperature=0`)

### 🧠 Accurate Answers With Citations  
The agent retrieves multiple document chunks and cites them directly in its responses.

---

## 📂 Project Structure

```
.
├── Stock_Market_Agent.py                 # Main RAG agent script
├── Stock_Market_Performance_2024.pdf     # Source PDF (required)
├── persist/ (auto-generated)             # ChromaDB persistent storage
└── README.md                             # Project documentation
```

---

## 📦 Requirements Installation

Install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Setup

Create a `.env` file:

```
OPENAI_API_KEY=your_openai_api_key_here
```

---

## ▶️ Usage

Run the agent:

```bash
python Stock_Market_Agent.py
```

---

## 🧬 How the Agent Works (Architecture)

1. Load PDF  
2. Split into chunks  
3. Embed and persist into Chroma vectorstore  
4. Expose retriever tool  
5. LangGraph agent flow:
   - LLM receives user input  
   - Decides whether retrieval is required  
   - Executes tool calls  
   - Loops until no more tools needed  
6. Returns final answer

---

## 📄 License

This project is provided for learning, experimentation, and RAG-based analysis.
