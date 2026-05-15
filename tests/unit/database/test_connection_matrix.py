"""
Test matrix: every combination of runtime x database target.

Runtime     | DB target        | Expected behaviour
------------|------------------|----------------------------------------------------
venv (host) | local postgres   | host "postgres" swapped to "localhost"; no hostaddr
venv (host) | supabase (cloud) | IPv4 hostaddr forced; sslmode=require preserved
docker      | local postgres   | host "postgres" kept as-is; no hostaddr
docker      | supabase (cloud) | IPv4 hostaddr forced; sslmode=require preserved

Each row is tested for:
  - get_database_url() URL fixup
  - get_connect_args()  → correct hostaddr / empty dict
  - init_engine()       → engine created successfully
  - init_db()           → create_all called
  - alembic env.py      → engine created with connect_args
"""

import importlib
import sys
from unittest.mock import MagicMock, patch

import pytest

LOCAL_DOCKER_URL = "postgresql://rajniti:rajniti@postgres:5432/rajniti"
LOCAL_LOCALHOST_URL = "postgresql://rajniti:rajniti@localhost:5432/rajniti"
SUPABASE_URL = (
    "postgresql://postgres:Rajniti%402026@db.ipyacfjxhvlvtprjyqsm.supabase.co"
    ":5432/postgres?sslmode=require"
)


def _reload_config():
    """Force-reload config module so env patches take effect."""
    import app.database.config as mod

    importlib.reload(mod)
    return mod


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _patch_env(env_dict):
    """Patch os.environ and os.getenv consistently."""

    def _getenv(key, default=""):
        return env_dict.get(key, default)

    return patch.dict("os.environ", env_dict, clear=False), patch(
        "os.getenv", side_effect=_getenv
    )


# ═════════════════════════════════════════════════════════════════════════════
# 1. config.py — get_database_url
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetDatabaseUrl:
    """Test URL retrieval and Docker hostname fixup."""

    def test_returns_empty_when_not_set(self):
        from app.database.config import get_database_url

        with (
            patch.dict("os.environ", {}, clear=False),
            patch("os.environ.get", return_value=None),
            patch("os.getenv", return_value=""),
        ):
            assert get_database_url() == ""

    def test_raises_when_required_and_not_set(self):
        from app.database.config import get_database_url

        with patch("os.getenv", return_value=""):
            with pytest.raises(ValueError, match="DATABASE_URL"):
                get_database_url(required=True)

    def test_venv_local_swaps_postgres_to_localhost(self):
        """venv + local: host 'postgres' → 'localhost' when DNS fails."""
        import socket as socket_mod

        from app.database.config import get_database_url

        with (
            patch(
                "os.getenv",
                side_effect=lambda k, d="": (
                    LOCAL_DOCKER_URL if k == "DATABASE_URL" else d
                ),
            ),
            patch("os.path.exists", return_value=False),
            patch(
                "app.database.config.socket.getaddrinfo",
                side_effect=socket_mod.gaierror("no DNS"),
            ),
        ):
            url = get_database_url()
            assert "localhost" in url
            assert "postgres:5432" not in url

    def test_docker_local_keeps_postgres_hostname(self):
        """docker + local: host 'postgres' kept because /.dockerenv exists."""
        from app.database.config import get_database_url

        with (
            patch(
                "os.getenv",
                side_effect=lambda k, d="": (
                    LOCAL_DOCKER_URL if k == "DATABASE_URL" else d
                ),
            ),
            patch("os.path.exists", return_value=True),
        ):
            url = get_database_url()
            assert "postgres:5432" in url

    def test_supabase_url_passed_through_unchanged(self):
        """Supabase URL has no 'postgres' hostname → returned as-is."""
        from app.database.config import get_database_url

        with patch(
            "os.getenv",
            side_effect=lambda k, d="": SUPABASE_URL if k == "DATABASE_URL" else d,
        ):
            url = get_database_url()
            assert url == SUPABASE_URL

    def test_supabase_url_preserves_sslmode(self):
        from app.database.config import get_database_url

        with patch(
            "os.getenv",
            side_effect=lambda k, d="": SUPABASE_URL if k == "DATABASE_URL" else d,
        ):
            url = get_database_url()
            assert "sslmode=require" in url

    def test_supabase_url_preserves_encoded_password(self):
        """The %40 in the password must survive (no double-encoding)."""
        from app.database.config import get_database_url

        with patch(
            "os.getenv",
            side_effect=lambda k, d="": SUPABASE_URL if k == "DATABASE_URL" else d,
        ):
            url = get_database_url()
            assert "%402026" in url


