"""
User database model with authentication and onboarding support.
"""

from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy.orm import Session

from ..base import Base


class User(Base):
    """
    User database model for authentication and onboarding.

    Stores user authentication details, profile information, and political preferences.
    """

    __tablename__ = "users"

    # Primary identification
    id = Column(String, primary_key=True, index=True)  # Google user ID
    email = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=True)
    username = Column(String, unique=True, nullable=True, index=True)
    profile_picture = Column(String, nullable=True)

    # Onboarding information
    state = Column(String, nullable=True)
    city = Column(String, nullable=True)
    pincode = Column(String, nullable=True)
    age_group = Column(String, nullable=True)

    # Constituency information (stored as plain strings, validated against JSON data)
    vs_constituency_id = Column(String, nullable=True)
    ls_constituency_id = Column(String, nullable=True)

    # Political preferences
    political_ideology = Column(
        String, nullable=True
    )  # e.g., "Rightist", "Leftist", "Communist", "Centrist", "Libertarian", "Neutral"

    # Onboarding status
    onboarding_completed = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, name={self.name})>"

    # CRUD Operations

    @classmethod
    def create(
        cls,
        session: Session,
        id: str,
        email: str,
        name: Optional[str] = None,
        profile_picture: Optional[str] = None,
    ) -> "User":
        """
        Create a new user.

        Args:
            session: Database session
            id: User ID (Google user ID)
            email: User email
            name: User's full name
            profile_picture: URL to profile picture

        Returns:
            Created user object
        """
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
        """Get user by ID."""
        return session.query(cls).filter(cls.id == user_id).first()

    @classmethod
    def get_by_email(cls, session: Session, email: str) -> Optional["User"]:
        """Get user by email."""
        return session.query(cls).filter(cls.email == email).first()

    @classmethod
    def get_by_username(cls, session: Session, username: str) -> Optional["User"]:
        """Get user by username."""
        return session.query(cls).filter(cls.username == username).first()

    @classmethod
    def is_username_available(cls, session: Session, username: str) -> bool:
        """Check if username is available."""
        return session.query(cls).filter(cls.username == username).first() is None

    @classmethod
    def get_all(cls, session: Session) -> List["User"]:
        """Get all users."""
        return session.query(cls).all()

    def update(self, session: Session, **kwargs) -> "User":
        """
        Update user fields.

        Args:
            session: Database session
            **kwargs: Fields to update

        Returns:
            Updated user object
        """
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
    ) -> "User":
        """
        Complete user onboarding with basic details.

        Args:
            session: Database session
            username: Unique username
            state: State of residence
            city: City of residence
            age_group: Age group

        Returns:
            Updated user object
        """
        self.username = username
        self.state = state
        self.city = city
        self.age_group = age_group
        self.onboarding_completed = True
        self.updated_at = datetime.utcnow()
        session.flush()
        return self

    def delete(self, session: Session) -> None:
        """Delete user."""
        session.delete(self)
        session.flush()

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "username": self.username,
            "profile_picture": self.profile_picture,
            "state": self.state,
            "city": self.city,
            "pincode": self.pincode,
            "age_group": self.age_group,
            "political_ideology": self.political_ideology,
            "onboarding_completed": self.onboarding_completed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
