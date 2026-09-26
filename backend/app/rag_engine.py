"""
AgriMind — RAG Retrieval Engine
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Retrieves the most relevant agronomic knowledge chunks from the knowledge
base for a given diagnostic query.

Two retrieval strategies (selected automatically):

1. **Semantic (preferred)** — Uses Google's ``text-embedding-004`` model to
   embed both the query and corpus chunks, then ranks by cosine similarity.
   Requires ``GEMINI_API_KEY`` to be set.

2. **Keyword BM25-style (fallback)** — Pure-Python TF-IDF-inspired scoring
   using token overlap + term frequency. No API key or extra dependencies
   required; always available.

Both strategies return a ``RetrievedContext`` object containing the top-k
chunks formatted for injection into the Gemini prompt.
"""

from __future__ import annotations

import logging
import math
import re
from dataclasses import dataclass, field
from typing import Optional

from app.knowledge_base import CORPUS

logger = logging.getLogger("agrimind.rag")

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class RetrievedChunk:
    id: str
    category: str
    topic: str
    text: str
    score: float


@dataclass
class RetrievedContext:
    query: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    strategy_used: str = "keyword"

    def format_for_prompt(self) -> str:
        """Format retrieved chunks into a clean block for the Gemini prompt."""
        if not self.chunks:
            return "No specific agronomic records retrieved for this query."

        lines = [
            f"[Retrieval strategy: {self.strategy_used} | "
            f"Top {len(self.chunks)} verified records]\n"
        ]
        for i, chunk in enumerate(self.chunks, 1):
            lines.append(
                f"--- RECORD {i}: {chunk.topic} ({chunk.category}) "
                f"[relevance: {chunk.score:.2f}] ---\n{chunk.text}\n"
            )
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Keyword (BM25-style) retrieval — always available
# ---------------------------------------------------------------------------

def _tokenize(text: str) -> list[str]:
    """Lowercase, strip punctuation, split on whitespace."""
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    return [t for t in text.split() if len(t) > 2]


def _build_idf(corpus: list[dict]) -> dict[str, float]:
    """Compute IDF scores across the entire corpus."""
    N = len(corpus)
    df: dict[str, int] = {}
    for doc in corpus:
        tokens = set(_tokenize(doc["text"] + " " + doc["topic"] + " " + doc["category"]))
        for tok in tokens:
            df[tok] = df.get(tok, 0) + 1
    return {tok: math.log((N + 1) / (freq + 1)) + 1 for tok, freq in df.items()}


_IDF_CACHE: dict[str, float] | None = None


def _get_idf() -> dict[str, float]:
    global _IDF_CACHE
    if _IDF_CACHE is None:
        _IDF_CACHE = _build_idf(CORPUS)
    return _IDF_CACHE


def _keyword_score(query_tokens: list[str], doc: dict, idf: dict[str, float]) -> float:
    """TF-IDF-style relevance score for a single document."""
    doc_text = (doc["text"] + " " + doc["topic"] + " " + doc["category"]).lower()
    doc_tokens = _tokenize(doc_text)
    doc_len = max(len(doc_tokens), 1)

    # Build term frequency for doc
    tf: dict[str, int] = {}
    for tok in doc_tokens:
        tf[tok] = tf.get(tok, 0) + 1

    # BM25 parameters
    k1, b, avg_dl = 1.5, 0.75, 150.0

    score = 0.0
    for tok in set(query_tokens):
        if tok not in idf:
            continue
        f = tf.get(tok, 0)
        bm25_tf = (f * (k1 + 1)) / (f + k1 * (1 - b + b * doc_len / avg_dl))
        score += idf[tok] * bm25_tf

    # Boost: if category matches the query
    return score


