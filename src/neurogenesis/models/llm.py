 from __future__ import annotations
 
 from typing import List, Optional
 
 from pydantic import BaseModel, Field
 
 
 class LLMMessage(BaseModel):
     role: str
     content: str
 
 
 class LLMRequest(BaseModel):
     model: str = "mock"
     messages: List[LLMMessage] = Field(default_factory=list)
     stream: bool = True
     temperature: float = 0.2
     max_tokens: int = 256
     trace_id: Optional[str] = None
 
 
 class LLMChunk(BaseModel):
     delta: str
     done: bool = False
     provider: str = "mock"
     model: str = "mock"
     trace_id: Optional[str] = None
