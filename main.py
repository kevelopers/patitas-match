import os
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def verify_environment_bootstrap() -> None:
    api_key = os.getenv("GEMINI_API_KEY", "empty_api_key")
    if api_key == "empty_api_key":
        logger.error("====================================================")
        logger.error("APPLICATION BOOTSTRAP WARNING: GEMINI_API_KEY IS EMPTY")
        logger.error("Please verify your local .env configuration file.")
        logger.error("====================================================")
    else:
        logger.info("Application environment verified successfully.")


verify_environment_bootstrap()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.db.database import engine, Base
from app.api.routes import auth, match, users, animals, rescues

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Patitas Match API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(animals.router)
app.include_router(match.router, prefix="/matches", tags=["Matches"])
app.include_router(rescues.router)


@app.get("/")
def check_health():
    return {"status": "ok", "service": "Patitas Match API is running"}
