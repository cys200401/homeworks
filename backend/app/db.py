from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Iterator

from psycopg import Connection, connect
from psycopg.rows import dict_row


def get_database_url() -> str:
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")
    return database_url


@contextmanager
def get_connection() -> Iterator[Connection]:
    connection = connect(get_database_url(), row_factory=dict_row)
    try:
        yield connection
    finally:
        connection.close()


def ping_database() -> bool:
    with get_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute("select 1")
            return cursor.fetchone() is not None
