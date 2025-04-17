from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator
from typing import List
import logging
import os

app = FastAPI()

# Setup logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/backend.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("backend")

# In-memory database
movies_db = [
    {"id": 1, "title": "Inception", "price": 10.0},
    {"id": 2, "title": "Interstellar", "price": 12.0},
    {"id": 3, "title": "The Matrix", "price": 9.0},
    {"id": 4, "title": "The Dark Knight", "price": 11.0},
    {"id": 5, "title": "Fight Club", "price": 8.5},
    {"id": 6, "title": "Pulp Fiction", "price": 9.5},
    {"id": 7, "title": "The Godfather", "price": 10.0},
    {"id": 8, "title": "The Shawshank Redemption", "price": 9.0},
    {"id": 9, "title": "Forrest Gump", "price": 8.0},
    {"id": 10, "title": "The Lord of the Rings", "price": 11.5},
    {"id": 11, "title": "The Social Network", "price": 7.5},
    {"id": 12, "title": "Gladiator", "price": 10.0},
    {"id": 13, "title": "Titanic", "price": 8.0},
    {"id": 14, "title": "Avengers: Endgame", "price": 12.0},
    {"id": 15, "title": "Avatar", "price": 11.0},
    {"id": 16, "title": "Joker", "price": 9.0},
    {"id": 17, "title": "The Prestige", "price": 8.5},
    {"id": 18, "title": "Whiplash", "price": 7.0},
    {"id": 19, "title": "Mad Max: Fury Road", "price": 8.0},
    {"id": 20, "title": "Parasite", "price": 9.5}
]
purchases = []  # to store purchases

# Models
class Purchase(BaseModel):
    movie_id: int
    user_id: int

class Feedback(BaseModel):
    movie_id: int
    comment: str

class Movie(BaseModel):
    title: str
    price: float

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/movies")
def get_movies():
    logger.info("Fetching all movies")
    return movies_db

@app.get("/movies/{movie_id}")
def get_movie(movie_id: int):
    logger.info(f"Fetching movie ID: {movie_id}")
    movie = next((m for m in movies_db if m["id"] == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    return movie

@app.get("/movies/search/{keyword}")
def search_movies(keyword: str):
    logger.info(f"Searching movies with keyword: {keyword}")
    return [m for m in movies_db if keyword.lower() in m["title"].lower()]

@app.post("/movies")
def add_movie(movie: Movie):
    new_id = max([m["id"] for m in movies_db], default=0) + 1
    movie_entry = {"id": new_id, "title": movie.title, "price": movie.price}
    movies_db.append(movie_entry)
    logger.info(f"Movie added: {movie_entry}")
    return {"message": "Movie added", "movie": movie_entry}

@app.post("/purchase")
def purchase_movie(purchase: Purchase):
    logger.info(f"User {purchase.user_id} purchased movie {purchase.movie_id}")
    purchases.append({"user_id": purchase.user_id, "movie_id": purchase.movie_id})
    return {"message": "Purchase successful"}

@app.get("/purchases/{user_id}")
def get_user_purchases(user_id: int):
    user_purchases = [p for p in purchases if p["user_id"] == user_id]
    movie_titles = [
        next((m["title"] for m in movies_db if m["id"] == p["movie_id"]), "Unknown")
        for p in user_purchases
    ]
    logger.info(f"Returning purchases for user {user_id}")
    return {"purchases": movie_titles}

@app.post("/feedback")
def leave_feedback(feedback: Feedback):
    logger.info(f"Feedback for movie {feedback.movie_id}: {feedback.comment}")
    return {"message": "Feedback received"}

# Prometheus metrics
Instrumentator().instrument(app).expose(app)
