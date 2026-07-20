# SQLite runtime store policy

## Inventory of Kobo-owned runtime SQLite stores

These stores are owned by Kobo runtime code and now use the shared connection policy helper:

- `src/Kobo/tasks/service.py`
- `src/Kobo/tasks/wake_queue.py`
- `src/Kobo/scheduler/service.py`
- `src/Kobo/intake/service.py`
- `src/Kobo/intake/workflow_setup_store.py`
- `src/Kobo/context/service.py`
- `src/Kobo/context/customer_profiles.py`
- `src/Kobo/context/link_aliases.py`
- `src/Kobo/context/thread_rollups.py`
- `src/Kobo/context/file_vault.py`
- `src/Kobo/interfaces/telegram/business.py`
- `src/Kobo/skills/service.py`
- `src/Kobo/business_knowledge/service.py`

LangGraph checkpoint internals are intentionally out of scope.

## Standard connection policy

`Kobo.persistence.sqlite.connect_sqlite` centralizes:

- nonzero `timeout` on `sqlite3.connect`
- `PRAGMA busy_timeout`
- `PRAGMA synchronous=NORMAL`
- optional `PRAGMA journal_mode=WAL` (enabled for runtime stores above)

## SQLAlchemy/SQLModel boundary decision

For this refactor, we keep raw `sqlite3` for Kobo-owned stores and standardize behavior through a thin helper.

Rationale:

- The lock failures came from inconsistent connection pragmas rather than query composition.
- Most stores are small, simple, and already stable with direct SQL statements.
- Migrating to SQLAlchemy Core/SQLModel would add dependency and migration overhead without directly reducing lock contention.

Boundary:

- Kobo durable runtime stores should use `connect_sqlite`.
- If future modules require cross-database portability, rich transaction orchestration, or declarative schema management, SQLAlchemy Core can be adopted module-by-module rather than globally.
