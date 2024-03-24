from datetime import datetime
from typing import TypeAlias, TypedDict

UrlId: TypeAlias = int
UrlCheckId: TypeAlias = int


class Url(TypedDict):
    id: UrlId
    name: str
    created_at: datetime


class UrlWithLastCheck(TypedDict):
    id: UrlId
    name: str
    last_check_date: datetime | None
    status_code: int | None


class UrlCheck(TypedDict):
    id: UrlCheckId
    url_id: UrlId
    status_code: int
    h1: str
    title: str
    description: str
    created_at: datetime
