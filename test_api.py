"""
Quick test script for SOCAR LLM API
"""

import requests
import json
from docs.sample_questions import questions

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_root():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    response = requests.get(BASE_URL)
    print(f"Status: {response.status_code}")
    print(json.dumps(response.json(), indent=2))
    print()

def test_llm(question: str):
    """Test LLM endpoint"""
    print(f"🔍 Testing LLM endpoint...")
    print(f"Question: {question}\n")

    payload = {
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": 0.2,
        "max_tokens": 1000
    }

    response = requests.post(f"{BASE_URL}/llm", json=payload)
    print(f"Status: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        print(f"Response time: {result['response_time']}s")
        print(f"Model: {result['model']}")
        print(f"\nAnswer:\n{result['response']}")
        print(f"\nSources:")
        for source in result['sources']:
            print(f"  - {source['pdf_name']}, Page {source['page_number']} (score: {source['relevance_score']})")
    else:
        print(f"Error: {response.text}")
    print()

if __name__ == "__main__":
    print("="*80)
    print("SOCAR LLM API Test Suite")
    print("="*80)
    print()

    # Test health
    try:
        test_health()
    except Exception as e:
        print(f"❌ Health check failed: {e}\n")

    # Test root
    try:
        test_root()
    except Exception as e:
        print(f"❌ Root endpoint failed: {e}\n")

    # Test LLM with sample question
    try:
        test_llm("Palçıq vulkanlarının təsir radiusu nə qədərdir?")
    except Exception as e:
        print(f"❌ LLM endpoint failed: {e}\n")

    print("="*80)
    print("✅ Test suite completed!")
    print("="*80)
