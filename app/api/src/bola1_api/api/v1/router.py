from fastapi import APIRouter

from bola1_api.api.v1 import activities, admin, auth, groups, matches, predictions, rankings, users

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(matches.router)
api_router.include_router(predictions.router)
api_router.include_router(rankings.router)
api_router.include_router(activities.router)
api_router.include_router(admin.router)
