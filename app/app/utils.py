import importlib
import random
import string
import uuid
from collections import defaultdict, namedtuple
from contextlib import contextmanager
from typing import Iterator
from urllib.parse import urlsplit, urlunsplit

import sqlalchemy as sa
from alembic.config import Config

from .settings import settings


def make_alembic_config(
    dsn: str, script_location: str | None = None
) -> Config:
    """
    Make alembic config for tests
    """
    alembic_cfg = Config(f"{settings.ROOT_DIR}/alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    if script_location:
        alembic_cfg.set_main_option(
            "script_location", f"{script_location}:migrations"
        )

    return alembic_cfg


def create_database(
    url: str, encoding: str = "utf8", template: str = "template1"
) -> None:
    """
    Create database for tests
    """
    db_url = urlsplit(url)
    postgres_db_url = urlunsplit(db_url._replace(path="/postgres"))
    engine = sa.create_engine(postgres_db_url, isolation_level="AUTOCOMMIT")
    with engine.begin() as conn:
        text = (
            f"CREATE DATABASE {db_url.path[1:]} ENCODING '{encoding}'"
            f"TEMPLATE {template}"
        )

        conn.execute(sa.text(text))
    engine.dispose()


def drop_database(url: str) -> None:
    db_url = urlsplit(url)
    postgres_db_url = urlunsplit(db_url._replace(path="/postgres"))
    engine = sa.create_engine(postgres_db_url, isolation_level="AUTOCOMMIT")
    with engine.begin() as conn:
        text = f"""
            SELECT pg_terminate_backend(pg_stat_activity.pid)
            FROM pg_stat_activity
            WHERE pg_stat_activity.datname = '{db_url.path[1:]}'
            AND pid <> pg_backend_pid();
            """
        conn.execute(sa.text(text))
        text = f"DROP DATABASE {db_url.path[1:]}"
        conn.execute(sa.text(text))


@contextmanager
def tmp_database(str_url: str, suffix: str = "", **kwargs) -> Iterator[str]:
    tmp_db_name = "_".join(
        [
            f"{random.choice(string.ascii_lowercase)}{uuid.uuid4().hex}",
            "temp_db",
            suffix,
        ]
    )
    tmp_db_url = urlsplit(str_url)
    str_url = urlunsplit(tmp_db_url._replace(path=f"/{tmp_db_name}"))
    create_database(str_url, **kwargs)

    try:
        yield str_url
    finally:
        drop_database(str_url)


# Represents test for 'data' migration.
# Contains revision to be tested, it's previous revision, and callbacks that
# could be used to perform validation.
MigrationValidationParamsGroup = namedtuple(
    "MigrationData",
    ["rev_base", "rev_head", "on_init", "on_upgrade", "on_downgrade"],
)


def load_migration_as_module(file: str):
    """
    Allows to import alembic migration as a module.
    """
    # pylint: disable=W4902,E1120
    return importlib.machinery.SourceFileLoader(
        file, str(settings.ROOT_DIR / "alembic" / "versions" / file)
    ).load_module()


def make_validation_params_groups(
    *migrations,
) -> list[MigrationValidationParamsGroup]:
    """
    Creates objects that describe test for data migrations.
    See examples in tests/data_migrations/migration_*.py.
    """
    data = []
    for migration in migrations:

        # Ensure migration has all required params
        for required_param in ["rev_base", "rev_head"]:
            if not hasattr(migration, required_param):
                raise RuntimeError(
                    f"{required_param} not specified for {migration.__name__}"
                )

        # Set up callbacks
        # pylint: disable=C0301
        callbacks = defaultdict(lambda: lambda *args, **kwargs: None)  # type: ignore
        for callback in ["on_init", "on_upgrade", "on_downgrade"]:
            if hasattr(migration, callback):
                callbacks[callback] = getattr(migration, callback)

        data.append(
            MigrationValidationParamsGroup(
                rev_base=migration.rev_base,
                rev_head=migration.rev_head,
                on_init=callbacks["on_init"],
                on_upgrade=callbacks["on_upgrade"],
                on_downgrade=callbacks["on_downgrade"],
            )
        )

    return data
