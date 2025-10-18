from fastapi import APIRouter, HTTPException, status
from ..services.tips_service import get_random_tip


router = APIRouter(prefix="/tips", tags=["Tips"])


@router.get("/today")
async def get_today_tip():
    try:
        tip = get_random_tip()
        return tip
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


