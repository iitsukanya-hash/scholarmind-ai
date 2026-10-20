import numpy as np
from dotenv import load_dotenv
from pathlib import Path
from google import genai
from pdf_loader import load_pdf
from Embedding import create_embeddings,create_query_embedding
from Retrieval import create_index,retrieve_chunk
from prompts import RESEARCH_REVIEW_PROMPT
load_dotenv()
client=genai.Client()
pdf_path=Path("data/research_paper.pdf")
chunks=load_pdf(pdf_path)
embeddings=np.array(create_embeddings(chunks),dtype="float32")
index=create_index(embeddings)
question=input("Ask Your Question:")
query=np.array(create_query_embedding(question),dtype="float32")
results=retrieve_chunk(query,index,chunks)
context="\n".join(c["text"]for c in results)
promt=RESEARCH_REVIEW_PROMPT.format(context=context,question=question)
response=client.models.generate_content(model="gemini-2.5-flash",contents=promt)
print(response.text)
