 from __future__ import annotations
 
 from fastapi import APIRouter, Request
 from fastapi.responses import StreamingResponse
 
 router = APIRouter(prefix="/v1/stream", tags=["stream"])
 
 
 @router.get("/{trace_id}")
 async def stream_trace(request: Request, trace_id: str) -> StreamingResponse:
     settings = request.app.state.settings
     generator = request.app.state.trace_hub.stream(trace_id, settings.sse_keepalive_s)
     return StreamingResponse(generator, media_type="text/event-stream")
