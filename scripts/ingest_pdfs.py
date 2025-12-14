"""
PDF Ingestion Script for SOCAR Hackathon
Processes all PDFs with VLM OCR and uploads to Pinecone

Based on benchmark results:
- OCR: Llama-4-Maverick-17B (87.75% CSR)
- Embedding: BAAI/bge-large-en-v1.5 (1024 dims)
- Chunking: 600 chars with 100 overlap
- Vector DB: Pinecone (cosine similarity)
"""

import os
import re
import time
import base64
from pathlib import Path
from typing import List, Dict
from io import BytesIO

import fitz  # PyMuPDF
from PIL import Image
from dotenv import load_dotenv
from openai import AzureOpenAI
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Load environment
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PDFS_DIR = PROJECT_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "output" / "ingestion"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Initialize clients
print("🔄 Initializing clients...")

azure_client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "hackathon"))

# Best performing embedding model from benchmarks
embedding_model = SentenceTransformer("BAAI/bge-large-en-v1.5")

# Best performing VLM from benchmarks
VLM_MODEL = "Llama-4-Maverick-17B-128E-Instruct-FP8"

# Optimal chunking parameters from benchmarks
CHUNK_SIZE = 600
CHUNK_OVERLAP = 100

print("✅ Clients initialized")


def pdf_to_images(pdf_path: str, dpi: int = 100) -> List[Image.Image]:
    """Convert PDF pages to PIL Images."""
    doc = fitz.open(pdf_path)
    images = []

    for page_num in range(len(doc)):
        page = doc[page_num]
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    doc.close()
    return images


def image_to_base64(image: Image.Image, format: str = "JPEG", quality: int = 85) -> str:
    """Convert PIL Image to base64 with compression."""
    buffered = BytesIO()
    image.save(buffered, format=format, quality=quality, optimize=True)
    return base64.b64encode(buffered.getvalue()).decode("utf-8")


def vlm_extract_text(pdf_path: str) -> str:
    """
    Extract text from PDF using VLM (Llama-4-Maverick).
    Best performer: 87.75% CSR, 75s for 12 pages
    """
    images = pdf_to_images(pdf_path, dpi=100)

    system_prompt = """You are an expert OCR system for historical oil & gas documents.

Extract ALL text from the image with 100% accuracy. Follow these rules:
1. Preserve EXACT spelling - including Azerbaijani, Russian, and English text
2. Maintain original Cyrillic characters - DO NOT transliterate
3. Keep all numbers, symbols, and special characters exactly as shown
4. Preserve layout structure (paragraphs, line breaks)
5. Include ALL text - headers, body, footnotes, tables, captions

Output ONLY the extracted text. No explanations, no descriptions."""

    all_text = []

    print(f"   Extracting text from {len(images)} pages...")
    for page_num, image in enumerate(tqdm(images, desc="   OCR Progress"), 1):
        # Convert to base64
        image_base64 = image_to_base64(image, format="JPEG", quality=85)

        messages = [
            {"role": "system", "content": system_prompt},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Extract all text from page {page_num}:"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                ]
            }
        ]

        try:
            response = azure_client.chat.completions.create(
                model=VLM_MODEL,
                messages=messages,
                temperature=0.0,  # Deterministic OCR
                max_tokens=4000
            )

            page_text = response.choices[0].message.content
            all_text.append(page_text)

        except Exception as e:
            print(f"      ❌ Error on page {page_num}: {e}")
            all_text.append("")  # Add empty page on error

    # Combine all pages
    full_text = "\n\n".join(all_text)
    return full_text


