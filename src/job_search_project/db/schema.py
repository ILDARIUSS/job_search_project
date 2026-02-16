from __future__ import annotations

from job_search_project.config import DBConfig
from job_search_project.db.db_utils import connect_db


def create_database(cfg: DBConfig) -> None:
    """
    Create database if not exists.
    We connect to 'postgres' service DB first, then CREATE DATABASE.
    """
    conn = connect_db(cfg, dbname_override="postgres")
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT 1 FROM pg_database WHERE datname = %s;", (cfg.dbname,))
            exists = cur.fetchone() is not None
            if not exists:
                cur.execute(f'CREATE DATABASE "{cfg.dbname}";')
    finally:
        conn.close()


def create_tables(cfg: DBConfig) -> None:
    """
    Create tables: employers and vacancies (FK one-to-many).
    По конспекту связь "один-ко-многим" реализуем через внешний ключ. :contentReference[oaicite:5]{index=5}
    """
    conn = connect_db(cfg)
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS employers (
                    employer_id BIGINT PRIMARY KEY,
                    name        VARCHAR(255) NOT NULL,
                    url         TEXT
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS vacancies (
                    vacancy_id     BIGINT PRIMARY KEY,
                    employer_id    BIGINT NOT NULL REFERENCES employers(employer_id) ON DELETE CASCADE,
                    name           VARCHAR(255) NOT NULL,
                    salary_from    INTEGER,
                    salary_to      INTEGER,
                    currency       VARCHAR(10),
                    url            TEXT NOT NULL
                );
                """
            )
        conn.commit()
    finally:
        conn.close()
