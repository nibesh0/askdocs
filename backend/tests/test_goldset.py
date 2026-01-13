"""
Gold Set Test Script - 5 Q/A pairs for RAG evaluation.
Run this after uploading a test document.
"""
import asyncio
import httpx
import time

API_URL = "http://localhost:8000"

# Test document content (upload this first)
TEST_DOCUMENT = """
# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence (AI) that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing algorithms that can access data and use it to learn for themselves.

## Types of Machine Learning

There are three main types of machine learning:

1. **Supervised Learning**: The algorithm learns from labeled training data. Examples include classification and regression tasks. Common algorithms are linear regression, decision trees, and neural networks.

2. **Unsupervised Learning**: The algorithm works with unlabeled data to find patterns. Examples include clustering and dimensionality reduction. K-means and principal component analysis (PCA) are popular methods.

3. **Reinforcement Learning**: The algorithm learns through trial and error by receiving rewards or penalties. It's used in robotics, game playing, and autonomous vehicles.

## Applications

Machine learning has numerous real-world applications:
- Email spam detection
- Product recommendations
- Voice assistants like Siri and Alexa
- Medical diagnosis
- Financial fraud detection
- Self-driving cars

## Challenges

Despite its power, machine learning faces several challenges:
- Requires large amounts of quality data
- Can perpetuate biases present in training data
- Models can be difficult to interpret (black box problem)
- Computational resources can be expensive
"""

# Gold set: 5 Q/A test pairs
GOLD_SET = [
    {
        "query": "What is machine learning?",
        "expected_keywords": ["artificial intelligence", "learn", "algorithm"],
        "description": "Basic concept question"
    },
    {
        "query": "What are the three main types of machine learning?",
        "expected_keywords": ["supervised", "unsupervised", "reinforcement"],
        "description": "Enumeration question - should cite multiple sources"
    },
    {
        "query": "What is the difference between supervised and unsupervised learning?",
        "expected_keywords": ["labeled", "unlabeled", "classification", "clustering"],
        "description": "Comparison question"
    },
    {
        "query": "What are some applications of machine learning?",
        "expected_keywords": ["spam", "recommendations", "diagnosis", "fraud"],
        "description": "List question"
    },
    {
        "query": "What is quantum computing?",
        "expected_keywords": ["cannot", "insufficient", "context"],
        "description": "No-answer question - not in document"
    }
]


async def upload_test_document():
    """Upload the test document."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            f"{API_URL}/api/upload",
            data={"text": TEST_DOCUMENT, "title": "Machine Learning Introduction"}
        )
        return response.json()


async def run_query(query: str, namespace: str = None):
    """Run a single query."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {"query": query}
        if namespace:
            payload["namespace"] = namespace
        response = await client.post(
            f"{API_URL}/api/query",
            json=payload
        )
        return response.json()


def evaluate_answer(answer: str, expected_keywords: list) -> dict:
    """Evaluate if answer contains expected keywords."""
    answer_lower = answer.lower()
    found = [kw for kw in expected_keywords if kw.lower() in answer_lower]
    missing = [kw for kw in expected_keywords if kw.lower() not in answer_lower]
    
    return {
        "found_keywords": found,
        "missing_keywords": missing,
        "recall": len(found) / len(expected_keywords) if expected_keywords else 0
    }


async def run_evaluation():
    """Run the full evaluation suite."""
    print("=" * 60)
    print("Mini RAG - Gold Set Evaluation")
    print("=" * 60)
    
    # Upload test document
    print("\n📤 Uploading test document...")
    upload_result = await upload_test_document()
    print(f"   ✓ Uploaded: {upload_result['stats']['chunks_created']} chunks")
    namespace = upload_result['stats']['namespace']
    
    # Run queries
    print("\n📋 Running test queries...\n")
    results = []
    
    for i, test in enumerate(GOLD_SET, 1):
        print(f"Test {i}: {test['description']}")
        print(f"   Query: {test['query']}")
        
        start = time.time()
        response = await run_query(test['query'], namespace)
        elapsed = time.time() - start
        
        evaluation = evaluate_answer(response['answer'], test['expected_keywords'])
        
        print(f"   Answer: {response['answer'][:100]}...")
        print(f"   Citations: {len(response.get('citations', []))}")
        print(f"   Time: {elapsed:.2f}s")
        print(f"   Recall: {evaluation['recall']*100:.0f}% ({len(evaluation['found_keywords'])}/{len(test['expected_keywords'])} keywords)")
        if evaluation['missing_keywords']:
            print(f"   Missing: {evaluation['missing_keywords']}")
        print()
        
        results.append({
            "test": test,
            "response": response,
            "evaluation": evaluation,
            "time": elapsed
        })
    
    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    
    avg_recall = sum(r['evaluation']['recall'] for r in results) / len(results)
    avg_time = sum(r['time'] for r in results) / len(results)
    
    print(f"Average Recall: {avg_recall*100:.1f}%")
    print(f"Average Response Time: {avg_time:.2f}s")
    print(f"Tests Passed: {sum(1 for r in results if r['evaluation']['recall'] >= 0.5)}/{len(results)}")


if __name__ == "__main__":
    asyncio.run(run_evaluation())
