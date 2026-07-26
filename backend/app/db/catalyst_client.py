"""app/db/catalyst_client.py - Re-export of unified CatalystDBClient"""
from app.db.catalyst import CatalystDBClient, get_db_client, get_datastore, init_catalyst, close_catalyst

# Singleton helper
_client_instance = None

def get_db() -> CatalystDBClient:
    global _client_instance
    if _client_instance is None:
        _client_instance = CatalystDBClient()
    return _client_instance

__all__ = ["CatalystDBClient", "get_db", "get_db_client", "get_datastore", "init_catalyst", "close_catalyst"]
