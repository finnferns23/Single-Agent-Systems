
# Document Drafter System
A lightweight document drafting system that blends human instructions with AI-driven editing. The system allows users to iteratively build, update, and save documents through natural dialogue. It uses LangGraph to manage conversational state, LangChain to structure messages and tools, and OpenAI models to drive reasoning and text generation.

---

## 🚀 Features

- **Interactive drafting loop** – The agent repeatedly asks for user instructions.
- **Human-in-the-loop editing** – Updates occur only when instructed by the user.
- **Two built-in tools**  
  - `update(content)`: Replace entire document content.  
  - `save(filename)`: Save final output to a `.txt` file and end the workflow.
- **Stateful conversation management** powered by LangGraph.
- **System prompt injects current document state** so the agent always knows the document content.
- **Automatic stop condition** – Workflow ends once a save tool message is detected.

---

## 📂 Project Structure

```
Document_Drafter.py
Document Drafter System.pdf
```

- `Document_Drafter.py` — Full implementation of the drafting agent.  
- PDF — Design explanation describing the system flow.

---

## 🧠 How It Works (Summary)

1. **Start**  
   The LangGraph workflow initiates and enters the `agent` node.

2. **Agent Interaction**  
   The agent (LLM) reviews the current document state, asks the user what to do next, and decides if a tool needs to be called.

3. **Tool Calls**  
   - `update` → Replaces document content → loop continues.  
   - `save` → Writes a `.txt` file → workflow ends.

4. **Finish**  
   Once the save event is triggered, the graph routes directly to `END`.

---

## 🛠️ Usage

Run the drafting system with:

```bash
python Document_Drafter.py
```

You'll see an interactive console loop:

1. AI asks what you'd like to do.
2. You can enter:

   * “update this with…”  
   * “change paragraph…”  
   * “save as final_draft.txt”
3. System executes the command, updates the document, and shows the content.
4. Saving ends the workflow automatically.

---

## 🔧 Tools

### `update(content: str)`

Replaces the entire document with your new content.

### `save(filename: str)`

Saves the current document to a text file and finishes the workflow.

---

## 🧩 Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

Make sure to create a `.env` file with your OpenAI API key:

```
OPENAI_API_KEY=your_key_here
```

---

## 📘 Technologies Used

* **Python**
* **LangChain**
* **LangChain OpenAI wrapper**
* **LangGraph**
* **python-dotenv**
* **OpenAI API**
* **Typing, Logging, and standard Python libraries**

---

## 📄 License

This project is for educational and workflow-automation purposes.
