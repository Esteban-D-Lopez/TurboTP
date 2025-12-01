import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv()

from src.agents.tools import get_vectorstore

def debug_rag():
    print("Initialize Vector Store...")
    try:
        vectorstore = get_vectorstore()
        
        # 1. Check collection count
        print(f"Total documents in DB: {vectorstore._collection.count()}")
        
        # 2. List unique sources (if possible, this might be slow on large DBs but okay for local)
        # We'll just peek at metadata of first 100 items or so if we can, 
        # but Chroma doesn't have a cheap "list distinct metadata" method.
        # Instead, let's just run a query that SHOULD hit the file.
        
        query = "intercompany service line agreements"
        print(f"\nQuerying: '{query}'")
        
        docs = vectorstore.similarity_search(query, k=10)
        
        print(f"\nTop {len(docs)} Results:")
        for i, doc in enumerate(docs):
            source = doc.metadata.get("source", "Unknown")
            print(f"{i+1}. Source: {source}")
            print(f"   Preview: {doc.page_content[:100]}...")
            print("-" * 50)
            
        # 3. Check specifically for the mock file if we know the name
        # The user screenshot shows "MockCompanyData.docx"
        target_file = "MockCompanyData.docx"
        print(f"\nChecking specifically for source: {target_file}")
        
        # We can try to filter by source if the vectorstore supports it directly
        # LangChain Chroma wrapper supports filter in similarity_search
        specific_docs = vectorstore.similarity_search(query, k=5, filter={"source": target_file})
        
        if specific_docs:
            print(f"✅ Found {len(specific_docs)} chunks from {target_file}!")
            for doc in specific_docs:
                print(f"   Preview: {doc.page_content[:100]}...")
        else:
            print(f"❌ No chunks found for {target_file} with this query.")
            
    except Exception as e:
        print(f"Error debugging RAG: {e}")

if __name__ == "__main__":
    debug_rag()
