class InvalidUrlException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class InvalidUrlCheckException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class UrlCheckHttpFailedException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)
