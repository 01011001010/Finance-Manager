import os
import psycopg2 as dbAdapter
from contextlib import contextmanager


DB_USER = os.getenv("POSTGRES_USER")
assert DB_USER is not None, "Backend container missing POSTGRES_USER value"
DB_PASS = os.getenv("POSTGRES_PASSWORD")
assert DB_PASS is not None, "Backend container missing POSTGRES_PASSWORD value"
DB = os.getenv("POSTGRES_DB")
assert DB is not None, "Backend container missing POSTGRES_DB value"
DB_HOST = os.getenv("DB_HOST")
assert DB_HOST is not None, "Backend container missing DB_HOST value"


def connectToDB():
    return dbAdapter.connect(
        host=DB_HOST,
        database=DB,
        user=DB_USER,
        password=DB_PASS
    )


@contextmanager
def dbSession():
    conn = connectToDB()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
