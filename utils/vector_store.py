import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.dimension = 384  # Default dimension for the specified model

    def create_index(self, text_chunks: List[str]) -> None:
        """
        Creates a FAISS index from the provided text chunks.
        """
        self.chunks = text_chunks
        embeddings = self.encoder.encode(text_chunks)
        
        # Initialize the FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Searches the vector store for relevant chunks.
        Returns list of (chunk, score) tuples.
        """
        if not self.index or not self.chunks:
            return []

        # Encode the query
        query_vector = self.encoder.encode([query])
        
        # Search the index
        distances, indices = self.index.search(
            np.array(query_vector).astype('float32'), k
        )
        
        # Return results with distances
        results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx < len(self.chunks):
                results.append((self.chunks[idx], float(distance)))
        
        return results

    def get_relevant_context(self, query: str, max_tokens: int = 1500) -> Optional[str]:
        """
        Returns concatenated relevant contexts for the query.
        """
        if not self.index:
            return None
            
        results = self.search(query)
        context = " ".join([chunk for chunk, _ in results])
        
        # Truncate to max_tokens (approximate)
        if len(context) > max_tokens:
            context = context[:max_tokens] + "..."
            
        return context
