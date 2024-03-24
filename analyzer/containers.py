from analyzer.app import app
from analyzer.db import Database
from analyzer.services import UrlDbService, UrlCheckHttpService, UrlCheckDbService
from validators import UrlDbValidator, UrlCheckHttpValidator, UrlCheckDbValidator

database = Database(
    database_url=app.config["DATABASE_URL"]
)

url_db_validator = UrlDbValidator()
url_check_db_validator = UrlCheckDbValidator()
url_check_http_validator = UrlCheckHttpValidator()

url_db_service = UrlDbService(
    database=database,
    validator=url_db_validator
)


url_check_db_service = UrlCheckDbService(
    database=database,
    validator=url_check_db_validator
)

url_check_http_service = UrlCheckHttpService(
    validator=url_check_http_validator
)
