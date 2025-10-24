# RAG Knowledge Bot - Simple Query Only

Overview

Answer natural-language questions over your SQL database. This project turns questions like “top 5 customers by revenue last quarter?” into SQL, runs the query, and replies with a concise answer—optionally with reasoning steps.

## Features

1. Plug in any SQL database supported by SQLAlchemy (SQLite by default)

2. LLM-driven SQL generation using LangChain chat models

3. Optional agent tools (e.g., proper-noun lookup to fix fuzzy names)

4. Quickstart with the Chinook sample DB

5. Tracing hooks for LangSmith (optional)


## Architecture

- Question → SQL (LLM drafts a syntactically correct, schema-aware query)

- Execute SQL (run against your DB via SQLAlchemy)

- Answer (LLM turns raw rows into a human response)


## Tech Stack

- Python 3.10+

- LangChain (core + community)

- LangGraph (for clean step orchestration)

- SQLAlchemy (via SQLDatabase helper)

- Optional: OpenAI or Google Gemini for models


## Setup Instructions

### Getting Started

### 1) Clone & create environment

```
git clone <your-repo-url>
cd <your-repo-folder>

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

### 2) Install dependencies

```
pip install -U langchain-community langgraph
# add a model provider (choose one)
pip install -U langchain-openai    # for OpenAI
# OR
pip install -U "langchain[google-genai]"  # for Gemini
```

The tutorial uses these packages and shows installing LangChain + LangGraph, with an optional model provider. [LangChain](https://python.langchain.com/docs/tutorials/sql_qa/)

### 3) (Optional) Set up sample data (SQLite + Chinook)

Create `Chinook.db` in the repo root. The tutorial links an easy one-liner to generate the SQLite database from SQL:

```
curl -s https://raw.githubusercontent.com/lerocha/chinook-database/master/ChinookDatabase/DataSources/Chinook_Sqlite.sql | sqlite3 Chinook.db
```

Then you can connect with:

```
from langchain_community.utilities import SQLDatabase
db = SQLDatabase.from_uri("sqlite:///Chinook.db")
```

[LangChain](https://python.langchain.com/docs/tutorials/sql_qa/)

### 4) Environment variables

Create a `.env` (or export env vars another way):

```
# choose one model provider:
export OPENAI_API_KEY=...
# or
export GOOGLE_API_KEY=...

# optional: LangSmith tracing
export LANGSMITH_API_KEY=...
export LANGSMITH_TRACING=true
```

The tutorial shows reading provider keys and optionally enabling LangSmith tracing. [LangChain](https://python.langchain.com/docs/tutorials/sql_qa/)

------

## Project Structure

```
.
├─ app/
│  ├─ chain.py          # question → SQL → answer pipeline (LCEL/LangGraph)
│  ├─ db.py             # SQLDatabase setup (SQLAlchemy URI)
│  ├─ prompts.py        # system/user prompts for SQL generation
│  ├─ agent_tools.py    # optional retriever tool for proper nouns
│  └─ cli.py            # simple CLI entrypoint
├─ Chinook.db           # (optional) sample DB
├─ .env.example
└─ README.md
```

------

## Configuration

Edit `app/db.py`:

```
from langchain_community.utilities import SQLDatabase
DB_URI = "sqlite:///Chinook.db"  # e.g., postgres://user:pass@host:5432/dbname
db = SQLDatabase.from_uri(DB_URI)
```

`SQLDatabase` is the SQLAlchemy-backed helper used in the tutorial to inspect tables, run queries, etc. [LangChain](https://python.langchain.com/docs/tutorials/sql_qa/)

------

## Prompts

A solid starting system prompt (adapted from the tutorial’s example):

```
Given an input question, create a syntactically correct {dialect} query to help find the answer.
Limit results to at most {top_k}. Return only relevant columns. Use only columns present in the provided schema.
Only use the following tables:
{table_info}
```

The tutorial demonstrates a similar system message that enforces correct schema usage and limiting results. [LangChain](https://python.langchain.com/docs/tutorials/sql_qa/)

------

## Running

### CLI

```
python -m app.cli "Which 5 artists have the most albums?"
```

Example flow:

1. The app fetches schema & table info
2. LLM drafts a SQL query
3. Query executes against your DB
4. LLM composes a friendly answer

### Python (notebook or script)

```
from app.chain import answer_question

print(answer_question("List the top 5 countries by total invoice amou
```


## FAQ




# Reference
1. https://python.langchain.com/docs/tutorials/sql_qa/