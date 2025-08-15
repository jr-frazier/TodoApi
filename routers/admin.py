from fastapi import  APIRouter
from typing import Annotated
from fastapi import  Depends, HTTPException, Path
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from starlette import status
from models import Todos, Users
from database import  SessionLocal
from routers.auth import get_current_user

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.get("/todo", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(Todos).all()

@router.get("/users", status_code=status.HTTP_200_OK)
async def get_all_users(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorized")

    return db.query(Users).all()
