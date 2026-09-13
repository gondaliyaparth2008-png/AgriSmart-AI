"""
app/db/base.py
--------------
Declarative base for all SQLAlchemy ORM models.

Import this Base in every model module and in session.py
so that `Base.metadata.create_all()` discovers all tables.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base.

    All ORM model classes must inherit from this Base.
    SQLAlchemy 2.x style — fully typed, no legacy `declarative_base()` call needed.
    """
    pass
