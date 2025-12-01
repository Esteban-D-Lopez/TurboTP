# TurboTP: Enterprise Transfer Pricing Workspace

TurboTP is an AI-powered workspace designed for Transfer Pricing (TP) consultants. It leverages **Google Gemini 2.5 Flash** and **LangGraph** to provide a multi-agent system for research, documentation drafting, and advisory.

## Features

*   **Research Center**: Conduct deep regulatory research across jurisdictions (US, OECD, Italy, etc.).
*   **Document Composer**: Generate compliant TP documentation (Local Files, Master Files) from financial data.
*   **Agent Assistant**: Chat with a specialized TP expert agent.
*   **Observability**: Full tracing of agent logic using **Arize Phoenix**.

## Tech Stack

*   **Frontend**: Streamlit
*   **Backend**: Python, LangGraph, LangChain
*   **Model**: Gemini 2.5 Flash
*   **Database**: ChromaDB (Vector Store)
*   **Observability**: Arize Phoenix

## Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/Esteban-D-Lopez/TurboTP.git
    cd TurboTP
    ```

2.  **Create Conda Environment**:
    ```bash
    conda create -n turbotp python=3.11 -y
    conda activate turbotp
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure Environment**:
    Copy `.env.example` to `.env` and add your API keys:
    ```bash
    cp .env.example .env
    ```
    *   `GOOGLE_API_KEY`: Required for Gemini.
    *   `PHOENIX_API_KEY`: Optional, for cloud tracing.

5.  **Ingest Knowledge Base**:
    Place PDF/Text files in `data/` (optional) and run:
    ```bash
    python src/tools/ingest.py
    ```

## Running the App

```bash
streamlit run main.py
```

## License

Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0).
