"""Lightweight wrapper so the project can be imported as
`voice_nav_backend` without adding a nested package directory.

This file exposes the existing `app` and `routes` modules when
someone does `import voice_nav_backend`.
"""
from importlib import import_module

def _safe_import(name):
    try:
        return import_module(name)
    except Exception:
        return None

app = _safe_import("app")
routes = _safe_import("routes")

__all__ = ["app", "routes"]