def keyword_retrieve(
    query: str,
    category: str,
    top_k: int = 4,
) -> RetrievedContext:
    """BM25-style keyword retrieval — no API key required."""
    query_tokens = _tokenize(query + " " + category)
    idf = _get_idf()

    scored = []
    for doc in CORPUS:
        score = _keyword_score(query_tokens, doc, idf)
        # Category match bonus
        if category.lower() in doc["category"].lower():
            score *= 1.4
        scored.append((score, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    chunks = [
        RetrievedChunk(
            id=doc["id"],
            category=doc["category"],
            topic=doc["topic"],
            text=doc["text"],
            score=round(score, 3),
        )
        for score, doc in top
        if score > 0
    ]

    logger.info(
        "[RAG/keyword] Retrieved %d chunks for query='%s'", len(chunks), query[:60]
    )
    return RetrievedContext(query=query, chunks=chunks, strategy_used="keyword-BM25")


# ---------------------------------------------------------------------------
# Semantic (embedding-based) retrieval — requires google-genai + GEMINI_API_KEY
# ---------------------------------------------------------------------------

def _cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two embedding vectors."""
    try:
        import numpy as np  # type: ignore[import-untyped]
        va = np.array(a, dtype=float)
        vb = np.array(b, dtype=float)
        denom = np.linalg.norm(va) * np.linalg.norm(vb)
        if denom == 0:
            return 0.0
        return float(np.dot(va, vb) / denom)
    except ImportError:
        # Pure-python fallback (slower but correct)
        dot = sum(x * y for x, y in zip(a, b))
        mag_a = math.sqrt(sum(x * x for x in a))
        mag_b = math.sqrt(sum(x * x for x in b))
        if mag_a == 0 or mag_b == 0:
            return 0.0
        return dot / (mag_a * mag_b)


# In-memory cache for corpus embeddings (populated once per process)
_CORPUS_EMBEDDINGS: list[tuple[dict, list[float]]] | None = None


def _embed_texts(texts: list[str], api_key: str) -> list[list[float]]:
    """Embed a list of texts using Google text-embedding-004."""
    from google import genai  # type: ignore[import-untyped]
    from google.genai import types  # type: ignore[import-untyped]

    client = genai.Client(api_key=api_key)
    embeddings = []
    for text in texts:
        result = client.models.embed_content(
            model="text-embedding-004",
            contents=text,
        )
        embeddings.append(result.embeddings[0].values)
    return embeddings


def _build_corpus_embeddings(api_key: str) -> list[tuple[dict, list[float]]]:
    """Embed the full corpus and cache results in memory."""
    global _CORPUS_EMBEDDINGS
    if _CORPUS_EMBEDDINGS is not None:
        return _CORPUS_EMBEDDINGS

    logger.info("[RAG/semantic] Building corpus embeddings (%d docs)…", len(CORPUS))
    texts = [doc["topic"] + ". " + doc["text"][:300] for doc in CORPUS]
    try:
        vecs = _embed_texts(texts, api_key)
        _CORPUS_EMBEDDINGS = list(zip(CORPUS, vecs))
        logger.info("[RAG/semantic] Corpus embeddings ready.")
    except Exception as exc:
        logger.warning("[RAG/semantic] Embedding failed: %s — falling back to keyword.", exc)
        _CORPUS_EMBEDDINGS = []
    return _CORPUS_EMBEDDINGS


def semantic_retrieve(
    query: str,
    category: str,
    api_key: str,
    top_k: int = 4,
) -> RetrievedContext:
    """Cosine-similarity retrieval over Google text-embedding-004 vectors."""
    corpus_emb = _build_corpus_embeddings(api_key)
    if not corpus_emb:
        logger.warning("[RAG/semantic] No corpus embeddings; falling back to keyword.")
        return keyword_retrieve(query, category, top_k)

    query_text = f"{category} diagnosis: {query}"
    try:
        q_vec = _embed_texts([query_text], api_key)[0]
    except Exception as exc:
        logger.warning("[RAG/semantic] Query embedding failed: %s", exc)
        return keyword_retrieve(query, category, top_k)

    scored = []
    for doc, doc_vec in corpus_emb:
        sim = _cosine_similarity(q_vec, doc_vec)
        # Category match bonus
        if category.lower() in doc["category"].lower():
            sim = min(sim * 1.25, 1.0)
        scored.append((sim, doc))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:top_k]

    chunks = [
        RetrievedChunk(
            id=doc["id"],
            category=doc["category"],
            topic=doc["topic"],
            text=doc["text"],
            score=round(score, 4),
        )
        for score, doc in top
    ]

    logger.info(
        "[RAG/semantic] Retrieved %d chunks for query='%s'", len(chunks), query[:60]
    )
    return RetrievedContext(query=query, chunks=chunks, strategy_used="semantic-embedding")


# ---------------------------------------------------------------------------
# Public entry point — auto-selects strategy
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    category: str,
    api_key: Optional[str] = None,
    top_k: int = 4,
    prefer_semantic: bool = True,
) -> RetrievedContext:
    """
    Retrieve the most relevant agronomic knowledge chunks for the query.

    Parameters
    ----------
    query:
        Combined text of field observations and any relevant visual cues.
    category:
        ``"Crops"``, ``"Poultry"``, or ``"Livestock"``.
    api_key:
        Gemini API key. If provided and ``prefer_semantic`` is True, uses
        semantic embedding-based retrieval; otherwise uses keyword BM25.
    top_k:
        Number of chunks to return.
    prefer_semantic:
        If True and ``api_key`` is set, attempt semantic retrieval first.
    """
    if api_key and prefer_semantic:
        return semantic_retrieve(query, category, api_key, top_k)
    return keyword_retrieve(query, category, top_k)
