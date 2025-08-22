from fastapi import APIRouter, Body, HTTPException
from typing import Annotated, Optional
from fastapi import  Depends
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Users, UserRoles
from database import  SessionLocal
from routers.auth import get_current_user, CreateUserRequest

router = APIRouter(
    prefix="/user",
    tags=["user"]
)

class UpdateUserRequest(BaseModel):
    username: Optional[str] = Field(min_length=3, max_length=50, default=None)
    email: Optional[str] = Field(min_length=3, max_length=50, default=None)
    first_name: Optional[str] = Field(min_length=3, max_length=50, default=None)
    last_name: Optional[str] = Field(min_length=3, max_length=50, default=None)
    role: Optional[UserRoles] = Field(default=None)
    phone_number: Optional[str] = Field(min_length=3, max_length=50, default=None)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserVerification(BaseModel):
    password: str
    new_password: str = Field(min_length=6)

@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    user_info = db.query(Users).filter(Users.id == user.get('id')).first()
    return user_info

@router.put("/", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, update_user_request: UpdateUserRequest):
    user_model = db.query(Users).filter(Users.id == user.get('id')).first()
    user_model.username = update_user_request.username or user_model.username
    user_model.email = update_user_request.email or user_model.email
    user_model.first_name = update_user_request.first_name or user_model.first_name
    user_model.last_name = update_user_request.last_name or user_model.last_name
    user_model.role = update_user_request.role or user_model.role
    user_model.phone_number = update_user_request.phone_number or user_model.phone_number
    db.add(user_model)
    db.commit()




@router.put("/update_password", status_code=status.HTTP_204_NO_CONTENT)
async def update_password(user: user_dependency, db: db_dependency, password_reset_request: UserVerification = Body(...) ):

    user_model = db.query(Users).filter(Users.id == user.get('id')).first()

    if not bcrypt_context.verify(password_reset_request.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Password")


    user_model.hashed_password = bcrypt_context.hash(password_reset_request.new_password)
    db.add(user_model)
    db.commit()


