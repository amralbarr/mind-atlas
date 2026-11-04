"""Request/response models for the assistant API.

See docs:
- ../../interview/interview-01/20-python-assistant-api-deep-dive.md
- ../../concepts/programming/python/pydantic.md
"""
from enum import Enum

from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=2000)
    conversation_id: str | None = None


class AnswerStatus(str, Enum):
    ANSWERED = "answered"      # answered with evidence
    ABSTAINED = "abstained"    # abstained: insufficient evidence
    ERROR = "error"            # a technical failure


class Evidence(BaseModel):
    chunk_id: str
    source: str
    page: int | None = None


class AskResponse(BaseModel):
    request_id: str
    status: AnswerStatus
    answer: str | None = None
    evidence: list[Evidence] = []
    reason: str | None = None  # why it abstained or failed
