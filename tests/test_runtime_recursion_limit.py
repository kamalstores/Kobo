from __future__ import annotations

from kobo.agent.runtime import KoboLangGraphRuntime


def test_recursion_limit_override_clamps_to_250() -> None:
    runtime = KoboLangGraphRuntime.__new__(KoboLangGraphRuntime)
    runtime.recursion_limit = 250

    assert runtime._effective_recursion_limit() == 250
    assert runtime._effective_recursion_limit(999) == 250
    assert runtime._effective_recursion_limit(3) == 5
