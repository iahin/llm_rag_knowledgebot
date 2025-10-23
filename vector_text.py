from pathlib import Path
import os
from typing import List
import pandas as pd

from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document

# Loaders and text splitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
    CSVLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter


# --- Paths ---
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "knowledgebase"
DB_DIR = BASE_DIR / "chroma_langchain_db_all"

embeddings = OllamaEmbeddings(model="llama3.2")
persist_dir = DB_DIR
# add_documents = not os.path.exists(persist_dir) # If DB does not exist, create it.
add_documents = os.path.exists(persist_dir)


# --- Texts Loaders ---
def load_docs_from_dir(dir_path: Path) -> List[Document]:
    """Load PDFs, DOCX, TXT/MD, and CSVs from a directory."""
    all_docs: List[Document] = []

    for path in dir_path.rglob("*"):
        if not path.is_file():
            continue

        suffix = path.suffix.lower()
        docs: List[Document] = []

        # --- PDF ---
        if suffix == ".pdf":
            loader = PyPDFLoader(str(path))
            docs = loader.load()

        # --- DOCX ---
        elif suffix == ".docx":
            loader = Docx2txtLoader(str(path))
            docs = loader.load()

        # --- TXT / MD ---
        elif suffix in {".txt", ".md"}:
            loader = TextLoader(str(path), encoding="utf-8")
            docs = loader.load()

        else:
            continue

        # normalize metadata
        for d in docs:
            d.metadata = {
                **d.metadata,
                "source": str(path),
                "page": d.metadata.get("page", 0),
            }
        all_docs.extend(docs)

    return all_docs


# --- Chunking function ---
def chunk(docs: List[Document]) -> List[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        add_start_index=True,
        separators=["\n\n", "\n", ". ", "! ", "? ", "; ", ": ", ", ", " ", ""],

    )
    return splitter.split_documents(docs)


# --- Load and chunk ---
raw_docs = load_docs_from_dir(DATA_DIR)
chunks = chunk(raw_docs)

# --- Assign stable IDs ---
ids = []
for i, d in enumerate(chunks):
    src = Path(d.metadata.get("source", "unknown")).name
    page = d.metadata.get("page", 0)
    start = d.metadata.get("start_index", 0)
    ids.append(f"{src}#p{page}-s{start}-i{i}")

# --- Create or load Chroma DB ---
vector_store = Chroma(
    collection_name="knowledge_mixed",
    persist_directory=persist_dir,
    embedding_function=embeddings,
)

# # If DB already exists and you want to add new docs, set add_documents = True manually.
if add_documents:
    vector_store.add_documents(documents=raw_docs, ids=ids)


# --- Build retriever ---
retriever = vector_store.as_retriever(
    search_type="similarity",  # or "mmr"
    search_kwargs={"k": 5},
)

# --- Example query ---
results = retriever.invoke("not good pizza")
for r in results:
    print(r.metadata["source"], r.page_content[:300], "...")
