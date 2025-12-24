# PDF RAG Question-Answering System

An intelligent PDF question-answering system powered by RAG (Retrieval-Augmented Generation). Upload PDFs, process them through a visual pipeline, and ask questions using Google's Gemini AI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![Gemini](https://img.shields.io/badge/Gemini-2.5_Flash-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **RAG Pipeline Visualization**: Interactive 4-stage pipeline showing the complete document processing flow
- **PDF Text Extraction**: Extract and parse text content from PDF documents
- **Smart Chunking**: Tokenize documents using tiktoken with configurable chunk sizes and overlap
- **Vector Embeddings**: Generate embeddings using Google's text-embedding-004 model
- **ChromaDB Storage**: Persistent vector storage for semantic search
- **AI-Powered Q&A**: Ask questions and get context-aware answers using Gemini 2.5 Flash
- **Source Attribution**: Each answer includes page references from the source document
- **Modern UI**: Clean, progressive interface with animations and dark code themes
- **RESTful API**: Easy-to-use API endpoints for integration

## Technology Stack

- **Backend**: FastAPI, Uvicorn
- **PDF Processing**: pdfplumber
- **AI/ML**: Google Gemini API (2.5 Flash, text-embedding-004)
- **Vector Database**: ChromaDB with persistent storage
- **Tokenization**: tiktoken (cl100k_base encoding)
- **Frontend**: Vanilla JavaScript, HTML5, CSS3, Marked.js for markdown rendering

## Installation

1. **Clone or download this repository**

2. **Create a `.env` file** in the project root:
   ```bash
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```
   Get your API key from [Google AI Studio](https://makersuite.google.com/app/apikey)

3. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart pdfplumber tiktoken chromadb google-generativeai python-dotenv
   ```

## Usage

### Starting the Server

Run the application:
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Using the Web Interface

The application features a 4-stage visual pipeline:

**Stage 1: Upload**
1. Navigate to `http://localhost:8000`
2. Click "Select PDF" and choose your document
3. Click "Process Document"

**Stage 2: JSON Preview**
- View the raw extracted text organized by pages

**Stage 3: Vector Embeddings**
- See how your document was chunked (800 tokens per chunk, 50 token overlap)
- Preview the first 5 chunks with page metadata

**Stage 4: Chat**
- Ask questions about your document
- Get AI-powered answers with source page references
- Answers are formatted in markdown for better readability

### API Endpoints

**Process PDF**
```http
POST /api/process
Content-Type: multipart/form-data

file: <PDF_FILE>
```

**Response**:
```json
{
  "status": "success",
  "json_preview": {
    "pages": [
      {"page_number": 1, "text": "..."}
    ]
  },
  "chunks_preview": [...],
  "total_chunks": 42
}
```

**Chat with Document**
```http
POST /api/chat
Content-Type: application/json

{
  "question": "What is the main topic of this document?"
}
```

**Response**:
```json
{
  "answer": "The document discusses...",
  "sources": [1, 3, 5]
}
```

### Example using Python

```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/process", files=files)
    data = response.json()
    print(f"Processed {data['total_chunks']} chunks")

chat_response = requests.post(
    "http://localhost:8000/api/chat",
    json={"question": "Summarize the key points"}
)
print(chat_response.json()["answer"])
```

## Architecture

### RAG Pipeline

1. **Extraction**: pdfplumber extracts raw text from each page
2. **Chunking**: tiktoken splits text into ~800 token chunks with 50 token overlap
3. **Embedding**: Gemini text-embedding-004 creates vector representations
4. **Storage**: ChromaDB stores vectors with metadata for semantic search
5. **Retrieval**: Query embeddings find the 5 most relevant chunks
6. **Generation**: Gemini 2.5 Flash generates contextual answers

### Data Flow

```
PDF Upload → Text Extraction → Tokenization → Vector Embedding
                                                      ↓
User Query ← Answer Generation ← Context Assembly ← Vector Search
```
## Development

### Project Structure

```
pdf_parser/
├── main.py           # FastAPI backend with RAG logic
├── index.html        # Multi-stage UI
├── script.js         # Frontend logic and API calls
├── style.css         # Modern styling with animations
├── .env              # API keys (not committed)
├── chroma_db/        # Persistent vector database
└── README.md
```

### Configuration

Adjust chunking parameters in [main.py](main.py):
```python
def chunk_text(text: str, page_num: int, chunk_size: int = 800, overlap: int = 50):
```

Change the number of retrieved chunks in the chat endpoint:
```python
results = collection.query(query_texts=[request.question], n_results=5)
```

### Customization

- **Change AI Model**: Modify `genai.GenerativeModel('gemini-2.5-flash')` to use a different Gemini model
- **Adjust Embeddings**: Change `model = "models/text-embedding-004"` in `GeminiEmbeddingFunction`
- **Modify UI**: Edit the 4-stage pipeline in [index.html](index.html) and [style.css](style.css)
