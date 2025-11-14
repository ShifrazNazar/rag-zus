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
    def __init__(
        self,
        products_dir: str = "data/products",
        index_dir: str = "data/faiss_index",
        embedding_model: str = "all-MiniLM-L6-v2",
        chunk_size: int = 500
    ):
        self.products_dir = Path(products_dir)
        self.index_dir = Path(index_dir)
        self.chunk_size = chunk_size
        self.embedding_model_name = embedding_model
        
        self.encoder: Optional[SentenceTransformer] = None
        self.index: Optional[faiss.Index] = None
        self.products: List[Dict[str, Any]] = []
        self.chunks: List[Dict[str, Any]] = []
        
        self.index_dir.mkdir(parents=True, exist_ok=True)
        self.products_dir.mkdir(parents=True, exist_ok=True)
        
        self._initialized = False
    
    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        self._initialize()
        self._initialized = True
    
    def _initialize(self) -> None:
        if SentenceTransformer is None:
            logger.warning("sentence-transformers not available, using fallback")
            return
        
        try:
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.encoder = SentenceTransformer(self.embedding_model_name)
            
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
                logger.info("Building new FAISS index from products")
                self._build_index()
                
        except Exception as e:
            logger.error(f"Error initializing RAG service: {e}", exc_info=True)
            self.encoder = None
            self.index = None
    
    def _load_products(self) -> List[Dict[str, Any]]:
        products = []
        
        if not self.products_dir.exists():
            logger.warning(f"Products directory not found: {self.products_dir}")
            return products
        
        for json_file in self.products_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        products.extend(data)
                    else:
                        products.append(data)
                logger.info(f"Loaded products from {json_file.name}")
            except Exception as e:
                logger.error(f"Error loading {json_file}: {e}")
        
        drinkware_categories = ["Tumbler", "Mugs"]
        filtered_products = [
            p for p in products 
            if p.get("category") in drinkware_categories
        ]
        
        if len(filtered_products) < len(products):
            logger.info(f"Filtered {len(products) - len(filtered_products)} non-drinkware products. Keeping {len(filtered_products)} drinkware items.")
        
        logger.info(f"Loaded {len(filtered_products)} drinkware products total")
        return filtered_products
    
    def _chunk_text(self, text: str, max_size: int) -> List[str]:
        if len(text) <= max_size:
            return [text]
        
        chunks = []
        words = text.split()
        current_chunk = []
        current_size = 0
        
        for word in words:
            word_size = len(word) + 1
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
        if self.encoder is None:
            logger.error("Encoder not initialized, cannot build index")
            return
        
        self.products = self._load_products()
        
        if not self.products:
            logger.warning("No products found, index will be empty")
            dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            self._save_index()
            return
        
        self.chunks = []
        for product in self.products:
            description = product.get("description", "") or product.get("name", "")
            if not description:
                continue
            
            category = product.get("category", "")
            if category:
                full_text = f"{category} {description}"
            else:
                full_text = description
            
            text_chunks = self._chunk_text(full_text, self.chunk_size)
            
            for chunk in text_chunks:
                self.chunks.append({
                    "product_id": product.get("id", len(self.chunks)),
                    "product_name": product.get("name", ""),
                    "text": chunk,
                    "product": product
                })
        
        if not self.chunks:
            logger.warning("No chunks created from products")
            dimension = self.encoder.get_sentence_embedding_dimension()
            self.index = faiss.IndexFlatL2(dimension)
            self._save_index()
            return
        
        logger.info(f"Generating embeddings for {len(self.chunks)} chunks")
        texts = [chunk["text"] for chunk in self.chunks]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        if np is None:
            raise ImportError("numpy is required for FAISS operations")
        embeddings = np.array(embeddings).astype('float32')
        
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        logger.info(f"Built FAISS index with {len(self.chunks)} vectors")
        
        self._save_index()
    
    def _save_index(self) -> None:
        if self.index is None:
            return
        
        try:
            index_path = self.index_dir / "index.faiss"
            metadata_path = self.index_dir / "metadata.json"
            
            faiss.write_index(self.index, str(index_path))
            
            metadata = {
                "products": self.products,
                "chunks": self.chunks
            }
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Saved index to {index_path}")
        except Exception as e:
            logger.error(f"Error saving index: {e}", exc_info=True)
    
    def search(self, query: str, top_k: int = 10) -> List[Dict[str, Any]]:
        self._ensure_initialized()
        
        if self.encoder is None or self.index is None:
            logger.warning("RAG service not properly initialized")
            return []
        
        if not query or not query.strip():
            return []
        
        if not self.chunks:
            logger.warning("No chunks available for search")
            return []
        
        try:
            try:
                top_k = int(top_k)
            except (ValueError, TypeError):
                top_k = 10
                logger.warning(f"Invalid top_k value, using default: 10")
            
            query_embedding = self.encoder.encode([query])
            if np is None:
                raise ImportError("numpy is required for FAISS operations")
            query_embedding = np.array(query_embedding).astype('float32')
            
            k = min(top_k, len(self.chunks))
            distances, indices = self.index.search(query_embedding, k)
            
            product_scores = {}
            
            for idx, distance in zip(indices[0], distances[0]):
                if idx >= len(self.chunks):
                    continue
                
                chunk = self.chunks[idx]
                product = chunk.get("product", {})
                product_id = product.get("id") or chunk.get("product_id")
                
                score = float(1 / (1 + distance))
                
                if product_id not in product_scores or score > product_scores[product_id]["score"]:
                    product_scores[product_id] = {
                        "name": product.get("name", chunk.get("product_name", "")),
                        "description": chunk.get("text", ""),
                        "price": product.get("price"),
                        "url": product.get("url"),
                        "score": score
                    }
            
            results = sorted(product_scores.values(), key=lambda x: x["score"], reverse=True)[:top_k]
            
            logger.info(f"Found {len(results)} products for query: {query}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching: {e}", exc_info=True)
            return []
    
    def rebuild_index(self) -> None:
        logger.info("Rebuilding FAISS index")
        self._ensure_initialized()
        self._build_index()


_rag_service: Optional[RAGService] = None


def get_rag_service() -> RAGService:
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service
