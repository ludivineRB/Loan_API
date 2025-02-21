from fastapi import Depends, HTTPException
from jose import jwt, JWTError
import os
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from app.models import User
from app.schemas import UserCreate
from app.database import get_session
from sqlmodel import Session, select

SECRET_KEY = os.getenv("SECRET_KEY")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return {"id": user.id, "email": user.email, "role": "admin" if user.is_admin else "user"}

def get_admin_user(current_user: dict = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == current_user["sub"])).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return user

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie si le mot de passe en clair correspond au hash stocké."""
    return pwd_context.verify(plain_password, hashed_password)