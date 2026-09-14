from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import init_db
from app.api.routes_ask import router as ask_router
from app.api.routes_documents import router as documents_router
from app.api.routes_eval import router as eval_router
from app.api.routes_health import router as health_router

app = FastAPI(title="Personal RAG Search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health_router)
app.include_router(documents_router)
app.include_router(ask_router)
app.include_router(eval_router)
