"""
app/db/catalyst.py
─────────────────────────────────────────────────────────────────────────────
100% Zoho Catalyst Cloud connection manager & unified serverless SDK client.
Replaces legacy Neo4j, Qdrant, and MongoDB drivers with native Data Store,
NoSQL, Cache, Stratus, QuickML, and Zia AI service connectors.
─────────────────────────────────────────────────────────────────────────────
"""
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional
import zcatalyst_sdk
from app.config import get_settings

logger = logging.getLogger(__name__)

# Module-level singletons
_catalyst_app = None
_datastore = None

class CatalystDBClient:
    """
    Unified 100% Zoho Catalyst Cloud Client replacing Neo4j, Qdrant, and MongoDB drivers.
    Provides connection management for Data Store SQL, NoSQL, Cache, Stratus, QuickML, and Zia.
    """
    def __init__(self, app_instance: Any = None):
        self.app = app_instance or _catalyst_app

    def get_table_service(self, table_name: str) -> Any:
        """Returns Catalyst Data Store SQL Table service instance."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.table(table_name)

    def get_nosql_service(self, collection_name: str) -> Any:
        """Returns Catalyst NoSQL Document collection service instance."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.nosql(collection_name)

    def get_cache_service(self) -> Any:
        """Returns Catalyst Cache Redis-compatible service instance."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.cache()

    def get_stratus_bucket(self, bucket_name: str = "rainfall-evidence-archive") -> Any:
        """Returns Catalyst Stratus Object Storage bucket service instance."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.filestore().bucket(bucket_name)

    def get_quickml_service(self) -> Any:
        """Returns Catalyst QuickML AI service instance (LLM, Embeddings, Knowledge Base)."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.quickml()

    def get_zia_service(self) -> Any:
        """Returns Catalyst Zia AI service instance (OCR, Vision, Speech, Translation)."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        return self.app.zia()

    def execute_sql_query(self, sql_query: str) -> List[Dict[str, Any]]:
        """Executes raw SQL query against Catalyst Data Store tables."""
        if not self.app:
            self.app = zcatalyst_sdk.initialize()
        zcql = self.app.zcql()
        return zcql.execute_query(sql_query)


async def init_catalyst() -> None:
    """
    Initialise the Zoho Catalyst SDK and unified cloud services.
    """
    global _catalyst_app, _datastore
    settings = get_settings()
    try:
        _catalyst_app = zcatalyst_sdk.initialize()
        _datastore = _catalyst_app.datastore() if hasattr(_catalyst_app, "datastore") else _catalyst_app
        logger.info("Zoho Catalyst 100% Native Cloud Services connected successfully.")
    except Exception as e:
        logger.error(f"Failed to initialize Zoho Catalyst: {e}")
        if settings.environment == "development":
            logger.warning("Running in development mode without Catalyst context. Cloud SDK calls will fail over.")
            _catalyst_app = zcatalyst_sdk.initialize() if hasattr(zcatalyst_sdk, "initialize") else None
        else:
            raise

async def close_catalyst() -> None:
    """Clean up cloud SDK resources."""
    global _catalyst_app, _datastore
    _catalyst_app = None
    _datastore = None
    logger.info("Zoho Catalyst resources cleaned up.")

# ── Backwards-Compatible Redirectors for Decommissioned Databases ───────────
async def init_neo4j() -> None:
    logger.info("Neo4j decommissioned in 100% Catalyst architecture. Redirecting to Catalyst Data Store Graph Engine.")

async def close_neo4j() -> None:
    pass

def get_neo4j() -> Any:
    return CatalystDBClient(_catalyst_app)

def get_driver() -> Any:
    return CatalystDBClient(_catalyst_app)

async def init_qdrant() -> None:
    logger.info("Qdrant decommissioned in 100% Catalyst architecture. Redirecting to Catalyst QuickML Knowledge Base.")

async def close_qdrant() -> None:
    pass

def get_qdrant() -> Any:
    return CatalystDBClient(_catalyst_app)

def get_client() -> Any:
    return CatalystDBClient(_catalyst_app)

# ── Core Dependencies ───────────────────────────────────────────────────────
def get_datastore() -> Any:
    """Synchronous dependency yielding a Catalyst Data Store client."""
    if _datastore is None and _catalyst_app is None:
        try:
            return zcatalyst_sdk.initialize()
        except Exception:
            return None
    return _datastore or _catalyst_app

async def get_db_client() -> AsyncGenerator[CatalystDBClient, None]:
    """FastAPI async dependency yielding unified CatalystDBClient."""
    yield CatalystDBClient(_catalyst_app)
