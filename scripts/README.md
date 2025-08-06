# Streamlit POC clients for the LLMKG project

## Requirements

- python 3.12+

## Getting started

### 1. Create a virtual environment
```bash
uv venv
```

### 2. Set up environment variables
Copy the example environment file and add your OpenAI API key:
```bash
cp .env.example .env
```

Then add your OpenAI API key to the `.env` file.

### 3. Install dependencies
```bash
uv sync
```

## Scripts

### Run the LLMKG Streamlit POC
```bash
uv run streamlit run poc_llm_knowledge_graph.py
```

### Run the LLM subject populator script
```bash
uv run python subjpopulate.py
```
