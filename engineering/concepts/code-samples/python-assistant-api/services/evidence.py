"""Evidence validation: makes sure the model never cites a source that was
never actually retrieved.

See: ../../../concepts/ai/evaluation/retrieval-metrics.md
"""
from schemas import AnswerStatus, AskResponse, Evidence


def validate_evidence(result: dict, chunks: list[dict], request_id: str) -> AskResponse:
    retrieved_ids = {c["id"] for c in chunks}
    cited_ids = set(result.get("cited_ids", []))

    if not cited_ids:
        return AskResponse(
            request_id=request_id,
            status=AnswerStatus.ABSTAINED,
            reason="answer_without_citations",
        )

    if not cited_ids <= retrieved_ids:  # the model cited a source that was never retrieved!
        return AskResponse(
            request_id=request_id,
            status=AnswerStatus.ERROR,
            reason="invalid_citation",
        )

    evidence = [
        Evidence(chunk_id=c["id"], source=c["source"], page=c.get("page"))
        for c in chunks
        if c["id"] in cited_ids
    ]
    return AskResponse(
        request_id=request_id,
        status=AnswerStatus.ANSWERED,
        answer=result["answer"],
        evidence=evidence,
    )
