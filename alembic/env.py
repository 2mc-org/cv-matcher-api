from logging.config import fileConfig

# Import SQLAlchemy
from sqlalchemy import engine_from_config, pool
from sqlalchemy.schema import SchemaItem
from sqlmodel import SQLModel

# Import SQLModel
from alembic import context
from app.core.environments import environments
from app.interrupt_registry.models.base import InterruptRegistry

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the database URL from our settings
config.set_main_option(
    "sqlalchemy.url", environments.get_db_url(async_driver=False)
)

# add your model's MetaData object here
# for 'autogenerate' support
# target_metadata: None = None
target_metadata = SQLModel.metadata

# LangGraph Postgres checkpointer tables (not in SQLModel metadata).
LANGGRAPH_CHECKPOINT_TABLES = frozenset({
    "checkpoints",
    "checkpoint_blobs",
    "checkpoint_writes",
    "checkpoint_migrations",
})


def include_object(
    object: SchemaItem,
    name: str | None,
    type_: str,
    reflected: bool,
    compare_to: SchemaItem | None,
) -> bool:
    """Exclude LangGraph checkpoint tables from autogenerate."""
    if type_ == "table" and name in LANGGRAPH_CHECKPOINT_TABLES:
        return False

    if type_ == "index":
        table_name = getattr(getattr(object, "table", None), "name", None)
        if table_name in LANGGRAPH_CHECKPOINT_TABLES:
            return False

    return True


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    # Create engine with explicit driver
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
