from chromadb.utils import embedding_functions
import asyncio

# We use ChromaDB's default embedding function (all-MiniLM-L6-v2)
_embedder = embedding_functions.DefaultEmbeddingFunction()

async def embed_text(text: str) -> list:
    """
    Generate an embedding vector for a string of text.
    Wrapped in asyncio.to_thread to prevent blocking the event loop 
    while the ONNX model runs inference.
    """
    if not text.strip():
        # Default empty vector (size 384 for MiniLM-L6-v2)
        return [0.0] * 384
        
    # Chroma returns a list of embeddings (one per document passed)
    # We pass 1 document and retrieve the first embedding Result
    result = await asyncio.to_thread(lambda: _embedder([text]))
    return result[0]
