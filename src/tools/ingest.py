import os
import json
import hashlib
from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
PERSIST_DIRECTORY = "./chroma_db"
DATA_DIRECTORY = "./data"
TRACKING_FILE = "./chroma_db/ingested_files.json"

def get_file_hash(file_path: str) -> str:
    """Generate SHA256 hash of file content for change detection."""
    with open(file_path, 'rb') as f:
        return hashlib.sha256(f.read()).hexdigest()

def load_tracking_data() -> dict:
    """Load the tracking file that stores which files have been ingested."""
    if os.path.exists(TRACKING_FILE):
        with open(TRACKING_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_tracking_data(data: dict):
    """Save the tracking data to disk."""
    os.makedirs(os.path.dirname(TRACKING_FILE), exist_ok=True)
    with open(TRACKING_FILE, 'w') as f:
        json.dump(data, indent=2, fp=f)

def ingest_documents():
    """
    Intelligently ingests documents from the data directory into ChromaDB.
    Only processes new or modified files.
    """
    # Create data directory if it doesn't exist
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
        print(f"Created {DATA_DIRECTORY}. Please place PDF/Text files there.")
        # Create a dummy file if empty
        dummy_path = os.path.join(DATA_DIRECTORY, "irc_482_dummy.txt")
        with open(dummy_path, "w") as f:
            f.write("IRC Section 482: Allocation of income and deductions among taxpayers.\n"
                    "In any case of two or more organizations, trades, or businesses (whether or not incorporated, whether or not organized in the United States, and whether or not affiliated) owned or controlled directly or indirectly by the same interests, the Secretary may distribute, apportion, or allocate gross income, deductions, credits, or allowances between or among such organizations, trades, or businesses, if he determines that such distribution, apportionment, or allocation is necessary in order to prevent evasion of taxes or clearly to reflect the income of any of such organizations, trades, or businesses.")
    
    # Load tracking data
    tracking_data = load_tracking_data()
    
    # Initialize embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Check if vector store exists
    vectorstore_exists = os.path.exists(PERSIST_DIRECTORY) and os.path.exists(os.path.join(PERSIST_DIRECTORY, "chroma.sqlite3"))
    
    if vectorstore_exists:
        # Load existing vector store
        vectorstore = Chroma(persist_directory=PERSIST_DIRECTORY, embedding_function=embeddings)
        print("Loaded existing vector store.")
    else:
        vectorstore = None
        print("No existing vector store found. Will create new one.")
    
    # Scan for files to ingest
    new_documents = []
    files_to_process = []
    
    for filename in os.listdir(DATA_DIRECTORY):
        file_path = os.path.join(DATA_DIRECTORY, filename)
        
        # Skip non-files
        if not os.path.isfile(file_path):
            continue
            
        # Only process supported formats
        if not (filename.endswith(".pdf") or filename.endswith(".txt")):
            continue
        
        # Calculate file hash
        current_hash = get_file_hash(file_path)
        
        # Check if file is new or modified
        if filename not in tracking_data or tracking_data[filename] != current_hash:
            files_to_process.append((filename, file_path, current_hash))
    
    if not files_to_process:
        print("No new or modified files to ingest. Vector store is up to date.")
        return
    
    print(f"Found {len(files_to_process)} new/modified file(s) to ingest.")
    
    # Load and split new documents
    for filename, file_path, file_hash in files_to_process:
        print(f"Processing: {filename}")
        
        try:
            if filename.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            else:  # .txt
                loader = TextLoader(file_path)
            
            docs = loader.load()
            new_documents.extend(docs)
            
            # Update tracking data
            tracking_data[filename] = file_hash
            
        except Exception as e:
            print(f"Error processing {filename}: {str(e)}")
            continue
    
    if not new_documents:
        print("No documents were successfully loaded.")
        return
    
    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(new_documents)
    
    print(f"Split into {len(splits)} chunks.")
    
    # Add to vector store
    if vectorstore is None:
        # Create new vector store
        vectorstore = Chroma.from_documents(
            documents=splits,
            embedding=embeddings,
            persist_directory=PERSIST_DIRECTORY
        )
        print(f"Created new vector store with {len(splits)} chunks.")
    else:
        # Add to existing vector store
        vectorstore.add_documents(splits)
        print(f"Added {len(splits)} new chunks to existing vector store.")
    
    # Save tracking data
    save_tracking_data(tracking_data)
    print("Ingestion complete. Tracking data updated.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest_documents()
