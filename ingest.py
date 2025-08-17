"""
ingest.py
This script processes, chunks, embeds, and loads data into a running ChromaDB instance.
"""
import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

import chromadb
from chromadb.utils import embedding_functions

# CONFIG
DATA_PATH = "./data/processed/filtered_complaints.csv"
CHROMA_PERSIST_DIR = "./chroma_data"
"""
ingest.py
This script processes, chunks, embeds, and loads data into a running ChromaDB instance.
"""
import os
import pandas as pd
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings

import chromadb
from chromadb.utils import embedding_functions

# CONFIG
COLLECTION_NAME = "complaints"
DATA_PATH = "./data/processed/filtered_complaints.csv"
CHROMA_PERSIST_DIR = "./chroma_data"

# --- LIMIT CHUNKS FOR TESTING (set to None for all, or e.g. 10000 for a subset) ---
MAX_CHUNKS = 10000  # Set to None to use all chunks

# 1. Load Data
df = pd.read_csv(DATA_PATH)
texts = df['cleaned_narrative'].astype(str).tolist()
metadatas = df.drop(columns=['cleaned_narrative']).to_dict(orient='records')

print("[1/4] Chunking data...")
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
chunks = []
chunk_metas = []
for text, meta in zip(texts, metadatas):
    for chunk in splitter.split_text(text):
        chunks.append(chunk)
        chunk_metas.append(meta)
print(f"Chunking complete. Total chunks: {len(chunks)}")

# Limit number of chunks for testing
if MAX_CHUNKS is not None:
    print(f"Limiting to first {MAX_CHUNKS} chunks for testing.")
    chunks = chunks[:MAX_CHUNKS]
    chunk_metas = chunk_metas[:MAX_CHUNKS]
print(f"Chunking complete. Total chunks: {len(chunks)}")
if len(chunks) > 100000:
    print("WARNING: You have over 100,000 chunks. ChromaDB local may not handle this well. Consider using a smaller subset or a more robust vector DB for production.")

# 3. Embed Chunks in batches with progress
print("[2/4] Embedding chunks (this may take a while)...")
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
BATCH_EMBED = 128
embeddings = []
for i in range(0, len(chunks), BATCH_EMBED):
    batch = chunks[i:i+BATCH_EMBED]
    batch_emb = embedding_fn(batch)
    embeddings.extend(batch_emb)
    print(f"Embedded {min(i+BATCH_EMBED, len(chunks))}/{len(chunks)} chunks", end='\r')
print(f"\nEmbedding complete. Total embeddings: {len(embeddings)}")

# 4. Connect to ChromaDB (local persistent mode)
print("[3/4] Connecting to ChromaDB and preparing collection...")
client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
collection = client.get_or_create_collection(COLLECTION_NAME)
print("Connected to ChromaDB.")
BATCH_SIZE = 10

# 5. Add to ChromaDB in batches
print("[4/4] Adding embeddings to ChromaDB in batches...")
BATCH_SIZE = 10
for i in range(0, len(chunks), BATCH_SIZE):
    batch_chunks = chunks[i:i+BATCH_SIZE]
    batch_embeddings = embeddings[i:i+BATCH_SIZE]
    batch_metas = chunk_metas[i:i+BATCH_SIZE]
    ids = [f"doc_{i+j}" for j in range(len(batch_chunks))]
    collection.add(
        documents=batch_chunks,
        embeddings=batch_embeddings,
        metadatas=batch_metas,
        ids=ids
    )
    print(f"Added {min(i+BATCH_SIZE, len(chunks))}/{len(chunks)} chunks to ChromaDB", end='\r')
print(f"\nIngested {len(chunks)} chunks into ChromaDB collection '{COLLECTION_NAME}'")
