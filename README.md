# Task 1: Exploratory Data Analysis & Preprocessing

This initial phase focused on understanding the raw Consumer Financial Protection Bureau (CFPB) complaint data and preparing it for our RAG pipeline.

## What Was Done

The process was executed in the `notebooks/01-EDA-and-Preprocessing.ipynb` notebook and involved the following key steps:

1. **Data Loading**:  
   - The full dataset of over **9.6 million complaints** was loaded into a pandas DataFrame.

2. **Exploratory Analysis**:  
   A detailed EDA was performed to understand the dataset's characteristics, specifically focusing on:
   - The distribution of complaints across all product categories.
   - The availability of Consumer complaint narrative text.
   - The word count distribution of the available narratives.

3. **Data Filtering**:  
   The dataset was filtered to align with the project's business objectives, which involved:
   - Isolating complaints related to the five target products: **Credit Card, Personal Loan, Savings Account, and Money Transfers**.
   - Removing all records that did not contain a **Consumer complaint narrative**, as this text is essential for our RAG model.

4. **Text Cleaning**:  
   The narrative text was cleaned and normalized to improve the quality of future embeddings. This included:
   - Lowercasing
   - Removing special characters
   - Stripping common boilerplate text.

5. **Saving the Output**:  
   The final, cleaned, and filtered DataFrame was saved to a new CSV file.

## Key Findings and Outputs

Our analysis of the raw data produced several critical insights that directly inform the subsequent stages of this project:

- **Massive Scale**:  
  The original dataset contains **9.6 million complaints**, confirming the need for an automated AI solution to handle this volume.

- **Narrative Availability is Key**:  
  Only **31%** of the total complaints include a narrative. Since our RAG system relies entirely on this text, over two-thirds of the raw data was filtered out, highlighting the importance of this specific feature.

- **Dominant Product Categories**:  
  The top complaint categories are overwhelmingly related to **"Credit reporting" and "Debt collection"**. Our target products, while significant, represent a smaller fraction, which validates the filtering step to create a focused dataset for CrediTrust's needs.

- **Narrative Length Varies Greatly**:  
  - The average complaint narrative is **~176 words** long.  
  - The distribution is heavily right-skewed, with most narratives being concise, but some extending to over **6,000 words**.  
  - **Implication**: This finding strongly justifies the need for a **text chunking strategy** in Task 2. Embedding extremely long documents as a single vector is ineffective; chunking will ensure the semantic meaning is preserved.

## Final Output

The primary deliverable of this task is a clean, filtered dataset ready for the next stage.

- **File**: `filtered_complaints.csv`  
- **Location**: `data/processed/filtered_complaints.csv`  
- **Purpose**: This file will serve as the direct input for **Task 2: Text Chunking, Embedding, and Vector Store Indexing**.

# Task 2: Chunking, Embedding, and Vector Store Indexing

With a clean dataset, the next step was to convert the unstructured text narratives into a machine-readable format optimized for semantic search. This involved text chunking, vector embedding, and indexing into a vector store.

## Chunking Strategy

Long complaint narratives are ineffective when embedded as a single vector, as the specific details can get diluted. To address this, we implemented a text chunking strategy using **LangChain's RecursiveCharacterTextSplitter**:

- **`chunk_size=1000` (characters)**:  
  Chosen as a balance between:
  - Being small enough to maintain semantic specificity
  - Large enough to contain meaningful context for answering questions

- **`chunk_overlap=100` (characters)**:  
  Ensures context is not lost at chunk boundaries by allowing key sentences split between chunks to be fully captured in at least one chunk.

### Outcome:
- **Original complaints**: ~200,000  
- **Resulting chunks**: ~350,000 (ready for embedding)

## Embedding Model Choice

We selected **`sentence-transformers/all-MiniLM-L6-v2`** for generating embeddings based on:

1. **Performance**:  
   - Strong balance of speed and accuracy  
   - Ideal for responsive yet effective semantic search  

2. **Efficiency**:  
   - "Mini" model → Low computational/memory requirements  
   - Runs on standard **CPU hardware** (no GPU needed)  

3. **Generalization**:  
   - Trained on diverse text → Suitable for financial complaint language  

## Vector Store Implementation

### Technology: **FAISS** (Facebook AI Similarity Search)
- E# Task 2: Chunking, Embedding, and Vector Store Indexing

With a clean dataset, the next step was to convert the unstructured text narratives into a machine-readable format optimized for semantic search. This involved text chunking, vector embedding, and indexing into a vector store.

## Chunking Strategy

Long complaint narratives are ineffective when embedded as a single vector, as the specific details can get diluted. To address this, we implemented a text chunking strategy using **LangChain's RecursiveCharacterTextSplitter**:

- **`chunk_size=1000` (characters)**:  
  Chosen as a balance between:
  - Being small enough to maintain semantic specificity
  - Large enough to contain meaningful context for answering questions

- **`chunk_overlap=100` (characters)**:  
  Ensures context is not lost at chunk boundaries by allowing key sentences split between chunks to be fully captured in at least one chunk.

### Outcome:
- **Original complaints**: ~200,000  
- **Resulting chunks**: ~350,000 (ready for embedding)

## Embedding Model Choice

We selected **`sentence-transformers/all-MiniLM-L6-v2`** for generating embeddings based on:

1. **Performance**:  
   - Strong balance of speed and accuracy  
   - Ideal for responsive yet effective semantic search  

2. **Efficiency**:  
   - "Mini" model → Low computational/memory requirements  
   - Runs on standard **CPU hardware** (no GPU needed)  

3. **Generalization**:  
   - Trained on diverse text → Suitable for financial complaint language  

## Vector Store Implementation

### Technology: **FAISS** (Facebook AI Similarity Search)
- Each text chunk → **384-dimensional vector**  
- **Metadata stored** with each vector:  
  - Complaint ID  
  - Product  
  - Issue  
  - Company  
  *(Essential for traceability in a trustworthy AI system)*  

### Output:
- Final FAISS index persisted to: `vector_store/`  
- Enables instant loading without reprocessing data  

## Key Takeaways
- **Chunking** prevents semantic dilution in long narratives  
- **all-MiniLM-L6-v2** balances speed, accuracy, and resource use  
- **FAISS + Metadata** ensures efficient retrieval with full auditability  ach text chunk → **384-dimensional vector**  
- **Metadata stored** with each vector:  
  - Complaint ID  
  - Product  
  - Issue  
  - Company  
  *(Essential for traceability in a trustworthy AI system)*  

### Output:
- Final FAISS index persisted to: `vector_store/`  
- Enables instant loading without reprocessing data  

## Key Takeaways
- **Chunking** prevents semantic dilution in long narratives  
- **all-MiniLM-L6-v2** balances speed, accuracy, and resource use  
- **FAISS + Metadata** ensures efficient retrieval with full auditability  