from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
import app.models
from app.api.routes import match, users, animals, rescues

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patitas Match API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(animals.router)
app.include_router(match.router)
app.include_router(rescues.router)


@app.get("/")
def check_health():
    return {"status": "ok", "service": "Patitas Match API is running"}