# ═════════════════════════════════════════════════════════════════════════════
# 2. config.py — get_connect_args
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetConnectArgs:
    """Test IPv4 hostaddr forcing across runtime × target combos."""

    def test_empty_when_no_database_url(self):
        from app.database.config import get_connect_args

        with patch("os.getenv", return_value=""):
            assert get_connect_args() == {}

    def test_empty_for_sqlite_url(self):
        from app.database.config import get_connect_args

        sqlite_url = "sqlite:///test.db"

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return sqlite_url
            if k == "DATABASE_SKIP_IPV4_FORCE":
                return ""
            return d

        with patch("os.getenv", side_effect=_getenv):
            assert get_connect_args() == {}

    def test_empty_when_skip_ipv4_force(self):
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_SKIP_IPV4_FORCE":
                return "1"
            if k == "DATABASE_URL":
                return SUPABASE_URL
            return d

        with patch("os.getenv", side_effect=_getenv):
            assert get_connect_args() == {}

    def test_venv_local_no_hostaddr_for_localhost(self):
        """localhost resolves to 127.0.0.1 → hostaddr=127.0.0.1."""
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return LOCAL_LOCALHOST_URL
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR"):
                return ""
            return d

        with (
            patch("os.getenv", side_effect=_getenv),
            patch(
                "app.database.config.socket.getaddrinfo",
                return_value=[(2, 1, 6, "", ("127.0.0.1", 5432))],
            ),
        ):
            args = get_connect_args()
            assert args == {"hostaddr": "127.0.0.1"}

    def test_supabase_forces_ipv4(self):
        """Supabase host must resolve to IPv4 and hostaddr gets set."""
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return SUPABASE_URL
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR"):
                return ""
            return d

        fake_ipv4 = ("3.6.80.100", 5432)
        with (
            patch("os.getenv", side_effect=_getenv),
            patch(
                "app.database.config.socket.getaddrinfo",
                return_value=[(2, 1, 6, "", fake_ipv4)],
            ),
        ):
            args = get_connect_args()
            assert args == {"hostaddr": "3.6.80.100"}

    def test_manual_hostaddr_override(self):
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return SUPABASE_URL
            if k == "DATABASE_HOSTADDR":
                return "1.2.3.4"
            if k == "DATABASE_SKIP_IPV4_FORCE":
                return ""
            return d

        with patch("os.getenv", side_effect=_getenv):
            args = get_connect_args()
            assert args == {"hostaddr": "1.2.3.4"}

    def test_returns_empty_when_dns_fails_completely(self):
        """If both getaddrinfo and gethostbyname fail, return {} (best effort)."""
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return SUPABASE_URL
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR"):
                return ""
            return d

        import socket as socket_mod

        with (
            patch("os.getenv", side_effect=_getenv),
            patch(
                "app.database.config.socket.getaddrinfo",
                side_effect=socket_mod.gaierror("no DNS"),
            ),
            patch(
                "app.database.config.socket.gethostbyname",
                side_effect=socket_mod.gaierror("no DNS"),
            ),
        ):
            args = get_connect_args()
            assert args == {}

    def test_fallback_to_gethostbyname(self):
        """When getaddrinfo(AF_INET) fails, gethostbyname is used as fallback."""
        from app.database.config import get_connect_args

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return SUPABASE_URL
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR"):
                return ""
            return d

        import socket as socket_mod

        with (
            patch("os.getenv", side_effect=_getenv),
            patch(
                "app.database.config.socket.getaddrinfo",
                side_effect=socket_mod.gaierror("fail"),
            ),
            patch("app.database.config.socket.gethostbyname", return_value="5.6.7.8"),
        ):
            args = get_connect_args()
            assert args == {"hostaddr": "5.6.7.8"}


# ═════════════════════════════════════════════════════════════════════════════
# 3. config.py — is_transaction_pooler
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestIsTransactionPooler:
    def test_port_6543(self):
        from app.database.config import is_transaction_pooler

        url = "postgresql://user:pass@host:6543/db"
        assert is_transaction_pooler(url) is True

    def test_pooler_in_host(self):
        from app.database.config import is_transaction_pooler

        url = "postgresql://user:pass@aws-0-us-east-1.pooler.supabase.com:5432/db"
        assert is_transaction_pooler(url) is True

    def test_direct_url(self):
        from app.database.config import is_transaction_pooler

        url = "postgresql://user:pass@db.xyz.supabase.co:5432/db"
        assert is_transaction_pooler(url) is False

    def test_empty(self):
        from app.database.config import is_transaction_pooler

        assert is_transaction_pooler("") is False


