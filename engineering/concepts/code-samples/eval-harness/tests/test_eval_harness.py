"""Verifies the evaluate() function's metrics against hand-computed
expected values — see ../../../concepts/ai/evaluation/retrieval-metrics.md's
own worked example for the numbers these mirror.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from eval_harness import evaluate, make_fake_retriever  # noqa: E402


def test_recall_and_precision_on_partial_hit():
    eval_set = [{"query": "q1", "relevant": ["a", "b", "c"]}]
    hits = {"q1": [("a", 0.9), ("x", 0.8), ("b", 0.76)]}
    retriever = make_fake_retriever(hits)
    result = evaluate(retriever, eval_set, k=5, threshold=0.75)
    assert result["Recall@5"] == round(2 / 3, 2)
    assert result["Precision@5"] == round(2 / 3, 2)


def test_mrr_rewards_higher_rank():
    eval_set = [{"query": "q1", "relevant": ["a"]}]
    hits_rank1 = {"q1": [("a", 0.9)]}
    hits_rank2 = {"q1": [("x", 0.9), ("a", 0.8)]}

    result_rank1 = evaluate(make_fake_retriever(hits_rank1), eval_set, threshold=0.75)
    result_rank2 = evaluate(make_fake_retriever(hits_rank2), eval_set, threshold=0.75)

    assert result_rank1["MRR"] == 1.0
    assert result_rank2["MRR"] == 0.5


def test_abstention_accuracy_on_out_of_scope_query():
    eval_set = [{"query": "unanswerable", "relevant": []}]
    correctly_silent = {"unanswerable": [("x", 0.5)]}  # below threshold
    result = evaluate(make_fake_retriever(correctly_silent), eval_set, threshold=0.75)
    assert result["Abstention accuracy"] == 1.0

    incorrectly_answered = {"unanswerable": [("x", 0.9)]}  # above threshold, shouldn't be
    result = evaluate(make_fake_retriever(incorrectly_answered), eval_set, threshold=0.75)
    assert result["Abstention accuracy"] == 0.0
