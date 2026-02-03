 from __future__ import annotations
 
 from fastapi import APIRouter, WebSocket
 
 router = APIRouter(prefix="/v1/ws", tags=["ws"])
 
 
 @router.websocket("")
 async def websocket_endpoint(websocket: WebSocket) -> None:
     await websocket.accept()
     while True:
         data = await websocket.receive_text()
         await websocket.send_text(f"echo: {data}")
