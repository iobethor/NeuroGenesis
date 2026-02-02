 from __future__ import annotations
 
 import json
 import subprocess
 
 import httpx
 import typer
 
 app = typer.Typer(help="NeuroGenesis CLI")
 
 
 def _run_compose(*args: str) -> int:
     cmd = ["docker", "compose", *args]
     return subprocess.call(cmd)
 
 
 @app.command()
 def up(detached: bool = True) -> None:
     """Start the local stack via docker compose."""
     args = ["up"]
     if detached:
         args.append("-d")
     raise SystemExit(_run_compose(*args))
 
 
 @app.command()
 def down() -> None:
     """Stop the local stack."""
     raise SystemExit(_run_compose("down"))
 
 
 @app.command()
 def migrate() -> None:
     """Placeholder for DB migrations."""
     typer.echo("Migrations are not wired yet. Use Alembic in the next iteration.")
 
 
 @app.command()
 def seed() -> None:
     """Seed local development data."""
     typer.echo("Seed step is not wired yet. Add seed fixtures in scripts/.")
 
 
 @app.command()
 def smoke(base_url: str = "http://localhost:8000") -> None:
     """Run a basic health smoke test."""
     response = httpx.get(f"{base_url}/health", timeout=5)
     typer.echo(json.dumps(response.json(), indent=2))
 
 
 @app.command("export-traces")
 def export_traces(trace_id: str, base_url: str = "http://localhost:8000") -> None:
     """Export trace history for a trace id."""
     response = httpx.get(f"{base_url}/v1/events/traces/{trace_id}", timeout=10)
     typer.echo(json.dumps(response.json(), indent=2))
 
 
 @app.command()
 def version() -> None:
     """Print CLI version."""
     typer.echo("neurogenesis-cli 0.1.0")