# ═════════════════════════════════════════════════════════════════════════════
# 4. session.py — init_engine
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInitEngine:
    """Test engine creation across combos."""

    def _reset_session(self):
        import app.database.session as m

        m.engine = None
        m.SessionLocal = None

    def test_returns_none_when_no_url(self):
        import app.database.session as m

        self._reset_session()
        try:
            with patch("app.database.session.get_database_url", return_value=""):
                assert m.init_engine() is None
        finally:
            self._reset_session()

    def test_returns_none_when_url_raises(self):
        import app.database.session as m

        self._reset_session()
        try:
            with patch("app.database.session.get_database_url", side_effect=ValueError):
                assert m.init_engine() is None
        finally:
            self._reset_session()

    def test_creates_engine_with_local_url(self):
        import app.database.session as m

        self._reset_session()
        mock_engine = MagicMock()
        mock_sf = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value=LOCAL_LOCALHOST_URL,
                ),
                patch(
                    "app.database.session.get_connect_args",
                    return_value={"hostaddr": "127.0.0.1"},
                ),
                patch("app.database.session.get_echo_mode", return_value=False),
                patch(
                    "app.database.session.create_engine", return_value=mock_engine
                ) as ce,
                patch("app.database.session.sessionmaker", return_value=mock_sf),
            ):
                result = m.init_engine()
                assert result is mock_engine
                ce.assert_called_once()
                call_kwargs = ce.call_args
                assert call_kwargs[1]["connect_args"] == {"hostaddr": "127.0.0.1"}
        finally:
            self._reset_session()

    def test_creates_engine_with_supabase_url(self):
        import app.database.session as m

        self._reset_session()
        mock_engine = MagicMock()
        mock_sf = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url", return_value=SUPABASE_URL
                ),
                patch(
                    "app.database.session.get_connect_args",
                    return_value={"hostaddr": "3.6.80.100"},
                ),
                patch("app.database.session.get_echo_mode", return_value=False),
                patch(
                    "app.database.session.create_engine", return_value=mock_engine
                ) as ce,
                patch("app.database.session.sessionmaker", return_value=mock_sf),
            ):
                result = m.init_engine()
                assert result is mock_engine
                call_kwargs = ce.call_args
                assert call_kwargs[1]["connect_args"] == {"hostaddr": "3.6.80.100"}
        finally:
            self._reset_session()

    def test_idempotent(self):
        import app.database.session as m

        m.engine = MagicMock()
        m.SessionLocal = MagicMock()
        try:
            with patch("app.database.session.get_database_url") as gu:
                result = m.init_engine()
                gu.assert_not_called()
                assert result is m.engine
        finally:
            self._reset_session()

    def test_returns_none_on_engine_creation_failure(self):
        import app.database.session as m

        self._reset_session()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value=LOCAL_LOCALHOST_URL,
                ),
                patch("app.database.session.get_connect_args", return_value={}),
                patch("app.database.session.get_echo_mode", return_value=False),
                patch(
                    "app.database.session.create_engine", side_effect=Exception("boom")
                ),
            ):
                assert m.init_engine() is None
                assert m.engine is None
                assert m.SessionLocal is None
        finally:
            self._reset_session()


# ═════════════════════════════════════════════════════════════════════════════
# 5. session.py — init_db
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestInitDb:
    """Test that init_db calls create_all correctly."""

    def _reset_session(self):
        import app.database.session as m

        m.engine = None
        m.SessionLocal = None

    def test_raises_when_no_engine(self):
        import app.database.session as m

        self._reset_session()
        try:
            with patch("app.database.session.get_database_url", return_value=""):
                with pytest.raises(RuntimeError, match="not configured"):
                    m.init_db()
        finally:
            self._reset_session()

    def test_calls_create_all_on_success(self):
        import app.database.session as m

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)
        m.engine = mock_engine
        m.SessionLocal = MagicMock()
        try:
            with (
                patch(
                    "app.database.session.get_database_url",
                    return_value=LOCAL_LOCALHOST_URL,
                ),
                patch("app.database.session.is_transaction_pooler", return_value=False),
                patch("app.database.base.Base.metadata") as mock_meta,
            ):
                m.init_db()
                mock_meta.create_all.assert_called_once()
        finally:
            self._reset_session()

    def test_warns_on_transaction_pooler(self):
        import app.database.session as m

        mock_engine = MagicMock()
        mock_conn = MagicMock()
        mock_engine.begin.return_value.__enter__ = MagicMock(return_value=mock_conn)
        mock_engine.begin.return_value.__exit__ = MagicMock(return_value=False)
        m.engine = mock_engine
        m.SessionLocal = MagicMock()
        pooler_url = "postgresql://u:p@pooler.supabase.com:6543/db"
        try:
            with (
                patch("app.database.session.get_database_url", return_value=pooler_url),
                patch("app.database.session.is_transaction_pooler", return_value=True),
                patch("app.database.base.Base.metadata"),
                patch("app.database.session.logger") as mock_logger,
            ):
                m.init_db()
                mock_logger.warning.assert_called()
                assert "pooler" in mock_logger.warning.call_args[0][0].lower()
        finally:
            self._reset_session()


