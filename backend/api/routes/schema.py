"""
Database Schema Management API Routes

Provides REST endpoints for managing database schemas and migrations.
"""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from backend.api.models import APIResponse
from backend.core.logging import get_logger
from backend.services.schema_management_service import ColumnType, ConstraintType, IndexType, schema_management_service

router = APIRouter(prefix="/schema", tags=["Schema Management"])
logger = get_logger(__name__)


class ColumnCreate(BaseModel):
    """Column creation request model."""
    name: str
    type: str
    nullable: bool | None = True
    default_value: str | None = None
    primary_key: bool | None = False
    unique: bool | None = False
    foreign_key: dict[str, str] | None = None


class ConstraintCreate(BaseModel):
    """Constraint creation request model."""
    name: str
    type: str
    columns: list[str]
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None
    check_condition: str | None = None


class IndexCreate(BaseModel):
    """Index creation request model."""
    name: str
    columns: list[str]
    type: str | None = "btree"
    unique: bool | None = False


class TableCreate(BaseModel):
    """Table creation request model."""
    name: str
    columns: list[ColumnCreate]
    constraints: list[ConstraintCreate] | None = None
    indexes: list[IndexCreate] | None = None
    description: str | None = None


class SchemaCreate(BaseModel):
    """Schema creation request model."""
    name: str
    tables: list[TableCreate]
    description: str | None = None


class SchemaUpdate(BaseModel):
    """Schema update request model."""
    tables: list[TableCreate] | None = None
    description: str | None = None


class MigrationCreate(BaseModel):
    """Migration creation request model."""
    name: str
    sql_up: str
    sql_down: str | None = None
    description: str | None = None


class SchemaDiffRequest(BaseModel):
    """Schema diff request model."""
    from_schema: str
    to_schema: str
    migration_name: str


