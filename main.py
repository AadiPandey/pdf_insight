import io
import pdfplumber
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import HTMLResponse
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
                    "text_preview": text[:200] + "..." if text else "", # Preview only to save space
                    "full_text": text,
                    "tables": tables,
                    "width": page.width,
                    "height": page.height
                })
            return data
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/parse")
async def parse_pdf(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    content = await file.read()
    json_result = extract_pdf_data(content)
    return json_result

# Serve the frontend
@app.get("/", response_class=HTMLResponse)
async def read_root():
    with open("index.html", "r") as f:
        return f.read()

if __name__ == "__main__":
    import uvicorn
    # Run the app on http://localhost:8000
    uvicorn.run(app, host="0.0.0.0", port=8000)