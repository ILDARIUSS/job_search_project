from __future__ import annotations

from typing import Any


class Vacancy:
    """
    Простая модель вакансии.
    Не используем dataclass — делаем обычный класс (часто требуют в проверках).
    """

    __slots__ = (
        "vacancy_id",
        "employer_id",
        "name",
        "salary_from",
        "salary_to",
        "currency",
        "url",
    )

    def __init__(
        self,
        vacancy_id: int,
        employer_id: int,
        name: str,
        salary_from: int | None,
        salary_to: int | None,
        currency: str | None,
        url: str,
    ) -> None:
        self.vacancy_id = vacancy_id
        self.employer_id = employer_id
        self.name = name
        self.salary_from = salary_from
        self.salary_to = salary_to
        self.currency = currency
        self.url = url

    def to_dict(self) -> dict[str, Any]:
        return {
            "vacancy_id": self.vacancy_id,
            "employer_id": self.employer_id,
            "name": self.name,
            "salary_from": self.salary_from,
            "salary_to": self.salary_to,
            "currency": self.currency,
            "url": self.url,
        }
