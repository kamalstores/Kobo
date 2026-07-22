from __future__ import annotations

import contextvars

from kobo.agent.runtime import KoboLangGraphRuntime


def test_runtime_active_thread_id_context_round_trip() -> None:
    runtime = object.__new__(KoboLangGraphRuntime)

    token = KoboLangGraphRuntime.set_active_thread_id(runtime, "thread_123")
    try:
        assert KoboLangGraphRuntime.get_active_thread_id(runtime) == "thread_123"
        assert runtime._active_thread_id == "thread_123"
    finally:
        KoboLangGraphRuntime.reset_active_thread_id(runtime, token)

    assert KoboLangGraphRuntime.get_active_thread_id(runtime) == ""
    assert runtime._active_thread_id == ""


def test_runtime_active_thread_id_reset_tolerates_cross_context() -> None:
    runtime = object.__new__(KoboLangGraphRuntime)

    other_context = contextvars.copy_context()
    token = other_context.run(KoboLangGraphRuntime.set_active_thread_id, runtime, "thread_123")

    assert KoboLangGraphRuntime.get_active_thread_id(runtime) == ""
    assert runtime._active_thread_id == "thread_123"

    KoboLangGraphRuntime.reset_active_thread_id(runtime, token)

    assert KoboLangGraphRuntime.get_active_thread_id(runtime) == ""
    assert runtime._active_thread_id == ""
