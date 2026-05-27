import uuid
import re
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterSchema(BaseModel):
    username: str
    password: str
    name: str
    role: str
    phone: Optional[str] = None

    @field_validator("phone")
    def validate_phone_format(cls, value: Optional[str]) -> Optional[str]:
        if value is not None:
            cleaned_value = str(value).strip()
            phone_regex = r"^(?:\+?58|0)?(?:412|414|424|416|426)\d{7}$"
            if not re.match(phone_regex, cleaned_value):
                raise ValueError("El formato del numero de telefono no es valido")
            return cleaned_value
        return value


class LoginSchema(BaseModel):
    username: str
    password: str


def get_database_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/register")
@router.post("/register/")
def register_user(payload: RegisterSchema, db: Session = Depends(get_database_session)):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="Username already registered")

    new_user = User(
        id=str(uuid.uuid4()),
        username=payload.username,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        name=payload.name,
        phone=payload.phone,
        size_preference="medium",
        energy_preference="medium",
        stage_preference="adult",
        has_yard=False,
    )
    db.add(new_user)
    db.commit()

    token = create_access_token(data={"sub": new_user.id})
    return {
        "status": "success",
        "access_token": token,
        "username": new_user.username,
        "role": new_user.role,
    }


@router.post("/login")
@router.post("/login/")
def login_user(
    payload: LoginSchema,
    db: Session = Depends(get_database_session),
):
    user = db.query(User).filter(User.username == payload.username).first()
    if user is None or user.hashed_password is None:
        raise HTTPException(status_code=401, detail="Usuario o clave invalida")

    if not verify_password(payload.password, str(user.hashed_password)):
        raise HTTPException(status_code=401, detail="Usuario o clave invalida")

    token = create_access_token(data={"sub": user.id})
    return {"status": "success", "access_token": token, "role": user.role}


@router.post("/logout")
@router.post("/logout/")
def logout_user():
    return {"status": "success"}
