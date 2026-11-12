import config

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, certificate, badge
from utils.auth import get_auth_client, close_auth_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    get_auth_client()
    yield
    await close_auth_client()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api")
app.include_router(certificate.router, prefix="/api")
app.include_router(badge.router, prefix="/api")