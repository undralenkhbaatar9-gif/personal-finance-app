from finance.db import Base, engine
from finance import models  # noqa: F401
from finance.seed import seed


def initialize_database() -> None:
    """Create the database schema and insert the spec-defined seed data."""
    if engine is None:
        raise RuntimeError("DATABASE_URL must be set in the environment or .env file")
    Base.metadata.create_all(bind=engine)
    seed()


if __name__ == "__main__":
    initialize_database()