@router.post("/", response_model=APIResponse)
async def create_schema(schema_data: SchemaCreate):
    """
    Create a new database schema.

    Args:
        schema_data: Schema creation data

    Returns:
        APIResponse with created schema
    """
    try:
        # Convert Pydantic models to dictionaries
        tables_dict = []
        for table in schema_data.tables:
            table_dict = table.dict()
            table_dict["columns"] = [col.dict() for col in table.columns]
            if table.constraints:
                table_dict["constraints"] = [constraint.dict() for constraint in table.constraints]
            if table.indexes:
                table_dict["indexes"] = [index.dict() for index in table.indexes]
            tables_dict.append(table_dict)

        schema = await schema_management_service.create_schema(
            name=schema_data.name,
            tables=tables_dict,
            description=schema_data.description
        )

        schema_dict = schema.__dict__.copy()
        schema_dict["tables"] = [table.__dict__ for table in schema.tables]

        return APIResponse(
            success=True,
            data=schema_dict,
            message=f"Schema '{schema_data.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create schema", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create schema: {str(e)}")


@router.get("/", response_model=APIResponse)
async def list_schemas():
    """
    List all database schemas.

    Returns:
        APIResponse with list of schemas
    """
    try:
        schemas = await schema_management_service.list_schemas()

        schemas_data = []
        for schema in schemas:
            schema_dict = schema.__dict__.copy()
            schema_dict["tables"] = []
            for table in schema.tables:
                table_dict = table.__dict__.copy()
                table_dict["columns"] = [col.__dict__ for col in table.columns]
                table_dict["constraints"] = [constraint.__dict__ for constraint in table.constraints]
                table_dict["indexes"] = [index.__dict__ for index in table.indexes]
                schema_dict["tables"].append(table_dict)
            schemas_data.append(schema_dict)

        return APIResponse(
            success=True,
            data=schemas_data,
            message=f"Retrieved {len(schemas_data)} schemas"
        )
    except Exception as e:
        logger.error("Failed to list schemas", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list schemas: {str(e)}")


@router.get("/{schema_name}", response_model=APIResponse)
async def get_schema(schema_name: str):
    """
    Get a specific database schema.

    Args:
        schema_name: Name of the schema to retrieve

    Returns:
        APIResponse with schema data
    """
    try:
        schema = await schema_management_service.get_schema(schema_name)

        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema {schema_name} not found")

        schema_dict = schema.__dict__.copy()
        schema_dict["tables"] = []
        for table in schema.tables:
            table_dict = table.__dict__.copy()
            table_dict["columns"] = [col.__dict__ for col in table.columns]
            table_dict["constraints"] = [constraint.__dict__ for constraint in table.constraints]
            table_dict["indexes"] = [index.__dict__ for index in table.indexes]
            schema_dict["tables"].append(table_dict)

        return APIResponse(
            success=True,
            data=schema_dict,
            message=f"Retrieved schema '{schema.name}'"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get schema", error=str(e), schema_name=schema_name)
        raise HTTPException(status_code=500, detail=f"Failed to get schema: {str(e)}")


@router.put("/{schema_name}", response_model=APIResponse)
async def update_schema(schema_name: str, update_data: SchemaUpdate):
    """
    Update an existing database schema.

    Args:
        schema_name: Name of the schema to update
        update_data: Update data

    Returns:
        APIResponse with updated schema
    """
    try:
        # Convert Pydantic models to dictionaries if provided
        tables_dict = None
        if update_data.tables:
            tables_dict = []
            for table in update_data.tables:
                table_dict = table.dict()
                table_dict["columns"] = [col.dict() for col in table.columns]
                if table.constraints:
                    table_dict["constraints"] = [constraint.dict() for constraint in table.constraints]
                if table.indexes:
                    table_dict["indexes"] = [index.dict() for index in table.indexes]
                tables_dict.append(table_dict)

        schema = await schema_management_service.update_schema(
            schema_name=schema_name,
            tables=tables_dict,
            description=update_data.description
        )

        if not schema:
            raise HTTPException(status_code=404, detail=f"Schema {schema_name} not found")

        schema_dict = schema.__dict__.copy()
        schema_dict["tables"] = []
        for table in schema.tables:
            table_dict = table.__dict__.copy()
            table_dict["columns"] = [col.__dict__ for col in table.columns]
            table_dict["constraints"] = [constraint.__dict__ for constraint in table.constraints]
            table_dict["indexes"] = [index.__dict__ for index in table.indexes]
            schema_dict["tables"].append(table_dict)

        return APIResponse(
            success=True,
            data=schema_dict,
            message=f"Schema '{schema.name}' updated successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to update schema", error=str(e), schema_name=schema_name)
        raise HTTPException(status_code=500, detail=f"Failed to update schema: {str(e)}")


@router.delete("/{schema_name}", response_model=APIResponse)
async def delete_schema(schema_name: str):
    """
    Delete a database schema.

    Args:
        schema_name: Name of the schema to delete

    Returns:
        APIResponse confirming deletion
    """
    try:
        success = await schema_management_service.delete_schema(schema_name)

        if not success:
            raise HTTPException(status_code=404, detail=f"Schema {schema_name} not found")

        return APIResponse(
            success=True,
            message="Schema deleted successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to delete schema", error=str(e), schema_name=schema_name)
        raise HTTPException(status_code=500, detail=f"Failed to delete schema: {str(e)}")


@router.post("/migrations/", response_model=APIResponse)
async def create_migration(migration_data: MigrationCreate):
    """
    Create a new database migration.

    Args:
        migration_data: Migration creation data

    Returns:
        APIResponse with created migration
    """
    try:
        migration = await schema_management_service.create_migration(
            name=migration_data.name,
            sql_up=migration_data.sql_up,
            sql_down=migration_data.sql_down,
            description=migration_data.description
        )

        return APIResponse(
            success=True,
            data=migration.__dict__,
            message=f"Migration '{migration_data.name}' created successfully"
        )
    except Exception as e:
        logger.error("Failed to create migration", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to create migration: {str(e)}")


@router.post("/migrations/{migration_id}/apply", response_model=APIResponse)
async def apply_migration(migration_id: str):
    """
    Apply a database migration.

    Args:
        migration_id: ID of the migration to apply

    Returns:
        APIResponse confirming application
    """
    try:
        success = await schema_management_service.apply_migration(migration_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Migration {migration_id} not found or cannot be applied")

        return APIResponse(
            success=True,
            message="Migration applied successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to apply migration", error=str(e), migration_id=migration_id)
        raise HTTPException(status_code=500, detail=f"Failed to apply migration: {str(e)}")


@router.post("/migrations/{migration_id}/rollback", response_model=APIResponse)
async def rollback_migration(migration_id: str):
    """
    Rollback a database migration.

    Args:
        migration_id: ID of the migration to rollback

    Returns:
        APIResponse confirming rollback
    """
    try:
        success = await schema_management_service.rollback_migration(migration_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Migration {migration_id} not found or cannot be rolled back")

        return APIResponse(
            success=True,
            message="Migration rolled back successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to rollback migration", error=str(e), migration_id=migration_id)
        raise HTTPException(status_code=500, detail=f"Failed to rollback migration: {str(e)}")


@router.get("/migrations/", response_model=APIResponse)
async def list_migrations(applied_only: bool = False):
    """
    List database migrations.

    Args:
        applied_only: If true, only return applied migrations

    Returns:
        APIResponse with list of migrations
    """
    try:
        migrations = await schema_management_service.list_migrations(applied_only)

        migrations_data = [migration.__dict__ for migration in migrations]

        return APIResponse(
            success=True,
            data=migrations_data,
            message=f"Retrieved {len(migrations_data)} migrations"
        )
    except Exception as e:
        logger.error("Failed to list migrations", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to list migrations: {str(e)}")


@router.post("/diff", response_model=APIResponse)
async def generate_migration_from_diff(diff_request: SchemaDiffRequest):
    """
    Generate migration from schema difference.

    Args:
        diff_request: Schema diff request data

    Returns:
        APIResponse with generated migration
    """
    try:
        migration = await schema_management_service.generate_migration_from_diff(
            from_schema=diff_request.from_schema,
            to_schema=diff_request.to_schema,
            migration_name=diff_request.migration_name
        )

        return APIResponse(
            success=True,
            data=migration.__dict__,
            message="Migration generated successfully from schema diff"
        )
    except Exception as e:
        logger.error("Failed to generate migration from diff", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to generate migration from diff: {str(e)}")


@router.get("/{schema_name}/export/{format}", response_model=APIResponse)
async def export_schema(schema_name: str, format: str):
    """
    Export a schema in specified format.

    Args:
        schema_name: Name of the schema to export
        format: Export format (sql, json)

    Returns:
        APIResponse with exported schema data
    """
    try:
        exported_data = await schema_management_service.export_schema(schema_name, format)

        return APIResponse(
            success=True,
            data={"format": format, "content": exported_data},
            message=f"Schema exported in {format} format"
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Failed to export schema", error=str(e), schema_name=schema_name, format=format)
        raise HTTPException(status_code=500, detail=f"Failed to export schema: {str(e)}")


@router.get("/types/columns", response_model=APIResponse)
async def get_column_types():
    """
    Get available column types.

    Returns:
        APIResponse with list of column types
    """
    try:
        column_types = [{"name": t.name, "value": t.value} for t in ColumnType]

        return APIResponse(
            success=True,
            data=column_types,
            message="Retrieved column types"
        )
    except Exception as e:
        logger.error("Failed to get column types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get column types: {str(e)}")


@router.get("/types/constraints", response_model=APIResponse)
async def get_constraint_types():
    """
    Get available constraint types.

    Returns:
        APIResponse with list of constraint types
    """
    try:
        constraint_types = [{"name": t.name, "value": t.value} for t in ConstraintType]

        return APIResponse(
            success=True,
            data=constraint_types,
            message="Retrieved constraint types"
        )
    except Exception as e:
        logger.error("Failed to get constraint types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get constraint types: {str(e)}")


@router.get("/types/indexes", response_model=APIResponse)
async def get_index_types():
    """
    Get available index types.

    Returns:
        APIResponse with list of index types
    """
    try:
        index_types = [{"name": t.name, "value": t.value} for t in IndexType]

        return APIResponse(
            success=True,
            data=index_types,
            message="Retrieved index types"
        )
    except Exception as e:
        logger.error("Failed to get index types", error=str(e))
        raise HTTPException(status_code=500, detail=f"Failed to get index types: {str(e)}")
