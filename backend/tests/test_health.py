import unittest

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.main import health_db


class DatabaseHealthTests(unittest.TestCase):
    def test_health_db_counts_sqlite_tables(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            with engine.begin() as connection:
                connection.exec_driver_sql("CREATE TABLE vehicles (id INTEGER PRIMARY KEY)")
                connection.exec_driver_sql("CREATE TABLE events (id INTEGER PRIMARY KEY)")

            with Session(engine) as session:
                self.assertEqual(
                    health_db(session),
                    {"status": "connected", "tables_found": 2},
                )
        finally:
            engine.dispose()


if __name__ == "__main__":
    unittest.main()
