from typing import Any
from fastapi import APIRouter, HTTPException, status
# from psycopg2 import errors as dbErrors  # move away from general Exceptions
from models.finance import TransactionWithDelta, settingPin
from db import dbSession


router = APIRouter(prefix="/transactions", tags=["Finance - Transactions"])


@router.post("/add")  # finance/transactions/add
def addNewTransaction(payload: TransactionWithDelta) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                # 1. Insert transaction
                cur.execute("""INSERT INTO finance.transactions (title)
                               VALUES (%s)
                               RETURNING id_t;""",
                            (payload.title,))
                (id_t,) = cur.fetchone() or (None,)

                # 2. Insert delta
                cur.execute("""INSERT INTO finance.deltas (ts, amount, id_a, tag,
                                                           subtitle)
                               VALUES (%s, %s, %s, %s, %s)
                               RETURNING id_d;""",
                            (payload.delta.ts,
                             payload.delta.amount,
                             payload.delta.id_a,
                             payload.delta.tag,
                             payload.delta.subtitle))
                (id_d,) = cur.fetchone() or (None,)

                # 3. Link delta to transaction
                cur.execute("""INSERT INTO finance.deltasPerTransaction (id_t, id_d)
                               VALUES (%s, %s);""",
                            (id_t, id_d))

                return {"status": "ok",
                        "detail": f"Transaction {id_t} and {id_d} added and linked"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.post("/pin")  # finance/transactions/pin
def setPin(payload: settingPin) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""UPDATE finance.transactions
                               SET pinned = %s
                               WHERE id_t = %s;""", (payload.newPin, payload.id_t))
                un = "" if payload.newPin else "un"
                return {"status": "ok",
                        "detail": f"Transaction {payload.id_t} {un}pinned successfully"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.get("/pinned")  # finance/transactions/pinned
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
                               FROM finance.completeDeltaInfo
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


@router.get("/overview")  # finance/transactions/overview
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
                               FROM finance.completeDeltaInfo
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
