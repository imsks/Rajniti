"""
Constituency database model with CRUD operations.
"""

from typing import List, Optional

from sqlalchemy import Column, String
from sqlalchemy.orm import Session

from ..base import Base


class Constituency(Base):
    """
    Constituency database model.

    Stores constituency (electoral district) information.
    """

    __tablename__ = "constituencies"

    # Columns
    id = Column(String, primary_key=True, index=True)  # unique_id (format: "{id}-{state_id}")
    original_id = Column(String, nullable=False)  # Original constituency ID for scraping
    name = Column(String, nullable=False, index=True)
    state_id = Column(String, nullable=False, index=True)

    def __repr__(self) -> str:
        return (
            f"<Constituency(id={self.id}, name={self.name}, state_id={self.state_id})>"
        )

    # CRUD Operations

    @classmethod
    def create(
        cls, session: Session, id: str, name: str, state_id: str, original_id: str = None
    ) -> "Constituency":
        """
        Create a new constituency.

        Args:
            session: Database session
            id: Unique constituency ID (format: "{original_id}-{state_id}")
            name: Constituency name
            state_id: State ID code
            original_id: Original constituency ID for scraping (defaults to extracting from id)

        Returns:
            Created Constituency instance
        """
        # If original_id not provided, extract from id (assuming format "{id}-{state_id}")
        if original_id is None:
            if "-" in id:
                original_id = id.split("-")[0]
            else:
                original_id = id
        
        constituency = cls(
            id=id,
            original_id=original_id,
            name=name,
            state_id=state_id,
        )
        session.add(constituency)
        session.flush()
        return constituency

    @classmethod
    def get_by_id(
        cls, session: Session, constituency_id: str
    ) -> Optional["Constituency"]:
        """
        Get constituency by ID.

        Args:
            session: Database session
            constituency_id: Constituency ID

        Returns:
            Constituency instance or None if not found
        """
        return session.query(cls).filter(cls.id == constituency_id).first()

    @classmethod
    def get_by_state(cls, session: Session, state_id: str) -> List["Constituency"]:
        """
        Get all constituencies for a state.

        Args:
            session: Database session
            state_id: State ID code

        Returns:
            List of Constituency instances
        """
        return session.query(cls).filter(cls.state_id == state_id).all()

    @classmethod
    def get_all(
        cls, session: Session, skip: int = 0, limit: int = 100
    ) -> List["Constituency"]:
        """
        Get all constituencies with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Constituency instances
        """
        return session.query(cls).offset(skip).limit(limit).all()

    def update(self, session: Session, **kwargs) -> "Constituency":
        """
        Update constituency attributes.

        Args:
            session: Database session
            **kwargs: Attributes to update

        Returns:
            Updated Constituency instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        """
        Delete this constituency.

        Args:
            session: Database session
        """
        session.delete(self)
        session.flush()

    @classmethod
    def bulk_create(
        cls, session: Session, constituencies: List[dict]
    ) -> List["Constituency"]:
        """
        Create multiple constituencies at once.

        Args:
            session: Database session
            constituencies: List of constituency dictionaries

        Returns:
            List of created Constituency instances
        """
        constituency_objects = [
            cls(
                id=c.get("unique_id", c.get("id")),  # Use unique_id if available, fallback to id
                original_id=c.get("id", c.get("original_id", "")),  # Original ID for scraping
                name=c["name"],
                state_id=c["state_id"],
            )
            for c in constituencies
        ]
        session.bulk_save_objects(constituency_objects, return_defaults=True)
        session.flush()
        return constituency_objects
