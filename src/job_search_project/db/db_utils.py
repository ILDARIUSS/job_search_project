from __future__ import annotations

from typing import Any, Iterable

import psycopg2
from psycopg2.extensions import connection as PGConnection

from job_search_project.config import DBConfig


def connect_db(cfg: DBConfig, dbname_override: str | None = None) -> PGConnection:
    """
    Create PostgreSQL connection.

    ВАЖНО (Windows):
    Иногда libpq/сервер возвращают сообщения в CP1251 (русская локаль),
    а psycopg2 пытается декодировать как UTF-8 -> UnicodeDecodeError.
    Поэтому:
    - принудительно задаем client_encoding=UTF8
    - просим сервер отдавать сообщения в 'C' (англ/ASCII) если возможно
    """
    try:
        return psycopg2.connect(
            host=cfg.host,
            port=cfg.port,
            dbname=dbname_override or cfg.dbname,
            user=cfg.user,
            password=cfg.password,
            options="-c client_encoding=UTF8 -c lc_messages=C",
        )
    except UnicodeDecodeError as e:
        raise RuntimeError(
            "Не удалось подключиться к PostgreSQL. Реальная ошибка подключения скрылась из-за "
            "проблемы декодирования (русская локаль/CP1251). Проверь: запущен ли PostgreSQL, "
            "верны ли DB_HOST/DB_PORT/DB_USER/DB_PASSWORD в .env."
        ) from e


def execute_many(conn: PGConnection, query: str, rows: Iterable[tuple[Any, ...]]) -> None:
    """Execute INSERT/UPDATE with many rows."""
    with conn.cursor() as cur:
        cur.executemany(query, list(rows))
    conn.commit()
