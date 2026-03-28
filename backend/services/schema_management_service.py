"""
Database Schema Management Service

Provides backend services for managing database schemas, migrations, and schema visualization.
"""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from backend.core.logging import get_logger

logger = get_logger(__name__)


class ColumnType(str, Enum):
    """Supported column types."""
    STRING = "string"
    TEXT = "text"
    INTEGER = "integer"
    BIGINT = "bigint"
    FLOAT = "float"
    BOOLEAN = "boolean"
    DATETIME = "datetime"
    DATE = "date"
    JSON = "json"
    UUID = "uuid"
    BINARY = "binary"


class ConstraintType(str, Enum):
    """Supported constraint types."""
    PRIMARY_KEY = "primary_key"
    FOREIGN_KEY = "foreign_key"
    UNIQUE = "unique"
    NOT_NULL = "not_null"
    CHECK = "check"


class IndexType(str, Enum):
    """Supported index types."""
    BTREE = "btree"
    HASH = "hash"
    GIN = "gin"
    GIST = "gist"


@dataclass
class Column:
    """Represents a database column."""
    name: str
    type: ColumnType
    nullable: bool = True
    default_value: str | None = None
    primary_key: bool = False
    unique: bool = False
    foreign_key: dict[str, str] | None = None  # {table: str, column: str}
    constraints: list[dict[str, Any]] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []


@dataclass
class Constraint:
    """Represents a table constraint."""
    name: str
    type: ConstraintType
    columns: list[str]
    referenced_table: str | None = None
    referenced_columns: list[str] | None = None
    check_condition: str | None = None


@dataclass
class Index:
    """Represents a database index."""
    name: str
    columns: list[str]
    type: IndexType = IndexType.BTREE
    unique: bool = False


@dataclass
class Table:
    """Represents a database table."""
    name: str
    columns: list[Column]
    constraints: list[Constraint] = None
    indexes: list[Index] = None
    description: str | None = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = []
        if self.indexes is None:
            self.indexes = []


@dataclass
class Schema:
    """Represents a complete database schema."""
    name: str
    tables: list[Table]
    version: str
    created_at: str
    updated_at: str
    description: str | None = None
    metadata: dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class Migration:
    """Represents a schema migration."""
    id: str
    name: str
    version: str
    sql_up: str
    created_at: str
    sql_down: str | None = None
    applied_at: str | None = None
    description: str | None = None


