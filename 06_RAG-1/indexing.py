
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_qdrant import Qdrant
import qdrant_client

load_dotenv()

PDF_PATH = Path(__file__).parent / "Preliminary Report VT.pdf"

# Qdrant connection details for a dev container setup.
QDRANT_URL = "http://vector-db:6333"
QDRANT_COLLECTION_NAME = "AI-Crash-Report"

# OpenAI Embedding model details.
EMBEDDING_MODEL = "text-embedding-3-large"


def main():
    """
    Main function to run the PDF indexing process.
    """
    print("Starting the PDF indexing process...")

    # --- 4. Check for PDF File ---
    if not PDF_PATH.exists():
        print(f"Error: The file '{PDF_PATH}' was not found.")
        print("Please make sure the PDF file is in the same directory as the script.")
        return

    # --- 5. Load the PDF Document ---
    try:
        print(f"Loading PDF from: {PDF_PATH}")
        loader = PyPDFLoader(file_path=str(PDF_PATH))
        docs = loader.load()
        
        # --- DEBUG: Check if the document loading worked ---
        if not docs:
            print("🚨 DEBUG ALERT: No documents were loaded from the PDF. The file might be empty or unreadable.")
            return
            
        print(f"✅ Successfully loaded {len(docs)} pages from the document.")
        # --- DEBUG: Print a sample of the loaded content to verify text extraction ---
        print("--- Sample content from first page ---")
        print(docs[0].page_content[:500])
        print("------------------------------------")

    except Exception as e:
        print(f"An error occurred while loading the PDF: {e}")
        return

    # --- 6. Split the Document into Chunks ---
    print("Splitting the document into smaller chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # The size of each chunk in characters.
        chunk_overlap=400   # Overlap helps maintain context between chunks.
    )
    split_docs = text_splitter.split_documents(documents=docs)
    
    # --- DEBUG: Check if the splitting worked ---
    if not split_docs:
        print("🚨 DEBUG ALERT: Document was loaded, but splitting resulted in zero chunks.")
        print("This can happen if the PDF contains images of text instead of actual text.")
        return
        
    print(f"✅ Document split into {len(split_docs)} chunks.")
    # --- DEBUG: Print a sample of the first chunk ---
    print("--- Sample content from first chunk ---")
    print(split_docs[0].page_content)
    print("-------------------------------------")


    # --- 7. Create OpenAI Embeddings ---
    try:
        print(f"Initializing embedding model: {EMBEDDING_MODEL}")
        embedding_model = OpenAIEmbeddings(
            model=EMBEDDING_MODEL,
            api_key=os.getenv("OPENAI_API_KEY")
        )
    except Exception as e:
        print(f"Failed to initialize OpenAI embeddings. Is your API key set correctly? Error: {e}")
        return

    # --- 8. Index Documents in Qdrant ---
    print(f"Connecting to Qdrant at {QDRANT_URL}...")
    print(f"Indexing {len(split_docs)} chunks into collection: '{QDRANT_COLLECTION_NAME}'")

    try:
        vector_store = Qdrant.from_documents(
            documents=split_docs,
            embedding=embedding_model,
            url=QDRANT_URL,
            collection_name=QDRANT_COLLECTION_NAME,
            force_recreate=True, # Use this to ensure you start with a fresh collection
        )
        print("\n========================================")
        print("✅ Indexing of the document is complete!")
        print("========================================")

    except Exception as e:
        print("\n========================================")
        print("❌ An error occurred during indexing.")
        print("========================================")
        print(f"Error: {e}")
        print("\nTroubleshooting tips:")


if __name__ == "__main__":
    main()
