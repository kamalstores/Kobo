"""Domain-specific tool registration helpers."""

from kobo.agent.tools.browser_tools import register_browser_tools
from kobo.agent.tools.composio_tools import register_composio_tools
from kobo.agent.tools.core_tools import register_core_tools
from kobo.agent.tools.intake_tools import register_intake_tools
from kobo.agent.tools.routine_tools import register_routine_tools
from kobo.agent.tools.skill_tools import register_skill_tools

__all__ = [
    "register_browser_tools",
    "register_composio_tools",
    "register_core_tools",
    "register_intake_tools",
    "register_routine_tools",
    "register_skill_tools",
]
