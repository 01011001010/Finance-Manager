import os
from typing import Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel  # TODO look more into validation
import psycopg2 as dbAdapter
from psycopg2 import errors as dbErrors
from contextlib import contextmanager


DB_USER = os.getenv("DB_FASTAPI_USER")
assert DB_USER is not None, "Backend container missing DB_FASTAPI_USER value"
DB_PASS = os.getenv("DB_FASTAPI_PASSWORD")
assert DB_PASS is not None, "Backend container missing DB_FASTAPI_PASSWORD value"
DB = os.getenv("DB_NAME")
assert DB is not None, "Backend container missing DB_NAME value"
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


class DeltaIn(BaseModel):
    ts: str  # ISO date from frontend
    subtitle: str | None = None
    amount: float
    id_a: int
    tag: int | None = None


class TransactionWithDelta(BaseModel):
    title: str
    delta: DeltaIn


class AddingDelta(BaseModel):
    id_t: int
    delta: DeltaIn


class AddingTag(BaseModel):
    tag_name: str


class PinId(BaseModel):
    id_t: int


app = FastAPI()


@app.post("/transactions/new")
def addNewTransaction(payload: TransactionWithDelta) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                # 1. Insert transaction
                cur.execute("""INSERT INTO transactions (title)
                               VALUES (%s)
                               RETURNING id_t;""",
                            (payload.title,))
                (id_t,) = cur.fetchone() or (None,)

                # 2. Insert delta
                cur.execute("""INSERT INTO deltas (ts, amount, id_a, tag, subtitle)
                               VALUES (%s, %s, %s, %s, %s)
                               RETURNING id_d;""",
                            (payload.delta.ts,
                             payload.delta.amount,
                             payload.delta.id_a,
                             payload.delta.tag,
                             payload.delta.subtitle))
                (id_d,) = cur.fetchone() or (None,)

                # 3. Link delta to transaction
                cur.execute("""INSERT INTO deltasPerTransaction (id_t, id_d)
                               VALUES (%s, %s);""",
                            (id_t, id_d))

                return {"status": "ok",
                        "detail": f"Transaction {id_t} and {id_d} added and linked"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/transactions/existing")
def addDeltaToExistingTransaction(payload: AddingDelta) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                # 1. Insert delta
                cur.execute("""INSERT INTO deltas (ts, amount, id_a, tag, subtitle)
                               VALUES (%s, %s, %s, %s, %s)
                               RETURNING id_d;""",
                            (payload.delta.ts,
                             payload.delta.amount,
                             payload.delta.id_a,
                             payload.delta.tag,
                             payload.delta.subtitle))
                (id_d,) = cur.fetchone() or (None,)

                # 2. Link delta to transaction
                cur.execute("""INSERT INTO deltasPerTransaction (id_t, id_d)
                               VALUES (%s, %s);""",
                            (payload.id_t, id_d))

                return {"status": "ok",
                        "detail": f"Transaction {payload.id_t} linked to delta {id_d}"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


def pinUnpin(payload: PinId, insert: bool):
    QUERY = ("""INSERT INTO pinnedTransactions (id_t)
                VALUES (%s);"""
             if insert else
             """DELETE FROM pinnedTransactions
                WHERE id_t = %s;""")
    UN = "" if insert else "un"

    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute(QUERY,
                            (payload.id_t,))

                return {"status": "ok",
                        "detail": f"Transaction {payload.id_t} {UN}pinned successfully"}

    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/transactions/pin")
def pinTransaction(payload: PinId) -> dict[str, str]:
    return pinUnpin(payload, True)


@app.post("/transactions/unpin")
def unpinTransaction(payload: PinId) -> dict[str, str]:
    return pinUnpin(payload, False)


@app.post("/add/tag")
def addTag(payload: AddingTag) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO tags (tag_name)
                               VALUES (%s)
                               RETURNING tag;""",
                            (payload.tag_name,))
                (tag,) = cur.fetchone() or (None,)

                return {"status": "ok",
                        "detail": f"Tag {payload.tag_name} added under id {tag}"}
    except dbErrors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag '{payload.tag_name}' already exists."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/accounts")
def getAccounts() -> list[dict[str, Any]] | dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT a.id_a,
                                      a.currency,
                                      a.account
                               FROM accounts a;""")
                rows = cur.fetchall()

        return [{"id_a": id_a,
                 "currency": currency,  # TODO swap for €, $, ... ?
                 "account": name}
                for id_a, currency, name in rows]
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/tags")
def getTags() -> list[dict[str, Any]] | dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT t.tag,
                                      t.tag_name
                               FROM tags t;""")
                rows = cur.fetchall()
        return [{"tag": tag,
                 "tag_name": name}
                for tag, name in rows]
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/pinned")
def getPinned() -> list[int] | dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT p.id_t
                               FROM pinnedTransactions p;""")
                rows = cur.fetchall()
        return [int(id_t) for (id_t,) in rows]
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/transactions")
def getTransactions():
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT t.id_t,
                                      t.title,
                                      d.subtitle,
                                      tags.tag_name,
                                      d.id_d,
                                      d.amount,
                                      a.currency,
                                      a.account,
                                      d.ts,
                                      d.ts_log
                               FROM transactions t
                               JOIN deltasPerTransaction dt ON dt.id_t = t.id_t
                               JOIN deltas d ON d.id_d = dt.id_d
                               JOIN accounts a ON a.id_a = d.id_a
                               LEFT JOIN tags ON tags.tag = d.tag
                               ORDER BY t.id_t, d.id_d;""")
                rows = cur.fetchall()

        transactions = {}
        for id_t, title, subtitle, tag, id_d, amount, curr, account, ts, ts_log in rows:
            if id_t not in transactions:
                transactions[id_t] = {"id": id_t,
                                      "title": title,
                                      "subtitle": subtitle,
                                      "deltas": []}

            transactions[id_t]["deltas"].append({"id": id_d,
                                                 "amount": str(amount),  # TODO float ?
                                                 "currency": curr,  # TODO swap € ?
                                                 "account": account,
                                                 "tag": tag,
                                                 "ts": ts.isoformat() if ts else None,
                                                 "ts_log": (ts_log.isoformat()
                                                            if ts_log else
                                                            None)})

        return list(transactions.values())
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.get("/deltaLog")
def getDeltaLog():
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT t.id_t,
                                      t.title,
                                      d.subtitle,
                                      tags.tag_name,
                                      d.id_d,
                                      d.amount,
                                      a.currency,
                                      a.account,
                                      d.ts,
                                      d.ts_log
                               FROM transactions t
                               JOIN deltasPerTransaction dt ON dt.id_t = t.id_t
                               JOIN deltas d ON d.id_d = dt.id_d
                               JOIN accounts a ON a.id_a = d.id_a
                               LEFT JOIN tags ON tags.tag = d.tag
                               ORDER BY d.ts_log;""")
                rows = cur.fetchall()

        transactions = []
        for id_t, title, subtitle, tag, id_d, amount, curr, account, ts, ts_log in rows:
            if not len(transactions) or id_t != transactions[-1]:
                transactions.append({"id": id_t,
                                     "title": title,
                                     "deltas": []})

            transactions[-1]["deltas"].append({"id": id_d,
                                               "subtitle": subtitle,
                                               "amount": str(amount),  # TODO float ?
                                               "currency": curr,  # TODO swap € ?
                                               "account": account,
                                               "tag": tag,
                                               "ts": ts.isoformat() if ts else None,
                                               "ts_log": (ts_log.isoformat()
                                                          if ts_log else
                                                          None)})

        return transactions
    except Exception as e:
        return {"status": "error", "detail": str(e)}
