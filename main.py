import io
import os
import pdfplumber
import tiktoken
import uvicorn
import chromadb
import google.generativeai as genai
from chromadb.utils import embedding_functions
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY not found in .env file")

genai.configure(api_key=GOOGLE_API_KEY)

app = FastAPI()

class GeminiEmbeddingFunction(embedding_functions.EmbeddingFunction):
    def __call__(self, input: List[str]) -> List[List[float]]:
        model = "models/text-embedding-004"
        return [
            genai.embed_content(model=model, content=text, task_type="retrieval_document")["embedding"]
            for text in input
        ]

chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(
    name="pdf_rag_gemini_v2",
    embedding_function=GeminiEmbeddingFunction()
)

class ChatRequest(BaseModel):
    question: str

def extract_pdf_data(file_bytes):
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            data = {"pages": []}
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                data["pages"].append({"page_number": i + 1, "text": text})
            return data
    except Exception as e:
        return {"error": str(e)}

def chunk_text(text: str, page_num: int, chunk_size: int = 800, overlap: int = 50):
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)
    total_tokens = len(tokens)
    chunks = []
    
    for i in range(0, total_tokens, chunk_size - overlap):
        chunk_tokens = tokens[i : i + chunk_size]
        chunk_text = encoding.decode(chunk_tokens)
        chunks.append({
            "chunk_id": f"pg{page_num}_chk{i}",
            "text": chunk_text,
            "metadata": {"page": page_num}
        })
        if i + chunk_size >= total_tokens: break
    return chunks

@app.post("/api/process")
async def process_pdf(file: UploadFile = File(...)):
    content = await file.read()
    
    raw_data = extract_pdf_data(content)
    
    all_chunks = []
    for page in raw_data.get("pages", []):
        chunks = chunk_text(page["text"], page["page_number"])
        all_chunks.extend(chunks)

    if not all_chunks:
        return {"error": "No text found in PDF"}

    try:
        chroma_client.delete_collection("pdf_rag_gemini_v2")
        global collection
        collection = chroma_client.create_collection(
            name="pdf_rag_gemini_v2",
            embedding_function=GeminiEmbeddingFunction()
        )
    except:
        pass

    collection.add(
        documents=[c["text"] for c in all_chunks],
        metadatas=[c["metadata"] for c in all_chunks],
        ids=[c["chunk_id"] for c in all_chunks]
    )

    return {
        "status": "success",
        "json_preview": raw_data,
        "chunks_preview": all_chunks[:5],
        "total_chunks": len(all_chunks)
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    results = collection.query(query_texts=[request.question], n_results=5)
    context_text = "\n\n".join(results['documents'][0])
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    
    prompt = f"""
    Answer the question using ONLY the context below. 
    Format the answer nicely in Markdown.
    
    Context:
    {context_text}
    
    Question: {request.question}
    """
    
    try:
        response = model.generate_content(prompt)
        return {
            "answer": response.text, 
            "sources": [m["page"] for m in results['metadatas'][0]]
        }
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "sources": []}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f: return f.read()

@app.get("/style.css")
async def get_css(): return FileResponse("style.css")

@app.get("/script.js")
async def get_js(): return FileResponse("script.js")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)