class SchemaManagementService:
    """Service for managing database schemas and migrations."""

    def __init__(self):
        self.schemas: dict[str, Schema] = {}
        self.migrations: dict[str, Migration] = {}
        self._initialize_default_schema()

    def _initialize_default_schema(self):
        """Initialize with default schema."""
        # Create default tables
        users_table = Table(
            name="users",
            columns=[
                Column("id", ColumnType.UUID, primary_key=True),
                Column("username", ColumnType.STRING, nullable=False, unique=True),
                Column("email", ColumnType.STRING, nullable=False, unique=True),
                Column("password_hash", ColumnType.STRING, nullable=False),
                Column("first_name", ColumnType.STRING),
                Column("last_name", ColumnType.STRING),
                Column("is_active", ColumnType.BOOLEAN, default_value="true"),
                Column("created_at", ColumnType.DATETIME, default_value="CURRENT_TIMESTAMP"),
                Column("updated_at", ColumnType.DATETIME, default_value="CURRENT_TIMESTAMP"),
            ],
            description="User accounts and authentication"
        )

        projects_table = Table(
            name="projects",
            columns=[
                Column("id", ColumnType.UUID, primary_key=True),
                Column("name", ColumnType.STRING, nullable=False),
                Column("description", ColumnType.TEXT),
                Column("owner_id", ColumnType.UUID, nullable=False),
                Column("status", ColumnType.STRING, default_value="'active'"),
                Column("created_at", ColumnType.DATETIME, default_value="CURRENT_TIMESTAMP"),
                Column("updated_at", ColumnType.DATETIME, default_value="CURRENT_TIMESTAMP"),
            ],
            constraints=[
                Constraint(
                    name="fk_projects_owner",
                    type=ConstraintType.FOREIGN_KEY,
                    columns=["owner_id"],
                    referenced_table="users",
                    referenced_columns=["id"]
                )
            ],
            description="Software projects managed by the system"
        )

        default_schema = Schema(
            name="default",
            tables=[users_table, projects_table],
            version="1.0.0",
            created_at=datetime.now(UTC).isoformat(),
            updated_at=datetime.now(UTC).isoformat(),
            description="Default application schema"
        )

        self.schemas["default"] = default_schema

    async def create_schema(
        self,
        name: str,
        tables: list[dict[str, Any]],
        description: str | None = None
    ) -> Schema:
        """Create a new database schema."""
        try:
            # Convert table dictionaries to Table objects
            table_objects = []
            for table_data in tables:
                columns = [
                    Column(
                        name=col["name"],
                        type=ColumnType(col["type"]),
                        nullable=col.get("nullable", True),
                        default_value=col.get("default_value"),
                        primary_key=col.get("primary_key", False),
                        unique=col.get("unique", False),
                        foreign_key=col.get("foreign_key")
                    )
                    for col in table_data.get("columns", [])
                ]

                constraints = [
                    Constraint(
                        name=constraint["name"],
                        type=ConstraintType(constraint["type"]),
                        columns=constraint["columns"],
                        referenced_table=constraint.get("referenced_table"),
                        referenced_columns=constraint.get("referenced_columns"),
                        check_condition=constraint.get("check_condition")
                    )
                    for constraint in table_data.get("constraints", [])
                ]

                indexes = [
                    Index(
                        name=index["name"],
                        columns=index["columns"],
                        type=IndexType(index.get("type", "btree")),
                        unique=index.get("unique", False)
                    )
                    for index in table_data.get("indexes", [])
                ]

                table = Table(
                    name=table_data["name"],
                    columns=columns,
                    constraints=constraints,
                    indexes=indexes,
                    description=table_data.get("description")
                )
                table_objects.append(table)

            schema = Schema(
                name=name,
                tables=table_objects,
                version="1.0.0",
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
                description=description
            )

            self.schemas[name] = schema

            logger.info(f"Created database schema: {name}", schema_name=name)
            return schema

        except Exception as e:
            logger.error("Failed to create schema", error=str(e))
            raise

    async def get_schema(self, schema_name: str) -> Schema | None:
        """Get a schema by name."""
        return self.schemas.get(schema_name)

    async def list_schemas(self) -> list[Schema]:
        """List all schemas."""
        return list(self.schemas.values())

    async def update_schema(
        self,
        schema_name: str,
        tables: list[dict[str, Any]] | None = None,
        description: str | None = None
    ) -> Schema | None:
        """Update an existing schema."""
        schema = self.schemas.get(schema_name)
        if not schema:
            return None

        try:
            if tables is not None:
                # Convert table dictionaries to Table objects
                table_objects = []
                for table_data in tables:
                    columns = [
                        Column(
                            name=col["name"],
                            type=ColumnType(col["type"]),
                            nullable=col.get("nullable", True),
                            default_value=col.get("default_value"),
                            primary_key=col.get("primary_key", False),
                            unique=col.get("unique", False),
                            foreign_key=col.get("foreign_key")
                        )
                        for col in table_data.get("columns", [])
                    ]

                    table = Table(
                        name=table_data["name"],
                        columns=columns,
                        description=table_data.get("description")
                    )
                    table_objects.append(table)

                schema.tables = table_objects

            if description:
                schema.description = description

            schema.updated_at = datetime.now(UTC).isoformat()
            schema.version = self._increment_version(schema.version)

            logger.info(f"Updated database schema: {schema_name}", schema_name=schema_name)
            return schema

        except Exception as e:
            logger.error("Failed to update schema", error=str(e), schema_name=schema_name)
            raise

    async def delete_schema(self, schema_name: str) -> bool:
        """Delete a schema."""
        if schema_name in self.schemas:
            del self.schemas[schema_name]
            logger.info("Deleted database schema", schema_name=schema_name)
            return True
        return False

    async def create_migration(
        self,
        name: str,
        sql_up: str,
        sql_down: str | None = None,
        description: str | None = None
    ) -> Migration:
        """Create a new migration."""
        try:
            migration_id = f"migration_{datetime.now().timestamp()}_{hash(name) % 10000}"
            version = self._generate_migration_version()

            migration = Migration(
                id=migration_id,
                name=name,
                version=version,
                sql_up=sql_up,
                sql_down=sql_down,
                created_at=datetime.now(UTC).isoformat(),
                description=description
            )

            self.migrations[migration_id] = migration

            logger.info(f"Created migration: {name}", migration_id=migration_id)
            return migration

        except Exception as e:
            logger.error("Failed to create migration", error=str(e))
            raise

    async def apply_migration(self, migration_id: str) -> bool:
        """Apply a migration."""
        migration = self.migrations.get(migration_id)
        if not migration:
            return False

        try:
            # In a real implementation, this would execute the SQL
            logger.info(f"Applying migration: {migration.name}", migration_id=migration_id)

            migration.applied_at = datetime.now(UTC).isoformat()
            return True

        except Exception as e:
            logger.error("Failed to apply migration", error=str(e), migration_id=migration_id)
            raise

    async def rollback_migration(self, migration_id: str) -> bool:
        """Rollback a migration."""
        migration = self.migrations.get(migration_id)
        if not migration or not migration.sql_down:
            return False

        try:
            # In a real implementation, this would execute the rollback SQL
            logger.info(f"Rolling back migration: {migration.name}", migration_id=migration_id)

            migration.applied_at = None
            return True

        except Exception as e:
            logger.error("Failed to rollback migration", error=str(e), migration_id=migration_id)
            raise

    async def list_migrations(self, applied_only: bool = False) -> list[Migration]:
        """List migrations."""
        migrations = list(self.migrations.values())

        if applied_only:
            migrations = [m for m in migrations if m.applied_at is not None]

        return sorted(migrations, key=lambda m: m.created_at, reverse=True)

    async def generate_migration_from_diff(
        self,
        from_schema: str,
        to_schema: str,
        migration_name: str
    ) -> Migration:
        """Generate migration SQL from schema difference."""
        try:
            from_schema_obj = self.schemas.get(from_schema)
            to_schema_obj = self.schemas.get(to_schema)

            if not from_schema_obj or not to_schema_obj:
                raise ValueError("Source or target schema not found")

            # Generate diff SQL (simplified implementation)
            sql_statements = []

            # Check for new tables
            from_table_names = {t.name for t in from_schema_obj.tables}
            to_table_names = {t.name for t in to_schema_obj.tables}

            new_tables = to_table_names - from_table_names
            for table_name in new_tables:
                table = next(t for t in to_schema_obj.tables if t.name == table_name)
                sql_statements.append(self._generate_create_table_sql(table))

            # In a real implementation, you'd also handle:
            # - Column additions/removals
            # - Column type changes
            # - Constraint changes
            # - Index changes

            sql_up = "\n".join(sql_statements) if sql_statements else "-- No changes needed"
            sql_down = f"-- Rollback for {migration_name}"  # Simplified

            migration = Migration(
                id=f"auto_migration_{datetime.now().timestamp()}",
                name=migration_name,
                version=self._generate_migration_version(),
                sql_up=sql_up,
                sql_down=sql_down,
                created_at=datetime.now(UTC).isoformat(),
                description=f"Auto-generated migration from {from_schema} to {to_schema}"
            )

            self.migrations[migration.id] = migration

            logger.info("Generated migration from schema diff",
                       from_schema=from_schema, to_schema=to_schema)
            return migration

        except Exception as e:
            logger.error("Failed to generate migration from diff", error=str(e))
            raise

    async def export_schema(self, schema_name: str, format: str = "sql") -> str:
        """Export schema in specified format."""
        schema = await self.get_schema(schema_name)
        if not schema:
            raise ValueError(f"Schema {schema_name} not found")

        if format.lower() == "sql":
            return self._to_sql(schema)
        elif format.lower() == "json":
            return json.dumps(asdict(schema), indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _increment_version(self, version: str) -> str:
        """Increment version number."""
        parts = version.split(".")
        if len(parts) >= 3:
            parts[2] = str(int(parts[2]) + 1)
        return ".".join(parts)

    def _generate_migration_version(self) -> str:
        """Generate migration version."""
        return datetime.now(UTC).strftime("%Y%m%d%H%M%S")

    def _generate_create_table_sql(self, table: Table) -> str:
        """Generate CREATE TABLE SQL statement."""
        columns_sql = []
        constraints_sql = []

        for column in table.columns:
            col_def = f"    {column.name} {column.type.value.upper()}"

            if not column.nullable:
                col_def += " NOT NULL"

            if column.default_value:
                col_def += f" DEFAULT {column.default_value}"

            if column.primary_key:
                col_def += " PRIMARY KEY"

            columns_sql.append(col_def)

        # Add constraints
        for constraint in table.constraints:
            if constraint.type == ConstraintType.FOREIGN_KEY:
                cols = ", ".join(constraint.columns)
                ref_cols = ", ".join(constraint.referenced_columns or [])
                constraints_sql.append(
                    f"    FOREIGN KEY ({cols}) REFERENCES {constraint.referenced_table}({ref_cols})"
                )

        all_definitions = columns_sql + constraints_sql
        definitions_str = ',\n'.join(all_definitions)
        return f"CREATE TABLE {table.name} (\n{definitions_str}\n);"

    def _to_sql(self, schema: Schema) -> str:
        """Convert schema to SQL."""
        statements = []

        for table in schema.tables:
            statements.append(self._generate_create_table_sql(table))
            statements.append("")  # Empty line between tables

        return "\n".join(statements)


# Global service instance
schema_management_service = SchemaManagementService()


