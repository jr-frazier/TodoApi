from database import Base
import enum
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum

class UserRoles(enum.Enum):
    ADMIN = "admin"
    USER = "user"

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRoles), default=UserRoles.USER)

class Todos(Base):
    # tells SQLAlchemy what table to use
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey('users.id'))
