import math
import re
from typing import List, Dict
from collections import Counter
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import TOP_K_RERANK, RERANK_THRESHOLD

W_BM25 = 1.0
W_TITLE_MATCH = 2.0
W_PHRASE_MATCH = 1.5
W_TERM_COVERAGE = 1.0
W_VECTOR_SCORE = 0.5

K1 = 1.5
B = 0.75


def tokenize(text: str) -> List[str]:
    text = text.lower()
    tokens = re.findall(r'\b[a-z0-9]+\b', text)
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                 'should', 'may', 'might', 'must', 'shall', 'can', 'of', 'at', 'by',
                 'for', 'with', 'about', 'against', 'between', 'into', 'through',
                 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up',
                 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further',
                 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
                 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
                 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
                 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'this',
                 'that', 'these', 'those', 'what', 'which', 'who', 'whom', 'it', 'its'}
    return [t for t in tokens if t not in stopwords and len(t) > 1]


def compute_bm25(query_tokens: List[str], doc_tokens: List[str], avg_doc_len: float, doc_freq: Dict[str, int], total_docs: int) -> float:
    doc_len = len(doc_tokens)
    doc_tf = Counter(doc_tokens)
    score = 0.0
    
    for term in query_tokens:
        if term in doc_tf:
            tf = doc_tf[term]
            df = doc_freq.get(term, 1)
            idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
            numerator = tf * (K1 + 1)
            denominator = tf + K1 * (1 - B + B * (doc_len / avg_doc_len))
            score += idf * (numerator / denominator)
    
    return score


def compute_title_match(query_tokens: List[str], title: str) -> float:
    title_tokens = set(tokenize(title))
    if not title_tokens:
        return 0.0
    matches = sum(1 for t in query_tokens if t in title_tokens)
    return matches / len(query_tokens) if query_tokens else 0.0


def compute_phrase_match(query: str, text: str) -> float:
    query_lower = query.lower()
    text_lower = text.lower()
    
    if query_lower in text_lower:
        return 1.0
    
    words = query_lower.split()
    if len(words) >= 2:
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
        matches = sum(1 for bg in bigrams if bg in text_lower)
        return matches / len(bigrams) if bigrams else 0.0
    
    return 0.0


def compute_term_coverage(query_tokens: List[str], doc_tokens: List[str]) -> float:
    if not query_tokens:
        return 0.0
    doc_set = set(doc_tokens)
    covered = sum(1 for t in query_tokens if t in doc_set)
    return covered / len(query_tokens)


async def rerank_documents(query: str, documents: List[Dict], top_k: int = TOP_K_RERANK) -> List[Dict]:
    if not documents:
        return []
    
    query_tokens = tokenize(query)
    
    doc_tokens_list = [tokenize(doc['text']) for doc in documents]
    total_docs = len(documents)
    avg_doc_len = sum(len(tokens) for tokens in doc_tokens_list) / total_docs if total_docs > 0 else 1
    
    doc_freq = {}
    for tokens in doc_tokens_list:
        for term in set(tokens):
            doc_freq[term] = doc_freq.get(term, 0) + 1
    
    scored_docs = []
    for i, doc in enumerate(documents):
        doc_tokens = doc_tokens_list[i]
        
        bm25_score = compute_bm25(query_tokens, doc_tokens, avg_doc_len, doc_freq, total_docs)
        title_score = compute_title_match(query_tokens, doc.get('title', ''))
        phrase_score = compute_phrase_match(query, doc['text'])
        coverage_score = compute_term_coverage(query_tokens, doc_tokens)
        vector_score = doc.get('score', 0)
        
        final_score = (
            W_BM25 * bm25_score +
            W_TITLE_MATCH * title_score +
            W_PHRASE_MATCH * phrase_score +
            W_TERM_COVERAGE * coverage_score +
            W_VECTOR_SCORE * vector_score
        )
        
        max_possible = W_BM25 * 10 + W_TITLE_MATCH + W_PHRASE_MATCH + W_TERM_COVERAGE + W_VECTOR_SCORE
        normalized_score = min(final_score / max_possible, 1.0) if max_possible > 0 else 0
        
        doc_copy = doc.copy()
        doc_copy['rerank_score'] = normalized_score
        scored_docs.append(doc_copy)
    
    scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
    
    filtered_docs = [doc for doc in scored_docs if doc['rerank_score'] >= RERANK_THRESHOLD]
    
    return filtered_docs[:top_k]


def check_sufficient_context(documents: List[Dict]) -> bool:
    if not documents:
        return False
    top_score = documents[0].get('rerank_score', 0)
    return top_score >= RERANK_THRESHOLD
