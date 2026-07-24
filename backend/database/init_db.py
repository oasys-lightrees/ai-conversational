"""Create all database tables and seed the built-in templates.

Simple bootstrap for local development (no migrations yet). Run with::

    python -m backend.database.init_db

For production, replace this with a migration tool such as Alembic.
"""

from backend.database import Base, engine
from backend.database.session import SessionLocal

# Importing the models package registers every table on ``Base.metadata``.
import backend.models  # noqa: F401
from backend.pipeline.seed import seed_default_templates


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    with SessionLocal() as session:
        seed_default_templates(session)


if __name__ == "__main__":
    init_db()
    print("Database tables created and templates seeded.")
