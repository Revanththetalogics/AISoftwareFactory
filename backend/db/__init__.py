"""
Database module for AI Software Factory.

This module provides database connectivity and session management
using SQLAlchemy with PostgreSQL.
"""

from backend.db.session import get_db, init_db, engine, SessionLocal
from backend.db.base import Base

__all__ = ["get_db", "init_db", "engine", "SessionLocal", "Base"]
