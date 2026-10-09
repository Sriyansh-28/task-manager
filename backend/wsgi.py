"""WSGI entrypoint for hosts that need a module-level `app` (e.g. Vercel)."""
from app import create_app

app = create_app()
