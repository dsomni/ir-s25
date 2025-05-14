import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from src.pippeline import Pipeline, RAGPipeline
from src.utils import load, parse_document_content

DATA_PATH = os.path.join("./data/scrapped/class_data_function__1_1")
CONFIG = dotenv_values(".env")

PIPELINE = Pipeline()
RAG_PIPELINE = RAGPipeline()

app = FastAPI()


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.path.exists(DATA_PATH):
        raise RuntimeError(
            f"Data path '{DATA_PATH}' does not exist. Please check your setup."
        )
    yield


# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update for production)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(query: str, indexer: str):
    if indexer == "bert":
        corrected_query, proposals = PIPELINE.ball_tree(query)
    elif indexer == "inverted_idx":
        corrected_query, proposals = PIPELINE.inverted_index(query)
    else:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Indexer '{indexer}' not found"
        )

    return {
        "corrected": corrected_query,
        "proposals": [{"document": doc, "score": score} for doc, score in proposals],
    }


@app.get("/document")
async def document_page(name: str):
    try:
        content = load(os.path.join(DATA_PATH, f"{name}.txt"))
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Document '{name}' not found"
        ) from e
    return {
        "name": name,
        **parse_document_content(content),
        "content": content,
    }


@app.get("/models")
async def get_llm_list():
    return [
        "qwen-2-72b",
        "evil",
        "command-r",
    ]


@app.get("/chat")
async def chat(prompt: str, k: int, model: str):
    return StreamingResponse(
        RAG_PIPELINE.request(prompt, model, k),
        media_type="text/event-stream",
    )


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(CONFIG["BACKEND_PORT"] or 8000),
        reload=bool(CONFIG["DEBUG"]),
        log_level="info" if bool(CONFIG["DEBUG"]) else "warning",
    )
