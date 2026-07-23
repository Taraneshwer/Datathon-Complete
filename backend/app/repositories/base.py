"""
app/repositories/base.py
─────────────────────────────────────────────────────────────────────────────
Base repository for Zoho Catalyst Data Store operations.
Provides generic CRUD and search methods using Catalyst ZCQL and Data Store APIs.
─────────────────────────────────────────────────────────────────────────────
"""
import json
import uuid
from typing import Any, Generic, TypeVar, List

import zcatalyst_sdk
from pydantic import BaseModel

from app.db.catalyst import get_datastore

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    """
    Abstract generic base repository for Catalyst Data Store.
    """
    def __init__(self, model_class: type[T], table_name: str):
        self.model_class = model_class
        self.table_name = table_name

    def _get_datastore(self) -> Any:
        return get_datastore()

    def _get_zcql(self) -> Any:
        # Depending on SDK, you can execute ZCQL via ZCQL instance
        return zcatalyst_sdk.ZCQL.get_instance()

    def _parse_row(self, row: dict[str, Any]) -> T:
        """Parse a Catalyst row dict into the Pydantic model."""
        # Catalyst returns rows nested like: {'TableName': {'column': 'value'}}
        data = row.get(self.table_name, row)
        
        # Handle stringified JSON fields, UUIDs, and datetimes gracefully
        parsed_data = {}
        for k, v in data.items():
            if isinstance(v, str) and (v.startswith('{') or v.startswith('[')):
                try:
                    v = json.loads(v)
                except Exception:
                    pass
            parsed_data[k] = v
            
        return self.model_class.model_validate(parsed_data)

    def _serialize_model(self, obj: T) -> dict[str, Any]:
        """Convert Pydantic model to a dict suitable for Catalyst Data Store."""
        data = obj.model_dump(mode="json", exclude_none=True)
        # Convert dict/lists to string if required by Catalyst
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                data[k] = json.dumps(v)
        return data

    async def get(self, id: uuid.UUID | str) -> T | None:
        """Fetch a single record by its application-level ID."""
        id_str = str(id)
        query = f"SELECT * FROM {self.table_name} WHERE id = '{id_str}'"
        try:
            result = self._get_zcql().execute_query(query)
            if not result:
                return None
            return self._parse_row(result[0])
        except Exception:
            return None

    async def create(self, obj: T) -> T:
        """Insert a new record into Data Store."""
        table = self._get_datastore().table(self.table_name)
        data = self._serialize_model(obj)
        table.insert_row(data)
        return obj

    async def update(self, obj: T) -> T:
        """Update an existing record in Data Store."""
        id_str = str(obj.id)
        # To update, we usually need the ROWID. We can fetch it first via ZCQL.
        query = f"SELECT ROWID FROM {self.table_name} WHERE id = '{id_str}'"
        result = self._get_zcql().execute_query(query)
        if not result:
            raise ValueError(f"Record with id {id_str} not found in {self.table_name}")
        
        row_id = result[0][self.table_name]["ROWID"]
        data = self._serialize_model(obj)
        data["ROWID"] = row_id
        
        table = self._get_datastore().table(self.table_name)
        table.update_row(data)
        return obj

    async def delete(self, id: uuid.UUID | str) -> bool:
        """Delete a record by its application-level ID."""
        id_str = str(id)
        query = f"SELECT ROWID FROM {self.table_name} WHERE id = '{id_str}'"
        result = self._get_zcql().execute_query(query)
        if not result:
            return False
            
        row_id = result[0][self.table_name]["ROWID"]
        table = self._get_datastore().table(self.table_name)
        table.delete_row(row_id)
        return True

    async def list(self, limit: int = 100, offset: int = 0) -> List[T]:
        """List all records."""
        query = f"SELECT * FROM {self.table_name} LIMIT {limit} OFFSET {offset}"
        try:
            result = self._get_zcql().execute_query(query)
            return [self._parse_row(row) for row in result]
        except Exception:
            return []

    async def search(self, where_clause: str) -> List[T]:
        """Execute a raw ZCQL search query (WHERE clause)."""
        query = f"SELECT * FROM {self.table_name} WHERE {where_clause}"
        try:
            result = self._get_zcql().execute_query(query)
            return [self._parse_row(row) for row in result]
        except Exception:
            return []

    async def execute_query(self, query: str) -> List[dict[str, Any]]:
        """Execute a raw ZCQL query and return raw dict results."""
        try:
            result = self._get_zcql().execute_query(query)
            return list(result) if result else []
        except Exception:
            return []
