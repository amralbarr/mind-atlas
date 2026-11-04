"""A real, runnable hybrid search implementation: BM25 keyword scoring +
cosine-similarity vector scoring, merged via Reciprocal Rank Fusion (RRF).

Companion to:
- ../../interview/interview-01/01-rag.md
- ../../concepts/ai/retrieval/hybrid-search.md
- ../../concepts/ai/retrieval/bm25.md
- ../../concepts/ai/retrieval/reciprocal-rank-fusion.md
- ../../overviews/ai/bm25-vs-hybrid-search-vs-rrf.md

Uses a tiny hand-rolled "embedding" (character-bigram hashing into a fixed
vector) instead of a real embedding model, so this runs with zero network
calls and no API key — the RRF merge logic itself is identical to a real
deployment; only the embedding step is a stand-in.
"""
import math
from collections import Counter

from rank_bm25 import BM25Okapi


def fake_embed(text: str, dim: int = 64) -> list[float]:
    """A deterministic, dependency-free stand-in for a real embedding
    model (e.g. BGE-M3) — hashes character trigrams into a fixed-size
    vector. Real deployments replace this with an actual embedding call;
    everything downstream (cosine similarity, RRF) works identically."""
    vec = [0.0] * dim
    text = text.lower()
    for i in range(len(text) - 2):
        trigram = text[i : i + 3]
        vec[hash(trigram) % dim] += 1.0
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b))


class HybridSearchIndex:
    """Builds both a BM25 keyword index and a vector index over the same
    corpus, and merges their rankings via RRF — see
    ../../concepts/ai/retrieval/reciprocal-rank-fusion.md for why RRF
    sidesteps the scale mismatch between BM25 scores and cosine similarity.
    """

    def __init__(self, documents: list[str]):
        self.documents = documents
        tokenized = [doc.lower().split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)
        self.embeddings = [fake_embed(doc) for doc in documents]

    def bm25_search(self, query: str, k: int) -> list[int]:
        scores = self.bm25.get_scores(query.lower().split())
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return ranked[:k]

    def vector_search(self, query: str, k: int) -> list[int]:
        q_vec = fake_embed(query)
        scores = [cosine_similarity(q_vec, doc_vec) for doc_vec in self.embeddings]
        ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        return ranked[:k]

    def hybrid_search(self, query: str, k: int = 5, rrf_k: int = 60) -> list[tuple[int, float]]:
        """Reciprocal Rank Fusion: each result's RRF score is the sum of
        1/(rrf_k + rank) across every ranked list it appears in — a result
        ranked highly by EITHER signal scores well, without needing the
        two signals' raw scores to be on the same scale."""
        bm25_ranked = self.bm25_search(query, k=20)
        vector_ranked = self.vector_search(query, k=20)

        rrf_scores: Counter = Counter()
        for rank, doc_id in enumerate(bm25_ranked):
            rrf_scores[doc_id] += 1.0 / (rrf_k + rank + 1)
        for rank, doc_id in enumerate(vector_ranked):
            rrf_scores[doc_id] += 1.0 / (rrf_k + rank + 1)

        merged = sorted(rrf_scores.items(), key=lambda item: item[1], reverse=True)
        return merged[:k]


if __name__ == "__main__":
    corpus = [
        "Employees are entitled to 30 days of paid annual leave per year.",
        "The expense reimbursement process requires manager approval within 5 days.",
        "Remote work is permitted up to 3 days per week with manager sign-off.",
        "Annual leave requests must be submitted at least 2 weeks in advance.",
        "The company provides health insurance covering employee and dependents.",
    ]
    index = HybridSearchIndex(corpus)

    query = "how many vacation days do I get"
    results = index.hybrid_search(query, k=3)

    print(f"Query: {query!r}\n")
    for doc_id, score in results:
        print(f"  RRF score {score:.4f}  —  {corpus[doc_id]}")
