import os
import shutil
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Configuration
PERSIST_DIRECTORY = "./chroma_db"
DATA_DIRECTORY = "./data"

def ingest_documents():
    """
    Ingests documents from the data directory into ChromaDB.
    """
    if not os.path.exists(DATA_DIRECTORY):
        os.makedirs(DATA_DIRECTORY)
        print(f"Created {DATA_DIRECTORY}. Please place PDF/Text files there.")
        # Create a dummy file if empty
        with open(os.path.join(DATA_DIRECTORY, "irc_482_dummy.txt"), "w") as f:
            f.write("IRC Section 482: Allocation of income and deductions among taxpayers.\n"
                    "In any case of two or more organizations, trades, or businesses (whether or not incorporated, whether or not organized in the United States, and whether or not affiliated) owned or controlled directly or indirectly by the same interests, the Secretary may distribute, apportion, or allocate gross income, deductions, credits, or allowances between or among such organizations, trades, or businesses, if he determines that such distribution, apportionment, or allocation is necessary in order to prevent evasion of taxes or clearly to reflect the income of any of such organizations, trades, or businesses.")
    
    documents = []
    for filename in os.listdir(DATA_DIRECTORY):
        file_path = os.path.join(DATA_DIRECTORY, filename)
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load())
        elif filename.endswith(".txt"):
            loader = TextLoader(file_path)
            documents.extend(loader.load())
            
    if not documents:
        print("No documents found to ingest.")
        return

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    # Create/Update Vector Store
    vectorstore = Chroma.from_documents(
        documents=splits,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )
    print(f"Ingested {len(splits)} chunks into ChromaDB.")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    ingest_documents()
