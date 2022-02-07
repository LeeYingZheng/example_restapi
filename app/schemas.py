from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional
import time

class Post(BaseModel):
    title: str
    content: str
    category: str
    location: Optional[str] = None
    rating: Optional[int] = Field(0, ge = 0, le = 5) 
    published: Optional[bool] = True

class UpdatePost(BaseModel):
    title: Optional[str]
    content: Optional[str]
    category: Optional[str]
    location: Optional[str] = None
    rating: Optional[int] = Field(0, ge = 0, le = 5) 
    published: Optional[bool] = True

class BaseUserResponse(BaseModel):
    id: int
    email: EmailStr
    username: str

    class Config:
        orm_mode = True

class BasePostResponse(Post):
    id: int
    date: datetime
    owner: BaseUserResponse

    class Config:
        orm_mode = True

class PostResponse(BaseModel):
    Post: BasePostResponse
    votes: int

    class Config:
        orm_mode = True

class User(BaseModel):
    email: EmailStr
    username: str
    password: str

class UpdateUser(BaseModel):
    email: Optional[EmailStr]
    username: Optional[str]

class UpdateUserPassword(BaseModel):
    password: str

class UserResponse(BaseUserResponse):
    date_created: datetime

    class Config:
        orm_mode = True

class UpdateUserResponse(BaseUserResponse):
    date_updated: Optional[str] = time.strftime("%d %B %Y %H:%M:%S", time.localtime())

    class Config:
        orm_mode = True

class UserLogin(BaseModel):
    username: str
    password: str

class EmailLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[str] = None

class Vote(BaseModel):
	post_id: int
	dir: bool