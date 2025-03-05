import uvicorn
from dotenv import dotenv_values
from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware

CONFIG = dotenv_values(".env")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Before start
    ### Check and build if necessary all the index/stuff
    yield
    # After finish


app = FastAPI(
    lifespan=lifespan,
)

# Allow CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (update for production)
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/search")
async def search(query: str):
    return {"proposals": [query] * 10}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=int(CONFIG["BACKEND_PORT"] or 8000),
        reload=bool(CONFIG["DEBUG"]),
        log_level="info" if bool(CONFIG["DEBUG"]) else "warning",
    )
