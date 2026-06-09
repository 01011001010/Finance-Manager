from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from csv import DictReader, writer as CSVwriter
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO, StringIO
from datetime import datetime
from psycopg2 import errors as dbErrors
from pydantic_extra_types.currency_code import ISO4217

# Custom imports
from db import dbSession
from services import addNewAccount, addNewTag, addNewTransactionWithMultipleDeltas
from services import getAccountIdDict, getTagIdDict
from utils import parseTagString
from models.finance import AddingAccount, AddingTag, DeltaIn
from models.finance import TransactionWithMultipleDeltas


router = APIRouter(prefix="/bulk", tags=["Finance - Bulk data operations"])


requiredHeadersTransactions = {"Title": "title", "Subtitle": "subtitle",
                               "Amount": "amount", "Currency": "currency", "Tag": "tag",
                               "Timestamp": "timestamp", "Account": "account"}
optionalHeadersTransactions = {"AnalyticsTs": "analyticstimestamp"}
assert all(isinstance(value, str) and value.islower()
           for value in requiredHeadersTransactions.values()
           ), "DEV ERROR: Required headers (transactions) should be lowercase strings"
assert all(isinstance(value, str) and value.islower()
           for value in optionalHeadersTransactions.values()
           ), "DEV ERROR: Optional headers (transactions) should be lowercase strings"

requiredHeadersAccounts = {"account": "account", "currency": "currency",
                           "openingDate": "openingdate"}
optionalHeadersAccounts = {"initialBalance": "initialbalance"}
assert all(isinstance(value, str) and value.islower()
           for value in requiredHeadersAccounts.values()
           ), "DEV ERROR: Required headers (accounts) should be lowercase strings"
assert all(isinstance(value, str) and value.islower()
           for value in optionalHeadersAccounts.values()
           ), "DEV ERROR: Optional headers (accounts) should be lowercase strings"


requiredHeadersTags = {"Tag": "tag"}
optionalHeadersTags = {"Archived": "archived"}
assert all(isinstance(value, str) and value.islower()
           for value in requiredHeadersTags.values()
           ), "DEV ERROR: Required headers (tags) should be lowercase strings"
assert all(isinstance(value, str) and value.islower()
           for value in optionalHeadersTags.values()
           ), "DEV ERROR: Optional headers (tags) should be lowercase strings"


