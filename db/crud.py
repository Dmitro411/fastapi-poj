from fastapi import HTTPException
from sqlalchemy.orm import Session
from db import models, schemas
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_book(db: Session, book: schemas.BookCreate):
    author = db.query(models.Author).filter(models.Author.id == book.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Athor not found")
    
    new_book = models.Book(name=book.name, description=book.description, pages=book.pages, img=book.img, author_id=book.author_id)
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book

def get_books(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Book).offset(skip).limit(limit).all()

def create_author(db: Session,author: schemas.AuthorCreate):
    new_author = models.Author(**author.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

def get_authors(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Author).offset(skip).limit(limit).all()


def delete_book(db: Session, book_id: int):
    book = db.query(models. Book).filter(models. Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(book)
    db.commit()
    return book

def delete_author(db: Session, author_id: int):
    author = db.query(models. Author).filter(models. Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    db.delete(author)
    db.commit()
    return author

def get_books_author(db: Session, author_id: int, skip: int = 0, limit: int = 10):
    author = db.query(models. Author).filter(models. Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return db.query(models.Book).filter(models. Book. author_id == author_id).offset(skip).limit(limit).all()

def get_user(db:Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email, password=pwd_context.hash(user.password))
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_book(db: Session, book_id: int, book_data: schemas.BookUpdate):
    book = db.query(models.Book).filter(models.Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_data.dict().items():
        setattr(book, key, value)
    db.commit()
    db.refresh(book)
    return book


def update_author(db: Session, author_id: int, author_data: schemas.BookUpdate):
    author = db.query(models.Author).filter(models.Author.id == author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    for key, value in author_data.dict().items():
        setattr(author, key, value)
    db.commit()
    db.refresh(author)
    return author

def delete_user(db: Session, user_id: int):
    pass
