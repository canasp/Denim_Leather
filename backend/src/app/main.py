from fastapi import Depends, FastAPI, HTTPException, Query, Form
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Annotated
from pydantic import BaseModel

app = FastAPI()

@app.get("/ping")
def pong():
    return {"ping": "pong!"}

@app.post("/pim")
def pim():
    return {"pim": "pam!"}

class FormData(BaseModel):
    username: str
    password: str

@app.post("/login/")
async def login(data: Annotated[FormData, Form()]):
    return data
