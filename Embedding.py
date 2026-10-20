from pathlib import Path 
from pdf_loader import load_pdf

from sentence_transformers import SentenceTransformer
model=SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
def create_embeddings(text_chunks):
    texts=[chunk["text"] for chunk in text_chunks]
    embeddings=model.encode(texts)
    return embeddings
def create_query_embedding(query):
    embedding=model.encode([query])
    return embedding