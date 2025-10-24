# RAG Knowledge Bot - Simple Query Only

Overview

This project demonstrates how to build a fully local AI agent using Python, leveraging:
- Ollama for running open‐source large language models locally
- LangChain for orchestrating retrieval & generation workflows
- A vector store + retrieval-augmented generation (RAG) architecture to ground responses in your own documents

With this setup, you’ll be able to load your local CSV data , embed it, store it in a vector database, then ask questions and have the system retrieve relevant chunks and generate answers.

For simple query only, does not include filtering, sql injection, chunking etc, different data type.

## Features

- Run a model locally (no cloud API required) via Ollama
- Ingest arbitrary data (e.g., text files, CSV, PDFs) into a vector store
- Build a “retriever + LLM” chain: retrieve relevant context → feed to LLM → answer the user
- Optional: build a simple agent that picks tools / functions based on the query

## Prerequisites
- Operating system: Windows / macOS / Linux (with sufficient RAM/CPU or GPU for the model)
- Python 3.9+
- Docker (if using a vector store container)
- Installed Ollama and pulled required model(s)
- Basic familiarity with Python and virtual environments

## Setup Instructions

### 1. Install Ollama & pull models

1. Install Ollama by following instructions on its website.

2. Pull your chosen LLM and embedding model, for example:

   ```
   ollama serve  
   ollama pull llama3  
   ollama pull mxbai-embed-large  
   ```

### 2. Create & activate a Python environment

```
python -m venv .venv  
source .venv/bin/activate   # or .venv\Scripts\activate on Windows  
pip install --upgrade pip  
```

### 3. Install dependencies

```
pip install langchain langchain-ollama your-vectorstore-module pandas  
```

### 4. Prepare your data

Place your dataset in a folder (e.g., `knowledgebase/`). For example, if you have a `reviews.csv`, make sure it has text + metadata columns.

### 5. Embed & store documents

In your code (e.g., `main.py`)

1. load your dataset
2. convert rows into `Document` objects (with `page_content`, `metadata`, `id`).
3. Create embeddings using Ollama embedding model.
4. Instantiate a vectorstore, add the documents.

### 6. Build retrieval & generation pipeline

- Create a `Retriever` (via your vectorstore) that given a query returns top k relevant documents.
- Create a prompt template that includes the retrieved context plus user question.
- Use the LLM (via Ollama) to generate an answer.

### 7. Optional: Build an Agent with tools

If desired, you can build a more advanced agent (via LangChain Agent APIs) that:

- Analyses the user query
- Chooses whether to call a tool/function (e.g., convert date, search web, etc)
- Uses retrieval + LLM to form answer

### 8. Run the application

```
python main.py  
```

Enter a question when prompted; the system will retrieve context and generate an answer.

## Project Structure

```
/project-root
  ├── knowledgebase/
      └── your_dataset.csv
  ├── main.py
  ├── vectorstore_utils.py
  ├── docs/
  ├── README.md
  └── requirements.txt
```

## Usage Example

```
> Enter your question (or 'exit'): When is the next meeting for Project Alpha?
The next meeting for Project Alpha is scheduled for 2026-05-13, and there are 372 days remaining until the meeting.
```

## Customization

- Swap in different LLMs or embedding models (via Ollama).
- Use different vector stores (ChromaDB, FAISS, SingleStore, etc).
- Use different document loaders (CSV, PDF, website scrape).
- Enhance prompts, change agent logic, add memory, streaming responses, etc.

## Troubleshooting & Tips

- Make sure your vectorstore index is generated before retrieval.
- Aim for small chunk sizes when splitting documents to improve retrieval relevance.
- Monitor context window of the LLM: don’t pass too much text.
- For large datasets, building/updating the vectorstore may take significant time.


## FAQ

Feeding raw CSV data to an LLM is a good use of resources. LLMs and RAG are not great at raw data analytics and it will cost a ton in tokens. Better strategy would be to dump Excel data into Sqlite3 and instruct the LLM to run SQL queries on that database.

1. 1. When querying for rating 1, it returns rating 5 or Langchain query not retunring all the sources of the queries, eg, asking for rating 1, returns only one source even though there are multiple rows with rating 1.
   - Langchain is a simlarity text retreival, not filtering. The filtering have to be done seperately before chaining to the LLM. Can use manually filter at vector or use SelfQueryRetriever that interprets the user’s question to infer the appropriate filter.


# Reference
1. https://python.langchain.com/docs/tutorials/sql_qa/