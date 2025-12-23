import io
import pdfplumber
import tiktoken
import uvicorn
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse, FileResponse 
from fastapi.staticfiles import StaticFiles

app = FastAPI()

def extract_pdf_data(file_bytes):
    """Core logic to convert PDF bytes to JSON structure"""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            data = {
                "metadata": pdf.metadata,
                "total_pages": len(pdf.pages),
                "pages": []
            }

            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                tables = page.extract_tables()
                
                data["pages"].append({
                    "page_number": i + 1,
                    "text_preview": text[:200] + "..." if text else "", 
                    "full_text": text,
                    "tables": tables,
                    "width": page.width,
                    "height": page.height
                })
            return data
    except Exception as e:
        return {"error": str(e)}

def chunk_text(text: str, page_num: int, chunk_size: int = 500, overlap: int = 50):
    """
    Splits text into chunks with overlap, preserving metadata.
    """
    encoding = tiktoken.get_encoding("cl100k_base") 
    tokens = encoding.encode(text)
    
    total_tokens = len(tokens)
    chunks = []

    for i in range(0, total_tokens, chunk_size - overlap):
        chunk_tokens = tokens[i : i + chunk_size]

        chunk_text = encoding.decode(chunk_tokens)
        
        chunks.append({
            "chunk_id": f"pg{page_num}_chk{len(chunks)+1}",
            "page_number": page_num,
            "token_count": len(chunk_tokens),
            "text": chunk_text
        })

        if i + chunk_size >= total_tokens:
            break
            
    return chunks



@app.post("/api/parse")
async def parse_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    content = await file.read()
    json_result = extract_pdf_data(content)
    return json_result

@app.post("/api/tokenize")
async def tokenize_pdf(file: UploadFile = File(...)):
    """
    1. Parses PDF
    2. Iterates through pages
    3. Chunks the text
    4. Returns flat list of chunks ready for embedding
    """
    content = await file.read()
    
    raw_data = extract_pdf_data(content)
    
    if "error" in raw_data:
        return raw_data

    all_chunks = []
    
    for page in raw_data["pages"]:
        page_text = page["full_text"]
        if page_text:
            clean_text = page_text.replace("\n", " ").strip()
            
            page_chunks = chunk_text(clean_text, page["page_number"])
            all_chunks.extend(page_chunks)

    return {
        "filename": file.filename,
        "total_chunks": len(all_chunks),
        "chunks": all_chunks
    }



@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f:
        return f.read()

@app.get("/style.css")
async def get_css():
    return FileResponse("style.css")

@app.get("/script.js")
async def get_js():
    return FileResponse("script.js")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)