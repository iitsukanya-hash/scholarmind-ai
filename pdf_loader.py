import fitz
from transformers import AutoTokenizer
tokenizer=AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
def load_pdf(pdf_path):
    pdf=fitz.open(pdf_path)
    documents=[]
    for page_number,page in enumerate(pdf,start=1):
        text=page.get_text('text').strip()

        if text:
            token_ids=tokenizer.encode(text,add_special_tokens=False)
            chunk_size=500
            overlap=80
            for start in range(0,len(token_ids),chunk_size-overlap):
                chunk_token_ids=token_ids[start:start+chunk_size]
                chunk_text=tokenizer.decode(chunk_token_ids,skip_special_tokens=True).strip()
                if chunk_text:
                    documents.append({'text':chunk_text,'page':page_number,'source':pdf_path.name})
    return documents 

if __name__ == "__main__":
    from pathlib import Path
    pdf_path=Path("data")/"research_paper.pdf"
    pages=load_pdf(pdf_path)
    print(f"pages containing text:{len(pages)}")
    print(f"Total chunks: {len(pages)}")
