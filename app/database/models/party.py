"""
Party database model with CRUD operations.
"""

from typing import List, Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from ..base import Base


class Party(Base):
    """
    Party database model.

    Stores political party information.
    """

    __tablename__ = "parties"

    # Columns
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    short_name = Column(String, nullable=False)
    symbol = Column(String, default="")

    def __repr__(self) -> str:
        return f"<Party(id={self.id}, name={self.name})>"

    # CRUD Operations

    @classmethod
    def create(
        cls, session: Session, id: str, name: str, short_name: str, symbol: str = ""
    ) -> "Party":
        """
        Create a new party.

        Args:
            session: Database session
            id: Party ID
            name: Full party name
            short_name: Short party name/abbreviation
            symbol: Party symbol (optional)

        Returns:
            Created Party instance
        """
        party = cls(
            id=id,
            name=name,
            short_name=short_name,
            symbol=symbol,
        )
        session.add(party)
        session.flush()
        return party

    @classmethod
    def get_by_id(cls, session: Session, party_id: str) -> Optional["Party"]:
        """
        Get party by ID.

        Args:
            session: Database session
            party_id: Party ID

        Returns:
            Party instance or None if not found
        """
        return session.query(cls).filter(cls.id == party_id).first()

    @classmethod
    def get_by_name(cls, session: Session, name: str) -> Optional["Party"]:
        """
        Get party by name (case-insensitive).

        Args:
            session: Database session
            name: Party name

        Returns:
            Party instance or None if not found
        """
        return session.query(cls).filter(cls.name.ilike(name)).first()

    @classmethod
    def get_all(
        cls, session: Session, skip: int = 0, limit: int = 100
    ) -> List["Party"]:
        """
        Get all parties with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Party instances
        """
        return session.query(cls).offset(skip).limit(limit).all()

    def update(self, session: Session, **kwargs) -> "Party":
        """
        Update party attributes.

        Args:
            session: Database session
            **kwargs: Attributes to update

        Returns:
            Updated Party instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        """
        Delete this party.

        Args:
            session: Database session
        """
        session.delete(self)
        session.flush()

    @classmethod
    def bulk_create(cls, session: Session, parties: List[dict]) -> List["Party"]:
        """
        Create multiple parties at once.

        Args:
            session: Database session
            parties: List of party dictionaries

        Returns:
            List of created Party instances
        """
        party_objects = [
            cls(
                id=p["id"],
                name=p["name"],
                short_name=p["short_name"],
                symbol=p.get("symbol", ""),
            )
            for p in parties
        ]
        session.bulk_save_objects(party_objects, return_defaults=True)
        session.flush()
        return party_objects
