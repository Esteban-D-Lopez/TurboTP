import os
from langchain.tools import tool
from langchain_community.vectorstores import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.tools import GoogleSearchRun
from langchain_community.utilities import GoogleSearchAPIWrapper
from googleapiclient.discovery import build
from typing import List, Optional

# Retriever imports
from src.utils.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document

# Initialize Vector Store (Lazy loading to avoid issues during import if not ready)
def get_vectorstore():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    return Chroma(persist_directory="./chroma_db", embedding_function=embeddings)


@tool
def search_regulations(query: str, filter_source: Optional[str] = None):
    """
    Searches the Transfer Pricing regulatory knowledge base (IRC 482, OECD Guidelines) AND user-uploaded internal documents.
    Uses Hybrid Search (Semantic + Keyword) for better accuracy.
    
    Args:
        query: The search query.
        filter_source: Optional filename to restrict search to (e.g., "MockCompanyData.docx"). Use this if the user asks to check a specific file.
    """
    try:
        vectorstore = get_vectorstore()
        
        # 1. Configure Semantic Retriever (Chroma)
        chroma_search_kwargs = {"k": 20}
        if filter_source:
            chroma_search_kwargs["filter"] = {"source": filter_source}
        chroma_retriever = vectorstore.as_retriever(search_kwargs=chroma_search_kwargs)
        
        # 2. Configure Keyword Retriever (BM25)
        # Fetch documents to build BM25 index
        # If filtering, only fetch relevant docs to speed up and improve precision
        get_kwargs = {}
        if filter_source:
            get_kwargs["where"] = {"source": filter_source}
            
        # Get all docs (or filtered subset) from Chroma to build in-memory BM25
        # Note: For very large DBs, this might be slow. Consider caching or persistent BM25.
        collection_data = vectorstore.get(**get_kwargs)
        
        documents = []
        if collection_data['documents']:
            for i, text in enumerate(collection_data['documents']):
                metadata = collection_data['metadatas'][i] if collection_data['metadatas'] else {}
                documents.append(Document(page_content=text, metadata=metadata))
        
        if not documents:
            return "No documents found to search."

        bm25_retriever = BM25Retriever.from_documents(documents)
        bm25_retriever.k = 20  # Match k with Chroma
        
        # 3. Create Ensemble Retriever
        # Weight: 0.5 Semantic, 0.5 Keyword
        ensemble_retriever = EnsembleRetriever(
            retrievers=[chroma_retriever, bm25_retriever],
            weights=[0.5, 0.5]
        )
        
        docs = ensemble_retriever.invoke(query)
        
        if not docs:
            return "No relevant documents found."
            
        # Format output with sources
        results = []
        for d in docs:
            source = d.metadata.get("source", "Unknown")
            results.append(f"Source: {source}\nContent: {d.page_content}")
            
        return "\n\n---\n\n".join(results)
    except Exception as e:
        return f"Error searching regulations: {str(e)}"

@tool
def web_search(query: str, domains: Optional[List[str]] = None):
    """
    Performs a web search for real-time information, news, or interest rates.
    Can optionally restrict searches to specific domains.
    
    Args:
        query: Search query
        domains: Optional list of domains to restrict search (e.g., ['irs.gov', 'oecd.org'])
    """
    if not os.getenv("GOOGLE_CSE_ID"):
        return "Web search tool is not configured (missing GOOGLE_CSE_ID)."
    
    try:
        # Add domain restrictions to query if provided
        search_query = query
        if domains:
            domain_filter = " OR ".join([f"site:{domain}" for domain in domains])
            search_query = f"{query} ({domain_filter})"
        
        search = GoogleSearchRun(api_wrapper=GoogleSearchAPIWrapper())
        results = search.run(search_query)
        
        return f"**Web Search Results:**\n\n{results}"
    except Exception as e:
        return f"Error performing web search: {str(e)}"

@tool
def youtube_search(query: str, max_results: int = 5):
    """
    Searches YouTube for relevant Transfer Pricing videos, lectures, and explanations.
    Uses the YouTube Data API v3 with existing Google API key.
    
    Args:
        query: Search query
        max_results: Maximum number of results to return (default: 5)
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        return "YouTube search requires GOOGLE_API_KEY to be configured."
    
    try:
        youtube = build('youtube', 'v3', developerKey=api_key)
        
        # Search for videos
        search_response = youtube.search().list(
            q=query,
            part='id,snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en',
            order='relevance'
        ).execute()
        
        if not search_response.get('items'):
            return "No YouTube videos found for this query."
        
        # Format results
        results = "**YouTube Videos:**\n\n"
        for item in search_response['items']:
            video_id = item['id']['videoId']
            title = item['snippet']['title']
            description = item['snippet']['description'][:150] + "..."
            channel = item['snippet']['channelTitle']
            url = f"https://www.youtube.com/watch?v={video_id}"
            
            results += f"- **{title}**\n"
            results += f"  *Channel:* {channel}\n"
            results += f"  *Link:* {url}\n"
            results += f"  *Description:* {description}\n\n"
        
        return results
        
    except Exception as e:
        return f"Error searching YouTube: {str(e)}"

# Web source domain mappings
WEB_SOURCE_DOMAINS = {
    "IRS": ["irs.gov"],
    "OECD": ["oecd.org"],
    "Deloitte": ["deloitte.com"],
    "PwC": ["pwc.com"],
    "EY": ["ey.com"],
    "KPMG": ["kpmg.com"]
}
