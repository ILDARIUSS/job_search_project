from __future__ import annotations

from job_search_project.api.hh_api import HHApiClient
from job_search_project.config import load_db_config
from job_search_project.db.schema import create_database, create_tables
from job_search_project.db.db_utils import connect_db, execute_many
from job_search_project.db.db_manager import DBManager
from job_search_project.utils import parse_salary


# Минимум 10 компаний по ТЗ.
# Можно заменить на свои employer_id с hh.ru
EMPLOYERS: list[int] = [
    1740,   # Яндекс
    3529,   # Сбер
    78638,  # Тинькофф (может отличаться)
    4181,   # VK (может отличаться)
    15478,  # Ozon (может отличаться)
    2180,   # Альфа-Банк (может отличаться)
    3776,   # МТС (может отличаться)
    3127,   # Ростелеком (может отличаться)
    67611,  # Skyeng (может отличаться)
    87021,  # Kaspersky (может отличаться)
]


def seed_data() -> None:
    """
    1) Создаём БД и таблицы
    2) Загружаем компании и вакансии с hh API
    3) Записываем в PostgreSQL
    """
    cfg = load_db_config()

    create_database(cfg)
    create_tables(cfg)

    api = HHApiClient()

    employers_rows: list[tuple[int, str, str | None]] = []
    vacancies_rows: list[tuple[int, int, str, int | None, int | None, str | None, str]] = []

    for employer_id in EMPLOYERS:
        emp = api.get_employer(employer_id)

        emp_id = int(emp["id"])
        emp_name = emp.get("name", "Unknown")
        emp_url = emp.get("alternate_url")

        employers_rows.append((emp_id, emp_name, emp_url))

        vacs = api.get_vacancies_by_employer(employer_id, per_page=100, pages=2)
        for v in vacs:
            salary_from, salary_to, currency = parse_salary(v.get("salary"))
            vacancies_rows.append(
                (
                    int(v["id"]),
                    emp_id,
                    v.get("name", "No title"),
                    salary_from,
                    salary_to,
                    currency,
                    v.get("alternate_url") or v.get("url", ""),
                )
            )

    conn = connect_db(cfg)
    try:
        execute_many(
            conn,
            """
            INSERT INTO employers (employer_id, name, url)
            VALUES (%s, %s, %s)
            ON CONFLICT (employer_id)
            DO UPDATE SET name = EXCLUDED.name, url = EXCLUDED.url;
            """,
            employers_rows,
        )

        execute_many(
            conn,
            """
            INSERT INTO vacancies (vacancy_id, employer_id, name, salary_from, salary_to, currency, url)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (vacancy_id)
            DO UPDATE SET
                employer_id = EXCLUDED.employer_id,
                name = EXCLUDED.name,
                salary_from = EXCLUDED.salary_from,
                salary_to = EXCLUDED.salary_to,
                currency = EXCLUDED.currency,
                url = EXCLUDED.url;
            """,
            vacancies_rows,
        )
    finally:
        conn.close()


def print_menu() -> None:
    print("\n=== job_search_project ===")
    print("1 — Создать БД/таблицы и загрузить данные (seed)")
    print("2 — Показать компании и кол-во вакансий")
    print("3 — Показать все вакансии")
    print("4 — Средняя зарплата")
    print("5 — Вакансии с зарплатой выше средней")
    print("6 — Поиск вакансий по ключевому слову")
    print("0 — Выход")


def main() -> None:
    cfg = load_db_config()
    manager = DBManager(cfg)

    while True:
        print_menu()
        choice = input("Выберите пункт: ").strip()

        if choice == "1":
            seed_data()
            print("Готово: данные загружены в БД.")
        elif choice == "2":
            rows = manager.get_companies_and_vacancies_count()
            for name, cnt in rows:
                print(f"{name}: {cnt}")
        elif choice == "3":
            rows = manager.get_all_vacancies()
            for company, vac, s_from, s_to, cur, url in rows:
                print(f"[{company}] {vac} | {s_from}-{s_to} {cur or ''} | {url}")
        elif choice == "4":
            avg = manager.get_avg_salary()
            print(f"Средняя зарплата (по расчетному значению): {avg:.2f}")
        elif choice == "5":
            rows = manager.get_vacancies_with_higher_salary()
            for company, vac, s_from, s_to, cur, url in rows:
                print(f"[{company}] {vac} | {s_from}-{s_to} {cur or ''} | {url}")
        elif choice == "6":
            kw = input("Введите ключевое слово: ").strip()
            rows = manager.get_vacancies_with_keyword(kw)
            for company, vac, s_from, s_to, cur, url in rows:
                print(f"[{company}] {vac} | {s_from}-{s_to} {cur or ''} | {url}")
        elif choice == "0":
            break
        else:
            print("Неизвестная команда.")


if __name__ == "__main__":
    main()
