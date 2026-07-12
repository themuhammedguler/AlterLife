"""
AlterLife – FastAPI Backend Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
)

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="AlterLife API",
    description=(
        "Hayat İçin Dijital İkiz ve RPG Karar Motoru – "
        "Backend REST API (FastAPI + LangGraph + Gemini)"
    ),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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


# ── Health Check ──────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "ok",
        "service": "AlterLife API",
        "version": app.version,
    }


@app.get("/", tags=["System"])
async def root():
    return {
        "message": "Welcome to AlterLife API – Enter the Simulation 🚀",
        "docs": "/docs",
        "health": "/health",
    }
