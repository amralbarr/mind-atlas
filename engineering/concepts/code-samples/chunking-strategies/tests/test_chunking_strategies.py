"""Verifies the core claim the handbook makes about these three
strategies: fixed-size chunking can bleed across a section boundary,
structure-aware chunking never does.

See: ../../../overviews/ai/chunking-strategies.md
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from chunking_strategies import (  # noqa: E402
    SAMPLE_DOCUMENT,
    fixed_size_chunks,
    structure_aware_chunks,
)


def test_fixed_size_can_cross_a_section_boundary():
    chunks = fixed_size_chunks(SAMPLE_DOCUMENT, size=200, overlap=40)
    # At least one chunk contains text from two different headings —
    # the exact failure mode structure-aware chunking is designed to avoid.
    crosses_boundary = any(
        "Leave Policy" in c and "Expense Reimbursement" in c for c in chunks
    )
    assert crosses_boundary


def test_structure_aware_never_crosses_a_heading():
    chunks = structure_aware_chunks(SAMPLE_DOCUMENT, max_size=300)
    headings_seen_per_chunk = [
        sum(1 for h in ("Leave Policy", "Expense Reimbursement", "Remote Work Policy") if h in c)
        for c in chunks
    ]
    assert all(count <= 1 for count in headings_seen_per_chunk)


def test_structure_aware_produces_one_chunk_per_section_here():
    chunks = structure_aware_chunks(SAMPLE_DOCUMENT, max_size=300)
    assert len(chunks) == 3
