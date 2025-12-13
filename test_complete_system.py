"""Complete system test"""

import requests
import json
from pathlib import Path

API_URL = "http://localhost:8000"

def test_health():
    """Test API health"""
    print("=" * 60)
    print("1. Testing API Health")
    print("=" * 60)
    response = requests.get(f"{API_URL}/")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    return response.status_code == 200


def test_ocr():
    """Test OCR endpoint"""
    print("\n" + "=" * 60)
    print("2. Testing OCR Endpoint")
    print("=" * 60)

    pdf_path = Path("data/pdfs/document_00.pdf")
    if not pdf_path.exists():
        print("❌ PDF not found")
        return False

    with open(pdf_path, "rb") as f:
        files = {"file": (pdf_path.name, f, "application/pdf")}
        response = requests.post(f"{API_URL}/ocr", files=files)

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Successfully processed {len(result)} pages")
        print(f"  First page preview: {result[0]['MD_text'][:100]}...")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False


def test_llm():
    """Test LLM endpoint"""
    print("\n" + "=" * 60)
    print("3. Testing LLM Endpoint (RAG)")
    print("=" * 60)

    messages = [
        {"role": "user", "content": "What geological formations are discussed?"}
    ]

    response = requests.post(
        f"{API_URL}/llm",
        json=messages,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Generated answer with {len(result['sources'])} sources")
        print(f"\nAnswer preview:")
        print(result["answer"][:300] + "...")
        print(f"\nSources:")
        for i, src in enumerate(result["sources"][:3], 1):
            print(f"  [{i}] {src['pdf_name']} - Page {src['page_number']}")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False


def test_llm_with_history():
    """Test LLM with chat history"""
    print("\n" + "=" * 60)
    print("4. Testing LLM with Chat History")
    print("=" * 60)

    messages = [
        {"role": "user", "content": "What is the South Caspian Basin?"},
        {"role": "assistant", "content": "The South Caspian Basin is a sedimentary basin..."},
        {"role": "user", "content": "Tell me more about its hydrocarbon potential."}
    ]

    response = requests.post(
        f"{API_URL}/llm",
        json=messages,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code == 200:
        result = response.json()
        print(f"✓ Generated contextual answer with chat history")
        print(f"  Answer length: {len(result['answer'])} characters")
        print(f"  Sources: {len(result['sources'])} documents")
        return True
    else:
        print(f"❌ Error: {response.status_code}")
        return False


if __name__ == "__main__":
    print("\n" + "🚀" * 30)
    print("SOCAR Document Processing System - Complete Test")
    print("🚀" * 30 + "\n")

    results = []
    results.append(("Health Check", test_health()))
    results.append(("OCR Endpoint", test_ocr()))
    results.append(("LLM Endpoint", test_llm()))
    results.append(("LLM Chat History", test_llm_with_history()))

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    for name, passed in results:
        status = "✓ PASS" if passed else "❌ FAIL"
        print(f"{status:10} - {name}")

    all_passed = all(r[1] for r in results)
    print("\n" + ("🎉" if all_passed else "❌") * 30)
    if all_passed:
        print("ALL TESTS PASSED - System Ready for Hackathon!")
    else:
        print("Some tests failed - please review")
    print(("🎉" if all_passed else "❌") * 30 + "\n")
