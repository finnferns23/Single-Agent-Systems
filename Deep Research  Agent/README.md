# **Deep Research Agent**
A multi-agent system that automates end-to-end research: planning searches, gathering insights, synthesizing long-form reports, and delivering results via email — all through a simple Gradio interface.


## 🚀 Overview
This project uses a coordinated set of agents to transform any user query into a complete research workflow. The system:
* Plans the most relevant web searches
* Executes searches in parallel
* Summarizes findings
* Generates a detailed long-form report
* Sends the final report via email
* Runs everything through an easy web UI

Built with async orchestration, LangChain-style agents, and OpenAI models.


## 🧠 System Architecture

```
User Query
   │
   ▼
Planner Agent → Generates 5 search terms
   │
   ▼
Search Agent → Executes searches & summarizes results
   │
   ▼
Writer Agent → Produces long-form markdown report
   │
   ▼
Email Agent → Converts report to HTML + sends via SendGrid
   │
   ▼
Output to user (UI + email)
```

The **ResearchManager** orchestrates the entire flow asynchronously and streams progress updates to the Gradio frontend.


## 📁 Project Structure

```
.
├── planner_agent.py
├── search_agent.py
├── writer_agent.py
├── email_agent.py
├── research_manager.py
├── deep_research_app.py   # Gradio interface
```


## ⚙️ Setup

### 1. Install dependencies
pip install -r requirements.txt

### 2. Add your environment variables
Create a `.env` file:

```
OPENAI_API_KEY=your_key
SENDGRID_API_KEY=your_key
```

### 3. Run the app
python deep_research_app.py

The interface opens in your browser automatically.


## 🧩 Agents Summary

### **Planner Agent**
Generates the most relevant search terms needed to answer the query.

### **Search Agent**
Uses a WebSearchTool to collect and summarize web information.

### **Writer Agent**
Creates a detailed, structured research report in markdown format.

### **Email Agent**
Converts the report to clean HTML and sends it via SendGrid.


## 🎛️ Usage

1. Open the Gradio UI
2. Enter a topic
3. Click **Run**
4. Watch the workflow execute step-by-step
5. Receive your detailed report on-screen and via email


## 📌 Notes

* Requires valid OpenAI + SendGrid API keys
* Ensure your SendGrid sender is verified
* Designed for async execution to speed up multi-search processing


