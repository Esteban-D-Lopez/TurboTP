from typing import List, Dict, Any
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document

class EnsembleRetriever(BaseRetriever):
    """
    Retriever that ensembles results from multiple retrievers.
    
    It uses Reciprocal Rank Fusion (RRF) to combine the results.
    """
    retrievers: List[BaseRetriever]
    weights: List[float]
    c: int = 60

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Get relevant documents for a given query.
        """
        # Get results from all retrievers
        results = []
        for retriever in self.retrievers:
            results.append(retriever.invoke(query, config={"callbacks": run_manager.get_child()}))
            
        # RRF Fusion
        rrf_score: Dict[str, float] = {}
        doc_map: Dict[str, Document] = {}
        
        for i, docs in enumerate(results):
            weight = self.weights[i] if i < len(self.weights) else 1.0
            
            for rank, doc in enumerate(docs):
                # Use content as unique key (or metadata source if available + content hash)
                # Simple approach: content string
                doc_key = doc.page_content
                if doc_key not in doc_map:
                    doc_map[doc_key] = doc
                    
                if doc_key not in rrf_score:
                    rrf_score[doc_key] = 0.0
                    
                rrf_score[doc_key] += weight / (rank + self.c)
                
        # Sort by score
        sorted_docs = sorted(rrf_score.items(), key=lambda x: x[1], reverse=True)
        
        return [doc_map[key] for key, score in sorted_docs]
