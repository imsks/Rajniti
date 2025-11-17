"""
Candidate database model with CRUD operations.
"""

import logging
from typing import Any, Dict, List, Optional

from sqlalchemy import Column
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String
from sqlalchemy.orm import Session
from sqlalchemy.types import JSON

from ..base import Base

logger = logging.getLogger(__name__)


class Candidate(Base):
    """
    Candidate database model.

    Stores election candidate information.
    """

    __tablename__ = "candidates"

    # Columns
    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    party_id = Column(String, nullable=False, index=True)
    constituency_id = Column(String, nullable=False, index=True)  # unique_id reference
    original_constituency_id = Column(
        String, nullable=True
    )  # Original ID for backward compatibility
    state_id = Column(String, nullable=False, index=True)
    image_url = Column(String, nullable=True)
    status = Column(SQLEnum("WON", "LOST", name="candidate_status"), nullable=False)
    type = Column(
        SQLEnum("MP", "MLA", name="candidate_type"), nullable=False, default="MP"
    )

    # New detailed information fields (JSON/JSONB for flexibility)
    # Using JSON for SQLite compatibility and JSONB for PostgreSQL performance
    education_background = Column(JSON, nullable=True)
    political_background = Column(JSON, nullable=True)
    family_background = Column(JSON, nullable=True)
    assets = Column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<Candidate(id={self.id}, name={self.name}, party_id={self.party_id})>"

    # CRUD Operations

    @classmethod
    def create(
        cls,
        session: Session,
        id: str,
        name: str,
        party_id: str,
        constituency_id: str,
        state_id: str,
        status: str,
        type: str = "MP",
        image_url: Optional[str] = None,
        original_constituency_id: Optional[str] = None,
        education_background: Optional[Dict[str, Any]] = None,
        political_background: Optional[Dict[str, Any]] = None,
        family_background: Optional[Dict[str, Any]] = None,
        assets: Optional[Dict[str, Any]] = None,
    ) -> "Candidate":
        """
        Create a new candidate.

        Args:
            session: Database session
            id: Candidate ID
            name: Candidate name
            party_id: Party ID
            constituency_id: Constituency unique_id (format: "{id}-{state_id}")
            state_id: State ID code
            status: Candidate status (WON/LOST)
            type: Candidate type (MP/MLA), defaults to MP
            image_url: URL to candidate image (optional)
            original_constituency_id: Original constituency ID for backward compatibility
            education_background: Education background data (optional)
            political_background: Political background data (optional)
            family_background: Family background data (optional)
            assets: Assets data (optional)

        Returns:
            Created Candidate instance
        """
        logger.info(f"Creating candidate: {name} (ID: {id})")
        if education_background:
            logger.debug(f"Education background provided for {name}")
        if political_background:
            logger.debug(f"Political background provided for {name}")
        if family_background:
            logger.debug(f"Family background provided for {name}")
        if assets:
            logger.debug(f"Assets information provided for {name}")

        candidate = cls(
            id=id,
            name=name,
            party_id=party_id,
            constituency_id=constituency_id,
            original_constituency_id=original_constituency_id,
            state_id=state_id,
            status=status,
            type=type,
            image_url=image_url,
            education_background=education_background,
            political_background=political_background,
            family_background=family_background,
            assets=assets,
        )
        session.add(candidate)
        session.flush()
        logger.info(f"Candidate {name} created successfully")
        return candidate

    @classmethod
    def get_by_id(cls, session: Session, candidate_id: str) -> Optional["Candidate"]:
        """
        Get candidate by ID.

        Args:
            session: Database session
            candidate_id: Candidate ID

        Returns:
            Candidate instance or None if not found
        """
        return session.query(cls).filter(cls.id == candidate_id).first()

    @classmethod
    def get_by_party(cls, session: Session, party_id: str) -> List["Candidate"]:
        """
        Get all candidates for a party.

        Args:
            session: Database session
            party_id: Party ID

        Returns:
            List of Candidate instances
        """
        return session.query(cls).filter(cls.party_id == party_id).all()

    @classmethod
    def get_by_constituency(
        cls, session: Session, constituency_id: str
    ) -> List["Candidate"]:
        """
        Get all candidates for a constituency.

        Args:
            session: Database session
            constituency_id: Constituency ID

        Returns:
            List of Candidate instances
        """
        return session.query(cls).filter(cls.constituency_id == constituency_id).all()

    @classmethod
    def get_winners(
        cls, session: Session, skip: int = 0, limit: int = 100
    ) -> List["Candidate"]:
        """
        Get all winning candidates with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Candidate instances
        """
        return (
            session.query(cls)
            .filter(cls.status == "WON")
            .offset(skip)
            .limit(limit)
            .all()
        )

    @classmethod
    def search_by_name(cls, session: Session, name: str) -> List["Candidate"]:
        """
        Search candidates by name (case-insensitive, partial match).

        Args:
            session: Database session
            name: Name to search for

        Returns:
            List of Candidate instances
        """
        return session.query(cls).filter(cls.name.ilike(f"%{name}%")).all()

    @classmethod
    def get_all(
        cls, session: Session, skip: int = 0, limit: int = 100
    ) -> List["Candidate"]:
        """
        Get all candidates with pagination.

        Args:
            session: Database session
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of Candidate instances
        """
        return session.query(cls).offset(skip).limit(limit).all()

    def update(self, session: Session, **kwargs) -> "Candidate":
        """
        Update candidate attributes.

        Args:
            session: Database session
            **kwargs: Attributes to update

        Returns:
            Updated Candidate instance
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        """
        Delete this candidate.

        Args:
            session: Database session
        """
        session.delete(self)
        session.flush()

    @classmethod
    def bulk_create(cls, session: Session, candidates: List[dict]) -> List["Candidate"]:
        """
        Create multiple candidates at once.

        Args:
            session: Database session
            candidates: List of candidate dictionaries

        Returns:
            List of created Candidate instances
        """
        logger.info(f"Bulk creating {len(candidates)} candidates")
        candidate_objects = [
            cls(
                id=c["id"],
                name=c["name"],
                party_id=c["party_id"],
                constituency_id=c.get(
                    "constituency_unique_id", c.get("constituency_id")
                ),
                original_constituency_id=c.get(
                    "constituency_id"
                ),  # Keep original for compatibility
                state_id=c["state_id"],
                status=c["status"],
                type=c.get("type", "MP"),
                image_url=c.get("image_url"),
                education_background=c.get("education_background"),
                political_background=c.get("political_background"),
                family_background=c.get("family_background"),
                assets=c.get("assets"),
            )
            for c in candidates
        ]
        session.bulk_save_objects(candidate_objects, return_defaults=True)
        session.flush()
        logger.info(f"Successfully bulk created {len(candidate_objects)} candidates")
        return candidate_objects
