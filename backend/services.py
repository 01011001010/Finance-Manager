from psycopg2.extensions import cursor
from psycopg2.sql import SQL, Identifier

# Custom imports
from models.finance import AddingAccount, AddingDelta, AddingTag, Archiving, DeltaIn
from models.finance import TransactionWithMultipleDeltas


# TODO move all backend logic here -> so only routing and db transaction management is
#      there (function reuse and clarity)
# TODO split services into same chunks like main backend structure

# TODO investigate all except clauses:
#      correct HTTP exception codes and details
#      appropriate Exception types
#       -> minimal catch all
#       -> no HTTPException should be intercepted and changed

def addNewTag(payload: AddingTag, cur: cursor) -> int | None:
    cur.execute("""INSERT INTO finance.tags (tag_name, parent_tag, archived)
                   VALUES (%s, %s, %s)
                   ON CONFLICT (tag_name, parent_tag) DO NOTHING
                   RETURNING tag;""",
                (payload.tag_name, payload.parent, payload.archived))
    (tag,) = cur.fetchone() or (None,)
    return tag


def addNewAccount(payload: AddingAccount, cur: cursor) -> tuple[int | None, str]:
    # TODO implement optional timestamp, if value is 0 (also in bulk)
    # 1. Insert account info
    cur.execute("""INSERT INTO finance.accounts (account, currency)
                   VALUES (%s, %s)
                   ON CONFLICT (account, currency) DO NOTHING
                   RETURNING id_a;""",
                (payload.name, payload.currency))
    (id_a,) = cur.fetchone() or (None,)

    if id_a is None:
        return (None, "Account creation failed during the creation of the account entry"
                      ", possibly due to being a duplicate")
    if abs(payload.balance) < 0.005:

        return id_a, ""

    # 2. Create transaction for initial balance if not 0.00
    tPayload = AddingDelta(id_t=1,  # Hardcoded in the schema
                           delta=DeltaIn(ts=payload.ts,
                                         subtitle=None,
                                         amount=payload.balance,
                                         id_a=id_a,
                                         tag=None))
    response = addDeltaToExistingTransaction(tPayload, cur)

    if response["status"] == "ok":
        return id_a, ""
    return (None, "Account creation failed during the creation of a delta for the "
                  "initial balance")


def addNewTransactionWithMultipleDeltas(payload: TransactionWithMultipleDeltas,
                                        cur: cursor) -> int:
    # 1. Insert transaction
    cur.execute("""INSERT INTO finance.transactions (title)
                VALUES (%s)
                RETURNING id_t;""",
                (payload.title,))
    (id_t,) = cur.fetchone() or (None,)

    for delta in payload.deltas:
        # 2.1. Insert delta
        cur.execute("""INSERT INTO finance.deltas (ts, amount, id_a,
                                                    tag, subtitle)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id_d;""",
                    (delta.ts,
                        delta.amount,
                        delta.id_a,
                        delta.tag,
                        delta.subtitle))
        (id_d,) = cur.fetchone() or (None,)

        # 2.2. Link delta to transaction
        cur.execute("""INSERT INTO finance.deltasPerTransaction (id_t,
                                                                    id_d)
                    VALUES (%s, %s);""",
                    (id_t, id_d))

    return len(payload.deltas)


def getAccountIdDict(cur: cursor) -> dict[tuple[str, str], int]:
    cur.execute("""SELECT a.id_a,
                          a.currency,
                          a.account
                   FROM finance.accounts a
                   ORDER BY a.id_a ASC;""")
    rows = cur.fetchall()

    return {(accountName, currency): int(id_a) for id_a, currency, accountName in rows}


def getTagIdDict(cur: cursor) -> dict[tuple[str, str], int]:
    cur.execute("""SELECT t.tag,
                          t.tag_name,
                          paren.tag_name
                   FROM finance.tags t
                   LEFT JOIN finance.tags paren ON t.parent_tag = paren.tag
                   ORDER BY t.parent_tag ASC NULLS FIRST, t.tag ASC;""")
    rows = cur.fetchall()
    return {(parent_name or '', tag): int(tag_id) for tag_id, tag, parent_name in rows}


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
