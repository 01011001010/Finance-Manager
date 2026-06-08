from typing import Any
from fastapi import APIRouter, HTTPException, status
from psycopg2 import errors as dbErrors

# Custom imports
from db import dbSession
from models.finance import AddingTag, Archiving
from services import archive, addNewTag


router = APIRouter(prefix="/tags", tags=["Finance - Tags"])


@router.post("/add")  # finance/tags/add
def addTag(payload: AddingTag) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                ID = addNewTag(payload, cur)
                if ID is None:
                    raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                                        detail=f"Tag '{payload.tag_name}' already "
                                               "exists.")
        return {"status": "ok",
                "detail": f"Tag {payload.tag_name} added under ID {ID}, nested under ID"
                          f" {payload.parent}"}

    except (dbErrors.IntegrityConstraintViolation, dbErrors.CheckViolation):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=("Non-cyclic nesting with max depth 1 violated. "
                                    f"Tag '{payload.tag_name}' was not added."))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.post("/archive")  # finance/tags/archive
def archiveTag(payload: Archiving) -> dict[str, str]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                return archive("tags", "tag", "Tag", payload, cur)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.get("")  # finance/tags
def getTags() -> dict[str, str | list[dict[str, Any]]]:
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                cur.execute("""SELECT t.tag,
                                      t.tag_name,
                                      t.archived,
                                      t.parent_tag,
                                      paren.tag_name
                               FROM finance.tags t
                               LEFT JOIN finance.tags paren ON t.parent_tag = paren.tag
                               ORDER BY t.parent_tag ASC NULLS FIRST, t.tag ASC;""")
                rows = cur.fetchall()
        return {"status": "ok",
                "data": [{"tag": tag,
                          "tag_name": name,
                          "hidden": hidden,
                          "parent": parent_id,
                          "parent_name": (parent_name
                                          if parent_name is not None
                                          else "")}
                         for tag, name, hidden, parent_id, parent_name in rows]}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
