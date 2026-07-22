"""Create all database tables.

Simple bootstrap for local development (no migrations yet). Run with::

    python -m backend.database.init_db

For production, replace this with a migration tool such as Alembic.
"""

from backend.database import Base, engine

# Importing the models package registers every table on ``Base.metadata``.
import backend.models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
