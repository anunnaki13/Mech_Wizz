from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models  # noqa: F401
from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    documents,
    emission_tests,
    health,
    hydrogen_strategy,
    investor,
    llm,
    map,
    plants,
    prefeed,
    prefeed_costs,
    prefeed_decision,
    prefeed_market,
    scenarios,
    scoring,
    sensitivity,
    settings,
    site_readiness,
    unit_profiles,
)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    if get_settings().app_env == "test":
        Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="MECH WIZ AI Digital Twin API", version="0.1.0", lifespan=lifespan)

app_settings = get_settings()
cors_allowed_origins = [
    origin.strip()
    for origin in app_settings.cors_allowed_origins.split(",")
    if origin.strip()
]
allow_all_origins = not cors_allowed_origins or "*" in cors_allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_all_origins else cors_allowed_origins,
    allow_credentials=False if allow_all_origins else app_settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_router = APIRouter(prefix="/api")
api_router.include_router(health.router)
api_router.include_router(plants.router)
api_router.include_router(emission_tests.router)
api_router.include_router(site_readiness.router)
api_router.include_router(hydrogen_strategy.router)
api_router.include_router(scenarios.router)
api_router.include_router(scoring.router)
api_router.include_router(map.router)
api_router.include_router(unit_profiles.router)
api_router.include_router(sensitivity.router)
api_router.include_router(investor.router)
api_router.include_router(settings.router)
api_router.include_router(llm.router)
api_router.include_router(documents.router)
api_router.include_router(prefeed.router)
api_router.include_router(prefeed_costs.router)
api_router.include_router(prefeed_decision.router)
api_router.include_router(prefeed_market.router)

app.include_router(api_router)
