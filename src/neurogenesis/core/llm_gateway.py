 from __future__ import annotations
 
 import asyncio
 from typing import AsyncIterator, Dict, Protocol
 
 from neurogenesis.models.llm import LLMChunk, LLMRequest
 
 
 class LLMProvider(Protocol):
     name: str
 
     async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
         ...
 
 
 class MockLLMProvider:
     name = "mock"
 
     async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
         prompt = " ".join(message.content for message in request.messages)
         tokens = (prompt or "hello").split()
         for token in tokens:
             await asyncio.sleep(0.05)
             yield LLMChunk(delta=f"{token} ", done=False, provider=self.name, model="mock")
         yield LLMChunk(delta="", done=True, provider=self.name, model="mock")
 
 
 class LLMGateway:
     def __init__(self) -> None:
         self._providers: Dict[str, LLMProvider] = {"mock": MockLLMProvider()}
 
     def register(self, provider: LLMProvider) -> None:
         self._providers[provider.name] = provider
 
     def get_provider(self, name: str) -> LLMProvider:
         return self._providers.get(name, self._providers["mock"])
 
     async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
         provider = self.get_provider(request.model)
         async for chunk in provider.stream(request):
             yield chunk
