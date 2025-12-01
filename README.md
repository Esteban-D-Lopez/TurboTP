# TurboTP: AI-Powered Transfer Pricing Workspace

TurboTP is an advanced, agentic AI workspace designed to revolutionize Transfer Pricing (TP) consulting. Built on **Google Gemini 2.5 Flash** and **LangGraph**, it employs a multi-agent "Plan-and-Execute" architecture to handle complex workflows like deep regulatory research, documentation drafting, and strategic advisory.

![Architecture Diagram](langgraph_architecture.png)

## 🚀 Key Features

### 1. 🧠 Research Center (Deep Research)
Unlike standard chatbots, the Research Center doesn't just guess. It acts like a senior analyst:
*   **Planning**: Breaks down complex queries (e.g., "Compare US vs OECD methods for intangibles") into a step-by-step research plan.
*   **Execution**: Systematically executes each step using **Web Search**, **Regulatory Knowledge Base**, and **YouTube**.
*   **Synthesis**: Combines findings into a comprehensive, cited report.
*   **Smart Follow-ups**: Remembers context, allowing you to ask "Summarize this in a table" without re-doing the research.

### 2. 📝 Document Composer (Drafting)
Automates the creation of TP documentation (Local Files, Master Files).
*   **Data Ingestion**: Upload Financials (Excel/CSV), Interview Notes (PDF/Docx), and previous reports.
*   **Section-Specific Planning**: Generates a drafting plan based on the specific section (e.g., "Functional Analysis") and available data.
*   **Drafting**: Produces high-quality, compliant text ready for review.

### 3. 🤖 Agent Assistant (Advisory & RAG)
A conversational expert for quick questions and internal knowledge management.
*   **Knowledge Base**: Upload your own internal documents (Intercompany Agreements, Policies, Past Audits) via the sidebar.
*   **RAG (Retrieval-Augmented Generation)**: The agent searches BOTH the external regulatory database (IRC 482, OECD) and your uploaded internal documents to provide accurate answers.
*   **Source Attribution**: Clearly cites whether info came from the Web, Regulations, or Internal Docs.

### 4. 🔍 Observability
*   **Arize Phoenix Integration**: Full tracing of agent thought processes, tool calls, and latency.
*   **Visual Debugging**: See exactly what the agents are planning and executing in real-time.

---

## 🛠️ Architecture

TurboTP uses a **Plan-and-Execute** pattern for complex tasks:
1.  **Supervisor**: Routes the user's request to the appropriate team (Research, Composer, or Assistant).
2.  **Planner**: Breaks the goal into atomic steps.
3.  **Executor**: Performs the steps using tools (Search, Vector DB, File Processing).
4.  **Replanner**: Monitors progress and adjusts the plan if steps fail or new information is found.
5.  **Synthesizer**: Compiles the final result.

---

## 💻 Setup & Installation

### Prerequisites
*   Python 3.10+
*   Google Cloud API Key (Gemini)
*   Google Programmable Search Engine ID (for Web Search)

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Esteban-D-Lopez/TurboTP.git
    cd TurboTP
    ```

2.  **Create Virtual Environment**:
    ```bash
    conda create -n turbotp python=3.11 -y
    conda activate turbotp
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Create a `.env` file in the root directory:
    ```env
    GOOGLE_API_KEY=your_gemini_api_key
    GOOGLE_CSE_ID=your_search_engine_id
    PHOENIX_API_KEY=your_phoenix_key  # Optional
    ```

### Running the App

```bash
streamlit run main.py
```

---

## 📖 Usage Guide

### Using the Research Center
1.  Select **Research Center** from the sidebar.
2.  Choose a Jurisdiction (US, OECD) and Topic.
3.  Click **Start Research**.
4.  Watch the agent generate a plan and execute steps.
5.  Ask follow-up questions like "Make a table of these methods" to refine the output.

### Using the Knowledge Base
1.  Select **Agent Assistant**.
2.  Open the **Knowledge Base** sidebar.
3.  Upload your PDF/Docx files (e.g., "Intercompany_Agreement_2024.pdf").
4.  Ask the assistant: "What are the payment terms in our intercompany agreement?"

---

## 📄 License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
