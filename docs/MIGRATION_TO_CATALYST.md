# Migration Guide: PostgreSQL to Zoho Catalyst Data Store

This document outlines the architectural changes, instructions, and considerations for migrating the AI Crime Intelligence Platform's primary persistence layer from PostgreSQL to Zoho Catalyst AppSail & Data Store.

## 1. Architectural Changes

The platform has successfully decoupled all relational persistence logic from SQLAlchemy and SQLModel, replacing it with the native **Zoho Catalyst SDK**.

### Before: PostgreSQL & ORM
- **Models**: Built using `sqlmodel.SQLModel` with embedded SQLAlchemy dialects (e.g., `PG_UUID`, `JSONB`).
- **Data Access**: Direct execution of raw SQL queries and ORM mappings using `AsyncSession`.
- **Primary Keys**: Application-generated `uuid.UUID` used as native primary keys.

### After: Catalyst Data Store & Repositories
- **Models**: Refactored to pure Pydantic `BaseModel`s. 
- **Data Access**: Introduced the **Repository Pattern** (`app.repositories`). Repositories completely abstract the Catalyst Data Store interactions via ZCQL and direct table operations.
- **Primary Keys**: Catalyst uses an internal `ROWID` as the native Primary Key. To prevent breaking external APIs and foreign key links in Neo4j/Qdrant, we now store the `uuid.UUID` in an `id` column. Lookups (`get()`) query the `id` column, while updates/deletes resolve the `ROWID` transparently within the Repository layer.

## 2. Configuration Updates

Your `backend/.env` now uses the following Catalyst variables instead of `POSTGRES_DSN`:
```env
# Zoho Catalyst Data Store
ZOHO_CATALYST_PROJECT_ID="your_project_id"
ZOHO_CATALYST_ENVIRONMENT="Development"
ZOHO_CATALYST_CLIENT_ID="your_client_id"
ZOHO_CATALYST_CLIENT_SECRET="your_client_secret"
```

## 3. Schema Generation

Because Catalyst Data Store does not support Alembic migrations, we have built a custom schema generator. 

Whenever you update the Pydantic models in `app.models.fir`, run the generator script to create the necessary JSON schema, which you can push using the Catalyst CLI.

```bash
cd backend
python scripts/catalyst_schema_generator.py
```
This will output `catalyst_schema.json` with the exact configurations needed to deploy the tables to Catalyst.

## 4. Rollback Strategy
If you ever need to roll back to PostgreSQL:
1. Reinstall `sqlmodel`, `sqlalchemy`, `asyncpg`, `alembic`.
2. Convert `app/models/fir.py` classes back to inherit from `SQLModel (table=True)`.
3. In `app.dependencies`, swap the injected Repositories for the `AsyncSession` dependency.
4. Replace repository calls in Routers/Services with SQLAlchemy `select()`, `add()`, `commit()` logic.

## 5. Next Steps for Deployment
- **Ensure Catalyst CLI is installed**: `npm install -g zcatalyst-cli`
- **Login**: `catalyst login`
- **Initialize Project**: `catalyst init` (Select AppSail & Data Store)
- **Deploy**: Push the Data Store schema and AppSail container.
