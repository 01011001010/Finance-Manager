from typing import Any
from fastapi import APIRouter, HTTPException, status
# from psycopg2 import errors as dbErrors  # move away from general Exceptions
from models.finance import AddingDelta
from db import dbSession
from services import addDeltaToExistingTransaction


router = APIRouter(prefix="/deltas", tags=["Finance - Deltas"])


@router.post("/add")  # finance/deltas/add
def addDelta(payload: AddingDelta) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                return addDeltaToExistingTransaction(payload, cur)

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
                                      full_tag_name,
                                      id_d,
                                      amount,
                                      currency,
                                      account,
                                      ts,
                                      ts_log,
                                      balance_after
                               FROM finance.completeDeltaInfo
                               ORDER BY ts DESC,
                                        id_t DESC,
                                        id_d DESC;""")
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
