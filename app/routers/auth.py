from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Response

from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)

router=APIRouter(prefix="/auth",tags=["Auth"])

@router.post("/register")
async def register(user:UserCreate,db: AsyncSession=Depends(get_db)):

    result=await db.execute(select(User).where(User.email==user.email))
    existing=result.scalar_one_or_none()

    if existing:
        raise HTTPException(status_code=400,detail="Email already registered")

    new_user=User(email=user.email, hashed_password=get_password_hash(user.password))
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return {"Message : ":"New User Successfully Registered"}


@router.post("/login", response_model=Token)
async def login(
    response: Response,form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(User).where(User.email == form_data.username))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        data={"sub": str(db_user.id)},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # True in production (HTTPS)
        samesite="lax"
    )
    return {"access_token": access_token, "token_type": "bearer"}
