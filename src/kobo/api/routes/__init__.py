"""API route registrars."""

from __future__ import annotations

from importlib import import_module
from typing import Any

_ROUTE_IMPORTS = {
    "register_chat_routes": "kobo.api.routes.chat",
    "register_composio_routes": "kobo.api.routes.composio",
    "register_debug_log_routes": "kobo.api.routes.debug_logs",
    "register_file_routes": "kobo.api.routes.files",
    "register_generic_chat_routes": "kobo.api.routes.generic_chat",
    "register_health_routes": "kobo.api.routes.health",
    "register_intake_workflow_routes": "kobo.api.routes.intake",
    "register_knowledge_routes": "kobo.api.routes.knowledge",
    "register_memory_routes": "kobo.api.routes.memory",
    "register_profile_routes": "kobo.api.routes.profiles",
    "register_scheduler_routes": "kobo.api.routes.scheduler",
    "register_skill_routes": "kobo.api.routes.skills",
    "register_system_routes": "kobo.api.routes.system",
    "register_task_routes": "kobo.api.routes.tasks",
    "register_telegram_business_routes": "kobo.api.routes.telegram_business",
    "register_telegram_webhook_health_routes": "kobo.api.routes.telegram_webhook_health",
    "register_telegram_webhook_routes": "kobo.api.routes.telegram_webhook",
    "register_tulpa_routes": "kobo.api.routes.tulpa",
    "register_user_context_routes": "kobo.api.routes.user_context",
    "register_wake_and_search_routes": "kobo.api.routes.wake_search",
    "register_web_event_routes": "kobo.api.routes.web_events",
}

__all__ = list(_ROUTE_IMPORTS)


def __getattr__(name: str) -> Any:
    module_name = _ROUTE_IMPORTS.get(name)
    if module_name is None:
        raise AttributeError(name)
    module = import_module(module_name)
    return getattr(module, name)
