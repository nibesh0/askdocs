import tiktoken
from typing import List, Dict
import re
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import CHUNK_SIZE, CHUNK_OVERLAP

encoding = tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    return len(encoding.encode(text))


def split_into_sentences(text: str) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, source: str = "unknown", title: str = "Untitled") -> List[Dict]:
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    chunks = []
    current_chunk = ""
    current_tokens = 0
    
    for para in paragraphs:
        para_tokens = count_tokens(para)
        
        if para_tokens > CHUNK_SIZE:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = ""
                current_tokens = 0
            
            sentences = split_into_sentences(para)
            for sentence in sentences:
                sent_tokens = count_tokens(sentence)
                
                if current_tokens + sent_tokens <= CHUNK_SIZE:
                    current_chunk += (" " if current_chunk else "") + sentence
                    current_tokens += sent_tokens
                else:
                    if current_chunk:
                        chunks.append(current_chunk)
                    current_chunk = sentence
                    current_tokens = sent_tokens
        
        elif current_tokens + para_tokens <= CHUNK_SIZE:
            current_chunk += ("\n\n" if current_chunk else "") + para
            current_tokens += para_tokens
        
        else:
            if current_chunk:
                chunks.append(current_chunk)
            current_chunk = para
            current_tokens = para_tokens
    
    if current_chunk:
        chunks.append(current_chunk)
    
    if CHUNK_OVERLAP > 0 and len(chunks) > 1:
        overlapped_chunks = []
        for i, chunk in enumerate(chunks):
            if i > 0:
                prev_sentences = split_into_sentences(chunks[i-1])
                overlap_text = ""
                overlap_tokens = 0
                
                for sent in reversed(prev_sentences):
                    sent_tokens = count_tokens(sent)
                    if overlap_tokens + sent_tokens <= CHUNK_OVERLAP:
                        overlap_text = sent + " " + overlap_text
                        overlap_tokens += sent_tokens
                    else:
                        break
                
                if overlap_text:
                    chunk = overlap_text.strip() + " " + chunk
            
            overlapped_chunks.append(chunk)
        chunks = overlapped_chunks
    
    result = []
    for i, chunk in enumerate(chunks):
        result.append({
            "text": chunk,
            "source": source,
            "title": title,
            "chunk_index": i,
            "token_count": count_tokens(chunk)
        })
    
    return result
