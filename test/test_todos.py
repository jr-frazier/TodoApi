from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from fastapi import status
from database import Base
from main import app
from routers.todos import get_db, get_current_user
from fastapi.testclient import TestClient
import pytest
from models import Todos

SQLITE_DATABASE_URL = 'sqlite:///./testdb.db'

engine = create_engine(
    SQLITE_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass = StaticPool
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

def override_get_current_user():
    return {"username": "testuser", "id": 1, "role": "admin"}


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

client = TestClient(app)

@pytest.fixture
def test_todo():
    todo = Todos(
        title="test todo 1",
        description="test todo description 1",
        priority=3,
        complete=False,
        owner_id=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as connection:
        connection.execute(text("DELETE FROM todos;"))
        connection.commit()

def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
             'complete': False,
             'description': 'test todo description 1',
             'id': 1,
             'owner_id': 1,
             'priority': 3,
             'title': 'test todo 1',
            }

def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/99')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "ID Not Found"}

def test_create_todo(test_todo):
    request_data= {
             'complete': False,
             'description': 'test todo description 2',
             'priority': 3,
             'title': 'test todo 2',
            }
    response = client.post('/todo/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED

    # Check to see if data was added to database
    db = TestingSessionLocal()
    todo_model = db.query(Todos).filter(Todos.id == 2).first()
    assert todo_model.title == request_data['title']
    assert todo_model.description == request_data['description']
    assert todo_model.priority == request_data['priority']
    assert todo_model.complete == request_data['complete']
    assert todo_model.owner_id == 1

def test_update_todo(test_todo):
    request_data={
        'title': 'new title',
        'description': 'new description',
        'priority': 2,
        'complete': True,
    }

    response = client.put('/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    todo_model = db.query(Todos).filter(Todos.id == 1).first()
    assert todo_model.title == request_data['title']
    assert todo_model.description == request_data['description']
    assert todo_model.priority == request_data['priority']
    assert todo_model.complete == request_data['complete']

def test_todo_not_found(test_todo):
    request_data = {
        'title': 'new title',
        'description': 'new description',
        'priority': 2,
        'complete': True,
    }

    response = client.put('/todo/99', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "ID Not Found"}

def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    todo_model = db.query(Todos).filter(Todos.id == 1).first()
    assert todo_model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/99')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    db = TestingSessionLocal()
    assert response.json() == {"detail": "ID Not Found"}