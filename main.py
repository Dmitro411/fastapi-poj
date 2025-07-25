from datetime import datetime, timedelta
from typing import Annotated
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from db import schemas, crud, models
from db.engine import session_local, create_db
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt

app = FastAPI(title="Books Library API", version="1.0.0")

# Шаблони та статика (за потреби)
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ініціалізація бази даних
create_db()

# Налаштування безпеки
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Хешування паролів
pwd_context = CryptContext(schemes=["sha256_crypt", "bcrypt"], deprecated="auto")

# Схема для OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Підключення до БД
def get_db():
    db = session_local()
    try:
        yield db
    finally:
        db.close()

# Створення JWT токена
def create_token(data: dict):
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + expires_delta
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Перевірка JWT токена
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Could not validate credentials")
        return payload
    except jwt.JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

# Отримання поточного користувача
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    username = payload.get("sub")
    user = crud.get_user(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# --- Роутери ---

@app.get("/")
async def homepage(request: Request):
    return templates.TemplateResponse("base.html", {"request": request})

#@app.get("/books/html")
#def all_books_html(request: Request, db: Session = Depends(get_db)):
    #books = crud.get_books(db)
    #return templates.TemplateResponse("all_books.html", {"request": request, "books": books})



@app.post("/users")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    '''Створення нового користувача'''
    return crud.create_user(db, user)

@app.post("/token")
async def get_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: Session = Depends(get_db)):
    '''Отримання токену'''
    user_data = crud.get_user(db, form_data.username)
    if not user_data or not pwd_context.verify(form_data.password, user_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    access_token = create_token({"sub": user_data.username})
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/books")
def all_books(db: Session = Depends(get_db)):
    '''Отримання всіх книг'''
    return crud.get_books(db)

@app.post("/books/create")
def create_book(book: schemas.BookCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Створення книги'''
    return crud.create_book(db, book)

@app.delete("/books/delete/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Видалення книги'''
    crud.delete_book(db, book_id)
    return JSONResponse(content={"message": f"Book with ID {book_id} deleted"})

@app.get("/authors")
def all_authors(db: Session = Depends(get_db)):
    '''Отримання всіх авторів'''
    return crud.get_authors(db)

@app.post("/authors/create")
def create_author(author: schemas.AuthorCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    '''Створення автора'''
    return crud.create_author(db, author)

@app.delete("/authors/delete/{author_id}")
def delete_author(author_id:int, db: Session = Depends (get_db), current_user: models.User = Depends(get_current_user)):
    return crud.delete_author(db, author_id)

@app.get("/authors/books/{author_id}")
def all_books_author(author_id:int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    author_books = crud.get_books_author(db, author_id)
    return author_books

@app.put("/books/update/{book_id}")
def update_book(book_id: int, book: schemas.BookUpdate, db: Session = Depends(get_db)):
    '''Оновлення книги'''
    return crud.update_book(db, book_id, book)

@app.put("/author/update/{author_id}")
def update_author(author_id: int, author: schemas.AuthorUpdate, db: Session = Depends(get_db)):
    '''Оновлення автора'''
    return crud.update_author(db, author_id, author)

# @app.get("/books/{author}")
# def author_books(author: str):
#     books_author = dict()
#     for book in books:
#         if books[book].author == author:
#             books_author.update({book: books[book]})
#     if books_author:
#         return  {"author_books": books_author}
#     raise HTTPException(status_code=400, detail="Книг такого автора не знайдено :(")

# @app.put("/books/update/{book_name}")
# def update_book(book_name: str, book: Book):
#     if book_name in books:
#         books [book_name] = book
#         return {book_name: book}
#     raise HTTPException(status_code=400, detail="Такої книги не знайдено :(")

# @app.delete("/books/delete/{book_name}")
# def delete_book(book_name: str):
#     if book_name in books:
#         del books[book_name]
#         return {'detail': "Книгу успішно видалено!"}
#     raise HTTPException(status_code=400, detail="Такої книги не знайдено :(")
