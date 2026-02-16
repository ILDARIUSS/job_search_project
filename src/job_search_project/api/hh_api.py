from __future__ import annotations

from typing import Any

import requests


HH_API_BASE = "https://api.hh.ru"


class HHApiClient:
    """Client for public hh.ru API (via requests). :contentReference[oaicite:8]{index=8}"""

    def __init__(self, timeout: int = 15) -> None:
        self._timeout = timeout
        self._session = requests.Session()

    def get_employer(self, employer_id: int) -> dict[str, Any]:
        r = self._session.get(
            f"{HH_API_BASE}/employers/{employer_id}",
            timeout=self._timeout,
        )
        r.raise_for_status()
        return r.json()

    def get_vacancies_by_employer(self, employer_id: int, per_page: int = 100, pages: int = 2) -> list[dict[str, Any]]:
        """
        Fetch vacancies for employer by search endpoint.
        pages=2 обычно хватает для демонстрации проекта; можно увеличить.
        """
        all_items: list[dict[str, Any]] = []
        for page in range(pages):
            r = self._session.get(
                f"{HH_API_BASE}/vacancies",
                params={
                    "employer_id": employer_id,
                    "per_page": per_page,
                    "page": page,
                },
                timeout=self._timeout,
            )
            r.raise_for_status()
            data = r.json()
            items = data.get("items", [])
            if not items:
                break
            all_items.extend(items)
        return all_items
