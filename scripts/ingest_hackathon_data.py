"""
Ingest ONLY PDFs from hackathon_data folder
Parallel processing with 4 workers using ThreadPoolExecutor (better for I/O-bound tasks)
"""

import os
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from dotenv import load_dotenv

# Load environment first (before any imports that need env vars)
load_dotenv()

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
PDFS_DIR = PROJECT_ROOT / "data" / "hackathon_data"  # Changed to hackathon_data
OUTPUT_DIR = PROJECT_ROOT / "output" / "ingestion"

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))


def worker_ingest(pdf_path: str):
    """
    Worker function to ingest a single PDF.
    Uses lazy imports to avoid issues with multiprocessing/threading.
    """
    try:
        # Import here to avoid global state issues in parallel execution
        import ingest_pdfs

        # Call the ingestion function
        result = ingest_pdfs.ingest_pdf(str(pdf_path))
        return result
    except Exception as e:
        import traceback
        return {
            "pdf_name": Path(pdf_path).name,
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc()
        }


def main():
    """Main parallel ingestion pipeline"""
    print("\n" + "="*70)
    print("🚀 HACKATHON DATA INGESTION (4x PARALLEL)")
    print("="*70)
    print(f"📂 PDF Directory: {PDFS_DIR}")
    print(f"⚡ Workers: 4 PDFs at once")
    print(f"🎯 Vector Database: Pinecone ({os.getenv('PINECONE_INDEX_NAME', 'hackathon')})")
    print("="*70)

    # Validate required environment variables
    required_env_vars = [
        "AZURE_OPENAI_API_KEY",
        "AZURE_OPENAI_ENDPOINT",
        "PINECONE_API_KEY",
        "PINECONE_INDEX_NAME"
    ]

    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        print(f"\n❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file.")
        return

    # Check if directory exists
    if not PDFS_DIR.exists():
        print(f"\n❌ Directory not found: {PDFS_DIR}")
        print(f"   Please create the directory and add PDFs to it.")
        return

    # Get all PDFs
    all_pdfs = sorted(PDFS_DIR.glob("*.pdf"))
    print(f"\n📚 Found {len(all_pdfs)} PDFs in hackathon_data folder")

    if not all_pdfs:
        print("\n❌ No PDFs found in hackathon_data folder!")
        print(f"   Please add PDF files to: {PDFS_DIR}")
        return

    for pdf in all_pdfs:
        print(f"   → {pdf.name}")

    print(f"\n⚡ Starting parallel processing with 4 workers...")
    print(f"⏱️  Estimated time: ~{len(all_pdfs) * 80 / 4 / 60:.1f} minutes\n")

    # Process in parallel using ThreadPoolExecutor
    # (Better for I/O-bound tasks like API calls to Azure and Pinecone)
    results = []
    completed = 0
    start_time = time.time()

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Submit all jobs
        future_to_pdf = {
            executor.submit(worker_ingest, str(pdf)): pdf
            for pdf in all_pdfs
        }

        # Collect results as they complete
        for future in as_completed(future_to_pdf):
            pdf = future_to_pdf[future]
            completed += 1

            try:
                result = future.result()
                results.append(result)

                if result.get("status") == "success":
                    elapsed = time.time() - start_time
                    avg_time = elapsed / completed
                    remaining = len(all_pdfs) - completed
                    eta = remaining * avg_time / 60

                    print(f"✅ [{completed}/{len(all_pdfs)}] {pdf.name}")
                    print(f"   📊 {result['num_vectors']} vectors, {result['time_total']:.1f}s")
                    print(f"   ⏱️  ETA: {eta:.1f} minutes remaining\n")
                else:
                    print(f"❌ [{completed}/{len(all_pdfs)}] {pdf.name} - {result.get('error', 'Unknown error')}\n")

            except Exception as e:
                print(f"❌ [{completed}/{len(all_pdfs)}] {pdf.name} - Error: {e}\n")
                results.append({
                    "pdf_name": pdf.name,
                    "status": "error",
                    "error": str(e)
                })

    total_time = time.time() - start_time

    # Summary
    print("\n" + "="*70)
    print("📊 INGESTION COMPLETE")
    print("="*70)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    print(f"\n✅ Successful: {len(successful)}/{len(all_pdfs)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total Time: {total_time/60:.1f} minutes")

    if successful:
        total_vectors = sum(r["num_vectors"] for r in successful)
        avg_time = sum(r["time_total"] for r in successful) / len(successful)
        print(f"\n📦 Total Vectors Uploaded: {total_vectors}")
        print(f"⏱️  Average Time per PDF: {avg_time:.1f}s")

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_file = OUTPUT_DIR / "hackathon_data_ingestion.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_folder": "hackathon_data",
            "total_pdfs": len(all_pdfs),
            "successful": len(successful),
            "failed": len(failed),
            "total_time_seconds": round(total_time, 2),
            "results": results
        }, f, indent=2, ensure_ascii=False)

    print(f"\n📄 Results saved to: {results_file}")

    # Final Pinecone stats
    try:
        from pinecone import Pinecone
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "hackathon"))
        stats = index.describe_index_stats()

        print(f"\n📊 Final Pinecone Stats:")
        # Handle both dict-like and object attribute access
        total_vectors = getattr(stats, 'total_vector_count', None) or stats.get('total_vector_count', 0)
        dimension = getattr(stats, 'dimension', None) or stats.get('dimension', 0)
        print(f"   Total Vectors: {total_vectors}")
        print(f"   Dimensions: {dimension}")

        # Show namespaces if available
        namespaces = getattr(stats, 'namespaces', None) or stats.get('namespaces', {})
        if namespaces:
            print(f"   Namespaces: {len(namespaces)}")
    except Exception as e:
        print(f"\n⚠️  Could not fetch Pinecone stats: {e}")
        print(f"   (This is non-fatal - ingestion was still successful)")

    print("\n" + "="*70)
    print("🎉 HACKATHON DATA INGESTION COMPLETE!")
    print("="*70)


if __name__ == "__main__":
    main()
