"""
data-sentinel FastAPI service.

Wraps the existing data comparison engine (the 'sentinel' package) in a REST API.
"""

from fastapi import FastAPI
from app.api.v1 import comparisons, health

from app.db import models  #noqa: F401 - needed to register models with Base
from app.db.base import Base
from app.db.session import engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="data-sentinel",
    description="Open-source data validation service."
                "Compares two sQLAlchemy-compatible databases.",
    version="0.1.0",
)

app.include_router(health.router, prefix="/api/v1", tags=["health"]) 
app.include_router(comparisons.router, prefix="/api/v1", tags=["comparison"])

@app.get("/")
def root():
    return {
        "servie": "data-sentinel",
        "version": "0.1.0",
        "docs": "/docs",
    }
