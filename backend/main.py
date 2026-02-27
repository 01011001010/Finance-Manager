import os
from typing import Any
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel  # TODO look more into validation
import psycopg2 as dbAdapter
from psycopg2 import errors as dbErrors
from psycopg2.sql import SQL, Identifier
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


class settingPin(BaseModel):
    id_t: int
    newPin: bool


class AddingAccount(BaseModel):
    ts: str  # ISO date from frontend
    name: str
    currency: str
    balance: float


class Archiving(BaseModel):
    id: int
    newArchivedState: bool


app = FastAPI()


@app.post("/add/transaction")
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post("/add/delta")
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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post("/add/account")
def addAccount(payload: AddingAccount) -> dict[str, str]:
    # DEV
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO accounts (account, currency, opened_ts,
                                                     opening_balance)
                               VALUES (%s, %s, %s, %s)
                               RETURNING id_a;""",
                            (payload.name, payload.currency, payload.ts,
                             payload.balance))
                (id_a,) = cur.fetchone() or (None,)

                return {"status": "ok",
                        "detail": (f"Account {payload.name} ({payload.currency}) added "
                                   f"under id {id_a}")}
    except dbErrors.UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Account '{payload.name} ({payload.currency})' already exists."
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


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
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Tag '{payload.tag_name}' already exists.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


def archive(table: str, col: str, id: int, newState: bool, name: str) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                query = SQL("""UPDATE {tbl}
                            SET archived = %s
                            WHERE {col} = %s;""").format(
                    tbl=Identifier(table),
                    col=Identifier(col)
                )
                cur.execute(query, (newState, id))
                message = "archived" if newState else "restored"
                return {"status": "ok",
                        "detail": f"{name} {id} {message}"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.post("/update/archive/tag")
def archiveTag(payload: Archiving) -> dict[str, str]:
    return archive("tags", "tag", payload.id, payload.newArchivedState, "Tag")


@app.post("/update/archive/account")
def archiveAccount(payload: Archiving) -> dict[str, str]:
    return archive("accounts", "id_a", payload.id, payload.newArchivedState, "Account")


@app.post("/update/pin")
def setPin(payload: settingPin) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""UPDATE transactions
                               SET pinned = %s
                               WHERE id_t = %s;""", (payload.newPin, payload.id_t))
                un = "" if payload.newPin else "un"
                return {"status": "ok",
                        "detail": f"Transaction {payload.id_t} {un}pinned successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/data/accounts")
def getAccounts() -> dict[str, str | list[dict[str, Any]]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT a.id_a,
                                      a.currency,
                                      a.account,
                                      a.archived
                               FROM accounts a
                               ORDER BY a.id_a ASC;""")
                rows = cur.fetchall()

        return {"status": "ok",
                "data": [{"id_a": id_a,
                          "currency": currency,
                          "account": name,
                          "hidden": hidden}
                         for id_a, currency, name, hidden in rows]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/data/tags")
def getTags() -> dict[str, str | list[dict[str, Any]]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT t.tag,
                                      t.tag_name,
                                      t.archived
                               FROM tags t
                               ORDER BY t.tag ASC;""")
                rows = cur.fetchall()
        return {"status": "ok",
                "data": [{"tag": tag,
                          "tag_name": name,
                          "hidden": hidden}
                         for tag, name, hidden in rows]}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/data/pinned")
def getPinned() -> dict[str, str | list[Any]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_t,
                                      title,
                                      pinned,
                                      subtitle,
                                      tag_name,
                                      id_d,
                                      amount,
                                      currency,
                                      account,
                                      ts,
                                      ts_log,
                                      balance_after
                               FROM completeDeltaInfo
                               WHERE pinned
                               ORDER BY ts DESC;""")
                rows = cur.fetchall()

        transactions = {}
        for id_t, title, pin, subt, tag, id_d, amount, curr, acc, ts, ts_log, b in rows:
            if id_t not in transactions:
                transactions[id_t] = {"id_t": id_t,
                                      "title": title,
                                      "pinned": pin,
                                      "deltas": []}

            transactions[id_t]["deltas"].append({"id_d": id_d,
                                                 "subtitle": subt,
                                                 "amount": float(amount),
                                                 "balance_after": float(b),
                                                 "currency": curr,
                                                 "account": acc,
                                                 "tag": tag,
                                                 "ts": ts.isoformat() if ts else None,
                                                 "ts_log": ts_log.isoformat()})

        return {"status": "ok", "data": list(transactions.values())}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/data/overview")
def getTransactionOverview() -> dict[str, str | list[Any]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_t,
                                      title,
                                      pinned,
                                      subtitle,
                                      tag_name,
                                      id_d,
                                      amount,
                                      currency,
                                      account,
                                      ts,
                                      ts_log,
                                      balance_after
                               FROM completeDeltaInfo
                               ORDER BY ts DESC;""")
                rows = cur.fetchall()

        transactions = {}
        data = []
        for id_t, title, pin, subt, tag, id_d, amount, curr, acc, ts, ts_log, b in rows:
            if id_t not in transactions:
                transactions[id_t] = {"id_t": id_t,
                                      "title": title,
                                      "pinned": pin,
                                      "deltas": []}

            transactions[id_t]["deltas"].append({"id_d": id_d,
                                                 "subtitle": subt,
                                                 "amount": float(amount),
                                                 "balance_after": float(b),
                                                 "currency": curr,
                                                 "account": acc,
                                                 "tag": tag,
                                                 "ts": ts.isoformat() if ts else None,
                                                 "ts_log": (ts_log.isoformat()
                                                            if ts_log else
                                                            None)})
            if not len(data) or id_t != data[-1]["id_t"]:
                data.append(transactions[id_t])

        return {"status": "ok", "data": data}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@app.get("/data/deltas")
def getDeltaLog() -> dict[str, str | list[Any]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT id_t,
                                      title,
                                      pinned,
                                      subtitle,
                                      tag_name,
                                      id_d,
                                      amount,
                                      currency,
                                      account,
                                      ts,
                                      ts_log,
                                      balance_after
                               FROM completeDeltaInfo
                               ORDER BY ts DESC;""")
                rows = cur.fetchall()

        transactions = []
        for id_t, title, pin, subt, tag, id_d, amount, curr, acc, ts, ts_log, b in rows:
            if not len(transactions) or id_t != transactions[-1]["id_t"]:
                transactions.append({"id_t": id_t,
                                     "title": title,
                                     "pinned": pin,
                                     "deltas": []})

            transactions[-1]["deltas"].append({"id_d": id_d,
                                               "subtitle": subt,
                                               "amount": float(amount),
                                               "balance_after": float(b),
                                               "currency": curr,
                                               "account": acc,
                                               "tag": tag,
                                               "ts": ts.isoformat() if ts else None,
                                               "ts_log": ts_log.isoformat()})

        return {"status": "ok", "data": transactions}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
