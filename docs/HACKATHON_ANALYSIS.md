# SOCAR Historical Document Processing Challenge - Analysis

## Challenge Overview

Transform historical handwritten and printed documents (oil & gas domain) into an interactive, searchable knowledge base with a chat agent interface.

## What We Need to Build

### 1. Three Core Components

#### A. OCR Processing Module

- Process PDFs with handwritten/printed text
- Handle multiple alphabets: Azerbaijani (Latin), Azerbaijani (Cyrillic), Russian
- Output: Markdown formatted text per page

#### B. Knowledge Base

- Store processed documents in searchable format
- Vector database implementation
- Efficient retrieval mechanism

#### C. Intelligent Chat Agent

- Natural language querying via REST API
- Contextual responses based on document content
- Conversation history awareness

## Document Types & Complexity

| Type          | Language/Script                  | Difficulty | Points |
| ------------- | -------------------------------- | ---------- | ------ |
| PDF Aze Print | Azerbaijani (Latin)              | Easy       | 2      |
| PDF Cyr Print | Azerbaijani (Cyrillic) / Russian | Medium     | 2      |
| PDF Aze Hand  | Azerbaijani (Handwritten)        | Hard       | 6      |

**Dataset**: 28 PDFs in `data/pdfs/` directory

## Evaluation Breakdown (Total: 1000 points)

### 1. OCR Benchmark (50% = 500 points)

- **Metrics**: CER (Character Error Rate) + WER (Word Error Rate)
- **Testing**: 3 hidden benchmark PDFs (one per difficulty)
- **Score Distribution**:
  - Easy: 125 points
  - Medium: 168.75 points
  - Hard: 206.25 points

**Key Challenge**: Handwritten Azerbaijani text = highest points!

### 2. Chatbot Benchmark (30% = 300 points)

- **Evaluation**: LLM Judge scoring
- **Questions**: 20 total (6 easy, 7 medium, 7 hard + 1 with chat history)
- **Scoring Criteria**:
  - Answer accuracy
  - Citation relevance (retrieved chunks quality)
  - Citation order (coherent sequence)

### 3. Architecture & Implementation (20% = 200 points)

- **Open-source deployable > Cloud solutions** (higher scores)
- Computational efficiency
- Innovation in approach
- Novel solutions for handwriting/multi-language

## Technical Constraints

- **No GPU available** (Azure VM, CPU only)
- Must optimize for CPU execution
- Azure OpenAI API provided
- Open-source LLM API keys available
- **Preference**: Open-source deployable solutions

## Required API Endpoints

### 1. POST /ocr

**Input**: PDF file (multipart/form-data)
**Output**:

```json
[
  {
    "page_number": 1,
    "MD_text": "## Section Title\nExtracted markdown text..."
  }
]
```

### 2. POST /llm

**Input**: Chat history

```json
[
  {
    "role": "user",
    "content": "Your question"
  }
]
```

**Output**:

```json
{
  "sources": [
    {
      "pdf_name": "report.pdf",
      "page_number": 3,
      "content": "Extracted text snippet..."
    }
  ],
  "answer": "Generated response..."
}
```

## Available Resources

### APIs

- **Azure OpenAI** - Credentials configured in `.env` file
- Open-source LLM models via Azure AI Foundry

### References

- HuggingFace: https://huggingface.co/SOCARAI
- Code Samples: https://github.com/neaorin/foundry-models-samples

## Recommended Implementation Strategy

### Phase 1: OCR Solution

**Options**:

1. **Azure AI Document Intelligence** (cloud-based, fast)

   - Pros: Great accuracy, multi-language support
   - Cons: Cloud-based (lower architecture score)
2. **TrOCR + EasyOCR** (hybrid approach)

   - TrOCR: Transformer-based OCR for handwriting
   - EasyOCR: Multi-language support (Latin, Cyrillic)
   - Pros: Open-source, deployable
   - Cons: Slower on CPU
3. **Tesseract + PaddleOCR** (fully open-source)

   - Tesseract: Mature OCR engine
   - PaddleOCR: Excellent for handwriting
   - Pros: Fully open-source, CPU optimized
   - Cons: May need language data training

**Recommendation**: Start with **Azure AI Document Intelligence** for quick wins, then optimize with **PaddleOCR/TrOCR** for higher architecture scores.

### Phase 2: Vector Database

**Options**:

1. **ChromaDB** - Lightweight, easy to deploy
2. **FAISS** - Fast similarity search, Facebook research
3. **Qdrant** - Production-ready, feature-rich

**Recommendation**: **ChromaDB** (easiest) or **FAISS** (fastest)

### Phase 3: LLM Integration (RAG Pipeline)

1. **Document Processing**:

   - Extract text via OCR
   - Chunk documents intelligently (preserve context)
   - Generate embeddings
2. **Retrieval**:

   - Vector search for relevant chunks
   - Reranking for citation order
   - Top-k retrieval
3. **Generation**:

   - Use Azure OpenAI or LLaMA models
   - Include retrieved context in prompt
   - Generate answer with citations

### Phase 4: API Implementation

- **Framework**: FastAPI (async, fast, easy)
- **File handling**: python-multipart for PDF uploads
- **Conversation**: Store chat history in memory/Redis

## Critical Success Factors

1. **Handwritten OCR Quality** (206.25 points from OCR alone!)

   - Focus on getting handwritten Azerbaijani working well
   - Test with sample documents
2. **Efficient Chunking Strategy**

   - Preserve context for better citations
   - Experiment with chunk size (256, 512, 1024 tokens)
3. **Citation Quality**

   - Return relevant chunks (citation relevance)
   - Order chunks logically (citation order)
   - Include page numbers and PDF names
4. **Architecture Score**

   - Maximize open-source components
   - Document deployment process
   - Show computational efficiency

## Deliverables Checklist

- [ ] Working OCR endpoint
- [ ] Working LLM endpoint
- [ ] Vector database setup
- [ ] RAG pipeline implementation
- [ ] README with:
  - [ ] System architecture diagram
  - [ ] Component documentation
  - [ ] Reasoning for technology choices
- [ ] 5-minute presentation
- [ ] GitHub repository

## Next Steps

1. Set up project structure
2. Test OCR solutions on sample PDFs
3. Implement basic endpoints
4. Build RAG pipeline
5. Optimize and test
6. Document everything
