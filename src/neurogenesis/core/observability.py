 from __future__ import annotations
 
 import logging
 from typing import Optional
 
 from fastapi import FastAPI
 
 from neurogenesis.core.logging import configure_logging
 
 logger = logging.getLogger("neurogenesis.observability")
 
 
 def configure_observability(app: FastAPI, log_level: str) -> None:
     configure_logging(log_level)
     _configure_tracing(app)
 
 
 def _configure_tracing(app: FastAPI) -> None:
     try:
         from opentelemetry import trace  # type: ignore
         from opentelemetry.exporter.otlp.proto.http.trace_exporter import (  # type: ignore
             OTLPSpanExporter,
         )
         from opentelemetry.instrumentation.fastapi import (  # type: ignore
             FastAPIInstrumentor,
         )
         from opentelemetry.sdk.resources import Resource  # type: ignore
         from opentelemetry.sdk.trace import TracerProvider  # type: ignore
         from opentelemetry.sdk.trace.export import BatchSpanProcessor  # type: ignore
 
         resource = Resource.create({"service.name": "neurogenesis-api"})
         provider = TracerProvider(resource=resource)
         span_processor = BatchSpanProcessor(OTLPSpanExporter())
         provider.add_span_processor(span_processor)
         trace.set_tracer_provider(provider)
         FastAPIInstrumentor.instrument_app(app)
         logger.info("OpenTelemetry tracing enabled")
     except Exception as exc:  # pylint: disable=broad-except
         logger.warning("Tracing disabled: %s", exc)
 
 
 def get_prometheus_app() -> Optional[FastAPI]:
     try:
         from prometheus_client import make_asgi_app  # type: ignore
 
         return make_asgi_app()
     except Exception:
         return None
