"""Wires the retrieval and generation layers together behind interfaces,
so the pipeline itself never knows or cares which concrete Retriever/LLM
implementation it's running against.

See: ../../interview/interview-01/20-python-assistant-api-deep-dive.md
"""
from schemas import AnswerStatus, AskResponse
from services.evidence import validate_evidence
from services.interfaces import LLMClient, Retriever


class AssistantPipeline:
    def __init__(self, retriever: Retriever, llm: LLMClient, min_score: float = 0.75):
        self.retriever = retriever
        self.llm = llm
        self.min_score = min_score

    async def ask(self, question: str, user) -> AskResponse:
        chunks = await self.retriever.search(question, user.groups, k=20)
        chunks = [c for c in chunks if c["score"] >= self.min_score]

        if not chunks:
            return AskResponse(
                request_id=user.request_id,
                status=AnswerStatus.ABSTAINED,
                reason="no_relevant_documents",
            )

        result = await self.llm.generate(question, chunks[:5])
        return validate_evidence(result, chunks[:5], user.request_id)
