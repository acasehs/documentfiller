#!/usr/bin/env python3
"""
Intelligent Content Processing Module
Handles decision between RAG and full prompt approaches based on content size and complexity
Includes document ingestion and context optimization strategies
"""

import os
import json
import hashlib
import sqlite3  # Built-in
import requests  # pip install requests
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
import pickle
import threading
import time

# Optional dependencies with graceful degradation
try:
    import tiktoken  # pip install tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    print("⚠ tiktoken not available - using character-based estimation")
    HAS_TIKTOKEN = False
    tiktoken = None

try:
    from sklearn.feature_extraction.text import TfidfVectorizer  # pip install scikit-learn
    from sklearn.metrics.pairwise import cosine_similarity
    import numpy as np  # pip install numpy
    HAS_SKLEARN = True
except ImportError:
    print("⚠ scikit-learn/numpy not available - using basic similarity")
    HAS_SKLEARN = False
    TfidfVectorizer = None
    cosine_similarity = None
    np = None

@dataclass
class DocumentChunk:
    """Represents a document chunk for RAG processing"""
    id: str
    content: str
    section_path: str
    char_count: int
    token_count: int
    embedding: Optional[List[float]] = None
    metadata: Dict = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

@dataclass
class ProcessingStrategy:
    """Represents the chosen processing strategy for content"""
    method: str  # "full_prompt", "rag", "hybrid"
    reason: str
    token_estimate: int
    chunk_count: int = 0
    confidence: float = 0.0

@dataclass
class ContentMetrics:
    """Content analysis metrics for processing decisions"""
    char_count: int
    token_count: int
    complexity_score: float
    technical_density: float
    section_count: int
    avg_section_length: int

