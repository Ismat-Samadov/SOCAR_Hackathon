"""
Clear all data from Pinecone index
One-time script for data cleanup before re-ingestion
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

def clear_pinecone_index():
    """Delete all vectors from Pinecone index"""

    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    index = pc.Index(os.getenv('PINECONE_INDEX_NAME', 'hackathon'))

    # Get current stats
    stats = index.describe_index_stats()
    total_vectors = stats['total_vector_count']

    print("="*80)
    print("PINECONE DATA CLEANUP")
    print("="*80)
    print(f"\nIndex: {os.getenv('PINECONE_INDEX_NAME', 'hackathon')}")
    print(f"Current vectors: {total_vectors}")
    print(f"Dimensions: {stats.get('dimension', 'N/A')}")

    if total_vectors == 0:
        print("\n✅ Index is already empty. Nothing to delete.")
        return

    # Confirm deletion
    print(f"\n⚠️  WARNING: This will delete ALL {total_vectors} vectors!")
    confirm = input("Type 'DELETE' to confirm: ")

    if confirm != 'DELETE':
        print("\n❌ Deletion cancelled. No data was removed.")
        return

    print("\n🗑️  Deleting all vectors...")

    try:
        # Delete all vectors
        index.delete(delete_all=True)

        print("✅ Deletion completed!")

        # Verify deletion
        import time
        time.sleep(2)  # Wait for deletion to propagate

        stats = index.describe_index_stats()
        remaining = stats['total_vector_count']

        print(f"\n📊 Final status:")
        print(f"   Remaining vectors: {remaining}")

        if remaining == 0:
            print("   ✅ Index successfully cleared!")
        else:
            print(f"   ⚠️  {remaining} vectors still remain (may need a moment to sync)")

    except Exception as e:
        print(f"\n❌ Error during deletion: {e}")

if __name__ == "__main__":
    clear_pinecone_index()
