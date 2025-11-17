"""
Environment variable checker for Rajniti application.

Logs missing and present environment variables on server startup.
"""
import logging
import os
from typing import Dict, List

logger = logging.getLogger(__name__)


def check_environment_variables() -> None:
    """
    Check and log environment variables status on server startup.

    Logs:
    - Missing optional environment variables
    - Present environment variables (without exposing sensitive values)
    """
    # Define environment variables with their properties
    env_vars: Dict[str, Dict[str, any]] = {
        # Required/Important variables (no defaults or sensitive defaults)
        "DATABASE_URL": {
            "required": False,
            "description": "Database connection string",
        },
        "SECRET_KEY": {
            "required": False,
            "description": "Flask secret key (using default in dev)",
        },
        "PERPLEXITY_API_KEY": {
            "required": False,
            "description": "Perplexity AI API key for search features",
        },
        # Optional configuration variables with defaults
        "FLASK_ENV": {
            "required": False,
            "description": "Flask environment",
            "default": "development",
        },
        "FLASK_HOST": {
            "required": False,
            "description": "Server host",
            "default": "0.0.0.0",
        },
        "FLASK_PORT": {
            "required": False,
            "description": "Server port",
            "default": "8080",
        },
        "FLASK_DEBUG": {
            "required": False,
            "description": "Debug mode",
            "default": "True",
        },
        "DB_ECHO": {
            "required": False,
            "description": "SQL query logging",
            "default": "false",
        },
    }

    missing_vars: List[str] = []
    present_vars: List[str] = []

    logger.info("=" * 60)
    logger.info("Environment Variables Check")
    logger.info("=" * 60)

    for var_name, var_info in env_vars.items():
        value = os.getenv(var_name)

        if value is None:
            missing_vars.append(var_name)
            default = var_info.get("default")
            if default:
                logger.info(
                    f"❌ {var_name}: Not set (using default: {default}) - "
                    f"{var_info['description']}"
                )
            else:
                logger.warning(f"⚠️  {var_name}: Not set - {var_info['description']}")
        else:
            present_vars.append(var_name)
            # Don't log the actual value for security
            logger.info(f"✓ {var_name}: Set - {var_info['description']}")

    logger.info("=" * 60)
    logger.info(f"Summary: {len(present_vars)} set, {len(missing_vars)} missing")
    logger.info("=" * 60)

    if missing_vars:
        logger.info("Missing variables: " + ", ".join(missing_vars))
        logger.info("Tip: Copy .env.example to .env and configure required variables")
