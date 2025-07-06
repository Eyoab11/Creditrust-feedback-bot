import os
import subprocess

# Define project structure
folders = [
    "app",
    "data/raw",
    "data/processed",
    "docs",
    "notebooks",
    "reports",
    "src",
    "tests",
    "vector_store"
]

files = {
    ".gitignore": """# Python artifacts
__pycache__/
*.py[cod]
*.ipynb_checkpoints
.env
.venv/
venv/
env/
data/raw/
data/processed/
vector_store/
.ipynb_checkpoints/
.DS_Store
Thumbs.db
""",
    "README.md": """# Intelligent Complaint Analysis for Financial Services

A RAG-powered internal chatbot to help CrediTrust teams analyze customer complaints in real time.
""",
    "requirements.txt": "",
    "app/app.py": "# Streamlit or Gradio app goes here\n",
    "data/raw/complaints.csv": "",
    "data/processed/filtered_complaints.csv": "",
    "docs/architecture.md": "# System Design and Architecture\n",
    "notebooks/01-EDA-and-Preprocessing.ipynb": "",
    "notebooks/02-Embedding-and-Indexing.ipynb": "",
    "reports/final_report.md": "# Final Report\n",
    "src/__init__.py": "",
    "src/config.py": "# Config variables\n",
    "src/data_processing.py": "# Preprocessing logic\n",
    "src/rag_pipeline.py": "# RAG pipeline logic\n",
    "tests/test_rag_pipeline.py": "# Unit tests for RAG pipeline\n",
    "vector_store/db_faiss": ""
}

# Create folders
for folder in folders:
    os.makedirs(folder, exist_ok=True)

# Create files with content
for path, content in files.items():
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

# Setup virtual environment
print("📦 Creating virtual environment...")
subprocess.run(["python", "-m", "venv", "venv"])

print("✅ Project structure and virtual environment created successfully.")