@router.post("/upload/transactions")
def uploadTransactions(file: UploadFile) -> dict[str, str]:
    requiredHeaders = requiredHeadersTransactions
    optionalHeaders = optionalHeadersTransactions

    # Check and parse uploaded csv file
    if file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    payloads = []
    try:
        reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
        # "utf-8-sig" due to BOM from e.g. Excel

        if not reader.fieldnames:
            raise HTTPException(status_code=422,
                                detail="The uploaded CSV file is empty or missing a "
                                       "header row.")

        reader.fieldnames = [name.lower() for name in reader.fieldnames]

        if missingFields := (set(requiredHeaders.values()) - set(reader.fieldnames)):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missingFields))}.")

        # Load account and tag IDs
        try:
            with dbSession() as conn:
                with conn.cursor() as cur:
                    tagIds = getTagIdDict(cur)
                    accountIds = getAccountIdDict(cur)
        except Exception:
            raise HTTPException(status_code=500,
                                detail="Error during load of tag or account IDs.")

        currentTitle = ""
        deltas = []
        for row in reader:
            if row[requiredHeaders["Title"]]:  # New group of deltas starts here
                # Add previously read transaction to payloads
                if currentTitle:  # Except at the start
                    payloads.append(TransactionWithMultipleDeltas(title=currentTitle,
                                                                  deltas=deltas))
                # Reset current transaction info
                currentTitle = row[requiredHeaders["Title"]]
                deltas = []

            # Fetch account ID
            id_a = accountIds.get((row[requiredHeaders["Account"]],
                                   row[requiredHeaders["Currency"]]), None)
            if id_a is None:  # Account not in the database
                raise HTTPException(status_code=422,
                                    detail=f"Account '{row[requiredHeaders['Account']]}"
                                           f" ({row[requiredHeaders['Currency']]})' not"
                                           " found.")

            # Parse the tag string
            # -> assumes parent_tag/child_tag or simply tag
            tag, subTag = parseTagString(row[requiredHeaders["Tag"]])

            # Fetch tag ID
            id_tag = tagIds.get((tag, subTag), None)
            if id_tag is None and (tag != "" or subTag != ""):  # Tag not found
                # TODO possibly just add the tag (or give the choice), currently aborts
                raise HTTPException(status_code=422,
                                    detail=f"Tag '{row[requiredHeaders['Tag']]}' "
                                           f"not found")

            # Create the delta with translated literals into IDs
            try:
                ts = datetime.fromisoformat(row[requiredHeaders["Timestamp"]])
                ts_a = (datetime.fromisoformat(row[optionalHeaders["AnalyticsTs"]])
                        if (optionalHeaders["AnalyticsTs"] in row
                            and row[optionalHeaders["AnalyticsTs"]] != "")
                        else None)
                amount = float(row[requiredHeaders["Amount"]])
            except ValueError as e:
                raise HTTPException(status_code=422,
                                    detail=f"Timestamp or float parsing failed: {e}")
            deltas.append(DeltaIn(ts=ts,
                                  analytics_ts=ts_a,
                                  subtitle=row[requiredHeaders["Subtitle"]],
                                  amount=amount,
                                  id_a=id_a,
                                  tag=id_tag))

        # Add the last transaction (no new line to trigger it in the loop)
        payloads.append(TransactionWithMultipleDeltas(title=currentTitle,
                                                      deltas=deltas))
    except HTTPException:
        # Let through HTTPExceptions
        raise
    except UnicodeDecodeError:
        # Catches cases where someone uploads a completely incompatible files e.g. .xlsx
        raise HTTPException(status_code=422,
                            detail="File encoding error. Please ensure the file is a "
                                   "valid UTF-8 text CSV.")
    except Exception as e:
        # Catch all
        # TODO specify further (see dbErrors import)
        raise HTTPException(status_code=500,
                            detail=f"Error during read of the csv file: {e}.")
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
    finally:
        file.file.close()

    # Commit parsed transactions into the database
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                deltaCount = sum([addNewTransactionWithMultipleDeltas(payload, cur)
                                  for payload
                                  in payloads])

        return {"status": "ok",
                "detail": (f"Added {len(payloads)} transactions containing {deltaCount}"
                           " deltas.")}
    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=500, detail=str(e))
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
        #         -> e.g. incorrect timestamp 2026-04-03 09:75:38+01 should be 422


