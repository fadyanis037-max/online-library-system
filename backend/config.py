import os


def _is_truthy(val: str | None) -> bool:
    return str(val).lower() in {"1", "true", "yes", "on"}


def _is_postgres_url(url: str) -> bool:
    return url.startswith(("postgresql://", "postgresql+psycopg://", "postgres://"))


def _has_postgres_driver() -> bool:
    try:
        import psycopg2  # type: ignore

        return True
    except Exception:
        try:
            import psycopg  # type: ignore

            return True
        except Exception:
            return False


class Config:
    """Base configuration for the Flask app.

    - Defaults to SQLite for development.
    - If `FORCE_SQLITE` is set to a truthy value, uses SQLite regardless of
      any `DATABASE_URL` present in the environment.
    - If `DATABASE_URL` is provided and points to PostgreSQL but the driver is
      not installed, gracefully falls back to SQLite.
    """

    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

    force_sqlite = _is_truthy(os.getenv("FORCE_SQLITE"))
    database_url = None if force_sqlite else os.getenv("DATABASE_URL")

    sqlite_path = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'library.db')}"

    use_database_url = False
    if database_url:
        # Normalize scheme if someone sets postgres://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)

        if _is_postgres_url(database_url):
            if _has_postgres_driver():
                SQLALCHEMY_DATABASE_URI = database_url
                use_database_url = True
            else:
                # Fallback to SQLite when driver is missing
                SQLALCHEMY_DATABASE_URI = sqlite_path
        else:
            SQLALCHEMY_DATABASE_URI = database_url
            use_database_url = True

    if not use_database_url:
        # SQLite file in the backend directory by default
        SQLALCHEMY_DATABASE_URI = os.getenv("SQLALCHEMY_DATABASE_URI", sqlite_path)

    SQLALCHEMY_TRACK_MODIFICATIONS = False


def get_config() -> type[Config]:
    return Config
