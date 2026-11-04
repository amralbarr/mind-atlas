"""The /ask endpoint: thin by design, formatting only. All real logic
lives in pipeline.py and the services/ layers so it can be tested without
the HTTP layer at all.
"""
from fastapi import APIRouter, Depends, Request

from auth import User, get_current_user
from pipeline import AssistantPipeline
from schemas import AnswerStatus, AskRequest, AskResponse

router = APIRouter()


def get_pipeline(request: Request) -> AssistantPipeline:
    return request.app.state.pipeline


@router.post("/ask", response_model=AskResponse)
async def ask(
    body: AskRequest,
    user: User = Depends(get_current_user),
    pipeline: AssistantPipeline = Depends(get_pipeline),
) -> AskResponse:
    try:
        return await pipeline.ask(body.question, user)
    except TimeoutError:
        return AskResponse(
            request_id=user.request_id,
            status=AnswerStatus.ERROR,
            reason="model_timeout",
        )