@router.post("/upload/tags")
def uploadTags(file: UploadFile) -> dict[str, str]:
    requiredHeaders = requiredHeadersTags
    optionalHeaders = optionalHeadersTags

    # Check and parse uploaded csv file
    if file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    payloads = []
    queuedTopLevelTags = set()
    addInTheSecondRound = []
    try:
        reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
        # "utf-8-sig" due to BOM from e.g. Excel

        if not reader.fieldnames:
            raise HTTPException(status_code=422,
                                detail="The uploaded CSV file is empty or missing a "
                                       "header row.")

        reader.fieldnames = [name.lower() for name in reader.fieldnames]

        if missingFields := (set(requiredHeaders.values()) - set(reader.fieldnames)):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missingFields))}")

        # Load tag IDs
        try:
            with dbSession() as conn:
                with conn.cursor() as cur:
                    tagIds = getTagIdDict(cur)
        except Exception:
            raise HTTPException(status_code=500, detail="Error during load of tag IDs.")

        for row in reader:
            tag, subTag = parseTagString(row[requiredHeaders["Tag"]])
            archived = bool(row.get(optionalHeaders["Archived"], False))

            if tag == "":  # Adding a top-level tag
                if subTag not in queuedTopLevelTags:
                    payloads.append(AddingTag(tag_name=subTag, archived=archived))
                    queuedTopLevelTags.add(subTag)
            elif tag in tagIds:  # Adding a subTag to an existing tag
                payloads.append(AddingTag(tag_name=subTag,
                                          parent=tagIds.get(("", tag), None),
                                          archived=archived))
            else:  # Add top-level tag and mark subTag to add after
                if tag not in queuedTopLevelTags:
                    payloads.append(AddingTag(tag_name=tag, archived=archived))
                    queuedTopLevelTags.add(tag)
                addInTheSecondRound.append((tag, subTag, archived))

    except HTTPException:
        # Let through HTTPExceptions
        raise
    except UnicodeDecodeError:
        # Catches cases where someone uploads a completely incompatible files e.g. .xlsx
        raise HTTPException(status_code=422,
                            detail="File encoding error. Please ensure the file is a "
                                   "valid UTF-8 text CSV.")
    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=500,
                            detail=f"Error during read of the csv file: {e}.")
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
    finally:
        file.file.close()

    if not payloads:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=("No tags specified in the CSV file."))

    # Commit parsed tags into the database
    addedTags = 0
    failedTags = []

    try:
        with dbSession() as conn:
            with conn.cursor() as cur:

                # Simple cases (adding only one tag per CSV entry)
                for payload in payloads:
                    ID = addNewTag(payload, cur)
                    if ID is not None:
                        addedTags += 1
                    else:
                        failedTags.append((payload))

                if addInTheSecondRound:  # Complex cases (nested with fresh parent)
                    # Reload IDs to include newly added
                    # TODO consider logging created IDs instead
                    tagIds = getTagIdDict(cur)

                    for tag, subTag, archived in addInTheSecondRound:
                        payload = AddingTag(tag_name=subTag,
                                            parent=tagIds.get(("", tag), None),
                                            archived=archived)
                        ID = addNewTag(payload, cur)
                        if ID is not None:
                            addedTags += 1
                        else:
                            failedTags.append(payload)

        return {"status": "ok",
                "detail": f"Tags added: {addedTags}; Tags that already existed: "
                          f"{len(failedTags)}.",
                "failed": repr(failedTags)}

    except (dbErrors.IntegrityConstraintViolation, dbErrors.CheckViolation):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail="Non-cyclic nesting with max depth 1 violated. Most "
                                   "likely a bug in the code.")
    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.post("/upload/accounts")
def uploadAccounts(file: UploadFile) -> dict[str, str]:
    requiredHeaders = requiredHeadersAccounts
    optionalHeaders = optionalHeadersAccounts

    # Check and parse uploaded csv file
    if file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    payloads = []
    try:
        reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
        # "utf-8-sig" due to BOM from e.g. Excel

        if not reader.fieldnames:
            raise HTTPException(status_code=422,
                                detail="The uploaded CSV file is empty or missing a "
                                       "header row.")

        reader.fieldnames = [name.lower() for name in reader.fieldnames]

        if missingFields := (set(requiredHeaders.values()) - set(reader.fieldnames)):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missingFields))}")

        for row in reader:
            try:
                ts = datetime.fromisoformat(row[requiredHeaders["openingDate"]])
                currency = ISO4217(row[requiredHeaders["currency"]])
                balance = float(row.get(optionalHeaders["initialBalance"], 0))
            except ValueError as e:
                raise HTTPException(status_code=422,
                                    detail="Timestamp, float or currency parsing failed"
                                           f": {e}")
            payloads.append(AddingAccount(ts=ts, name=row[requiredHeaders["account"]],
                                          currency=currency, balance=balance))

    except HTTPException:
        # Let through HTTPExceptions
        raise
    except UnicodeDecodeError:
        # Catches cases where someone uploads a completely incompatible files e.g. .xlsx
        raise HTTPException(status_code=422,
                            detail="File encoding error. Please ensure the file is a "
                                   "valid UTF-8 text CSV.")
    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=500,
                            detail=f"Error during read of the csv file: {e}.")
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
    finally:
        file.file.close()

    if not payloads:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                            detail=("No accounts specified in the CSV file."))

    # Commit parsed accounts into the database
    added = 0
    failed = []
    try:
        with dbSession() as conn:
            with conn.cursor() as cur:
                for payload in payloads:
                    ID, errorMsg = addNewAccount(payload, cur)
                    if ID is not None:
                        added += 1
                    else:
                        failed.append(((payload, errorMsg)))

        return {"status": "ok",
                "detail": f"Accounts added: {added}; Accounts that already existed: "
                          f"{len(failed)}.",
                "failed": repr(failed)}

    except HTTPException:
        raise
    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))


