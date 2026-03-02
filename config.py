# config.py

import os


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///tasks.db"  # default local dev
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    