# ═════════════════════════════════════════════════════════════════════════════
# 6. Full matrix: venv/docker × local/supabase — init_engine smoke test
# ═════════════════════════════════════════════════════════════════════════════

MATRIX = [
    # (label, database_url, is_docker, expected_url_contains, expected_hostaddr_key)
    ("venv+local", LOCAL_DOCKER_URL, False, "localhost", True),
    ("venv+supabase", SUPABASE_URL, False, "supabase.co", True),
    ("docker+local", LOCAL_DOCKER_URL, True, "postgres:5432", False),
    ("docker+supabase", SUPABASE_URL, True, "supabase.co", True),
]


@pytest.mark.unit
@pytest.mark.parametrize(
    "label,database_url,is_docker,url_substr,expect_hostaddr", MATRIX
)
class TestConnectionMatrix:
    """End-to-end config→engine creation for each combo."""

    def test_url_resolution(
        self, label, database_url, is_docker, url_substr, expect_hostaddr
    ):
        import socket as socket_mod

        from app.database.config import get_database_url

        def _exists(p):
            if p == "/.dockerenv":
                return is_docker
            return False

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return database_url
            return d

        def _getaddrinfo(host, port, *a, **kw):
            if host == "postgres" and not is_docker:
                raise socket_mod.gaierror("no DNS for 'postgres' on host")
            return [(2, 1, 6, "", ("127.0.0.1", port or 5432))]

        with (
            patch("os.getenv", side_effect=_getenv),
            patch("os.path.exists", side_effect=_exists),
            patch("app.database.config.socket.getaddrinfo", side_effect=_getaddrinfo),
        ):
            url = get_database_url()
            assert url_substr in url, f"[{label}] expected '{url_substr}' in '{url}'"

    def test_connect_args(
        self, label, database_url, is_docker, url_substr, expect_hostaddr
    ):
        import socket as socket_mod

        from app.database.config import get_connect_args

        def _exists(p):
            if p == "/.dockerenv":
                return is_docker
            return False

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return database_url
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR"):
                return ""
            return d

        def _getaddrinfo(host, port, *a, **kw):
            if host == "postgres":
                if not is_docker:
                    raise socket_mod.gaierror("no DNS")
                return [(2, 1, 6, "", ("172.18.0.2", 5432))]
            return [(2, 1, 6, "", ("3.6.80.100", 5432))]

        with (
            patch("os.getenv", side_effect=_getenv),
            patch("os.path.exists", side_effect=_exists),
            patch("app.database.config.socket.getaddrinfo", side_effect=_getaddrinfo),
            patch(
                "app.database.config.socket.gethostbyname", return_value="3.6.80.100"
            ),
        ):
            args = get_connect_args()
            if expect_hostaddr:
                assert "hostaddr" in args, f"[{label}] expected hostaddr in {args}"

    def test_engine_creation(
        self, label, database_url, is_docker, url_substr, expect_hostaddr
    ):
        """Full pipeline: env → config → engine."""
        import socket as socket_mod

        import app.database.session as m

        m.engine = None
        m.SessionLocal = None

        mock_engine = MagicMock()
        mock_sf = MagicMock()

        def _getenv(k, d=""):
            if k == "DATABASE_URL":
                return database_url
            if k in ("DATABASE_SKIP_IPV4_FORCE", "DATABASE_HOSTADDR", "DB_ECHO"):
                return ""
            return d

        def _exists(p):
            if p == "/.dockerenv":
                return is_docker
            return False

        def _getaddrinfo(host, port, *a, **kw):
            if host == "postgres" and not is_docker:
                raise socket_mod.gaierror("no DNS")
            return [(2, 1, 6, "", ("127.0.0.1", port or 5432))]

        try:
            with (
                patch("os.getenv", side_effect=_getenv),
                patch("os.path.exists", side_effect=_exists),
                patch(
                    "app.database.config.socket.getaddrinfo", side_effect=_getaddrinfo
                ),
                patch(
                    "app.database.config.socket.gethostbyname", return_value="127.0.0.1"
                ),
                patch(
                    "app.database.session.create_engine", return_value=mock_engine
                ) as ce,
                patch("app.database.session.sessionmaker", return_value=mock_sf),
            ):
                result = m.init_engine()
                assert result is mock_engine, f"[{label}] init_engine returned None"
                ce.assert_called_once()
        finally:
            m.engine = None
            m.SessionLocal = None


