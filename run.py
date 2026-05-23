"""
Development server entry point for the Rajniti application.
"""

import logging
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

from app import create_app  # noqa: E402
from app.core.env_checker import check_environment_variables  # noqa: E402


def main():
    """Main entry point for the development server."""
    # Setup basic logging first
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    logger = logging.getLogger("rajniti.server")

    # Check environment variables on startup
    check_environment_variables()

    # Get environment
    env = os.getenv("FLASK_ENV", "development")

    # Create app with specified environment
    app = create_app()

    # Server configuration
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    port = int(os.getenv("FLASK_PORT", "8000"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    logger.info(f"Starting Rajniti development server on {host}:{port}")
    logger.info(f"Debug mode: {debug}, Environment: {env}")

    # Run the application
    app.run(host=host, port=port, debug=debug, threaded=True)


if __name__ == "__main__":
    main()
