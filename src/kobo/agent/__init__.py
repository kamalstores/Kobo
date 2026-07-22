"""Agent runtime package."""

from __future__ import annotations

__all__ = ["KoboLangGraphRuntime"]


def __getattr__(name: str):
    if name == "KoboLangGraphRuntime":
        from kobo.agent.runtime import KoboLangGraphRuntime

        return KoboLangGraphRuntime
    raise AttributeError(f"module 'kobo.agent' has no attribute {name!r}")
