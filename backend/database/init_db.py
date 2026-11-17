"""Create all database tables and seed the built-in templates.

Simple bootstrap for local development (no migrations yet). Run with::

    python -m backend.database.init_db

Seeding never overwrites an existing template, so a change to ``DEFAULT_CONFIG``
does not reach an already-seeded database. To pull one through, re-sync the
built-in templates (this discards any admin-UI edits to those two templates)::

    python -m backend.database.init_db --refresh-builtins

For production, replace this with a migration tool such as Alembic.
"""

import sys

from backend.database import Base, engine
from backend.database.session import SessionLocal

# Importing the models package registers every table on ``Base.metadata``.
import backend.models  # noqa: F401
from backend.pipeline.seed import refresh_builtin_templates, seed_default_templates


def init_db(refresh_builtins: bool = False) -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_default_templates(session)
        if refresh_builtins:
            for name in refresh_builtin_templates(session):
                print(f"Refreshed built-in template: {name}")


if __name__ == "__main__":
    init_db(refresh_builtins="--refresh-builtins" in sys.argv[1:])
    print("Database tables created and templates seeded.")
