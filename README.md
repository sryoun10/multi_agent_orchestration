# Multi-Agent Orchestration

A modular FastAPI-based orchestrator demo for secure, intent-aware routing across specialized agents.
Features retrieval-augmented generation (RAG), neural summarization, input validation, and semantic scoring.
Designed for compliance-first automation and architectural clarity.

## Features
- Intent scoring and routing via `triage_agent.py`
- Retrieval-Augmented Generation (`rag_agent.py`) using LangChain + FAISS
- Structured summarization via Hugging Face Transformers (`ml_agent.py`)
- Fallback handling through `live_agent.py`
- Stock data stub agent (`data_agent.py`)
- Input validation + logging via `input_guard.py`
- Jinja2-based UI with templated response formatting
- Token-aware RAG logic, graceful error handling, and logging throughout

## File Structure
```
multi_agent_orchestration/
├── main.py # FastAPI app and orchestration logic
├── input_guard.py # Input validation and escalation
├── agents/
|  ├── triage_agent.py # Routes intent to correct agent
|  ├── data_agent.py # Returns mock stock data
|  ├── synthesis_agent.py # Summarizes data
|  ├── ml_agent.py # Neural text summarization via transformers
|  ├── rag_agent.py # RAG pipeline using FAISS + HuggingFace embeddings
|  └── live_agent.py # Fallback response logic
├── knowledge/
|  ├── compliance.txt
│  ├── sec_policy.txt
|  └── compliance_handbook.txt
├── templates/
|  ├── index.html # Homepage form
|  └── result.html # Output rendering
├── utils/
|  └── intent_detector.py
├── escalation_log.txt # Logged escalations
├── logging_config.py # Logging setup
├── README.md # Project documentation
└── requirements.txt # Dependencies for project
```

## Setup Instructions
1. Clone the repo
2. Install dependencies:
```bash
pip install -r requirements.txt
# Run the server:
python -m uvicorn main:app --reload # OR python -m uvicorn main:app --port 8080 --reload
# Visit http://localhost:8000 or http://localhost:8080 depending on command used above
```
3. To enable RAG functionality, set your OpenAI key:
```bash
$env:OPENAI_API_KEY = "your-key-here"
```

## Usage
- Input an intent into the text field on the homepage (`index.html`), e.g.:
    - Fetch Stock Price
    - Summarize data
    - or for neural summarization:
        ```
        In Q2 2024, the company saw a 12% increase in revenue driven by strong performance in its cloud services division. Operating expenses rose slightly due to increased investment in R&D and talent acquisition. The leadership team remains optimistic about continued growth in international markets and plans to expand its product offerings in the second half of the year.
        ```
    - For an example of RAG:
        ```
        What is Rule 10b5-1 and how does it affect employee stock trading?
        ```
- Inputs are directed to one of several agents, based on weighted scoring of the input values.
- Inputs are also validated by `input_guard.py` to prevent inappropriate inputs or attacks. Try the following input to see how this works:
    ```
    DROP TABLE users
    ```
- Results are rendered on `result.html`

## Agent Routing Overview
This orchestration system uses weighted keyword scoring and governance logic to route user queries to specialized agents.
Below is the end-to-end breakdown.


### Step 1: Input Submission
- User submits query via homepage form or direct URL (/orchestrate)
- Input is first passed to input_guard.py for validation:
- Checks for SQL injection, unsafe terms, or empty payloads
- Logs escalations to escalation_log.txt
- If flagged, routes to live_agent.py

### Step 2: Intent Detection (intent_detector.py)
- Scoring logic assigns weights based on keyword matches:
```
| Intent | Sample Keywords | 
| rag_query | "sec", "compliance", "policy", "handbook", "10b5-1" | 
| ml_summarize | "analyze", "growth", "revenue", "forecast", "earnings" | 
| summarize | "summary", "summarize", "overview", "explain this" | 
| get_data | "stock", "price", "fetch", "ticker" | 
```

- Highest scoring intent is selected. If no clear match → routes to live_agent

### Triage and Routing (triage_agent.py)
- Routes intent to corresponding agent module:
```Python
if intent == "get_data":
    return "data_agent"
elif intent == "summarize":
    return "synthesis_agent"
elif intent == "ml_summarize":
    return "ml_agent"
elif intent == "rag_query":
    return "rag_agent"
elif intent == "invalid":
    return "input_guard"
elif intent == "escalate":
    return "input_guard"
else:
    return "live_agent"
```

### Step 4: Agent Execution
- rag_agent.py
    ```
    - Uses LangChain FAISS index for semantic retrieval
    - Embedded .txt knowledge sources in /knowledge/
    - Returns real-world regulatory, policy, or handbook answers
    ```
- ml_agent.py
    ```
    - Uses Hugging Face Transformer model for neural summarization
    - Optimized for structured paragraphs, earnings, reports
    ```
- live_agent.py
    ```
    - Offers fallback replies for unmatches queries
    - Can be expanded for small talk or escalation
    ```
- data_agent.py
    ```
    - Returns mock stock data (price, ticker, user)
    - Can be integrated with real-time APIs in future
    ```

### Step 5: Response Rendering (result.html)
- Displays agent response with context-aware labels.
- Includes back button and optional error

## Future Enhancements
- Vectorstore caching for persistent RAG index
- Chunk metadata display (e.g., source doc, token count)
- Session memory and multi-turn routing
- Upload UI for adding .txt retrieval sources
- Endpoint testing harness for routing accuracy across edge cases

## Author & Purpose
Steve Young - Data Engineer and AI governance enthusiast.
This demo supports transition into modular, governance-aware orchestration and portfolio-grade retrieval workflows.