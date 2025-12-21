# 📄 PDF to JSON Parser

A modern, web-based PDF parser that extracts structured data from PDF files and converts them to JSON format. Built with FastAPI and featuring a clean, responsive UI.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **PDF Text Extraction**: Extract all text content from PDF documents
- **Table Detection**: Automatically detect and extract tables from PDFs
- **Metadata Parsing**: Extract PDF metadata (author, title, creation date, etc.)
- **Page-by-Page Analysis**: Get detailed information for each page including dimensions
- **Beautiful UI**: Modern, gradient-themed interface with smooth animations
- **Real-time Processing**: Instant PDF parsing with loading states
- **Syntax Highlighting**: Color-coded JSON output for better readability
- **RESTful API**: Easy-to-use API endpoint for programmatic access

## 🚀 Future Roadmap

This project serves as the foundation for a more advanced **PDF Question-Answering System** that will:
- Allow users to upload multiple PDFs
- Parse and index PDF content
- Enable natural language queries on the uploaded documents
- Provide AI-powered answers based on PDF content
- Support document embeddings and semantic search

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python)
- **PDF Processing**: pdfplumber
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Server**: Uvicorn ASGI server

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

## 🔧 Installation

1. **Clone or download this repository**

2. **Install dependencies**:
   ```bash
   pip install fastapi uvicorn python-multipart pdfplumber
   ```

## 🚀 Usage

### Starting the Server

Run the application:
```bash
python main.py
```

The server will start on `http://localhost:8000`

### Using the Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. Click "Choose File" and select a PDF
3. Click "Parse PDF" to process the document
4. View the extracted JSON data with syntax highlighting

### API Endpoint

**Parse PDF**
```http
POST /api/parse
Content-Type: multipart/form-data

file: <PDF_FILE>
```

**Example using cURL**:
```bash
curl -X POST "http://localhost:8000/api/parse" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@your_document.pdf"
```

**Example using Python**:
```python
import requests

with open("document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/parse", files=files)
    json_data = response.json()
    print(json_data)
```

## 📊 Response Format

```json
{
  "metadata": {
    "Author": "John Doe",
    "Title": "Sample Document",
    "CreationDate": "D:20231215120000"
  },
  "total_pages": 5,
  "pages": [
    {
      "page_number": 1,
      "text_preview": "First 200 characters of text...",
      "full_text": "Complete text content of the page",
      "tables": [
        [
          ["Header 1", "Header 2"],
          ["Data 1", "Data 2"]
        ]
      ],
      "width": 612.0,
      "height": 792.0
    }
  ]
}
```
## 🚧 Development

### Adding New Features

The codebase is structured for easy extension:

1. **Backend** (`main.py`): Add new extraction logic in `extract_pdf_data()`
2. **Frontend** (`index.html`): Modify UI components in HTML/CSS/JS sections
3. **API**: Add new endpoints following FastAPI patterns

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

**Note**: This is a base implementation designed to be extended into a full PDF question-answering system with AI capabilities.
