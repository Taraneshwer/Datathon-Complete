"""app/db/__init__.py"""
from app.db.catalyst import (
    CatalystDBClient,
    close_catalyst,
    close_neo4j,
    close_qdrant,
    get_client,
    get_datastore,
    get_db_client,
    get_driver,
    get_neo4j,
    get_qdrant,
    init_catalyst,
    init_neo4j,
    init_qdrant,
)

__all__ = [
    "CatalystDBClient",
    # Catalyst Data Store & Unified Client
    "init_catalyst", "close_catalyst", "get_datastore", "get_db_client",
    # Neo4j Redirectors (Decommissioned)
    "init_neo4j", "close_neo4j", "get_neo4j", "get_driver",
    # Qdrant Redirectors (Decommissioned)
    "init_qdrant", "close_qdrant", "get_qdrant", "get_client",
]
