from psycopg2.extensions import cursor
from psycopg2.sql import SQL, Identifier

# Custom imports
from models.finance import AddingDelta, Archiving


# TODO move all backend logic here -> so only routing and db transaction management is
#      there (function reuse and clarity)
# TODO split services into same chunks like main backend structure

# TODO investigate all except clauses:
#      correct HTTP exception codes and details
#      appropriate Exception types
#       -> minimal catch all
#       -> no HTTPException should be intercepted and changed


def addDeltaToExistingTransaction(payload: AddingDelta, cur: cursor) -> dict[str, str]:
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


def archive(table: str, col: str, messageName: str,
            payload: Archiving, cur: cursor) -> dict[str, str]:
    # Archiving tags and accounts
    query = SQL("""UPDATE finance.{tbl}
                   SET archived = %s
                   WHERE {col} = %s;""").format(
        tbl=Identifier(table),
        col=Identifier(col)
    )
    cur.execute(query, (payload.newArchivedState, payload.id))
    message = "archived" if payload.newArchivedState else "restored"
    return {"status": "ok",
            "detail": f"{messageName} with ID: {payload.id} {message}"}
