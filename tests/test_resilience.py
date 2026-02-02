 import pytest
 
 from neurogenesis.api.main import create_app
 from neurogenesis.models.events import EventEnvelope
 
 
 @pytest.mark.asyncio
 async def test_fallback_on_handler_failure() -> None:
     app = create_app()
     bus = app.state.event_bus
     incidents = app.state.incident_log
 
     async def failing_handler(_: EventEnvelope) -> None:
         raise RuntimeError("boom")
 
     async def fallback_handler(envelope: EventEnvelope) -> EventEnvelope:
         return EventEnvelope(
             event_type="fallback",
             capability=envelope.capability,
             trace_id=envelope.trace_id,
             source="fallback",
         )
 
     bus.register("unstable", failing_handler, fallback=fallback_handler, retries=1)
     event = EventEnvelope(event_type="test", capability="unstable")
     result = await bus.route_event(event)
 
     assert result is not None
     assert result.event_type == "fallback"
     assert incidents.list()
