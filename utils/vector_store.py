import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Optional, Dict

class VectorStore:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.encoder = SentenceTransformer(model_name)
        self.index = None
        self.chunks = []
        self.dimension = 384  # Default dimension for the specified model
        self.section_weights = {
            'OVERVIEW': 1.3,  # Prioritize overview information
            'FAQS': 1.2,
            'SESSION_DETAILS': 1.2,
            'LOCATION_DETAILS': 1.1,
            'PRICING': 1.1
        }

    def create_index(self, text_chunks: List[str]) -> None:
        """
        Creates a FAISS index from the provided text chunks with section awareness.
        """
        self.chunks = text_chunks
        embeddings = self.encoder.encode(text_chunks)

        # Initialize the FAISS index
        self.index = faiss.IndexFlatL2(self.dimension)
        self.index.add(np.array(embeddings).astype('float32'))

    def search(self, query: str, k: int = 3) -> List[Tuple[str, float]]:
        """
        Searches the vector store for relevant chunks with section-aware scoring.
        """
        if not self.index or not self.chunks:
            return []

        # Encode the query
        query_vector = self.encoder.encode([query])

        # Get more results initially for reranking
        initial_k = min(k * 2, len(self.chunks))
        distances, indices = self.index.search(
            np.array(query_vector).astype('float32'), initial_k
        )

        # Apply section weights and rerank results
        weighted_results = []
        for idx, distance in zip(indices[0], distances[0]):
            if idx >= len(self.chunks):
                continue

            chunk = self.chunks[idx]
            weight = 1.0

            # Apply section weights if chunk is from a specific section
            for section, section_weight in self.section_weights.items():
                if f"[{section}]" in chunk:
                    weight = section_weight
                    break

            weighted_distance = distance / weight
            weighted_results.append((chunk, weighted_distance))

        # Sort by weighted distance and return top k
        weighted_results.sort(key=lambda x: x[1])
        return weighted_results[:k]

    def get_relevant_context(self, query: str, max_tokens: int = 1500) -> Optional[str]:
        """
        Returns concatenated relevant contexts with overview priority.
        """
        if not self.index:
            return None

        results = self.search(query)

        # Always include overview if it exists
        overview_chunk = next(
            (chunk for chunk, _ in results if "[OVERVIEW]" in chunk),
            None
        )

        # Group other results by section
        sections: Dict[str, List[str]] = {}
        other_chunks: List[str] = []

        for chunk, _ in results:
            if chunk == overview_chunk:
                continue

            is_section = False
            for section in self.section_weights.keys():
                if f"[{section}]" in chunk:
                    section_name = section.lower()
                    if section_name not in sections:
                        sections[section_name] = []
                    sections[section_name].append(chunk)
                    is_section = True
                    break
            if not is_section:
                other_chunks.append(chunk)

        # Combine contexts with overview first
        context_parts = []
        if overview_chunk:
            context_parts.append(overview_chunk)

        # Add section-specific content
        for section_name, chunks in sections.items():
            if chunks:
                context_parts.append(f"\n=== {section_name.upper()} ===\n")
                context_parts.extend(chunks)

        # Add other relevant chunks
        if other_chunks:
            context_parts.extend(other_chunks)

        context = "\n\n".join(context_parts)

        # Truncate to max_tokens (approximate)
        if len(context) > max_tokens:
            context = context[:max_tokens] + "..."

        return context