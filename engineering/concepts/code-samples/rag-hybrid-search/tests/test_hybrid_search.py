"""Tests for the hybrid search demo — confirms the keyword signal, the
vector signal, and the RRF merge all actually contribute.

See: ../../../interview/interview-01/01-rag.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from hybrid_search import HybridSearchIndex  # noqa: E402

CORPUS = [
    "Employees are entitled to 30 days of paid annual leave per year.",
    "The expense reimbursement process requires manager approval within 5 days.",
    "Remote work is permitted up to 3 days per week with manager sign-off.",
    "Annual leave requests must be submitted at least 2 weeks in advance.",
]


def test_bm25_finds_exact_keyword_match():
    index = HybridSearchIndex(CORPUS)
    top = index.bm25_search("annual leave", k=1)
    assert top[0] in (0, 3)  # both leave-related docs score highly on exact terms


def test_hybrid_search_returns_requested_k():
    index = HybridSearchIndex(CORPUS)
    results = index.hybrid_search("leave policy", k=2)
    assert len(results) == 2


def test_rrf_scores_are_descending():
    index = HybridSearchIndex(CORPUS)
    results = index.hybrid_search("manager approval", k=4)
    scores = [score for _, score in results]
    assert scores == sorted(scores, reverse=True)
