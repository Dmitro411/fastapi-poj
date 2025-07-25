from pydantic import BaseModel
from typing import List, Optional


class BookBase(BaseModel):
    name: str
    description: str
    pages: int
    img: Optional[str] = None
    author_id: int

class AuthorBase(BaseModel):
    first_name: str
    last_name: str
    bio: Optional[str] = None

class Book(BookBase):
    id: int
    author: AuthorBase

    class Config: 
        otm_mode = True

class Author(AuthorBase):
    id: int

    class Config: 
        otm_mode = True

class BookCreate(BookBase):
    pass

class AuthorCreate(AuthorBase):
    pass

class BookUpdate(BookBase):
    name: str
    description: str
    pages: int
    img: Optional[str] = None

class AuthorUpdate(AuthorBase):
    pass

class UserBase(BaseModel):
    username: str
    email: Optional[str] = None
    password: str

class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config: 
        from_attributes = True