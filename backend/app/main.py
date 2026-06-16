import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

# Configure basic logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

from app.api.chat import router as chat_router
from app.database.connection import engine

app = FastAPI(
    title="MemoryCart AI API",
    description="Backend API for processing user interactions with RAG and Memory",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# Register the chat router
app.include_router(chat_router, prefix="/api")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up MemoryCart AI Backend...")
    try:
        # Test DB connection
        with engine.connect() as connection:
            logger.info("Database connection successfully established.")
    except Exception as e:
        logger.error(f"Failed to connect to the database on startup: {e}")

@app.get("/")
def root_endpoint():
    """
    Root endpoint to verify the API is running.
    """
    return {"message": "Welcome to the MemoryCart AI API"}

@app.get("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    """
    return {"status": "ok", "message": "Service is healthy"}