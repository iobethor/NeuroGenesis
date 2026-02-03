 from __future__ import annotations
 
 from fastapi import APIRouter, Request
 
 router = APIRouter()
 
 
 @router.get("/health")
 async def health(request: Request) -> dict:
     settings = request.app.state.settings
     return {
         "status": "ok",
         "service": settings.service_name,
         "safe_mode": settings.safe_mode,
     }
