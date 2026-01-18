# Lightweight wrapper package so the project can be installed/imported as
# `voice_nav_backend` while keeping the existing layout (`app/`, `routes/`).
# This uses importlib to import the top-level `app` and `routes` modules.

from importlib import import_module

try:
    app = import_module("app")
except Exception:
    app = None

try:
    routes = import_module("routes")
except Exception:
    routes = None

__all__ = ["app", "routes"]
