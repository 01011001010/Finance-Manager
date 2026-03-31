from typing import Any
from fastapi import APIRouter, HTTPException, status
# from psycopg2 import errors as dbErrors  # move away from general Exceptions
from models.finance import AddingDelta
from db import dbSession


router = APIRouter(prefix="/deltas", tags=["Finance - Deltas"])


@router.post("/add")  # finance/deltas/add
def addDeltaToExistingTransaction(payload: AddingDelta) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                # 1. Insert delta
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

                # 2. Link delta to transaction
                cur.execute("""INSERT INTO finance.deltasPerTransaction (id_t, id_d)
                               VALUES (%s, %s);""",
                            (payload.id_t, id_d))

                return {"status": "ok",
                        "detail": f"Transaction {payload.id_t} linked to delta {id_d}"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.get("")  # finance/deltas
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
                               FROM finance.completeDeltaInfo
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