@router.post("/upload/zip")
def uploadZip(file: UploadFile) -> dict[str, str]:
    # TODO implement everything
    raise HTTPException(status_code=404,
                        detail="Not implemented yet.")


@router.get("/download")
def export_zip() -> StreamingResponse:
    fileTs = datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    try:
        zipBuffer = BytesIO()

        with dbSession() as conn:
            with conn.cursor() as cur:
                with ZipFile(zipBuffer, "w", ZIP_DEFLATED) as zipFile:

                    # Accounts
                    csvBuffer = StringIO()
                    writer = CSVwriter(csvBuffer)
                    writer.writerow(["account", "currency", "archived",
                                     "initialBalance", "openingDate"])

                    cur.execute("""SELECT a.currency,
                                          a.account,
                                          a.archived,
                                          d.amount,
                                          d.ts
                               FROM finance.accounts a
                               LEFT JOIN finance.completeDeltaInfo d ON d.id_a = a.id_a
                               WHERE d.id_t = 1
                               ORDER BY a.account ASC;""")
                    # Assumes use of a reserved id_t hardcoded in the schema definition.
                    # Unless broken somewhere else, it should not be possible to have
                    # duplicate entries for the same account name and currency pair.
                    # This will not crash, in case this happens, but any subsequent
                    # import will.
                    for currency, account, archived, amount, ts in cur:
                        writer.writerow([account, currency, archived, amount, ts])
                    zipFile.writestr("accounts.csv", csvBuffer.getvalue())

                    # Tags
                    csvBuffer = StringIO()
                    writer = CSVwriter(csvBuffer)
                    writer.writerow(["tag", "archived"])

                    cur.execute("""SELECT t.full_tag_name,
                                          t.archived
                               FROM finance.tagsWithFullName t
                               ORDER BY t.parent_tag ASC NULLS FIRST;""")
                    for tag, archived in cur:
                        writer.writerow([tag, archived])
                    zipFile.writestr("tags.csv", csvBuffer.getvalue())

                    # # Transactions and deltas
                    csvBuffer = StringIO()
                    writer = CSVwriter(csvBuffer)
                    writer.writerow(["title", "subtitle", "amount", "account",
                                     "currency", "tag", "timestamp",
                                     "analyticsTimestamp", "pinned"])

                    cur.execute("""SELECT d.id_t,
                                          d.title,
                                          d.subtitle,
                                          d.amount,
                                          d.account,
                                          d.currency,
                                          d.full_tag_name,
                                          d.ts,
                                          d.ts_analytics,
                                          d.pinned
                               FROM finance.completeDeltaInfo d
                               ORDER BY d.id_t ASC;""")

                    previousId_t = None
                    for (id_t, title, subtitle, amount, account, currency, tag, ts,
                         ts_a, pinned) in cur:
                        writer.writerow(["" if id_t == previousId_t else title,
                                         subtitle,
                                         amount,
                                         account,
                                         currency,
                                         tag,
                                         ts,
                                         ts_a,
                                         pinned])
                        previousId_t = id_t
                    zipFile.writestr("transactions.csv", csvBuffer.getvalue())

        zipBuffer.seek(0)

        return StreamingResponse(zipBuffer, media_type="application/x-zip-compressed",
                                 headers={"Content-Disposition": 'attachment; filename='
                                                                 f'"export {fileTs}'
                                                                 '.zip"'})

    except Exception as e:
        # Catch all
        # TODO specify further if possible
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
