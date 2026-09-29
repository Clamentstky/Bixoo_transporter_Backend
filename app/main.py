import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.modules.auth import router as auth_router
from app.modules.transporter.profile import router as profile_router
from app.modules.transporter.documents import router as documents_router
from app.modules.transporter.vehicles import router as vehicles_router
from app.modules.transporter.loads import router as loads_router
from app.modules.transporter.trips import router as trips_router
from app.modules.transporter.settlements import router as settlements_router
from app.modules.transporter.wallet import router as wallet_router
from app.modules.transporter.dashboard import router as dashboard_router
from app.modules.notifications import router as notifications_router
from app.modules.transporter.chats import router as chats_router

app.include_router(auth_router.router)
app.include_router(profile_router.router)
app.include_router(documents_router.router)
app.include_router(vehicles_router.router)
app.include_router(loads_router.router)
app.include_router(trips_router.router)
app.include_router(settlements_router.router)
app.include_router(wallet_router.router)
app.include_router(dashboard_router.router)
app.include_router(notifications_router.router)
app.include_router(chats_router.router)

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "app": settings.APP_NAME}
