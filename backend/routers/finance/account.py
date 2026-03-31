from typing import Any
from fastapi import APIRouter, HTTPException, status
from psycopg2 import errors as dbErrors
from psycopg2.sql import SQL, Identifier
from models.finance import AddingAccount, Archiving
from db import dbSession


router = APIRouter(prefix="/accounts", tags=["Finance - Accounts"])


@router.post("/add")  # finance/accounts/add
def addAccount(payload: AddingAccount) -> dict[str, str]:
    # DEV
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""INSERT INTO finance.accounts (account, currency,
                                                             opened_ts, opening_balance)
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


def archive(table: str, col: str, id: int, newState: bool, name: str) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                query = SQL("""UPDATE finance.{tbl}
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


@router.post("/archive")  # finance/accounts/archive
def archiveAccount(payload: Archiving) -> dict[str, str]:
    return archive("accounts", "id_a", payload.id, payload.newArchivedState, "Account")


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
