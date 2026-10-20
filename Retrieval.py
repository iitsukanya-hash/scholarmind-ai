import faiss
def create_index(embeddings):
    dimension=embeddings.shape[1]
    index=faiss.IndexFlatL2(dimension)
    index.add(embeddings)
    return index 
def search_index(query_embedding,index,top_k=5):
    distances,indices=index.search(query_embedding,top_k)
    return distances,indices 

def retrieve_chunk(query_embedding,index,chunks,top_k=5):
    distances,indices= search_index(query_embedding,index,top_k)

    retrieved_chunks=[]
    for i in indices[0]:
        if i!=-1:
            retrieved_chunks.append(chunks[i])
    return retrieved_chunks