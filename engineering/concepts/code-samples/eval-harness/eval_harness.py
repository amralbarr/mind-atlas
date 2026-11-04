"""A real retrieval evaluation harness: runs a fixed test set through a
retriever function and computes Recall@k, Precision@k, MRR, and
abstention accuracy — the regression-test pattern you build BEFORE tuning
chunking, embeddings, or re-ranking, so you can tell whether a change
actually helped.

Companion to:
- ../../interview/interview-01/02-eval.md
- ../../interview/interview-01/15-evaluation-metrics-workshop.md
- ../../concepts/ai/evaluation/retrieval-metrics.md
- ../../concepts/ai/evaluation/fixed-evaluation-dataset.md
"""


def evaluate(retrieve_fn, eval_set, k=5, threshold=0.75):
    """retrieve_fn(query, k) -> list[(chunk_id, score)], already ranked.

    An eval_set item with an empty "relevant" list is an intentionally
    out-of-scope query — the expected behavior is abstention (returning
    nothing above threshold), scored separately as abstention accuracy.
    """
    recalls, precisions, rrs, abstain_correct = [], [], [], []

    for item in eval_set:
        hits = retrieve_fn(item["query"], k)
        kept = [chunk_id for chunk_id, score in hits if score >= threshold]
        relevant = set(item["relevant"])

        if not relevant:  # out-of-scope query
            abstain_correct.append(len(kept) == 0)
            continue

        found = [c for c in kept if c in relevant]
        recalls.append(len(found) / len(relevant))
        precisions.append(len(found) / len(kept) if kept else 0.0)
        rank = next((i + 1 for i, c in enumerate(kept) if c in relevant), None)
        rrs.append(1 / rank if rank else 0.0)

    avg = lambda xs: round(sum(xs) / len(xs), 2) if xs else None
    return {
        f"Recall@{k}": avg(recalls),
        f"Precision@{k}": avg(precisions),
        "MRR": avg(rrs),
        "Abstention accuracy": avg(abstain_correct),
    }


# --- A fixed evaluation set — see fixed-evaluation-dataset.md for why this
# must stay stable across runs, not be regenerated per evaluation. ---
EVAL_SET = [
    {"query": "What is the leave policy?",
     "relevant": ["doc_42_chunk_3", "doc_42_chunk_4", "doc_15_chunk_1"]},
    {"query": "How do I submit an expense report?",
     "relevant": ["doc_7_chunk_2"]},
    {"query": "What is the CEO's salary?",
     "relevant": []},  # intentionally out-of-scope
]


def make_fake_retriever(hit_table):
    """Builds a retrieve_fn backed by a fixed lookup table instead of a
    real vector store — swap this for a real retriever call and the
    evaluate() logic above needs no changes at all."""

    def retrieve_fn(query, k):
        return hit_table.get(query, [])[:k]

    return retrieve_fn


if __name__ == "__main__":
    # A deliberately imperfect retriever: finds 2 of 3 for query 1, finds
    # the single relevant chunk for query 2 but ranked 2nd, and correctly
    # returns nothing for the out-of-scope query.
    fake_hits = {
        "What is the leave policy?": [
            ("doc_42_chunk_3", 0.89), ("doc_8_chunk_2", 0.81),
            ("doc_42_chunk_4", 0.79), ("doc_30_chunk_1", 0.71), ("doc_12_chunk_6", 0.68),
        ],
        "How do I submit an expense report?": [
            ("doc_3_chunk_1", 0.80), ("doc_7_chunk_2", 0.76),
        ],
        "What is the CEO's salary?": [
            ("doc_1_chunk_1", 0.52),
        ],
    }
    retriever = make_fake_retriever(fake_hits)
    results = evaluate(retriever, EVAL_SET, k=5, threshold=0.75)

    print("Evaluation results:")
    for metric, value in results.items():
        print(f"  {metric}: {value}")
