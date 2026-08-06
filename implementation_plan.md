# Phase 10: Integration & Chat UI

We will build the final end-to-end system: a Streamlit Chat UI connecting to a FastAPI backend, which orchestrates our CrewAI agents.

## User Review Required
> [!WARNING]
> Because `crewai` currently requires Python <3.14 (and fails to compile locally on Windows Python 3.14), we are relying on our Python 3.12 Docker container to run the agents. The FastAPI backend must run *inside* this container, and the Streamlit UI can run either locally or inside the container. 

## Proposed Changes

### 1. Backend (FastAPI)
#### [NEW] `api/main.py`
A lightweight FastAPI server running on port 8000. It will expose a single POST endpoint `/chat` that accepts a user query, invokes the CrewAI orchestrator (`agents.crew.run_crew`), and returns the finalized narrative string.

### 2. Frontend (Streamlit)
#### [NEW] `ui/app.py`
A chat interface utilizing Streamlit's `st.chat_message`. It will maintain conversation history and send the user's prompt to the FastAPI backend at `http://localhost:8000/chat`. 

### 3. Infrastructure
#### [MODIFY] `docker-compose.yml`
We will configure Docker Compose to spin up the API and expose port 8000, instead of just running a one-off CLI command.

## Verification Plan
### Manual Verification
1. Run `docker-compose up` to start the API backend.
2. Run `streamlit run ui/app.py` natively on the host.
3. Ask the system a question through the web UI and verify the response appears.