class IntelligentContentProcessor:
    """Handles intelligent content processing strategy selection"""

    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.rag_threshold = self.config.get('rag_threshold', 10000)  # characters
        self.max_prompt_tokens = self.config.get('max_prompt_tokens', 8000)
        self.chunk_size = self.config.get('chunk_size', 1000)  # characters
        self.chunk_overlap = self.config.get('chunk_overlap', 100)  # characters

        # Initialize tokenizer (OpenAI's tiktoken for consistent token counting)
        if HAS_TIKTOKEN:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")
            except:
                self.tokenizer = None
        else:
            self.tokenizer = None

        # Initialize document store (SQLite for simplicity)
        self.db_path = self.config.get('document_store_path', 'document_store.db')
        self.init_document_store()

        # TF-IDF for content similarity (lightweight alternative to embeddings)
        if HAS_SKLEARN:
            self.vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.vectorizer = None

        # Cache for processed documents
        self.content_cache = {}
        self.cache_ttl = timedelta(hours=1)
    
    def init_document_store(self):
        """Initialize SQLite database for document storage"""
        try:
            os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        except:
            pass
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS document_chunks (
                        id TEXT PRIMARY KEY,
                        document_path TEXT,
                        section_path TEXT,
                        content TEXT,
                        char_count INTEGER,
                        token_count INTEGER,
                        embedding BLOB,
                        metadata TEXT,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                ''')
                
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS document_metadata (
                        document_path TEXT PRIMARY KEY,
                        total_chunks INTEGER,
                        processing_strategy TEXT,
                        last_processed TIMESTAMP,
                        content_hash TEXT
                    )
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_document_path 
                    ON document_chunks(document_path)
                ''')
                
                conn.execute('''
                    CREATE INDEX IF NOT EXISTS idx_section_path 
                    ON document_chunks(section_path)
                ''')
                
                conn.commit()
        except Exception as e:
            print(f"Error initializing document store: {e}")
    
    def analyze_content_metrics(self, content: str, sections: List = None) -> ContentMetrics:
        """Analyze content to determine processing requirements"""
        char_count = len(content)
        
        # Estimate token count
        if self.tokenizer:
            token_count = len(self.tokenizer.encode(content))
        else:
            # Fallback: rough estimation (1 token ≈ 4 characters for English)
            token_count = char_count // 4
        
        # Calculate complexity score based on various factors
        complexity_factors = []
        
        # Sentence length complexity
        sentences = content.split('. ')
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            complexity_factors.append(min(1.0, avg_sentence_length / 20))  # Normalize to 0-1
        
        # Technical term density (simplified)
        technical_indicators = [
            'system', 'process', 'function', 'method', 'algorithm', 'protocol',
            'configuration', 'implementation', 'framework', 'architecture',
            'interface', 'specification', 'parameter', 'component', 'module'
        ]
        
        word_count = len(content.split())
        technical_count = sum(content.lower().count(term) for term in technical_indicators)
        technical_density = technical_count / word_count if word_count > 0 else 0
        complexity_factors.append(min(1.0, technical_density * 10))
        
        # Code/syntax density
        code_indicators = ['()', '{}', '[]', '=', ';', '->', '=>', '::']
        code_count = sum(content.count(indicator) for indicator in code_indicators)
        code_density = code_count / char_count if char_count > 0 else 0
        complexity_factors.append(min(1.0, code_density * 100))
        
        complexity_score = sum(complexity_factors) / len(complexity_factors) if complexity_factors else 0
        
        # Section analysis
        section_count = len(sections) if sections else content.count('\n\n') + 1
        avg_section_length = char_count // section_count if section_count > 0 else char_count
        
        return ContentMetrics(
            char_count=char_count,
            token_count=token_count,
            complexity_score=complexity_score,
            technical_density=technical_density,
            section_count=section_count,
            avg_section_length=avg_section_length
        )
    
    def determine_processing_strategy(self, content: str, sections: List = None, 
                                    query_context: str = "") -> ProcessingStrategy:
        """Determine optimal processing strategy based on content analysis"""
        metrics = self.analyze_content_metrics(content, sections)
        
        # Decision factors
        factors = {
            'size': metrics.char_count,
            'tokens': metrics.token_count,
            'complexity': metrics.complexity_score,
            'sections': metrics.section_count
        }
        
        # Strategy decision logic
        if metrics.token_count <= self.max_prompt_tokens * 0.6:
            # Content fits comfortably in prompt
            strategy = ProcessingStrategy(
                method="full_prompt",
                reason=f"Content size ({metrics.token_count} tokens) fits within prompt limits",
                token_estimate=metrics.token_count,
                confidence=0.9
            )
        
        elif metrics.char_count > self.rag_threshold and metrics.section_count > 5:
            # Large, multi-section document - use RAG
            estimated_chunks = (metrics.char_count // self.chunk_size) + 1
            strategy = ProcessingStrategy(
                method="rag",
                reason=f"Large document ({metrics.char_count} chars, {metrics.section_count} sections) benefits from RAG",
                token_estimate=self.max_prompt_tokens,  # RAG uses fixed context
                chunk_count=estimated_chunks,
                confidence=0.8
            )
        
        elif metrics.complexity_score > 0.7 and metrics.section_count > 3:
            # High complexity content - use hybrid approach
            strategy = ProcessingStrategy(
                method="hybrid",
                reason=f"High complexity ({metrics.complexity_score:.2f}) suggests hybrid RAG+prompt approach",
                token_estimate=self.max_prompt_tokens,
                chunk_count=min(5, metrics.section_count),
                confidence=0.7
            )
        
        else:
            # Default to full prompt with truncation if needed
            strategy = ProcessingStrategy(
                method="full_prompt",
                reason="Standard content suitable for direct prompting",
                token_estimate=min(metrics.token_count, self.max_prompt_tokens),
                confidence=0.6
            )
        
        return strategy
    
    def chunk_content(self, content: str, document_path: str, sections: List = None) -> List[DocumentChunk]:
        """Split content into chunks for RAG processing"""
        chunks = []
        
        if sections:
            # Chunk by sections first
            for section in sections:
                section_content = getattr(section, 'get_existing_content', lambda: str(section))()
                section_path = getattr(section, 'get_full_path', lambda: str(section))()
                
                if len(section_content) > self.chunk_size:
                    # Split large sections
                    section_chunks = self._split_text_by_size(
                        section_content, 
                        section_path,
                        document_path
                    )
                    chunks.extend(section_chunks)
                else:
                    # Keep small sections intact
                    chunk_id = self._generate_chunk_id(document_path, section_path)
                    chunk = DocumentChunk(
                        id=chunk_id,
                        content=section_content,
                        section_path=section_path,
                        char_count=len(section_content),
                        token_count=self._estimate_tokens(section_content),
                        metadata={'document_path': document_path, 'section_based': True}
                    )
                    chunks.append(chunk)
        else:
            # Split by size when no section structure
            chunks = self._split_text_by_size(content, document_path, document_path)
        
        return chunks
    
    def _split_text_by_size(self, text: str, section_path: str, document_path: str) -> List[DocumentChunk]:
        """Split text into size-based chunks with overlap"""
        chunks = []
        start = 0
        chunk_num = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence break within overlap range
                break_point = text.rfind('. ', start, end + self.chunk_overlap)
                if break_point == -1:
                    break_point = text.rfind('\n', start, end + self.chunk_overlap)
                if break_point != -1 and break_point > start:
                    end = break_point + 1
            
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunk_id = self._generate_chunk_id(document_path, f"{section_path}_chunk_{chunk_num}")
                
                chunk = DocumentChunk(
                    id=chunk_id,
                    content=chunk_content,
                    section_path=f"{section_path} (chunk {chunk_num})",
                    char_count=len(chunk_content),
                    token_count=self._estimate_tokens(chunk_content),
                    metadata={
                        'document_path': document_path,
                        'chunk_number': chunk_num,
                        'start_pos': start,
                        'end_pos': end
                    }
                )
                chunks.append(chunk)
                chunk_num += 1
            
            # Move start position with overlap
            start = end - self.chunk_overlap
            
        return chunks
    
    def _generate_chunk_id(self, document_path: str, section_path: str) -> str:
        """Generate unique chunk ID"""
        content = f"{document_path}::{section_path}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text"""
        if self.tokenizer:
            return len(self.tokenizer.encode(text))
        else:
            return len(text) // 4  # Rough approximation
    
    def store_chunks(self, chunks: List[DocumentChunk], document_path: str):
        """Store chunks in document store"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Clear existing chunks for this document
                conn.execute('DELETE FROM document_chunks WHERE document_path = ?', (document_path,))
                
                # Insert new chunks
                for chunk in chunks:
                    conn.execute('''
                        INSERT INTO document_chunks 
                        (id, document_path, section_path, content, char_count, token_count, 
                         metadata, created_at, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        chunk.id,
                        document_path,
                        chunk.section_path,
                        chunk.content,
                        chunk.char_count,
                        chunk.token_count,
                        json.dumps(chunk.metadata),
                        datetime.now().isoformat(),
                        datetime.now().isoformat()
                    ))
                
                # Update document metadata
                content_hash = self._calculate_content_hash(chunks)
                conn.execute('''
                    INSERT OR REPLACE INTO document_metadata
                    (document_path, total_chunks, processing_strategy, last_processed, content_hash)
                    VALUES (?, ?, ?, ?, ?)
                ''', (
                    document_path,
                    len(chunks),
                    'rag',
                    datetime.now().isoformat(),
                    content_hash
                ))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error storing chunks: {e}")
    
    def _calculate_content_hash(self, chunks: List[DocumentChunk]) -> str:
        """Calculate hash of chunk contents for change detection"""
        content = ''.join(chunk.content for chunk in chunks)
        return hashlib.sha256(content.encode()).hexdigest()
    
    def retrieve_relevant_chunks(self, query: str, document_path: str, 
                               max_chunks: int = 5) -> List[DocumentChunk]:
        """Retrieve most relevant chunks for a query using TF-IDF similarity"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT id, content, section_path, char_count, token_count, metadata
                    FROM document_chunks
                    WHERE document_path = ?
                    ORDER BY section_path
                ''', (document_path,))
                
                rows = cursor.fetchall()
                if not rows:
                    return []
                
                chunks = []
                contents = []
                
                for row in rows:
                    chunk = DocumentChunk(
                        id=row[0],
                        content=row[1],
                        section_path=row[2],
                        char_count=row[3],
                        token_count=row[4],
                        metadata=json.loads(row[5]) if row[5] else {}
                    )
                    chunks.append(chunk)
                    contents.append(row[1])
                
                if not contents:
                    return []
                
                # Calculate TF-IDF similarity
                try:
                    # Fit vectorizer on chunk contents plus query
                    all_texts = contents + [query]
                    tfidf_matrix = self.vectorizer.fit_transform(all_texts)
                    
                    # Get query vector (last row)
                    query_vector = tfidf_matrix[-1]
                    chunk_vectors = tfidf_matrix[:-1]
                    
                    # Calculate cosine similarity
                    similarities = cosine_similarity(query_vector, chunk_vectors).flatten()
                    
                    # Get top chunks by similarity
                    top_indices = np.argsort(similarities)[::-1][:max_chunks]
                    
                    relevant_chunks = [chunks[i] for i in top_indices if similarities[i] > 0.1]
                    
                    return relevant_chunks
                    
                except Exception as e:
                    print(f"Error in similarity calculation: {e}")
                    # Fallback: return first max_chunks chunks
                    return chunks[:max_chunks]
                
        except Exception as e:
            print(f"Error retrieving chunks: {e}")
            return []
    
    def build_rag_context(self, query: str, document_path: str, 
                         sections: List = None) -> Tuple[str, List[DocumentChunk]]:
        """Build RAG context by retrieving and formatting relevant chunks"""
        relevant_chunks = self.retrieve_relevant_chunks(query, document_path)
        
        if not relevant_chunks:
            return "No relevant content found.", []
        
        # Build context string
        context_parts = []
        total_tokens = 0
        used_chunks = []
        
        for chunk in relevant_chunks:
            # Check if adding this chunk would exceed token limit
            if total_tokens + chunk.token_count > (self.max_prompt_tokens * 0.7):
                break
            
            context_parts.append(f"Section: {chunk.section_path}\nContent: {chunk.content}\n")
            total_tokens += chunk.token_count
            used_chunks.append(chunk)
        
        context = "\n---\n".join(context_parts)
        
        if not context:
            context = "Content available but too large for context window."
        
        return context, used_chunks
    
    def process_content_with_strategy(self, content: str, query: str, 
                                    document_path: str, sections: List = None) -> Dict:
        """Process content using the optimal strategy"""
        strategy = self.determine_processing_strategy(content, sections, query)
        
        result = {
            'strategy': strategy,
            'context': '',
            'chunks_used': [],
            'processing_time': 0
        }
        
        start_time = time.time()
        
        try:
            if strategy.method == "full_prompt":
                # Use full content, truncate if necessary
                if strategy.token_estimate > self.max_prompt_tokens:
                    truncated = self._truncate_content(content, self.max_prompt_tokens * 0.8)
                    result['context'] = truncated
                    result['truncated'] = True
                else:
                    result['context'] = content
                    result['truncated'] = False
            
            elif strategy.method == "rag":
                # Use RAG approach
                chunks = self.chunk_content(content, document_path, sections)
                self.store_chunks(chunks, document_path)
                
                context, used_chunks = self.build_rag_context(query, document_path, sections)
                result['context'] = context
                result['chunks_used'] = used_chunks
                result['total_chunks'] = len(chunks)
            
            elif strategy.method == "hybrid":
                # Hybrid approach: key sections + RAG for details
                if sections:
                    # Get summary of all sections
                    section_summaries = []
                    for section in sections[:3]:  # Limit to first 3 sections
                        section_content = getattr(section, 'get_existing_content', lambda: str(section))()
                        summary = section_content[:200] + "..." if len(section_content) > 200 else section_content
                        section_summaries.append(f"Section: {getattr(section, 'get_full_path', lambda: str(section))()}\n{summary}")
                    
                    base_context = "\n\n".join(section_summaries)
                    
                    # Add RAG context for specific query
                    chunks = self.chunk_content(content, document_path, sections)
                    self.store_chunks(chunks, document_path)
                    
                    rag_context, used_chunks = self.build_rag_context(query, document_path, sections)
                    
                    result['context'] = f"Document Overview:\n{base_context}\n\n---\n\nRelevant Details:\n{rag_context}"
                    result['chunks_used'] = used_chunks
                else:
                    # Fallback to RAG if no sections
                    chunks = self.chunk_content(content, document_path)
                    self.store_chunks(chunks, document_path)
                    
                    context, used_chunks = self.build_rag_context(query, document_path)
                    result['context'] = context
                    result['chunks_used'] = used_chunks
            
        except Exception as e:
            print(f"Error in content processing: {e}")
            # Fallback to truncated content
            result['context'] = self._truncate_content(content, self.max_prompt_tokens * 0.8)
            result['error'] = str(e)
        
        result['processing_time'] = time.time() - start_time
        return result
    
    def _truncate_content(self, content: str, max_tokens: int) -> str:
        """Truncate content to fit within token limit"""
        if self.tokenizer:
            tokens = self.tokenizer.encode(content)
            if len(tokens) <= max_tokens:
                return content
            
            # Truncate tokens and decode back to text
            truncated_tokens = tokens[:int(max_tokens)]
            return self.tokenizer.decode(truncated_tokens)
        else:
            # Rough character-based truncation
            max_chars = int(max_tokens * 4)
            if len(content) <= max_chars:
                return content
            
            return content[:max_chars] + "\n\n[Content truncated for length]"
    
    def cleanup_old_chunks(self, days_old: int = 7):
        """Clean up old document chunks"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    DELETE FROM document_chunks 
                    WHERE created_at < ?
                ''', (cutoff_date.isoformat(),))
                
                conn.execute('''
                    DELETE FROM document_metadata 
                    WHERE last_processed < ?
                ''', (cutoff_date.isoformat(),))
                
                conn.commit()
                
        except Exception as e:
            print(f"Error cleaning up old chunks: {e}")
    
    def get_processing_stats(self) -> Dict:
        """Get statistics about document processing"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT 
                        COUNT(DISTINCT document_path) as total_documents,
                        COUNT(*) as total_chunks,
                        AVG(char_count) as avg_chunk_size,
                        SUM(char_count) as total_content_size
                    FROM document_chunks
                ''')
                
                row = cursor.fetchone()
                
                return {
                    'total_documents': row[0] or 0,
                    'total_chunks': row[1] or 0,
                    'avg_chunk_size': row[2] or 0,
                    'total_content_size': row[3] or 0,
                    'database_size': os.path.getsize(self.db_path) if os.path.exists(self.db_path) else 0
                }
                
        except Exception as e:
            print(f"Error getting processing stats: {e}")
            return {}
