class BaseUrlException(Exception):
    def __init__(self, detail: str) -> None:
        super().__init__(detail)


class InvalidUrlException(BaseUrlException):
    pass


class InvalidUrlInsertionException(BaseUrlException):
    pass


class InvalidUrlCheckException(BaseUrlException):
    pass


class InvalidUrlCheckInsertionException(BaseUrlException):
    pass


class UrlCheckHttpFailedException(BaseUrlException):
    pass
