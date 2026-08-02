from fastapi import APIRouter, HTTPException, status
from typing import Any

# Custom imports
from db import dbSession
from models.finance import AddingAccount, Archiving
from services import addNewAccount, archive


router = APIRouter(prefix="/accounts", tags=["Finance - Accounts"])


@router.post("/add")  # finance/accounts/add
def addAccount(payload: AddingAccount) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                ID, errorMsg = addNewAccount(payload, cur)
                if ID is None:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail=f"Account creation failed: {errorMsg}.")
                return {"status": "ok",
                        "detail": f"Account {payload.name} initiated with ID {ID} and "
                                  f"starting balance {payload.balance} from "
                                  f"{payload.ts}."}
    except HTTPException:
        raise
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
                                      a.archived,
                                      a.ts,
                                      a.balance_after
                               FROM finance.accountsWithCurrentBalance a
                               ORDER BY a.id_a ASC;""")
                rows = cur.fetchall()

        return {"status": "ok",
                "data": [{"id_a": id_a,
                          "currency": currency,
                          "account": name,
                          "hidden": hidden,
                          "balance": balance,
                          "ts": ts}
                         for id_a, currency, name, hidden, ts, balance in rows]}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
