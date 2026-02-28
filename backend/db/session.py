<<<<<<< HEAD
﻿"""
Database session configuration
Supports Neon PostgreSQL (SSL), standard PostgreSQL, and SQLite fallback
"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.config import settings
import os
import logging
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

logger = logging.getLogger(__name__)


def _clean_db_url(url: str):
    """
    Remove psycopg2-unsupported parameters (e.g. channel_binding)
    and return cleaned URL + connect_args dict.
    """
    connect_args = {}
    
    # Parse URL
    parsed = urlparse(url)
    params = parse_qs(parsed.query, keep_blank_values=True)
    
    # Extract sslmode for connect_args
    if "sslmode" in params:
        connect_args["sslmode"] = params.pop("sslmode")[0]
    
    # Remove channel_binding - NOT supported by psycopg2
    params.pop("channel_binding", None)
    
    # Rebuild clean URL
    clean_query = urlencode({k: v[0] for k, v in params.items()})
    clean_parsed = parsed._replace(query=clean_query)
    clean_url = urlunparse(clean_parsed)
    
    return clean_url, connect_args


def _create_engine():
    db_url = settings.DATABASE_URL

    # ── Neon / PostgreSQL ──────────────────────────────────────
    if db_url.startswith("postgresql") or db_url.startswith("postgres"):
        try:
            clean_url, connect_args = _clean_db_url(db_url)
            
            # Force SSL for Neon
            if "neon.tech" in db_url and "sslmode" not in connect_args:
                connect_args["sslmode"] = "require"

            engine = create_engine(
                clean_url,
                connect_args=connect_args,
                echo=settings.DEBUG,
                pool_pre_ping=True,
                pool_size=5,
                max_overflow=10,
                pool_recycle=300,   # Neon closes idle connections after 5min
                pool_timeout=30,
            )
            # Verify connection
            with engine.connect() as conn:
                result = conn.execute(text("SELECT version()"))
                ver = result.fetchone()[0][:50]
            logger.info(f"Connected to PostgreSQL: {ver}")
            print(f"Connected to PostgreSQL (Neon)")
            return engine

        except Exception as e:
            logger.warning(f"PostgreSQL failed: {type(e).__name__}: {e}")
            print(f"PostgreSQL failed ({e}), falling back to SQLite")

    # ── SQLite fallback ────────────────────────────────────────
    sqlite_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "freelancing_agency.db")
    )
    print(f"Using SQLite: {sqlite_path}")
    return create_engine(
        f"sqlite:///{sqlite_path}",
        connect_args={"check_same_thread": False},
        echo=False,
    )


engine = _create_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_background_session():
    """
    Create a DB session for background threads with NullPool.
    NullPool means each call gets a fresh connection (no pool sharing)
    so background threads never block waiting for pool slots from HTTP requests.
    """
    from sqlalchemy.pool import NullPool

    db_url = settings.DATABASE_URL
    if db_url.startswith("postgresql") or db_url.startswith("postgres"):
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(db_url)
        params = parse_qs(parsed.query, keep_blank_values=True)
        params.pop("channel_binding", None)
        sslmode = params.pop("sslmode", ["require"])[0]
        clean_query = urlencode({k: v[0] for k, v in params.items()})
        clean_url = urlunparse(parsed._replace(query=clean_query))

        bg_engine = create_engine(
            clean_url,
            connect_args={
                "sslmode": sslmode,
                "connect_timeout": 15,       # 15s connection timeout
            },
            poolclass=NullPool,
            echo=False,
        )
    else:
        # SQLite fallback
        sqlite_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "..", "freelancing_agency.db")
        )
        bg_engine = create_engine(
            f"sqlite:///{sqlite_path}",
            connect_args={"check_same_thread": False},
            echo=False,
        )

    BgSession = sessionmaker(autocommit=False, autoflush=False, bind=bg_engine)
    return BgSession()


def get_db():
    """FastAPI dependency - yields a database session"""
=======
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.config import DATABASE_URL

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
>>>>>>> 65e52cf1c6d95a55f86841050ddc5f9f1b34c086
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
