from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router

app = FastAPI(
    title="MemoryCart AI",
    description="AI-driven e-commerce assistant with long-term memory",
    version="1.0.0"
)

# Enable CORS for the frontend application
origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register the chat router
app.include_router(chat_router)

# Health check route
@app.get("/")
def health_check():
    """
    Health check endpoint returning the status of the service.
    """
    return {"status": "running"}
