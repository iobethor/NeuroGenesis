 from __future__ import annotations
 
 import asyncio
 from typing import Any, Awaitable, Callable, Tuple, Type
 
 
 async def run_with_timeout(awaitable: Awaitable[Any], timeout_ms: int) -> Any:
     return await asyncio.wait_for(awaitable, timeout=timeout_ms / 1000)
 
 
 async def retry_async(
     func: Callable[[], Awaitable[Any]],
     attempts: int,
     base_delay_ms: int,
     retry_on: Tuple[Type[BaseException], ...] = (Exception,),
 ) -> Any:
     last_error: BaseException | None = None
     for attempt in range(1, attempts + 1):
         try:
             return await func()
         except retry_on as exc:
             last_error = exc
             if attempt >= attempts:
                 break
             await asyncio.sleep((base_delay_ms * attempt) / 1000)
     if last_error:
         raise last_error
     raise RuntimeError("retry_async exhausted without error")
