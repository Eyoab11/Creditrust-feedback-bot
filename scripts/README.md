# scripts/

This folder contains utility and one-time scripts for data processing and ingestion.

- `ingest.py`: Processes, chunks, embeds, and loads complaint data into ChromaDB. Run this script once after preparing your data, or when you need to re-index.

Scripts in this folder are not part of the main application runtime, but are essential for setup and data engineering tasks.
