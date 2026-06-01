from fastapi import APIRouter, HTTPException, status
from psycopg2 import errors as dbErrors
from typing import Any

# Custom imports
from db import dbSession
from models.finance import AddingAccount, Archiving, AddingDelta, DeltaIn
from services import archive, addDeltaToExistingTransaction


router = APIRouter(prefix="/accounts", tags=["Finance - Accounts"])


@router.post("/add")  # finance/accounts/add
def addAccount(payload: AddingAccount) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                # 1. Insert account info
                cur.execute("""INSERT INTO finance.accounts (account, currency)
                               VALUES (%s, %s)
                               RETURNING id_a;""",
                            (payload.name, payload.currency))
                (id_a,) = cur.fetchone() or (None,)

                if id_a is None:
                    raise HTTPException(status.HTTP_500_INTERNAL_SERVER_ERROR,
                                        detail="Account creation failed to give id_a")

                if abs(payload.balance) < 0.005:
                    return {"status": "ok",
                            "detail": f"Account {payload.name} initiated with ID {id_a}"
                                      f" and starting balance 0.00."}

                # 2. Create transaction for initial balance if not 0.00
                tPayload = AddingDelta(id_t=1,  # Hardcoded in the schema
                                       delta=DeltaIn(ts=payload.ts,
                                                     subtitle=None,
                                                     amount=payload.balance,
                                                     id_a=id_a,
                                                     tag=None))
                response = addDeltaToExistingTransaction(tPayload, cur)

                if response["status"] == "ok":
                    return {"status": "ok",
                            "detail": f"Account {payload.name} initiated with ID {id_a}"
                                      f" and starting balance {payload.balance} from "
                                      f"{payload.ts}."}

                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                    detail="Account creation failed during creation of "
                                           "a delta for the initial balance")
    except HTTPException:
        raise
    except dbErrors.UniqueViolation:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail=f"Account '{payload.name} ({payload.currency})' "
                                   "already exists.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.post("/archive")  # finance/accounts/archive
def archiveAccount(payload: Archiving) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                return archive("accounts", "id_a", "Account", payload, cur)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.get("")  # finance/accounts
def getAccounts() -> dict[str, str | list[dict[str, Any]]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT a.id_a,
                                      a.currency,
                                      a.account,
                                      a.archived
                               FROM finance.accounts a
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
