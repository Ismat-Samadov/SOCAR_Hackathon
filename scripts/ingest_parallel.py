"""
Parallel PDF Ingestion - 4x Faster
Processes 4 PDFs simultaneously without affecting quality
"""

import os
import sys
import time
import json
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment
load_dotenv()

# Import from the main ingestion script
PROJECT_ROOT = Path(__file__).parent.parent
PDFS_DIR = PROJECT_ROOT / "data" / "pdfs"
OUTPUT_DIR = PROJECT_ROOT / "output" / "ingestion"

# Import the ingestion function
import ingest_pdfs

def get_already_processed():
    """Check which PDFs are already in Pinecone"""
    try:
        from pinecone import Pinecone

        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index = pc.Index(os.getenv("PINECONE_INDEX_NAME", "hackathon"))

        # Query to get all unique PDF names
        results = index.query(
            vector=[0.0] * 1024,
            top_k=10000,
            include_metadata=True
        )

        processed = set()
        for match in results.get('matches', []):
            pdf_name = match.get('metadata', {}).get('pdf_name')
            if pdf_name:
                processed.add(pdf_name)

        return processed
    except Exception as e:
        print(f"Warning: Could not check existing PDFs: {e}")
        return set()


def worker_ingest(pdf_path: str):
    """Worker function to ingest a single PDF"""
    try:
        result = ingest_pdfs.ingest_pdf(str(pdf_path))
        return result
    except Exception as e:
        return {
            "pdf_name": Path(pdf_path).name,
            "status": "error",
            "error": str(e)
        }


def main():
    """Main parallel ingestion pipeline"""
    print("\n" + "="*70)
    print("🚀 PARALLEL PDF INGESTION (4x FASTER)")
    print("="*70)
    print(f"📂 PDF Directory: {PDFS_DIR}")
    print(f"⚡ Workers: 4 PDFs at once")
    print(f"🎯 Vector Database: Pinecone ({os.getenv('PINECONE_INDEX_NAME')})")
    print("="*70)

    # Get all PDFs
    all_pdfs = sorted(PDFS_DIR.glob("*.pdf"))
    print(f"\n📚 Found {len(all_pdfs)} total PDFs")

    # Check what's already done
    print("\n🔍 Checking Pinecone for already processed PDFs...")
    already_processed = get_already_processed()

    if already_processed:
        print(f"✅ Already processed: {len(already_processed)} PDFs")
        for pdf in sorted(already_processed):
            print(f"   ✓ {pdf}")

    # Filter to only unprocessed PDFs
    pdfs_to_process = [
        pdf for pdf in all_pdfs
        if pdf.name not in already_processed
    ]

    if not pdfs_to_process:
        print("\n🎉 All PDFs already processed!")
        return

    print(f"\n⏳ Remaining to process: {len(pdfs_to_process)} PDFs")
    for pdf in pdfs_to_process:
        print(f"   → {pdf.name}")

    print(f"\n⚡ Starting parallel processing with 4 workers...")
    print(f"⏱️  Estimated time: ~{len(pdfs_to_process) * 80 / 4 / 60:.1f} minutes\n")

    # Process in parallel
    results = []
    completed = 0
    start_time = time.time()

    with ProcessPoolExecutor(max_workers=4) as executor:
        # Submit all jobs
        future_to_pdf = {
            executor.submit(worker_ingest, str(pdf)): pdf
            for pdf in pdfs_to_process
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
                    remaining = len(pdfs_to_process) - completed
                    eta = remaining * avg_time / 60

                    print(f"✅ [{completed}/{len(pdfs_to_process)}] {pdf.name}")
                    print(f"   📊 {result['num_vectors']} vectors, {result['time_total']:.1f}s")
                    print(f"   ⏱️  ETA: {eta:.1f} minutes remaining\n")
                else:
                    print(f"❌ [{completed}/{len(pdfs_to_process)}] {pdf.name} - {result.get('error', 'Unknown error')}\n")

            except Exception as e:
                print(f"❌ [{completed}/{len(pdfs_to_process)}] {pdf.name} - Error: {e}\n")
                results.append({
                    "pdf_name": pdf.name,
                    "status": "error",
                    "error": str(e)
                })

    total_time = time.time() - start_time

    # Summary
    print("\n" + "="*70)
    print("📊 PARALLEL INGESTION COMPLETE")
    print("="*70)

    successful = [r for r in results if r.get("status") == "success"]
    failed = [r for r in results if r.get("status") == "error"]

    print(f"\n✅ Successful: {len(successful)}/{len(pdfs_to_process)}")
    print(f"❌ Failed: {len(failed)}")
    print(f"⏱️  Total Time: {total_time/60:.1f} minutes")

    if successful:
        total_vectors = sum(r["num_vectors"] for r in successful)
        avg_time = sum(r["time_total"] for r in successful) / len(successful)
        print(f"\n📦 Total Vectors Uploaded: {total_vectors}")
        print(f"⏱️  Average Time per PDF: {avg_time:.1f}s")

    # Save results
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    results_file = OUTPUT_DIR / "parallel_ingestion_results.json"

    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_pdfs": len(pdfs_to_process),
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
        print(f"   Total Vectors: {stats.get('total_vector_count', 0)}")
        print(f"   Dimensions: {stats.get('dimension', 0)}")
    except Exception as e:
        print(f"\nCould not fetch Pinecone stats: {e}")

    print("\n" + "="*70)
    print("🎉 ALL DONE!")
    print("="*70)


if __name__ == "__main__":
    main()
