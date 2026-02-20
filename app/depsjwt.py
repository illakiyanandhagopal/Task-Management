from fastapi import Request, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from jose import JWTError, jwt
from sqlalchemy import select

from app.database import AsyncSessionLocal, get_db
from app.core.security import SECRET_KEY, ALGORITHM
from app.models import User

async def get_current_user_from_cookies(
        request: Request, db: AsyncSession = Depends(get_db)
):
    token=request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    result = await db.execute(select(User).where(User.id == int(user_id)))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user