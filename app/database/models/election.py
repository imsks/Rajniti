"""
Election database model with CRUD operations.
"""

from datetime import date
from typing import List, Optional

from sqlalchemy import Column, Date, Integer, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Session

from ..base import Base


class Election(Base):
    """
    Election database model.

    Stores election information and metadata.
    """

    __tablename__ = "elections"

    # Columns
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    type = Column(SQLEnum("LOK_SABHA", "VIDHAN_SABHA", name="election_type"), nullable=False)
    year = Column(Integer, nullable=False, index=True)
    total_constituencies = Column(Integer, nullable=True)
    total_candidates = Column(Integer, nullable=True)
    total_parties = Column(Integer, nullable=True)
    result_status = Column(
        SQLEnum("DECLARED", "PENDING", "ONGOING", name="result_status"), nullable=True
    )

    def __repr__(self) -> str:
        return f"<Election(id={self.id}, name={self.name}, year={self.year})>"

    # CRUD Operations

    @classmethod
    def create(
        cls,
        session: Session,
        id: str,
        name: str,
        type: str,
        year: int,
        total_constituencies: Optional[int] = None,
        total_candidates: Optional[int] = None,
        total_parties: Optional[int] = None,
        result_status: Optional[str] = None,
    ) -> "Election":
        """
        Create a new election.

        Args:
            session: Database session
            id: Election ID (e.g., "lok-sabha-2024")
            name: Election name
            type: Election type (LOK_SABHA/VIDHAN_SABHA)
            year: Election year
            date: Election date (optional)
            total_constituencies: Total number of constituencies (optional)
            total_candidates: Total number of candidates (optional)
            total_parties: Total number of parties (optional)
            result_status: Result status (DECLARED/PENDING/ONGOING) (optional)

        Returns:
            Created Election instance
        """
        election = cls(
            id=id,
            name=name,
            type=type,
            year=year,
            date=date,
            total_constituencies=total_constituencies,
            total_candidates=total_candidates,
            total_parties=total_parties,
            result_status=result_status,
        )
        session.add(election)
        session.flush()
        return election

    @classmethod
    def get_by_id(cls, session: Session, election_id: str) -> Optional["Election"]:
        """
        Get election by ID.

        Args:
            session: Database session
            election_id: Election ID

        Returns:
            Election instance or None if not found
        """
        return session.query(cls).filter(cls.id == election_id).first()

    @classmethod
    def get_all(
        cls, session: Session, skip: int = 0, limit: int = 100
    ) -> List["Election"]:
        """
        Get all elections with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Election instances
        """
        return session.query(cls).order_by(cls.year.desc()).offset(skip).limit(limit).all()

    @classmethod
    def get_by_year(cls, session: Session, year: int) -> List["Election"]:
        """
        Get elections by year.

        Args:
            session: Database session
            year: Election year

        Returns:
            List of Election instances
        """
        return session.query(cls).filter(cls.year == year).all()

    @classmethod
    def get_by_type(cls, session: Session, election_type: str) -> List["Election"]:
        """
        Get elections by type.

        Args:
            session: Database session
            election_type: Election type (LOK_SABHA/VIDHAN_SABHA)

        Returns:
            List of Election instances
        """
        return session.query(cls).filter(cls.type == election_type).all()

    def update(self, session: Session, **kwargs) -> "Election":
        """
        Update election attributes.

        Args:
            session: Database session
            **kwargs: Attributes to update

        Returns:
            Updated Election instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        """
        Delete this election.

        Args:
            session: Database session
        """
        session.delete(self)
        session.flush()

    @classmethod
    def bulk_create(cls, session: Session, elections: List[dict]) -> List["Election"]:
        """
        Create multiple elections at once.

        Args:
            session: Database session
            elections: List of election dictionaries

        Returns:
            List of created Election instances
        """
        election_objects = [
            cls(
                id=e["election_id"] if "election_id" in e else e["id"],
                name=e["name"],
                type=e["type"],
                year=e["year"],
                date=e.get("date"),
                total_constituencies=e.get("total_constituencies"),
                total_candidates=e.get("total_candidates"),
                total_parties=e.get("total_parties"),
                result_status=e.get("result_status"),
            )
            for e in elections
        ]
        session.bulk_save_objects(election_objects, return_defaults=True)
        session.flush()
        return election_objects

