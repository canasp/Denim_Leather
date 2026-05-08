from fastapi import Depends, FastAPI, HTTPException, Query, Form, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from pydantic import BaseModel
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

import jwt


#DATABASE

class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str = Field(default=None, index=True)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


#OAUTH2

SECRET_KEY = "5c17b574606c6e775cb0329fb8d27c8ff816a4eee39f0568c6c2afe5ebe893ea"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

password_hash = PasswordHash.recommended()

DUMMY_HASH = password_hash.hash("dummypassword")

#FUNCTIONS VERIFY HASH PASSWORD

def verify_password(plain_password, hashed_password):
    return  password_hash.verify(plain_password, hashed_password)

def get_password_hash(password):
    return password_hash.hash(password)


app = FastAPI()

#ENDPOINTS

@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post("/users/")
def create_user(user: User, session: SessionDep) -> User:
   #hash password    
    user.password = get_password_hash(user.password)

    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@app.get("/users/")
def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 100,
) -> list[User]:
    users = session.exec(select(User).offset(offset).limit(limit)).all()
    return users

@app.get("/users/{user_id}")
def read_user(user_id: int, session: SessionDep) -> User:
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/users/{user_id}")
def delete_user(user_id: int, session: SessionDep):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"ok": True}

class FormData(BaseModel):
    username: str
    password: str


# LOGIN JSON BODY
""" @app.post("/login/") 
def login(username: str , password: str, session: SessionDep) -> User:
    user = session.query(User).filter(User.username == username)
 
    if not user:
        verify_password(user.password, DUMMY_HASH)
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(user.password, password):
        return {"ok": True} """


# LOGIN FORM
@app.post("/login/") 
def login(data: Annotated[FormData, Form()], session: SessionDep) -> User:
    user = session.query(User).filter(User.username == data.username)
    print("User",User)
    print("data",data)
    print("user",user)
    if not user:
        verify_password(data.password, DUMMY_HASH)
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(data.password, user.user_password):
        return {"ok": True}
