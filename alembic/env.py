from __future__ import annotations
from logging.config import fileConfig
from alembic import context
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app.db import engine
from sqlmodel import SQLModel

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = SQLModel.metadata

def run_migrations_offline():
    context.configure(
        url=str(engine.url),
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    connectable = engine
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()