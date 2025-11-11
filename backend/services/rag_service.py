"""
RAG (Retrieval Augmented Generation) service for product search.
Uses FAISS vector store with embeddings for semantic search.
"""
import os
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

try:
    import numpy as np
    import faiss
    from sentence_transformers import SentenceTransformer
except ImportError:
    np = None
    faiss = None
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for product search using FAISS vector store."""
    
    def __init__(
        self,
        products_dir: str = "data/products",
        index_dir: str = "data/faiss_index",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500
    ):
        """
        Initialize RAG service.
        
        Args:
            products_dir: Directory containing product JSON files
            index_dir: Directory to store FAISS index
            embedding_model: Sentence transformer model name
            chunk_size: Maximum chunk size for product descriptions
        """
        self.products_dir = Path(products_dir)
        self.index_dir = Path(index_dir)
        self.chunk_size = chunk_size
        self.embedding_model_name = embedding_model
        
        # Initialize components
        self.encoder: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.products: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        
        # Create directories if they don't exist
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.products_dir.mkdir(parents=True, exist_ok=True)
        
        # Load or build index
        self._initialize()
    
    def _initialize(self) -> None:
        """Initialize encoder and load/build FAISS index."""
        if SentenceTransformer is None:
            logger.warning("sentence-transformers not available, using fallback")
            return
        
        try:
            # Load embedding model
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)
            
            # Try to load existing index
            index_path = self.index_dir / "index.faiss"
            metadata_path = self.index_dir / "metadata.json"
            
            if index_path.exists() and metadata_path.exists():
                logger.info("Loading existing FAISS index")
                self.index = faiss.read_index(str(index_path))
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                    self.products = metadata.get("products", [])
                    self.chunks = metadata.get("chunks", [])
                logger.info(f"Loaded index with {len(self.chunks)} chunks")
            else:
                # Build new index from products
                logger.info("Building new FAISS index from products")
                self._build_index()
                
        except Exception as e:
            logger.error(f"Error initializing RAG service: {e}", exc_info=True)
            self.encoder = None
            self.index = None
    
    def _load_products(self) -> List[Dict[str, Any]]:
        """Load product data from JSON files."""
        products = []
        
        if not self.products_dir.exists():
            logger.warning(f"Products directory not found: {self.products_dir}")
            return products
        
        # Load all JSON files in products directory
        for json_file in self.products_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Handle both single product and list of products
                    if isinstance(data, list):
                        products.extend(data)
                    else:
                        products.append(data)
                logger.info(f"Loaded products from {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        logger.info(f"Loaded {len(products)} products total")
        return products
    
    def _chunk_text(self, text: str, max_size: int) -> List[str]:
        """
        Split text into chunks of maximum size.
        
        Args:
            text: Text to chunk
            max_size: Maximum chunk size in characters
            
        Returns:
            List of text chunks
        """
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1  # +1 for space
            if current_size + word_size > max_size and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [word]
                current_size = word_size
            else:
                current_chunk.append(word)
                current_size += word_size
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _build_index(self) -> None:
        """Build FAISS index from product data."""
        if self.encoder is None:
            logger.error("Encoder not initialized, cannot build index")
            return
        
        # Load products
        self.products = self._load_products()
        
        if not self.products:
            logger.warning("No products found, index will be empty")
            # Create empty index
            dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            self._save_index()
            return
        
        # Create chunks from product descriptions
        self.chunks = []
        for product in self.products:
            description = product.get("description", "") or product.get("name", "")
            if not description:
                continue
            
            # Chunk the description
            text_chunks = self._chunk_text(description, self.chunk_size)
            
            for chunk in text_chunks:
                self.chunks.append({
                    "product_id": product.get("id", len(self.chunks)),
                    "product_name": product.get("name", ""),
                    "text": chunk,
                    "product": product  # Store full product for retrieval
                })
        
        if not self.chunks:
            logger.warning("No chunks created from products")
            dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            self._save_index()
            return
        
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(self.chunks)} chunks")
        texts = [chunk["text"] for chunk in self.chunks]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        if np is None:
            raise ImportError("numpy is required for FAISS operations")
        embeddings = np.array(embeddings).astype('float32')
        
        # Create FAISS index
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        logger.info(f"Built FAISS index with {len(self.chunks)} vectors")
        
        # Save index
        self._save_index()
    
    def _save_index(self) -> None:
        """Save FAISS index and metadata to disk."""
        if self.index is None:
            return
        
        try:
            index_path = self.index_dir / "index.faiss"
            metadata_path = self.index_dir / "metadata.json"
            
            # Save FAISS index
            faiss.write_index(self.index, str(index_path))
            
            # Save metadata
            metadata = {
                "products": self.products,
                "chunks": self.chunks
            }
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved index to {index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}", exc_info=True)
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for products using semantic similarity.
        
        Args:
            query: Search query string
            top_k: Number of top results to return
            
        Returns:
            List of product dictionaries with similarity scores
        """
        if self.encoder is None or self.index is None:
            logger.warning("RAG service not properly initialized")
            return []
        
        if not query or not query.strip():
            return []
        
        if not self.chunks:
            logger.warning("No chunks available for search")
            return []
        
        try:
            # Encode query
            query_embedding = self.encoder.encode([query])
            if np is None:
                raise ImportError("numpy is required for FAISS operations")
            query_embedding = np.array(query_embedding).astype('float32')
            
            # Search in FAISS index
            k = min(top_k, len(self.chunks))
            distances, indices = self.index.search(query_embedding, k)
            
            # Retrieve products
            results = []
            seen_products = set()
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= len(self.chunks):
                    continue
                
                chunk = self.chunks[idx]
                product = chunk.get("product", {})
                product_id = product.get("id") or chunk.get("product_id")
                
                # Avoid duplicates
                if product_id in seen_products:
                    continue
                seen_products.add(product_id)
                
                results.append({
                    "name": product.get("name", chunk.get("product_name", "")),
                    "description": chunk.get("text", ""),
                    "price": product.get("price"),
                    "url": product.get("url"),
                    "score": float(1 / (1 + distance))  # Convert distance to similarity
                })
                
                if len(results) >= top_k:
                    break
            
            logger.info(f"Found {len(results)} products for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}", exc_info=True)
            return []
    
    def rebuild_index(self) -> None:
        """Rebuild the FAISS index from scratch."""
        logger.info("Rebuilding FAISS index")
        self._build_index()


# Global instance (singleton pattern)
_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    """Get or create the global RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

