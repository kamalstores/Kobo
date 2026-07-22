"""Integrations: Browser Use, CapSolver, Composio, web-search, and external service connectors."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

__all__ = ["BrowserUseLocalManager", "CapSolverClient", "ComposioService", "HeadroomService"]

if TYPE_CHECKING:
    from kobo.integrations.browser_use_local import BrowserUseLocalManager
    from kobo.integrations.capsolver import CapSolverClient
    from kobo.integrations.composio import ComposioService
    from kobo.integrations.headroom import HeadroomService


def __getattr__(name: str) -> Any:
    if name == "BrowserUseLocalManager":
        from kobo.integrations.browser_use_local import BrowserUseLocalManager

        return BrowserUseLocalManager
    if name == "CapSolverClient":
        from kobo.integrations.capsolver import CapSolverClient

        return CapSolverClient
    if name == "ComposioService":
        from kobo.integrations.composio import ComposioService

        return ComposioService
    if name == "HeadroomService":
        from kobo.integrations.headroom import HeadroomService

        return HeadroomService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
