"""
Database module for AI Software Factory.

This module provides database connectivity and session management
using SQLAlchemy with PostgreSQL.
"""

from backend.db.base import Base
from backend.db.session import SessionLocal, engine, get_db, init_db

__all__ = ["get_db", "init_db", "engine", "SessionLocal", "Base"]
