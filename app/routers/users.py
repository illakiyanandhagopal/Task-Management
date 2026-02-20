from fastapi import APIRouter, Depends
from app.deps import get_current_user
from app.models import User

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user.role, current_user.id
