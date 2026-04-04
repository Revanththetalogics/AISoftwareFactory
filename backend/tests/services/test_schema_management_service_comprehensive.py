"""
Comprehensive tests for SchemaManagementService to increase coverage.
"""

import json
from datetime import UTC, datetime

import pytest
from backend.services.schema_management_service import (
    Column,
    ColumnType,
    Constraint,
    ConstraintType,
    Index,
    IndexType,
    Migration,
    Schema,
    SchemaManagementService,
    Table,
)


class TestSchemaManagementService:
    """Comprehensive tests for SchemaManagementService."""

    @pytest.fixture
    def schema_service(self):
        """Create SchemaManagementService instance."""
        return SchemaManagementService()

    def test_init(self, schema_service):
        """Test SchemaManagementService initialization."""
        assert schema_service is not None
        assert hasattr(schema_service, "schemas")
        assert hasattr(schema_service, "migrations")
        assert isinstance(schema_service.schemas, dict)
        assert isinstance(schema_service.migrations, dict)

        # Should have default schema initialized
        assert len(schema_service.schemas) > 0
        assert "default" in schema_service.schemas

    def test_default_schema_initialization(self, schema_service):
        """Test that default schema is properly initialized."""
        default_schema = schema_service.schemas.get("default")
        assert default_schema is not None
        assert isinstance(default_schema, Schema)
        assert default_schema.name == "default"
        assert len(default_schema.tables) >= 2  # Should have users and projects tables

        # Check users table
        users_table = next((t for t in default_schema.tables if t.name == "users"), None)
        assert users_table is not None
        assert isinstance(users_table, Table)
        assert len(users_table.columns) > 0

        # Check projects table
        projects_table = next((t for t in default_schema.tables if t.name == "projects"), None)
        assert projects_table is not None
        assert len(projects_table.columns) > 0
        assert len(projects_table.constraints) > 0

    @pytest.mark.asyncio
    async def test_create_schema_success(self, schema_service):
        """Test creating schema successfully."""
        tables_data = [
            {
                "name": "test_table",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True, "nullable": False},
                    {"name": "name", "type": "string", "nullable": False},
                ],
                "description": "Test table",
            }
        ]

        result = await schema_service.create_schema(
            name="test_schema", tables=tables_data, description="Test schema description"
        )

        assert result is not None
        assert isinstance(result, Schema)
        assert result.name == "test_schema"
        assert result.description == "Test schema description"
        assert len(result.tables) == 1

        table = result.tables[0]
        assert isinstance(table, Table)
        assert table.name == "test_table"
        assert len(table.columns) == 2

        # Check columns
        id_column = next(c for c in table.columns if c.name == "id")
        assert id_column.type == ColumnType.INTEGER
        assert id_column.primary_key is True
        assert id_column.nullable is False

        name_column = next(c for c in table.columns if c.name == "name")
        assert name_column.type == ColumnType.STRING
        assert name_column.nullable is False

    @pytest.mark.asyncio
    async def test_create_schema_with_constraints(self, schema_service):
        """Test creating schema with constraints."""
        tables_data = [
            {
                "name": "orders",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "user_id", "type": "integer", "nullable": False},
                ],
                "constraints": [
                    {
                        "name": "fk_orders_user",
                        "type": "foreign_key",
                        "columns": ["user_id"],
                        "referenced_table": "users",
                        "referenced_columns": ["id"],
                    }
                ],
            }
        ]

        result = await schema_service.create_schema("orders_schema", tables_data)

        table = result.tables[0]
        assert len(table.constraints) == 1

        constraint = table.constraints[0]
        assert isinstance(constraint, Constraint)
        assert constraint.name == "fk_orders_user"
        assert constraint.type == ConstraintType.FOREIGN_KEY
        assert constraint.columns == ["user_id"]
        assert constraint.referenced_table == "users"

    @pytest.mark.asyncio
    async def test_create_schema_with_indexes(self, schema_service):
        """Test creating schema with indexes."""
        tables_data = [
            {
                "name": "indexed_table",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "email", "type": "string"},
                ],
                "indexes": [{"name": "idx_email", "columns": ["email"], "type": "btree", "unique": True}],
            }
        ]

        result = await schema_service.create_schema("indexed_schema", tables_data)

        table = result.tables[0]
        assert len(table.indexes) == 1

        index = table.indexes[0]
        assert isinstance(index, Index)
        assert index.name == "idx_email"
        assert index.columns == ["email"]
        assert index.type == IndexType.BTREE
        assert index.unique is True

    @pytest.mark.asyncio
    async def test_get_schema_success(self, schema_service):
        """Test getting existing schema."""
        # Create a schema first
        tables_data = [{"name": "test", "columns": [{"name": "id", "type": "integer"}]}]
        created_schema = await schema_service.create_schema("get_test", tables_data)

        result = await schema_service.get_schema("get_test")

        assert result is not None
        assert result.name == "get_test"
        assert result.version == created_schema.version

    @pytest.mark.asyncio
    async def test_get_schema_not_found(self, schema_service):
        """Test getting non-existent schema."""
        result = await schema_service.get_schema("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_schemas(self, schema_service):
        """Test listing all schemas."""
        # Should at least have the default schema
        result = await schema_service.list_schemas()
        assert isinstance(result, list)
        assert len(result) >= 1

        for schema in result:
            assert isinstance(schema, Schema)

    @pytest.mark.asyncio
    async def test_update_schema_success(self, schema_service):
        """Test updating existing schema."""
        # Create initial schema
        tables_data = [{"name": "original_table", "columns": [{"name": "id", "type": "integer"}]}]
        await schema_service.create_schema("update_test", tables_data)

        # Update with new tables
        new_tables_data = [
            {
                "name": "updated_table",
                "columns": [{"name": "id", "type": "integer", "primary_key": True}, {"name": "name", "type": "string"}],
            }
        ]

        result = await schema_service.update_schema(
            schema_name="update_test", tables=new_tables_data, description="Updated description"
        )

        assert result is not None
        assert result.description == "Updated description"
        assert len(result.tables) == 1
        assert result.tables[0].name == "updated_table"
        # Version should be incremented
        assert result.version != "1.0.0"

    @pytest.mark.asyncio
    async def test_update_schema_partial_update(self, schema_service):
        """Test partial schema update (only description)."""
        # Create initial schema
        tables_data = [{"name": "test", "columns": [{"name": "id", "type": "integer"}]}]
        original = await schema_service.create_schema("partial_update_test", tables_data)
        original_version = original.version

        # Update only description
        result = await schema_service.update_schema(
            schema_name="partial_update_test", description="New description only"
        )

        assert result is not None
        assert result.description == "New description only"
        # Tables should remain unchanged
        assert len(result.tables) == 1
        assert result.tables[0].name == "test"
        # Version should still be incremented
        assert result.version != original_version

    @pytest.mark.asyncio
    async def test_update_schema_not_found(self, schema_service):
        """Test updating non-existent schema."""
        result = await schema_service.update_schema("nonexistent", description="test")
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_schema_success(self, schema_service):
        """Test deleting existing schema."""
        # Create schema first
        tables_data = [{"name": "test", "columns": [{"name": "id", "type": "integer"}]}]
        await schema_service.create_schema("delete_test", tables_data)

        # Verify it exists
        assert "delete_test" in schema_service.schemas

        # Delete it
        result = await schema_service.delete_schema("delete_test")

        assert result is True
        assert "delete_test" not in schema_service.schemas

    @pytest.mark.asyncio
    async def test_delete_schema_not_found(self, schema_service):
        """Test deleting non-existent schema."""
        result = await schema_service.delete_schema("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_create_migration_success(self, schema_service):
        """Test creating migration successfully."""
        result = await schema_service.create_migration(
            name="test_migration",
            sql_up="CREATE TABLE test (id INTEGER);",
            sql_down="DROP TABLE test;",
            description="Test migration description",
        )

        assert result is not None
        assert isinstance(result, Migration)
        assert result.name == "test_migration"
        assert result.sql_up == "CREATE TABLE test (id INTEGER);"
        assert result.sql_down == "DROP TABLE test;"
        assert result.description == "Test migration description"
        assert result.applied_at is None
        assert len(result.id) > 0
        assert len(result.version) > 0

    @pytest.mark.asyncio
    async def test_create_migration_without_rollback(self, schema_service):
        """Test creating migration without rollback SQL."""
        result = await schema_service.create_migration(
            name="one_way_migration", sql_up="ALTER TABLE users ADD COLUMN age INTEGER;"
        )

        assert result is not None
        assert result.sql_down is None

    @pytest.mark.asyncio
    async def test_apply_migration_success(self, schema_service):
        """Test applying migration successfully."""
        # Create migration first
        migration = await schema_service.create_migration(name="apply_test", sql_up="SELECT 1;")

        # Apply it
        result = await schema_service.apply_migration(migration.id)

        assert result is True

        # Check that it's marked as applied
        updated_migration = schema_service.migrations[migration.id]
        assert updated_migration.applied_at is not None

    @pytest.mark.asyncio
    async def test_apply_migration_not_found(self, schema_service):
        """Test applying non-existent migration."""
        result = await schema_service.apply_migration("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_rollback_migration_success(self, schema_service):
        """Test rolling back migration successfully."""
        # Create and apply migration first
        migration = await schema_service.create_migration(
            name="rollback_test", sql_up="SELECT 1;", sql_down="SELECT 2;"
        )

        await schema_service.apply_migration(migration.id)
        assert migration.applied_at is not None

        # Roll it back
        result = await schema_service.rollback_migration(migration.id)

        assert result is True

        # Check that it's marked as not applied
        updated_migration = schema_service.migrations[migration.id]
        assert updated_migration.applied_at is None

    @pytest.mark.asyncio
    async def test_rollback_migration_no_rollback_sql(self, schema_service):
        """Test rolling back migration without rollback SQL."""
        # Create migration without rollback SQL
        migration = await schema_service.create_migration(name="no_rollback_test", sql_up="SELECT 1;")

        await schema_service.apply_migration(migration.id)

        # Try to rollback
        result = await schema_service.rollback_migration(migration.id)

        assert result is False  # Should fail because no rollback SQL

    @pytest.mark.asyncio
    async def test_rollback_migration_not_found(self, schema_service):
        """Test rolling back non-existent migration."""
        result = await schema_service.rollback_migration("nonexistent")
        assert result is False

    @pytest.mark.asyncio
    async def test_list_migrations_all(self, schema_service):
        """Test listing all migrations."""
        # Create a few migrations
        await schema_service.create_migration("migration_1", "SELECT 1;")
        await schema_service.create_migration("migration_2", "SELECT 2;")

        result = await schema_service.list_migrations()
        assert isinstance(result, list)
        assert len(result) >= 2

        for migration in result:
            assert isinstance(migration, Migration)

    @pytest.mark.asyncio
    async def test_list_migrations_applied_only(self, schema_service):
        """Test listing only applied migrations."""
        # Create migrations
        mig1 = await schema_service.create_migration("applied_test_1", "SELECT 1;")
        await schema_service.create_migration("applied_test_2", "SELECT 2;")

        # Apply one of them
        await schema_service.apply_migration(mig1.id)

        result = await schema_service.list_migrations(applied_only=True)
        assert isinstance(result, list)
        assert len(result) == 1
        assert result[0].id == mig1.id

    @pytest.mark.asyncio
    async def test_generate_migration_from_diff_success(self, schema_service):
        """Test generating migration from schema difference."""
        # Create two schemas
        schema1_tables = [
            {
                "name": "users",
                "columns": [{"name": "id", "type": "integer", "primary_key": True}, {"name": "name", "type": "string"}],
            }
        ]

        schema2_tables = [
            {
                "name": "users",
                "columns": [
                    {"name": "id", "type": "integer", "primary_key": True},
                    {"name": "name", "type": "string"},
                    {"name": "email", "type": "string"},  # New column
                ],
            },
            {
                "name": "orders",  # New table
                "columns": [{"name": "id", "type": "integer", "primary_key": True}],
            },
        ]

        await schema_service.create_schema("source_schema", schema1_tables)
        await schema_service.create_schema("target_schema", schema2_tables)

        # Generate migration
        result = await schema_service.generate_migration_from_diff(
            from_schema="source_schema", to_schema="target_schema", migration_name="diff_migration_test"
        )

        assert result is not None
        assert isinstance(result, Migration)
        assert result.name == "diff_migration_test"
        assert "CREATE TABLE orders" in result.sql_up
        assert len(result.sql_up) > 0

    @pytest.mark.asyncio
    async def test_generate_migration_from_diff_missing_schema(self, schema_service):
        """Test generating migration with missing schema."""
        with pytest.raises(ValueError) as exc_info:
            await schema_service.generate_migration_from_diff(
                from_schema="nonexistent_source", to_schema="target_schema", migration_name="test"
            )

        assert "Source or target schema not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_schema_sql_format(self, schema_service):
        """Test exporting schema as SQL."""
        # Create a simple schema
        tables_data = [
            {
                "name": "export_test",
                "columns": [{"name": "id", "type": "integer", "primary_key": True}, {"name": "name", "type": "string"}],
            }
        ]

        await schema_service.create_schema("export_schema", tables_data)

        result = await schema_service.export_schema("export_schema", "sql")

        assert isinstance(result, str)
        assert len(result) > 0
        assert "CREATE TABLE export_test" in result
        assert "id INTEGER" in result
        assert "name STRING" in result

    @pytest.mark.asyncio
    async def test_export_schema_json_format(self, schema_service):
        """Test exporting schema as JSON."""
        # Create a simple schema
        tables_data = [{"name": "json_test", "columns": [{"name": "id", "type": "integer", "primary_key": True}]}]

        await schema_service.create_schema("json_export_schema", tables_data)

        result = await schema_service.export_schema("json_export_schema", "json")

        assert isinstance(result, str)
        result_dict = json.loads(result)

        assert result_dict["name"] == "json_export_schema"
        assert len(result_dict["tables"]) == 1
        assert result_dict["tables"][0]["name"] == "json_test"

    @pytest.mark.asyncio
    async def test_export_schema_invalid_format(self, schema_service):
        """Test exporting schema with invalid format."""
        with pytest.raises(ValueError) as exc_info:
            await schema_service.export_schema("default", "xml")

        assert "Unsupported format: xml" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_export_schema_not_found(self, schema_service):
        """Test exporting non-existent schema."""
        with pytest.raises(ValueError) as exc_info:
            await schema_service.export_schema("nonexistent", "sql")

        assert "Schema nonexistent not found" in str(exc_info.value)

    def test_increment_version(self, schema_service):
        """Test version incrementing."""
        result = schema_service._increment_version("1.0.0")
        assert result == "1.0.1"

        result = schema_service._increment_version("2.5.3")
        assert result == "2.5.4"

    def test_generate_migration_version(self, schema_service):
        """Test migration version generation."""
        result = schema_service._generate_migration_version()
        assert isinstance(result, str)
        assert len(result) == 14  # YYYYMMDDHHMMSS format
        # Should be numeric
        assert result.isdigit()

    def test_generate_create_table_sql(self, schema_service):
        """Test SQL generation for table creation."""
        table = Table(
            name="test_table",
            columns=[
                Column("id", ColumnType.INTEGER, primary_key=True, nullable=False),
                Column("name", ColumnType.STRING, nullable=False),
                Column("age", ColumnType.INTEGER, default_value="18"),
            ],
            constraints=[
                Constraint(
                    name="fk_test",
                    type=ConstraintType.FOREIGN_KEY,
                    columns=["id"],
                    referenced_table="users",
                    referenced_columns=["id"],
                )
            ],
        )

        result = schema_service._generate_create_table_sql(table)

        assert isinstance(result, str)
        assert "CREATE TABLE test_table" in result
        assert "id INTEGER NOT NULL PRIMARY KEY" in result
        assert "name STRING NOT NULL" in result
        assert "age INTEGER DEFAULT 18" in result
        assert "FOREIGN KEY (id) REFERENCES users(id)" in result

    def test_to_sql_conversion(self, schema_service):
        """Test full schema to SQL conversion."""
        schema = Schema(
            name="test_schema",
            tables=[
                Table(name="table1", columns=[Column("id", ColumnType.INTEGER, primary_key=True)]),
                Table(name="table2", columns=[Column("name", ColumnType.STRING)]),
            ],
            version="1.0.0",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
        )

        result = schema_service._to_sql(schema)

        assert isinstance(result, str)
        assert "CREATE TABLE table1" in result
        assert "CREATE TABLE table2" in result
        # Should have empty line between tables
        assert "\n\n" in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
