"""
AlterLife – FastAPI Backend Entry Point
"""

import logging
import os
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from api.v1.routers import (
    auth,
    user,
    simulations,
    skills,
    quests,
    integrations,
    library,
    analytics,
    agents,
    briefing,
    community,
    coach,
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AlterLife API",
    description=(
        "Hayat İçin Dijital İkiz ve RPG Karar Motoru – "
        "Backend REST API (FastAPI + LangGraph + Groq)"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
logger = logging.getLogger("alterlife.api")

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
CORS_ORIGINS = [origin.strip() for origin in CORS_ORIGINS if origin.strip()]

if os.getenv("ENVIRONMENT", "development").lower() == "production":
    insecure_secret = "alterlife_super_secret_session_key_2026"
    if os.getenv("JWT_SECRET_KEY", insecure_secret) == insecure_secret:
        raise RuntimeError("Production için güçlü ve benzersiz JWT_SECRET_KEY yapılandırılmalı.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
    started_at = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - started_at) * 1000
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["X-Request-ID"] = request_id
    logger.info(
        "%s %s status=%s duration_ms=%.2f request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response

# ── Routers ───────────────────────────────────────────────────────────────────
API_PREFIX = "/api/v1"

app.include_router(auth.router,         prefix=API_PREFIX, tags=["Auth"])
app.include_router(user.router,         prefix=API_PREFIX, tags=["User"])
app.include_router(simulations.router,  prefix=API_PREFIX, tags=["Simulations"])
app.include_router(skills.router,       prefix=API_PREFIX, tags=["Skills"])
app.include_router(quests.router,       prefix=API_PREFIX, tags=["Quests"])
app.include_router(integrations.router, prefix=API_PREFIX, tags=["Integrations"])
app.include_router(library.router,      prefix=API_PREFIX, tags=["Library"])
app.include_router(analytics.router,    prefix=API_PREFIX, tags=["Analytics"])
app.include_router(agents.router,       prefix=API_PREFIX, tags=["Agents"])
app.include_router(briefing.router,     prefix=API_PREFIX, tags=["Briefing"])
app.include_router(community.router,    prefix=API_PREFIX, tags=["Community"])
app.include_router(coach.router,        prefix=API_PREFIX, tags=["Coach"])


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    from api.v1.database import get_db_mode

    return {
        "status": "ok",
        "service": "AlterLife API",
        "version": app.version,
        "database": get_db_mode(),
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to AlterLife API – Enter the Simulation 🚀",
        "docs": "/docs",
        "health": "/health",
    }
