"""Service-token authentication for internal/automation callers.

The token is read from ``RAJNITI_SERVICE_TOKEN``. Callers present it either in the
``X-Service-Token`` header or as a bearer value in the ``Authorization`` header.

When the variable is unset, service-token routes are disabled (503) rather than
open — an unconfigured deployment must never expose write endpoints.
"""

from __future__ import annotations

import hmac
import logging
import os
from functools import wraps
from typing import Optional

from flask import jsonify, request

logger = logging.getLogger(__name__)

SERVICE_TOKEN_ENV = "RAJNITI_SERVICE_TOKEN"


def _configured_token() -> Optional[str]:
    token = (os.getenv(SERVICE_TOKEN_ENV) or "").strip()
    return token or None


def _presented_token() -> Optional[str]:
    token = (request.headers.get("X-Service-Token") or "").strip()
    if token:
        return token

    auth = (request.headers.get("Authorization") or "").strip()
    if auth.lower().startswith("bearer "):
        return auth[7:].strip() or None

    return None


def has_valid_service_token() -> bool:
    """True when the request carries the configured service token."""
    expected = _configured_token()
    presented = _presented_token()

    if not expected or not presented:
        return False

    return hmac.compare_digest(expected, presented)


def require_service_token(view):
    """Reject requests that do not carry a valid service token."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if _configured_token() is None:
            logger.error("%s is not configured; refusing request.", SERVICE_TOKEN_ENV)
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Service token authentication is not configured",
                        "code": "SERVICE_TOKEN_NOT_CONFIGURED",
                    }
                ),
                503,
            )

        if not has_valid_service_token():
            return (
                jsonify(
                    {
                        "success": False,
                        "error": "Invalid or missing service token",
                        "code": "SERVICE_TOKEN_INVALID",
                    }
                ),
                401,
            )

        return view(*args, **kwargs)

    return wrapper
