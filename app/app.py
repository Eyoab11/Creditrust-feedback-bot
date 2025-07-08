# app/app.py

import gradio as gr
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_community.llms import HuggingFacePipeline
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
import time

# --- 1. SETUP THE MODEL AND RAG CHAIN (This part runs only once on startup) ---

print("Setting up the RAG application...")
start_time = time.time()

# Define paths and model IDs
VECTOR_STORE_PATH = "../vector_store/db_faiss"
EMBEDDING_MODEL_ID = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL_ID = "microsoft/phi-2"

# Load the embedding model
print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_ID)

# Load the vector store
print("Loading vector store...")
db = FAISS.load_local(VECTOR_STORE_PATH, embeddings, allow_dangerous_deserialization=True)
retriever = db.as_retriever(search_kwargs={'k': 5})
print("Retriever is ready.")

# Load the LLM
# IMPORTANT: This runs on CPU by default on most local machines. It will be slow.
# For GPU, ensure you have CUDA installed and a compatible torch version.
print("Loading LLM... This may take a while and use significant RAM.")
model = AutoModelForCausalLM.from_pretrained(
    LLM_MODEL_ID,
    trust_remote_code=True,
    torch_dtype="auto",
    device_map="auto" # Use 'auto' to leverage GPU if available, otherwise CPU
)
tokenizer = AutoTokenizer.from_pretrained(LLM_MODEL_ID, trust_remote_code=True)
pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=512, temperature=0.1)
llm = HuggingFacePipeline(pipeline=pipe)
print("LLM is ready.")

# Define the prompt template
prompt_template = """
Instruct: You are a helpful financial analyst assistant for CrediTrust.
Use ONLY the following retrieved complaint excerpts to answer the question.
Your answer should be a direct summary of the provided context. Do not add outside information.
If the context is not enough to answer, state that you don't have enough information.

Context:
{context}

Question:
{question}

Output:
"""
prompt = PromptTemplate.from_template(prompt_template)

# Create the final RAG chain
combine_docs_chain = create_stuff_documents_chain(llm, prompt)
rag_chain = {
    "context": (lambda x: x["question"]) | retriever,
    "question": RunnablePassthrough()
} | combine_docs_chain

end_time = time.time()
print(f"Application setup complete. Time taken: {end_time - start_time:.2f} seconds.")

# --- 2. DEFINE THE FUNCTION FOR GRADIO ---

def get_rag_response(message, history):
    """
    This function is called by the Gradio chat interface.
    It takes the user's message and the conversation history,
    invokes the RAG chain, and formats the output.
    """
    print(f"\nProcessing new message: {message}")

    # Invoke the chain with a dictionary containing the question
    response = rag_chain.invoke({"question": message})

    # The actual generated text is in the 'answer' key
    answer = response.get('answer', "Sorry, I couldn't generate an answer.")

    # --- Fulfilling the "Display Sources" Requirement ---
    # We will append the sources to the answer for the user to see.
    sources = response.get('context', [])
    if sources:
        answer += "\n\n--- \n**Sources Used:**\n"
        for i, source in enumerate(sources):
            # Extracting metadata
            product = source.metadata.get('product', 'N/A')
            issue = source.metadata.get('issue', 'N/A')
            complaint_id = source.metadata.get('complaint_id', 'N/A')

            # Appending a formatted source string
            answer += (
                f"\n**{i+1}. Complaint ID: {complaint_id}** (Product: {product})\n"
                f"> *'{source.page_content[:150].strip()}...'* \n"
            )

    return answer

# --- 3. CREATE AND LAUNCH THE GRADIO INTERFACE ---

print("Launching Gradio interface...")
iface = gr.ChatInterface(
    fn=get_rag_response,
    title="Intelligent Complaint Analysis for CrediTrust 💡",
    description="Ask a question about customer complaints across our financial products. The AI will find relevant complaints and summarize the key issues for you.",
    examples=[
        "Why are people unhappy with BNPL?",
        "What are the main issues with credit card fees?",
        "Summarize problems related to money transfers being delayed."
    ],
    theme="soft"
)

if __name__ == "__main__":
    iface.launch()