"""
User database model with authentication and onboarding support.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, JSON, String
from sqlalchemy.orm import Session

from ..base import Base


class User(Base):
    """
    User database model for authentication and onboarding.
    """

    __tablename__ = "users"

    # Primary identification
    id = Column(String, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True, index=True)
    profile_picture = Column(String, nullable=True)

    # Onboarding information
    phone = Column(String, nullable=True)           # ← NEW
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    age_group = Column(String, nullable=True)

    # Constituency information
    vs_constituency_id = Column(String, nullable=True)
    ls_constituency_id = Column(String, nullable=True)

    # Political preferences
    political_ideology = Column(String, nullable=True)
    preferred_parties = Column(JSON, nullable=True)     # ← NEW (stores string[])
    topics_of_interest = Column(JSON, nullable=True)    # ← NEW (stores string[])

    # Onboarding status
    onboarding_completed = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    # ── CRUD Operations ───────────────────────────────────────────────────────

    @classmethod
    def create(
        cls,
        session: Session,
        id: str,
        email: str,
        name: Optional[str] = None,
        profile_picture: Optional[str] = None,
    ) -> "User":
        user = cls(
            id=id,
            email=email,
            name=name,
            profile_picture=profile_picture,
            onboarding_completed=False,
        )
        session.add(user)
        session.flush()
        return user

    @classmethod
    def get_by_id(cls, session: Session, user_id: str) -> Optional["User"]:
        return session.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> Optional["User"]:
        return session.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_username(cls, session: Session, username: str) -> Optional["User"]:
        return session.query(cls).filter(cls.username == username).first()

    @classmethod
    def is_username_available(cls, session: Session, username: str) -> bool:
        return session.query(cls).filter(cls.username == username).first() is None

    @classmethod
    def get_all(cls, session: Session) -> List["User"]:
        return session.query(cls).all()

    def update(self, session: Session, **kwargs) -> "User":
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
        session.flush()
        return self

    def complete_onboarding(
        self,
        session: Session,
        username: Optional[str] = None,
        state: Optional[str] = None,
        city: Optional[str] = None,
        age_group: Optional[str] = None,
        phone: Optional[str] = None,
        political_ideology: Optional[str] = None,
        preferred_parties: Optional[list] = None,
        topics_of_interest: Optional[list] = None,
    ) -> "User":
        self.username = username
        self.state = state
        self.city = city
        self.age_group = age_group
        self.phone = phone
        self.political_ideology = political_ideology
        self.preferred_parties = preferred_parties or []
        self.topics_of_interest = topics_of_interest or []
        self.onboarding_completed = True
        self.updated_at = datetime.utcnow()
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        session.delete(self)
        session.flush()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "username": self.username,
            "profile_picture": self.profile_picture,
            "phone": self.phone,
            "state": self.state,
            "city": self.city,
            "pincode": self.pincode,
            "age_group": self.age_group,
            "political_ideology": self.political_ideology,
            "preferred_parties": self.preferred_parties or [],
            "topics_of_interest": self.topics_of_interest or [],
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }