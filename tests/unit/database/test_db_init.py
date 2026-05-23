"""
Unit tests for database initialization and session management.
Tests verify the fixes for:
- Empty DATABASE_URL handling in init_engine()
- DB init and health checks in app.database.session
- get_db_session() error handling
"""

from unittest.mock import MagicMock, Mock, patch

import pytest


@pytest.mark.unit
class TestInitEngine:
    """Tests for app.database.session.init_engine()."""

    def test_returns_none_when_database_url_empty(self):
        """init_engine returns None when DATABASE_URL is empty."""
        import app.database.session as session_mod

        session_mod.engine = None
        session_mod.SessionLocal = None
        try:
            with patch("app.database.session.get_database_url", return_value=""):
                result = session_mod.init_engine()
            assert result is None
            assert session_mod.engine is None
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None

    def test_returns_none_when_database_url_raises(self):
        """init_engine returns None when get_database_url raises ValueError."""
        import app.database.session as session_mod

        session_mod.engine = None
        session_mod.SessionLocal = None
        try:
            with patch(
                "app.database.session.get_database_url",
                side_effect=ValueError("no url"),
            ):
                result = session_mod.init_engine()
            assert result is None
            assert session_mod.engine is None
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None

    def test_creates_engine_with_valid_url(self):
        """init_engine creates engine and SessionLocal when URL is valid."""
        import app.database.session as session_mod

        session_mod.engine = None
        session_mod.SessionLocal = None
        mock_engine = MagicMock()
        mock_session_factory = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value="sqlite:///:memory:",
                ),
                patch(
                    "app.database.session.create_engine",
                    return_value=mock_engine,
                ),
                patch(
                    "app.database.session.sessionmaker",
                    return_value=mock_session_factory,
                ),
            ):
                result = session_mod.init_engine()
            assert result is mock_engine
            assert session_mod.engine is mock_engine
            assert session_mod.SessionLocal is mock_session_factory
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None

    def test_idempotent_when_already_initialized(self):
        """init_engine returns existing engine without calling get_database_url."""
        import app.database.session as session_mod

        mock_engine = MagicMock()
        mock_session_factory = MagicMock()
        session_mod.engine = mock_engine
        session_mod.SessionLocal = mock_session_factory
        try:
            with patch("app.database.session.get_database_url") as mock_get_url:
                result = session_mod.init_engine()
            assert result is mock_engine
            mock_get_url.assert_not_called()
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None


@pytest.mark.unit
class TestGetDbSession:
    """Tests for app.database.base.get_db_session()."""

    def test_raises_when_no_session_factory(self):
        """get_db_session raises RuntimeError when SessionLocal is None."""
        import app.database.session as session_mod
        from app.database.base import get_db_session

        session_mod.engine = None
        session_mod.SessionLocal = None
        try:
            with patch("app.database.session.init_engine"):
                with pytest.raises(RuntimeError) as exc_info:
                    with get_db_session():
                        pass
            assert "Database is not configured" in str(exc_info.value)
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None

    def test_commits_on_success(self):
        """get_db_session commits when context exits normally."""
        import app.database.session as session_mod
        from app.database.base import get_db_session

        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        session_mod.engine = MagicMock()
        session_mod.SessionLocal = mock_session_factory
        try:
            with get_db_session() as session:
                assert session is mock_session
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None

    def test_rollback_on_error(self):
        """get_db_session rolls back and does not commit when exception raised."""
        import app.database.session as session_mod
        from app.database.base import get_db_session

        mock_session = MagicMock()
        mock_session_factory = MagicMock(return_value=mock_session)
        session_mod.engine = MagicMock()
        session_mod.SessionLocal = mock_session_factory
        try:
            with pytest.raises(ValueError):
                with get_db_session():
                    raise ValueError("test error")
            mock_session.rollback.assert_called_once()
            mock_session.commit.assert_not_called()
            mock_session.close.assert_called_once()
        finally:
            session_mod.engine = None
            session_mod.SessionLocal = None


@pytest.mark.unit
class TestInitDb:
    """Tests for app.database.session.init_db()."""

    def _reset_session(self):
        import app.database.session as session_mod

        session_mod.engine = None
        session_mod.SessionLocal = None

    def test_raises_when_no_database_url(self):
        """init_db raises RuntimeError when DATABASE_URL is empty."""
        import app.database.session as session_mod

        self._reset_session()
        try:
            with patch("app.database.session.get_database_url", return_value=""):
                with pytest.raises(RuntimeError, match="not configured"):
                    session_mod.init_db()
        finally:
            self._reset_session()

    def test_completes_on_success(self):
        """init_db creates tables when connection succeeds."""
        import app.database.session as session_mod

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = Mock(return_value=False)
        session_mod.engine = mock_engine
        session_mod.SessionLocal = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value="postgresql://user:pass@localhost/db",
                ),
                patch("app.database.session.is_transaction_pooler", return_value=False),
                patch("app.database.base.Base.metadata") as mock_meta,
            ):
                session_mod.init_db()
            mock_meta.create_all.assert_called_once()
        finally:
            self._reset_session()

    def test_propagates_error_on_begin_failure(self):
        """init_db propagates when engine.begin raises."""
        from sqlalchemy.exc import SQLAlchemyError

        import app.database.session as session_mod

        mock_engine = MagicMock()
        mock_engine.begin.side_effect = SQLAlchemyError("connection failed")
        session_mod.engine = mock_engine
        session_mod.SessionLocal = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value="postgresql://user:pass@localhost/db",
                ),
                patch("app.database.session.is_transaction_pooler", return_value=False),
            ):
                with pytest.raises(SQLAlchemyError):
                    session_mod.init_db()
        finally:
            self._reset_session()


@pytest.mark.unit
class TestCheckDbHealth:
    """Tests for app.database.session.check_db_health()."""

    def test_returns_false_when_engine_none(self):
        """check_db_health returns False when engine is None."""
        import app.database.session as session_mod

        original = session_mod.engine
        session_mod.engine = None
        try:
            result = session_mod.check_db_health()
            assert result is False
        finally:
            session_mod.engine = original

    def test_returns_true_when_healthy(self):
        """check_db_health returns True when connection succeeds."""
        import app.database.session as session_mod

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=False)
        mock_engine.connect.return_value = mock_conn

        original = session_mod.engine
        session_mod.engine = mock_engine
        try:
            result = session_mod.check_db_health()
            assert result is True
        finally:
            session_mod.engine = original

    def test_returns_false_on_error(self):
        """check_db_health returns False when connect raises SQLAlchemyError."""
        from sqlalchemy.exc import SQLAlchemyError

        import app.database.session as session_mod

        mock_engine = MagicMock()
        mock_engine.connect.side_effect = SQLAlchemyError("connection failed")

        original = session_mod.engine
        session_mod.engine = mock_engine
        try:
            result = session_mod.check_db_health()
            assert result is False
        finally:
            session_mod.engine = original
