"""
backend/scripts/catalyst_schema_generator.py

This script reads the Pydantic models in `app.models.fir` and generates the
equivalent Zoho Catalyst Data Store schema. It can optionally execute the
table creation directly via the Catalyst SDK if configured, or output the
required schema definitions for the Catalyst CLI.
"""
import sys
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from typing import Any, Union, get_args, get_origin

from pydantic import BaseModel

from app.models.fir import AuditTrail, BlockchainRecord, Case, EvidenceItem, Officer, SystemAlert


def map_type_to_catalyst(py_type: Any) -> str:
    """Map python types to Catalyst Data Store column types."""
    # Handle Optional[X] / X | None
    origin = get_origin(py_type)
    if origin is Union:
        args = get_args(py_type)
        if type(None) in args:
            py_type = [a for a in args if a is not type(None)][0]

    if py_type == str:
        return "varchar"
    if py_type == int:
        return "bigint"
    if py_type == float:
        return "double"
    if py_type == bool:
        return "boolean"
    if hasattr(py_type, "__name__"):
        name = py_type.__name__
        if name == "UUID":
            return "varchar"
        if name == "datetime":
            return "datetime"
        if name == "date":
            return "date"
        
    # Enums, dicts, lists become varchars (JSON encoded or string values)
    return "varchar"

def generate_schema(models: list[tuple[str, type[BaseModel]]]) -> dict[str, Any]:
    schema = {}
    for table_name, model in models:
        columns = []
        for field_name, field_info in model.model_fields.items():
            col_type = map_type_to_catalyst(field_info.annotation)
            
            # id is always our application primary key but not necessarily catalyst PK (ROWID is)
            is_unique = (field_name == "id" or field_name == "badge_number" or field_name == "fir_number")
            is_mandatory = field_info.is_required()
            
            columns.append({
                "column_name": field_name,
                "data_type": col_type,
                "is_mandatory": is_mandatory,
                "is_unique": is_unique,
                "max_length": 2000 if col_type == "varchar" else None
            })
        
        schema[table_name] = columns
    return schema

def main():
    models = [
        ("officers", Officer),
        ("cases", Case),
        ("evidence_items", EvidenceItem),
        ("system_alerts", SystemAlert),
        ("audit_trails", AuditTrail),
        ("blockchain_records", BlockchainRecord),
    ]

    schema = generate_schema(models)
    
    output_file = Path(__file__).parent / "catalyst_schema.json"
    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)
        
    print(f"[SUCCESS] Schema successfully generated at {output_file}")
    print("[INFO] To apply this schema automatically, use Catalyst CLI or Web Console.")
    print("$ catalyst datastore:push")
    
if __name__ == "__main__":
    main()
