"""
Check Pinecone index status and statistics
Quick utility to inspect vector database
"""

import os
from dotenv import load_dotenv
from pinecone import Pinecone

# Load environment variables
load_dotenv()

def check_pinecone_status():
    """Display Pinecone index information"""

    try:
        # Initialize Pinecone
        pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
        index_name = os.getenv('PINECONE_INDEX_NAME', 'hackathon')
        index = pc.Index(index_name)

        # Get index statistics
        stats = index.describe_index_stats()

        print("="*80)
        print("PINECONE INDEX STATUS")
        print("="*80)

        print(f"\n📊 Index Information:")
        print(f"   Name: {index_name}")
        print(f"   Total Vectors: {stats.get('total_vector_count', 0):,}")
        print(f"   Dimensions: {stats.get('dimension', 'N/A')}")

        # Check namespaces if any
        if 'namespaces' in stats and stats['namespaces']:
            print(f"\n📁 Namespaces:")
            for ns_name, ns_stats in stats['namespaces'].items():
                ns_display = ns_name if ns_name else "(default)"
                print(f"   {ns_display}: {ns_stats.get('vector_count', 0):,} vectors")

        # Index configuration
        print(f"\n⚙️  Configuration:")
        print(f"   API Key: {os.getenv('PINECONE_API_KEY')[:10]}..." if os.getenv('PINECONE_API_KEY') else "   API Key: Not set")

        # Connection status
        if stats.get('total_vector_count', 0) > 0:
            print(f"\n✅ Status: Connected and populated")
        else:
            print(f"\n⚠️  Status: Connected but empty")

    except Exception as e:
        print("="*80)
        print("PINECONE CONNECTION ERROR")
        print("="*80)
        print(f"\n❌ Error: {e}")
        print("\nPlease check:")
        print("  1. PINECONE_API_KEY in .env file")
        print("  2. PINECONE_INDEX_NAME in .env file")
        print("  3. Index exists in your Pinecone account")

if __name__ == "__main__":
    check_pinecone_status()
