import google.generativeai as genai
from typing import List, Dict
import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import GEMINI_API_KEY, GEMINI_MODEL

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(GEMINI_MODEL)

SYSTEM_PROMPT = """You are a helpful assistant that answers questions based ONLY on the provided sources.

RULES:
1. Only use information from the provided sources
2. Cite sources using [1], [2], etc. inline in your answer
3. If the sources don't contain enough information, say "I cannot answer this based on the provided context."
4. Be concise but comprehensive
5. Never make up information not in the sources"""


async def generate_answer(query: str, sources: List[Dict]) -> Dict:
    start_time = time.time()
    
    if not sources:
        return {
            "answer": "I cannot answer this based on the provided context. No relevant sources were found.",
            "citations": [],
            "timing_ms": int((time.time() - start_time) * 1000),
            "token_estimate": 0
        }
    
    sources_text = "\n\n".join([
        f"[{i+1}] {source['text']}"
        for i, source in enumerate(sources)
    ])
    
    prompt = f"""{SYSTEM_PROMPT}

SOURCES:
{sources_text}

QUESTION: {query}

Provide a comprehensive answer with inline citations [1], [2], etc."""

    try:
        response = model.generate_content(prompt)
        answer = response.text
        
        citations = []
        for i, source in enumerate(sources):
            citations.append({
                "number": i + 1,
                "text": source['text'][:300] + "..." if len(source['text']) > 300 else source['text'],
                "source": source.get('source', 'Unknown'),
                "title": source.get('title', 'Untitled'),
                "score": source.get('rerank_score', source.get('score', 0))
            })
        
        token_estimate = (len(prompt) + len(answer)) // 4
        
        return {
            "answer": answer,
            "citations": citations,
            "timing_ms": int((time.time() - start_time) * 1000),
            "token_estimate": token_estimate
        }
        
    except Exception as e:
        return {
            "answer": f"Error generating answer: {str(e)}",
            "citations": [],
            "timing_ms": int((time.time() - start_time) * 1000),
            "token_estimate": 0
        }


def estimate_cost(token_count: int) -> Dict:
    input_tokens = int(token_count * 0.7)
    output_tokens = int(token_count * 0.3)
    
    input_cost = (input_tokens / 1_000_000) * 0.075
    output_cost = (output_tokens / 1_000_000) * 0.30
    
    return {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": round(input_cost + output_cost, 6)
    }
