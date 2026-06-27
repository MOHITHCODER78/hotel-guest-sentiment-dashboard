from fastapi import APIRouter, Depends

from app import models
from app.api.deps import get_current_user
from app.schemas import AnalysisResponse, APIResponse, ReviewRequest
from app.services.analysis import analyze_review_text

router = APIRouter(prefix="/analyze", tags=["Analysis"])


@router.post("", response_model=APIResponse[AnalysisResponse])
async def analyze_review(
    request: ReviewRequest,
    _: models.User = Depends(get_current_user),
):
    result = analyze_review_text(request.text)
    return APIResponse(data=result)
