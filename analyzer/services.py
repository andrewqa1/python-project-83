from datetime import datetime

import psycopg2.errors
import requests
from bs4 import BeautifulSoup
from analyzer.models import Url, UrlCheck, UrlCheckId, UrlId, UrlWithLastCheck
from analyzer.validators import UrlCheckDbValidator, UrlCheckHttpValidator, UrlDbValidator

from analyzer.db import Database
from analyzer.exceptions import (
    InvalidUrlCheckException,
    InvalidUrlException,
    UrlCheckHttpFailedException,
)


class UrlDbService:
    def __init__(self, database: Database, validator: UrlDbValidator) -> None:
        self.database = database
        self.validator = validator

    def create_url(self, url: str) -> UrlId | None:
        if self.validator.validate(url):
            try:
                query = f"INSERT INTO urls (name, created_at) VALUES ('{url}', '{datetime.now()}') RETURNING id;"
                returned = self.database.fetch_val(query=query)
            except psycopg2.IntegrityError as exc:
                raise InvalidUrlException(detail=f"URL {url} already exists!") from exc
            else:
                return returned.id
        else:
            raise InvalidUrlException(detail=f"Invalid URL {url} format!")

    def list_urls(self) -> list[Url]:
        query = "SELECT id, name, created_at FROM urls;"
        returned_urls = self.database.fetch_many(query=query)
        return [
            Url(id=url.id, name=url.name, created_at=url.created_at)
            for url in returned_urls
        ]

    def get_url(self, ind: int) -> Url | None:
        query = f"SELECT id, name, created_at FROM urls WHERE id = {ind}"
        returned_url = self.database.fetch_val(query=query)
        return (
            Url(
                id=returned_url.id,
                name=returned_url.name,
                created_at=returned_url.created_at,
            )
            if returned_url
            else None
        )

    def list_urls_with_checks(self) -> list[UrlWithLastCheck]:
        query = (
            "SELECT u.id, u.name, json_agg(json_build_object("
            "'status_code', uc.status_code, 'check_date', uc.created_at)) AS checks FROM urls u LEFT JOIN "
            "url_checks uc ON uc.url_id = u.id GROUP BY u.id"
        )
        returned_urls = self.database.fetch_many(query=query)
        urls_with_checks = []
        for returned_url in returned_urls:
            sorted_checks = sorted(returned_url.checks, key=lambda e: e["check_date"])
            urls_with_checks.append(
                UrlWithLastCheck(
                    id=returned_url.id,
                    name=returned_url.name,
                    last_check_date=sorted_checks[-1]["check_date"],
                    status_code=sorted_checks[-1]["status_code"],
                )
            )
        return urls_with_checks


class UrlCheckDbService:
    def __init__(self, database: Database, validator: UrlCheckDbValidator) -> None:
        self.database = database
        self.validator = validator

    def create_url_check(self, url_id: int, url_check: dict) -> UrlCheckId | None:
        if self.validator.validate(url_check):
            description = url_check["description"].replace("'", '"')
            h1 = url_check["h1"].replace("'", '"')
            title = url_check["title"].replace("'", '"')
            try:
                query = (
                    f"INSERT INTO url_checks (url_id, status_code, h1, title, description, created_at) "
                    f"VALUES ({url_id}, {url_check['status_code']}, '{h1}', '{title}', "
                    f"'{description}', '{datetime.now()}') RETURNING id;"
                )
                returned = self.database.fetch_val(query=query)
            except psycopg2.Error as exc:
                raise InvalidUrlCheckException(
                    detail=f"Error inserting url check!"
                ) from exc
            else:
                return returned.id
        else:
            raise InvalidUrlCheckException(
                detail=f"Invalid url check {url_check} format!"
            )

    def get_url_checks(self, url_id: int) -> list[UrlCheck] | None:
        query = (
            f"SELECT id, url_id, status_code, h1, title, description, created_at "
            f"FROM url_checks WHERE url_id = {url_id}"
        )
        returned_url_checks = self.database.fetch_many(query=query)
        return [
            UrlCheck(
                id=returned_url_check.id,
                url_id=returned_url_check.url_id,
                status_code=returned_url_check.status_code,
                title=returned_url_check.title,
                description=returned_url_check.description,
                created_at=returned_url_check.created_at,
                h1=returned_url_check.h1,
            )
            for returned_url_check in returned_url_checks
        ]


class UrlCheckHttpService:
    def __init__(self, validator: UrlCheckHttpValidator) -> None:
        self.validator = validator

    def get_page_data(self, url: str) -> dict:
        if self.validator.validate(url):
            response = requests.get(url)
            soup = BeautifulSoup(response.text, "html.parser")

            title = soup.find("title").text if soup.find("title") else ""
            h1 = soup.find("h1").text if soup.find("h1") else ""
            description = soup.find("meta", attrs={"name": "description"})
            content_description = description["content"] if description else ""

            return {
                "status_code": response.status_code,
                "title": title[:255],
                "description": content_description[:255],
                "h1": h1[:255],
            }

        else:
            raise UrlCheckHttpFailedException(detail=f"Check for {url} failed!")
