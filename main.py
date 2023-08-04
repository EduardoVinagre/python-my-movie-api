from fastapi import FastAPI, Body, Path, Query, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security.http import HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Any, Coroutine, Optional, List

from starlette.requests import Request
from jwt_manager import create_token, validate_token
from fastapi.security import HTTPBearer

movies = [
    {
        "id": 1,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": "2009",
        "rating": 7.8,
        "category": "Acción"
    },
    {
        "id": 2,
        "title": "Avatar",
        "overview": "En un exuberante planeta llamado Pandora viven los Na'vi, seres que ...",
        "year": "2009",
        "rating": 7.8,
        "category": "Acción"
    }
]

app = FastAPI()
app.title = "Mi aplicación con FastAPI"
app.version = "0.0.1"

class JWTBearer(HTTPBearer):
    async def __call__(self, request: Request):
        print('Hola1')
        auth = await super().__call__(request)
        print('Hola2')
        data = validate_token(auth.credentials)
        print('Hola3')
        if data['email'] != "admin@gmail.com":
            raise HTTPException(status_code=403, detail="Invalid credentials")

class User(BaseModel):
    email: str
    password: str

class Movie(BaseModel):
    id: Optional[int] = None
    title: str = Field(min_length=5, max_length=15)
    overview: str = Field(min_length=15, max_length=50)
    year: int = Field(le=2022)
    rating: float
    category: str

    class Config:
        json_schema_extra = {
            "examples": [{
                "id": 1,
                "title": "Mi pelicula",
                "overview": "Descripción de la pelicula",
                "year": 2022,
                "rating": 9.8,
                "category": "Acción"
            }]
        }

@app.get('/', tags=['home'])
def message():
   # return "Hello world!"
   # ---------------------
   # return {
   #     "Hello": "world"
   # }
   # ---------------------
    return HTMLResponse('<h1>Hello world</h1>')


@app.post('/login', tags=['auth'])
def login(user: User):
    if user.email == "admin@gmail.com" and user.password == "admin":
        token = create_token(user.dict())    
        return JSONResponse(status_code=200, content=token)
    return JSONResponse(status_code=402, content={})

@app.get('/movies', tags=['movies'], response_model=List[Movie], status_code=200, dependencies=[Depends(JWTBearer())])
def get_movies() -> List[Movie]:
    return JSONResponse(status_code=200, content=movies)


@app.get('/movies/{id}', tags=['movies'], response_model=Movie, status_code=200)
def get_movie(id: int = Path(ge=1, le=2000)) -> Movie:
    for item in movies:
        if item['id'] == id:
            return JSONResponse(status_code=200, content=item)
    return JSONResponse(status_code=404, content=[])


@app.get('/movies/', tags=['movies'], response_model=dict)
def get_movies_by_category(category: str = Query(min_length=5, max_length=50)):
    return list(filter(lambda movie: movie['category'] == category, movies))


# @app.post('/movies', tags=['movies'])
# def create_movie(id: int = Body(), tittle: str = Body(), overview: str = Body(), year: int = Body(), rating: float = Body(), category: str = Body()):
#     movies.append({
#         "id": id,
#         "title": tittle,
#         "overview": overview,
#         "year": year,
#         "rating": rating,
#         "category": category
#     })
#     return movies

@app.post('/movies', tags=['movies'], response_model=dict, status_code=201)
def create_movie(movie: Movie):
    movies.append(movie)
    return JSONResponse(status_code=201, content= {"message":"Se ha registrado la pelicula"})


# @app.put('/movies/{id}', tags=["movies"])
# def update_movie(id: int, tittle: str = Body(), overview: str = Body(), year: int = Body(), rating: float = Body(), category: str = Body()):
#     for item in movies:
#         if item['id'] == id:
#             item['title'] = tittle
#             item['overview'] = overview
#             item['year'] = year
#             item['rating'] = rating
#             item['category'] = category
#     return movies

@app.put('/movies/{id}', tags=["movies"], response_model=dict, status_code=200)
def update_movie(id: int, movie: Movie):
    for item in movies:
        if item['id'] == id:
            item['title'] = movie.tittle
            item['overview'] = movie.overview
            item['year'] = movie.year
            item['rating'] = movie.rating
            item['category'] = movie.category
    return JSONResponse(status_code=200, content={"message":"Se ha modificado la pelicula"})


@app.delete('/movies/{id}', tags=['movies'], status_code=200)
def delete_movie(id: int):
    for item in movies:
        if item['id'] == id:
            movies.remove(item)
            return JSONResponse(status_code=200, content={"message": "Se ha eliminado la pelicula"})
