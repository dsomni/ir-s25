import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.pippeline import Pipeline

CONFIG = dotenv_values(".env")

PIPELINE = Pipeline()

app = FastAPI()

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update for production)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(query: str):
    corrected_query, proposals = PIPELINE(query)
    return {
        "corrected": corrected_query,
        "proposals": [{"document": doc, "score": score} for doc, score in proposals],
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(CONFIG["BACKEND_PORT"] or 8000),
        reload=bool(CONFIG["DEBUG"]),
        log_level="info" if bool(CONFIG["DEBUG"]) else "warning",
    )
