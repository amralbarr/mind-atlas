# RAG Hybrid Search — Runnable Example

A real [BM25](../../ai/retrieval/bm25.md) + vector + [Reciprocal Rank Fusion](../../ai/retrieval/reciprocal-rank-fusion.md) (RRF) merge, runnable with zero
network calls or API keys — companion to
[How would you choose an embedding model / handle hybrid search?](../../interview/interview-01/01-rag.md).

The embedding step is a dependency-free stand-in (character-trigram hashing,
see `fake_embed()` in `hybrid_search.py`) so this runs instantly offline; the
[BM25](../../ai/retrieval/bm25.md) index, cosine similarity, and RRF merge logic are the real thing — swap
`fake_embed()` for a real embedding model call and nothing else changes.

## Run it

```bash
cd code-samples
python3 -m venv .venv
.venv/bin/pip install -r rag-hybrid-search/requirements.txt
.venv/bin/python3 rag-hybrid-search/hybrid_search.py
.venv/bin/pytest rag-hybrid-search/tests/ -v
```

## Concepts this demonstrates

- [Hybrid Search](../../ai/retrieval/hybrid-search.md)
- [BM25](../../ai/retrieval/bm25.md)
- [Reciprocal Rank Fusion (RRF)](../../ai/retrieval/reciprocal-rank-fusion.md)
- [BM25 vs. Hybrid Search vs. RRF](../../../overviews/ai/bm25-vs-hybrid-search-vs-rrf.md)

## Related

- [RAG — Interview Q&A](../../interview/interview-01/01-rag.md)
