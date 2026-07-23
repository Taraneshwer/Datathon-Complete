"""
app/db/catalyst.py
─────────────────────────────────────────────────────────────────────────────
Zoho Catalyst Data Store connection manager.
Exposes a singleton client for Data Store access.
─────────────────────────────────────────────────────────────────────────────
"""
import logging

import zcatalyst_sdk

from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level singletons
_catalyst_app = None
_datastore = None

async def init_catalyst() -> None:
    """
    Initialise the Zoho Catalyst SDK and Data Store client.
    """
    global _catalyst_app, _datastore
    settings = get_settings()

    try:
        # Initialize the catalyst app instance.
        _catalyst_app = zcatalyst_sdk.initialize()
        _datastore = _catalyst_app.datastore()
        logger.info("Zoho Catalyst Data Store connected successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Zoho Catalyst: {e}")
        if settings.environment == "development":
            logger.warning("Running in development mode without Catalyst context. Data Store calls will fail.")
        else:
            raise


async def close_catalyst() -> None:
    """Clean up any resources (mostly a placeholder for compatibility)."""
    global _catalyst_app, _datastore
    _catalyst_app = None
    _datastore = None
    logger.info("Zoho Catalyst resources cleaned up.")


from typing import Any, AsyncGenerator

def get_datastore() -> Any:
    """
    Synchronous dependency yielding a Catalyst Data Store client.
    """
    if _datastore is None:
        raise RuntimeError("Catalyst Data Store not initialised. Call init_catalyst() first.")
    return _datastore


async def get_db_client() -> AsyncGenerator[Any, None]:
    """
    FastAPI async dependency yielding a Catalyst Data Store client.
    """
    yield get_datastore()
