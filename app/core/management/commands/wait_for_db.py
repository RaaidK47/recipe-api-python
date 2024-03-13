"""
Django command to wait for the database to be available.
"""

import time
from psycopg2 import OperationalError as Psycopg2OpError

from typing import Any
from django.db.utils import OperationalError
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Django command to wait for database."""

    def handle(self, *args: Any, **options: Any):
        """Entrypoint for command (wait_for_db)"""
        self.stdout.write('Waiting for database...')  # Standard Output to Log Things to Screen # noqa: E501
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])  # Exception Raised if DB is not ready # noqa: E501
                db_up = True
            except (Psycopg2OpError, OperationalError):
                self.stdout.write('Database unavailable, waiting 1 second...')
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS('Database available!'))
