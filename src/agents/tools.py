import os
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.tools import GoogleSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper

# Initialize Vector Store (Lazy loading to avoid issues during import if not ready)
def get_vectorstore():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)

@tool
def search_regulations(query: str):
    """
    Searches the Transfer Pricing regulatory knowledge base (IRC 482, OECD Guidelines).
    Use this to find specific legal texts, regulations, and guidelines.
    """
    try:
        vectorstore = get_vectorstore()
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
        docs = retriever.invoke(query)
        return "\n\n".join([d.page_content for d in docs])
    except Exception as e:
        return f"Error searching regulations: {str(e)}"

@tool
def web_search(query: str):
    """
    Performs a web search for real-time information, news, or interest rates.
    """
    # Note: This requires GOOGLE_CSE_ID and GOOGLE_API_KEY
    # For this demo, if CSE is not configured, we might mock or use a different search.
    # Assuming standard GoogleSearchAPIWrapper if keys are present.
    if not os.getenv("GOOGLE_CSE_ID"):
        return "Web search tool is not configured (missing GOOGLE_CSE_ID)."
    
    search = GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper())
    return search.run(query)
