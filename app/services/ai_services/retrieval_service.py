from app.config import config
import pinecone

# Initialize Pinecone DB Connection
pinecone.init(api_key=config.PINECONE_API_KEY)

# index = pinecone.Index(name="chatbot-index")
index = pinecone.Index(config.VECTOR_DB_INDEX_NAME)

def search_vector_db(vector: list, top_k: int = 5):
    """
    Desc: Search the vector database for the most similar vectors
    Return: the top k most similar vectors
    """
    results = index.query(queries=vector, top_k=top_k)
    return results