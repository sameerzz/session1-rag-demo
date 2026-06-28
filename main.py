from __future__ import annotations

import asyncio
import random

from fastapi import FastAPI
from pydantic import BaseModel
from prometheus_fastapi_instrumentator import Instrumentator


app = FastAPI(
    title="RAG Observability Lab API",
    version="1.0.0",
    description="Minimal FastAPI service for generating RED telemetry in Grafana.",
)


class ChatRequest(BaseModel):
    message: str


async def simulate_rag_latency() -> float:
    # Simulates retrieval + generation time so students can observe latency behavior.
    delay_seconds = round(random.uniform(0.5, 3.0), 2)
    await asyncio.sleep(delay_seconds)
    return delay_seconds


@app.post("/chat")
async def chat(req: ChatRequest) -> dict:
    delay_seconds = await simulate_rag_latency()
    return {
        "answer": f"Simulated RAG response for: {req.message}",
        "latency_seconds": delay_seconds,
    }


# Exposes /metrics on the same host interface as the API so Prometheus can scrape it.
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