# ═════════════════════════════════════════════════════════════════════════════
# 7. Alembic env.py — no ConfigParser interpolation bug
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestAlembicEnv:
    """Verify Alembic env.py doesn't trigger ConfigParser %-interpolation."""

    def test_url_with_percent_does_not_crash(self):
        """URLs with %40 must not raise configparser.InterpolationSyntaxError."""
        from app.database.config import get_database_url

        with patch(
            "os.getenv",
            side_effect=lambda k, d="": SUPABASE_URL if k == "DATABASE_URL" else d,
        ):
            url = get_database_url()
            assert "%40" in url

    def test_alembic_env_uses_create_engine_not_engine_from_config(self):
        """alembic/env.py must use create_engine directly."""
        import ast
        from pathlib import Path

        env_path = Path(__file__).resolve().parents[3] / "alembic" / "env.py"
        source = env_path.read_text()

        assert "create_engine" in source
        assert "engine_from_config" not in source
        assert "config.set_main_option" not in source


# ═════════════════════════════════════════════════════════════════════════════
# 8. base.py — get_db_session
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestGetDbSession:
    def test_raises_when_no_session_factory(self):
        import app.database.session as m
        from app.database.base import get_db_session

        m.engine = None
        m.SessionLocal = None
        try:
            with patch("app.database.session.init_engine"):
                with pytest.raises(RuntimeError, match="not configured"):
                    with get_db_session():
                        pass
        finally:
            m.engine = None
            m.SessionLocal = None

    def test_commits_on_success(self):
        import app.database.session as m
        from app.database.base import get_db_session

        mock_session = MagicMock()
        mock_sf = MagicMock(return_value=mock_session)
        m.engine = MagicMock()
        m.SessionLocal = mock_sf
        try:
            with get_db_session() as s:
                assert s is mock_session
            mock_session.commit.assert_called_once()
            mock_session.close.assert_called_once()
        finally:
            m.engine = None
            m.SessionLocal = None

    def test_rollback_on_error(self):
        import app.database.session as m
        from app.database.base import get_db_session

        mock_session = MagicMock()
        mock_sf = MagicMock(return_value=mock_session)
        m.engine = MagicMock()
        m.SessionLocal = mock_sf
        try:
            with pytest.raises(ValueError):
                with get_db_session():
                    raise ValueError("boom")
            mock_session.rollback.assert_called_once()
            mock_session.commit.assert_not_called()
        finally:
            m.engine = None
            m.SessionLocal = None


# ═════════════════════════════════════════════════════════════════════════════
# 9. resolve_ipv4 helper
# ═════════════════════════════════════════════════════════════════════════════


@pytest.mark.unit
class TestResolveIpv4:
    def test_returns_ipv4_from_getaddrinfo(self):
        from app.database.config import resolve_ipv4

        with patch(
            "app.database.config.socket.getaddrinfo",
            return_value=[(2, 1, 6, "", ("10.0.0.1", 5432))],
        ):
            assert resolve_ipv4("example.com", 5432) == "10.0.0.1"

    def test_falls_back_to_gethostbyname(self):
        import socket as socket_mod

        from app.database.config import resolve_ipv4

        with (
            patch(
                "app.database.config.socket.getaddrinfo",
                side_effect=socket_mod.gaierror,
            ),
            patch("app.database.config.socket.gethostbyname", return_value="10.0.0.2"),
        ):
            assert resolve_ipv4("example.com", 5432) == "10.0.0.2"

    def test_returns_empty_on_total_failure(self):
        import socket as socket_mod

        from app.database.config import resolve_ipv4

        with (
            patch(
                "app.database.config.socket.getaddrinfo",
                side_effect=socket_mod.gaierror,
            ),
            patch(
                "app.database.config.socket.gethostbyname",
                side_effect=socket_mod.gaierror,
            ),
        ):
            assert resolve_ipv4("example.com", 5432) == ""
