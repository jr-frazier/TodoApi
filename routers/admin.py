from fastapi import  APIRouter
from typing import Annotated
from fastapi import  Depends, HTTPException, Path
from sqlalchemy.orm import Session
from fastapi import status
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

@router.delete("/user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency, db: db_dependency, user_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail="Unauthorized")
    user_model = db.query(Users).filter(Users.id == user_id).first()
    if user_model is None:
        raise HTTPException(status_code=404, detail="ID Not Found")
    if user_model.id == user.get('id'):
        raise HTTPException(status_code=400, detail="Cannot delete yourself")

    db.delete(user_model)
    db.commit()
