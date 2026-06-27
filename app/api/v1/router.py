from fastapi import APIRouter

from app.api.v1.endpoints import analytics, analyze, auth, jobs, reviews

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(analyze.router)
api_router.include_router(jobs.router)
api_router.include_router(reviews.router)
api_router.include_router(analytics.router)