def clean_text_for_vectordb(text: str) -> str:
    """
    Clean text for vector database storage.
    CRITICAL: Remove image markdown - images are ONLY for /ocr endpoint!
    """
    # Remove image markdown references
    clean = re.sub(r'!\[Image\]\([^)]+\)', '', text)

    # Normalize whitespace
    clean = re.sub(r'\n\s*\n+', '\n\n', clean)
    clean = clean.strip()

    return clean


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Chunk text with overlap for better context preservation.
    Optimal config from benchmarks: 600 chars, 100 overlap
    """
    if not text or len(text) == 0:
        return []

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at word boundary
        if end < len(text) and not text[end].isspace():
            last_space = chunk.rfind(' ')
            if last_space > chunk_size - 100:  # Keep chunk reasonably sized
                chunk = chunk[:last_space]
                end = start + last_space

        chunk = chunk.strip()
        if chunk:  # Only add non-empty chunks
            chunks.append(chunk)

        start = end - overlap if end < len(text) else end

    return chunks


def ingest_pdf(pdf_path: str) -> Dict:
    """
    Full ingestion pipeline for one PDF:
    1. VLM OCR (Llama-4-Maverick)
    2. Clean text (remove images)
    3. Chunk (600/100)
    4. Embed (bge-large-en)
    5. Upsert to Pinecone
    """
    pdf_name = Path(pdf_path).name
    start_time = time.time()

    print(f"\n{'='*70}")
    print(f"📄 Processing: {pdf_name}")
    print(f"{'='*70}")

    # Step 1: OCR with VLM
    print("   Step 1/5: Running VLM OCR...")
    ocr_start = time.time()
    raw_text = vlm_extract_text(pdf_path)
    ocr_time = time.time() - ocr_start
    print(f"   ✅ OCR complete: {len(raw_text)} characters ({ocr_time:.1f}s)")

    # Step 2: Clean text (remove image markdown)
    print("   Step 2/5: Cleaning text...")
    clean = clean_text_for_vectordb(raw_text)
    print(f"   ✅ Cleaned: {len(clean)} characters")

    # Step 3: Chunk text
    print("   Step 3/5: Chunking text...")
    chunks = chunk_text(clean, chunk_size=CHUNK_SIZE, overlap=CHUNK_OVERLAP)
    print(f"   ✅ Created {len(chunks)} chunks")

    if len(chunks) == 0:
        print("   ⚠️  No chunks created - skipping document")
        return {
            "pdf_name": pdf_name,
            "status": "skipped",
            "reason": "no_text_extracted",
            "time": time.time() - start_time
        }

    # Step 4: Generate embeddings
    print(f"   Step 4/5: Generating embeddings...")
    embed_start = time.time()
    embeddings = embedding_model.encode(chunks, show_progress_bar=True)
    embed_time = time.time() - embed_start
    print(f"   ✅ Embeddings generated ({embed_time:.1f}s)")

    # Step 5: Prepare vectors for Pinecone
    print("   Step 5/5: Upserting to Pinecone...")
    vectors = []

    # Calculate approximate page numbers
    # (simple heuristic: distribute chunks evenly across document)
    doc = fitz.open(pdf_path)
    num_pages = len(doc)
    doc.close()

    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        # Estimate page number (chunks distributed across pages)
        estimated_page = int((i / len(chunks)) * num_pages) + 1

        vectors.append({
            "id": f"{pdf_name}_chunk_{i}",
            "values": embedding.tolist(),
            "metadata": {
                "pdf_name": pdf_name,
                "page_number": estimated_page,
                "content": chunk  # Changed from "text" to "content" to match API expectations
            }
        })

    # Upsert in batches
    batch_size = 100
    upsert_start = time.time()

    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        index.upsert(vectors=batch)

    upsert_time = time.time() - upsert_start
    total_time = time.time() - start_time

    print(f"   ✅ Upserted {len(vectors)} vectors ({upsert_time:.1f}s)")
    print(f"\n   🎉 Complete: {pdf_name}")
    print(f"   📊 Total time: {total_time:.1f}s")
    print(f"   📊 Breakdown: OCR={ocr_time:.1f}s, Embed={embed_time:.1f}s, Upload={upsert_time:.1f}s")

    return {
        "pdf_name": pdf_name,
        "status": "success",
        "num_chunks": len(chunks),
        "num_vectors": len(vectors),
        "text_length": len(clean),
        "time_total": round(total_time, 2),
        "time_ocr": round(ocr_time, 2),
        "time_embedding": round(embed_time, 2),
        "time_upsert": round(upsert_time, 2)
    }


def ingest_all_pdfs(clear_existing: bool = False):
    """
    Ingest all PDFs from data/pdfs directory.

    Args:
        clear_existing: If True, clear existing index before ingestion
    """
    print("\n" + "="*70)
    print("🚀 SOCAR PDF INGESTION PIPELINE")
    print("="*70)
    print(f"📂 PDF Directory: {PDFS_DIR}")
    print(f"🎯 Vector Database: Pinecone ({os.getenv('PINECONE_INDEX_NAME')})")
    print(f"🤖 OCR Model: {VLM_MODEL}")
    print(f"📊 Embedding Model: BAAI/bge-large-en-v1.5")
    print(f"✂️  Chunking: {CHUNK_SIZE} chars, {CHUNK_OVERLAP} overlap")
    print("="*70)

    # Clear index if requested
    if clear_existing:
        print("\n⚠️  Clearing existing vectors from index...")
        response = input("Are you sure? This will delete ALL vectors. (yes/no): ")
        if response.lower() == "yes":
            index.delete(delete_all=True)
            print("✅ Index cleared")
            time.sleep(2)  # Wait for index to stabilize
        else:
            print("❌ Clearing cancelled")
            return

    # Get all PDFs
    pdf_files = sorted(PDFS_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"\n❌ No PDF files found in {PDFS_DIR}")
        return

    print(f"\n📚 Found {len(pdf_files)} PDF files")

    # Process each PDF
    results = []
    start_time = time.time()

    for pdf_path in pdf_files:
        try:
            result = ingest_pdf(str(pdf_path))
            results.append(result)
        except Exception as e:
            print(f"\n❌ Error processing {pdf_path.name}: {e}")
            results.append({
                "pdf_name": pdf_path.name,
                "status": "error",
                "error": str(e)
            })

    total_time = time.time() - start_time

    # Summary
    print("\n" + "="*70)
    print("📊 INGESTION SUMMARY")
    print("="*70)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]
    skipped = [r for r in results if r.get("status") == "skipped"]

    print(f"\n✅ Successful: {len(successful)}/{len(pdf_files)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏭️  Skipped: {len(skipped)}")
    print(f"\n⏱️  Total Time: {total_time/60:.1f} minutes")

    if successful:
        total_chunks = sum(r["num_chunks"] for r in successful)
        total_vectors = sum(r["num_vectors"] for r in successful)
        avg_time = sum(r["time_total"] for r in successful) / len(successful)

        print(f"\n📦 Total Chunks: {total_chunks}")
        print(f"🔢 Total Vectors: {total_vectors}")
        print(f"⏱️  Average Time per PDF: {avg_time:.1f}s")

    # Check index stats
    stats = index.describe_index_stats()
    print(f"\n📊 Pinecone Index Stats:")
    print(f"   Total Vectors: {stats.get('total_vector_count', 0)}")
    print(f"   Dimensions: {stats.get('dimension', 0)}")

    # Save detailed results
    import json
    results_file = OUTPUT_DIR / "ingestion_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_pdfs": len(pdf_files),
            "successful": len(successful),
            "failed": len(failed),
            "skipped": len(skipped),
            "total_time_seconds": round(total_time, 2),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Detailed results saved to: {results_file}")
    print("\n" + "="*70)
    print("🎉 INGESTION COMPLETE!")
    print("="*70)


def test_single_pdf(pdf_name: str = "document_00.pdf"):
    """Test ingestion with a single PDF."""
    pdf_path = PDFS_DIR / pdf_name

    if not pdf_path.exists():
        print(f"❌ PDF not found: {pdf_path}")
        return

    print(f"\n🧪 Testing with: {pdf_name}")
    result = ingest_pdf(str(pdf_path))

    print("\n📊 Test Result:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    import sys
    import json

    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]

        if command == "test":
            # Test with single PDF
            pdf_name = sys.argv[2] if len(sys.argv) > 2 else "document_00.pdf"
            test_single_pdf(pdf_name)

        elif command == "clear":
            # Clear index and ingest all
            ingest_all_pdfs(clear_existing=True)

        elif command == "stats":
            # Show current index stats
            stats = index.describe_index_stats()
            print("\n📊 Pinecone Index Stats:")
            if stats:
                print(f"   Total Vectors: {stats.get('total_vector_count', 0)}")
                print(f"   Dimensions: {stats.get('dimension', 0)}")
                if 'namespaces' in stats:
                    print(f"   Namespaces: {stats.get('namespaces', {})}")
            else:
                print("   No stats available")

        else:
            print("Usage:")
            print("  python ingest_pdfs.py          - Ingest all PDFs (append)")
            print("  python ingest_pdfs.py clear    - Clear index and ingest all")
            print("  python ingest_pdfs.py test     - Test with document_00.pdf")
            print("  python ingest_pdfs.py test document_05.pdf  - Test with specific PDF")
            print("  python ingest_pdfs.py stats    - Show index statistics")

    else:
        # Default: ingest all PDFs (append mode)
        ingest_all_pdfs(clear_existing=False)
