import os
from dotenv import load_dotenv

load_dotenv()


def load_settings(app, settings) -> None:
    for setting, value in settings.items():
        app.config[setting] = value


SETTINGS_CONFIG = {
    "SECRET_KEY": os.environ.get("SECRET_KEY", default=""),
    "DATABASE_URL": os.environ.get("DATABASE_URL", default=""),
    "DEBUG": os.environ.get("DEBUG", default=False)
}
