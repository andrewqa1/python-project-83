from urllib.parse import urlparse

import requests
from requests.exceptions import RequestException


class UrlDbValidator:
    def __init__(self) -> None:
        self.validator = urlparse

    def validate(self, url: str) -> bool:
        return bool(self.validator(url).scheme) and url


class UrlCheckHttpValidator:

    def __init__(self) -> None:
        self.validator = requests.get

    def validate(self, url: str) -> bool:
        try:
            self.validator(url).raise_for_status()
        except RequestException:
            return False
        else:
            return True


class UrlCheckDbValidator:
    def validate(self, url_check: dict) -> bool:
        try:
            is_valid_status = isinstance(url_check["status_code"], int) and (
                100 <= url_check["status_code"] <= 526
            )
            is_valid_description = isinstance(url_check["description"], str)
            is_valid_h1 = isinstance(url_check["h1"], str)
            is_valid_title = isinstance(url_check["title"], str)

        except KeyError:
            return False
        else:
            return all(
                [is_valid_status, is_valid_description, is_valid_title, is_valid_h1]
            )
