 from __future__ import annotations
 
 import json
 from uuid import uuid4
 
 from fastapi import APIRouter, Request
 from fastapi.responses import StreamingResponse
 
 from neurogenesis.models.llm import LLMRequest
 
 router = APIRouter(prefix="/v1/llm", tags=["llm"])
 
 
 @router.post("/stream")
 async def stream_llm(request: Request, body: LLMRequest) -> StreamingResponse:
     trace_id = body.trace_id or str(uuid4())
     body.trace_id = trace_id
     gateway = request.app.state.llm_gateway
     trace_hub = request.app.state.trace_hub
 
     async def event_stream():
         async for chunk in gateway.stream(body):
             payload = chunk.model_dump()
             payload["trace_id"] = trace_id
             await trace_hub.emit(trace_id, "llm_chunk", payload)
             data = json.dumps(payload, ensure_ascii=True)
             yield f"data: {data}\n\n"
 
     return StreamingResponse(event_stream(), media_type="text/event-stream")
