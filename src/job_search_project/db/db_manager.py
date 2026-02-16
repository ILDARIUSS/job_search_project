from __future__ import annotations

from typing import Any

from job_search_project.config import DBConfig
from job_search_project.db.db_utils import connect_db


class DBManager:
    """
    Класс для работы с данными в БД.
    Методы требуются заданием курсового проекта. :contentReference[oaicite:9]{index=9}
    """

    def __init__(self, cfg: DBConfig) -> None:
        self._cfg = cfg

    def get_companies_and_vacancies_count(self) -> list[tuple[str, int]]:
        """Получает список всех компаний и количество вакансий у каждой компании."""
        conn = connect_db(self._cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name, COUNT(v.vacancy_id) AS вакансий
                    FROM employers e
                    LEFT JOIN vacancies v ON v.employer_id = e.employer_id
                    GROUP BY e.employer_id, e.name
                    ORDER BY вакансий DESC;
                    """
                )
                return cur.fetchall()
        finally:
            conn.close()

    def get_all_vacancies(self) -> list[tuple[str, str, int | None, int | None, str | None, str]]:
        """
        Получает список всех вакансий:
        название компании, название вакансии, зарплата_from, зарплата_to, валюта, ссылка.
        В критериях указано, что тут должен быть JOIN. :contentReference[oaicite:10]{index=10}
        """
        conn = connect_db(self._cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name,
                           v.name,
                           v.salary_from,
                           v.salary_to,
                           v.currency,
                           v.url
                    FROM vacancies v
                    INNER JOIN employers e ON e.employer_id = v.employer_id
                    ORDER BY e.name, v.name;
                    """
                )
                return cur.fetchall()
        finally:
            conn.close()

    def get_avg_salary(self) -> float:
        """
        Получает среднюю зарплату по вакансиям.
        В критериях указано использование AVG. :contentReference[oaicite:11]{index=11}
        """
        conn = connect_db(self._cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT AVG(salary_value) 
                    FROM (
                        SELECT 
                            CASE
                                WHEN salary_from IS NOT NULL AND salary_to IS NOT NULL THEN (salary_from + salary_to) / 2.0
                                WHEN salary_from IS NOT NULL THEN salary_from
                                WHEN salary_to IS NOT NULL THEN salary_to
                                ELSE NULL
                            END AS salary_value
                        FROM vacancies
                    ) t
                    WHERE salary_value IS NOT NULL;
                    """
                )
                res = cur.fetchone()
                return float(res[0]) if res and res[0] is not None else 0.0
        finally:
            conn.close()

    def get_vacancies_with_higher_salary(self) -> list[tuple[str, str, int | None, int | None, str | None, str]]:
        """
        Получает вакансии, у которых зарплата выше средней по всем вакансиям.
        """
        avg_salary = self.get_avg_salary()
        conn = connect_db(self._cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name,
                           v.name,
                           v.salary_from,
                           v.salary_to,
                           v.currency,
                           v.url
                    FROM vacancies v
                    INNER JOIN employers e ON e.employer_id = v.employer_id
                    WHERE
                        CASE
                            WHEN v.salary_from IS NOT NULL AND v.salary_to IS NOT NULL THEN (v.salary_from + v.salary_to) / 2.0
                            WHEN v.salary_from IS NOT NULL THEN v.salary_from
                            WHEN v.salary_to IS NOT NULL THEN v.salary_to
                            ELSE NULL
                        END > %s
                    ORDER BY e.name, v.name;
                    """,
                    (avg_salary,),
                )
                return cur.fetchall()
        finally:
            conn.close()

    def get_vacancies_with_keyword(self, keyword: str) -> list[tuple[str, str, int | None, int | None, str | None, str]]:
        """
        Получает вакансии, в названии которых содержатся переданные слова (LIKE).
        В критериях прямо указан LIKE. :contentReference[oaicite:12]{index=12} :contentReference[oaicite:13]{index=13}
        """
        pattern = f"%{keyword.strip()}%"
        conn = connect_db(self._cfg)
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT e.name,
                           v.name,
                           v.salary_from,
                           v.salary_to,
                           v.currency,
                           v.url
                    FROM vacancies v
                    INNER JOIN employers e ON e.employer_id = v.employer_id
                    WHERE v.name ILIKE %s
                    ORDER BY e.name, v.name;
                    """,
                    (pattern,),
                )
                return cur.fetchall()
        finally:
            conn.close()
