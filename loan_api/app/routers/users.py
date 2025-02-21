from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.models import User
from app.auth import hash_password, verify_password, create_access_token
from app.database import get_session
from app.schemas import UserCreate, UserLogin, TokenResponse, UserActivation
from app.database import get_session
from app.dependencies import get_admin_user, get_current_user
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/auth", tags=["Auth"])

# @router.post("/login", response_model=TokenResponse)
# def login(user_data: UserLogin, session: Session = Depends(get_session)):
#     user = session.exec(select(User).where(User.email == user_data.email)).first()
#     if not user or not verify_password(user_data.password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")
#     print(f"DEBUG: User found: {user}")
#     print(f"DEBUG: Hashed password in DB: {user.hashed_password}")
#     return TokenResponse(access_token=create_access_token({"sub": user.email}), token_type="bearer")

# @router.post("/login", response_model=TokenResponse)
# def login(user_data: UserLogin, session: Session = Depends(get_session)):
#     user = session.exec(select(User).where(User.email == user_data.email)).first()

#     if not user or not verify_password(user_data.password, user.hashed_password):
#         raise HTTPException(status_code=400, detail="Invalid credentials")

#     if not user.is_active:
#         raise HTTPException(
#             status_code=403,
#             detail="Your account is not activated. Please reset your password to activate it."
#         )

#     print(f"DEBUG: User found: {user}")
#     print(f"DEBUG: Hashed password in DB: {user.hashed_password}")

#     return TokenResponse(access_token=create_access_token({"sub": user.email}), token_type="bearer")
@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_active:
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Your account is not activated. Please reset your password to activate it.",
                "redirect": "/auth/activation"
            }
        )

    print(f"DEBUG: User found: {user}")
    print(f"DEBUG: Hashed password in DB: {user.hashed_password}")

    return TokenResponse(access_token=create_access_token({"sub": user.email}), token_type="bearer")


@router.post("/activation")
def activate_account(user_data: UserActivation, session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.email == user_data.email)).first()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_password = hash_password(user_data.new_password)
    user.is_active = True
    session.add(user)
    session.commit()
    return {"message": "Account activated"}

@router.post("/admin/users", status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_session), admin: User = Depends(get_admin_user)):
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = User(
        email=user.email,
        hashed_password=hash_password(user.password),
        is_admin=user.is_admin
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "Utilisateur créé avec succès"}

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"email": current_user["sub"], "role": current_user.get("role")}