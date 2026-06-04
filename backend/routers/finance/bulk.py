from fastapi import APIRouter, UploadFile, HTTPException, status
from fastapi.responses import StreamingResponse
from csv import DictReader, writer as CSVwriter
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO, StringIO
from datetime import datetime
# from psycopg2 import errors as dbErrors  # TODO move away from catch-all Exceptions

# Custom imports
from db import dbSession
from services import addNewTransactionWithMultipleDeltas, getAccountIdDict, getTagIdDict
from models.finance import TransactionWithMultipleDeltas, DeltaIn


router = APIRouter(prefix="/bulk", tags=["Finance - Bulk data operations"])


@router.post("/upload/transactions")
def uploadTransactions(file: UploadFile) -> dict[str, str]:
    # TODO implement case insensitivity for headers
    requiredHeaders = {"Title": "Title", "Subtitle": "Subtitle", "Currency": "Currency",
                       "Amount": "Amount", "Tag": "Tag", "Timestamp": "Timestamp",
                       "AnalyticsTs": "AnalyticsTimestamp", "Account": "Account"}

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

        if missingHeaders := set(requiredHeaders.values()) - set(reader.fieldnames):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missingHeaders))}")

        tagIds = getTagIdDict()
        accountIds = getAccountIdDict()

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

            # Parse the tag string
            # -> assumes parent_tag/child_tag or simply tag
            tag, subTag = map(str.strip,
                              ('/' + row[requiredHeaders["Tag"]]).split('/')[-2:])

            # Fetch account ID
            id_a = accountIds.get((row[requiredHeaders["Account"]],
                                   row[requiredHeaders["Currency"]]), None)
            if id_a is None:  # Account not in the database
                raise HTTPException(status_code=422,
                                    detail=f"Account '{row[requiredHeaders['Account']]}"
                                           f" ({row[requiredHeaders['Currency']]})' not"
                                           " found.")

            # Fetch tag ID
            id_tag = tagIds.get((tag, subTag), None)
            if id_tag is None and (tag != "" or subTag != ""):  # Tag not found
                # TODO possibly just add the tag (or give the choice), currently aborts
                raise HTTPException(status_code=422,
                                    detail=f"Tag '{'/'.join(((tag, subTag)))}' "
                                           f"not found.")

            # Create the delta with translated literals into IDs
            try:
                ts = datetime.fromisoformat(row[requiredHeaders["Timestamp"]])
                ts_a = datetime.fromisoformat(row[requiredHeaders["AnalyticsTs"]])
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
                            detail=f"Error during read of the csv file: {e}")
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
                        "detail": (f"Added {len(payloads)} transactions containing "
                                   f"{deltaCount} deltas")}
    except Exception as e:
        # TODO specify further (see dbErrors import)
        raise HTTPException(status_code=500, detail=str(e))
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
        #         -> e.g. incorrect timestamp 2026-04-03 09:75:38+01 should be 422


@router.post("/upload/tags")
def uploadTags(file: UploadFile) -> dict[str, str]:
    requiredHeaders = {"tag": "tag"}

    # Check and parse uploaded csv file
    if file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    # payloads = []
    try:
        reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
        # "utf-8-sig" due to BOM from e.g. Excel

        if not reader.fieldnames:
            raise HTTPException(status_code=422,
                                detail="The uploaded CSV file is empty or missing a "
                                       "header row.")

        if missing_headers := set(requiredHeaders.values()) - set(reader.fieldnames):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missing_headers))}")

        # TODO implement file parsing
        raise HTTPException(status_code=404,
                            detail="Not implemented yet.")
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
                            detail=f"Error during read of the csv file: {e}")
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
    finally:
        file.file.close()

    # TODO implement database commit
    # Commit parsed tags into the database
    # try:
    #     with dbSession() as conn:
    #         with conn.cursor() as cur:
    #             # TODO

    #             return {"status": "ok",
    #                     "detail": (f"Added {len(payloads)} tags")}
    # except Exception as e:
    #     # TODO specify further (see dbErrors import)
    #     raise HTTPException(status_code=500, detail=str(e))
    #     # note: 500 is not too bad, if the db is not working as is should.
    #     #       If the contents of the payload are not ok, if should be 422
    #     #         -> e.g. incorrect timestamp 2026-04-03 09:75:38+01 should be 422


@router.post("/upload/accounts")
def uploadAccounts(file: UploadFile) -> dict[str, str]:
    requiredHeaders = {"account": "account", "currency": "currency",
                       "initialBalance": "initialBalance", "openingDate": "openingDate"}

    # Check and parse uploaded csv file
    if file.filename is None or not file.filename.endswith(".csv"):
        raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    # payloads = []
    try:
        reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
        # "utf-8-sig" due to BOM from e.g. Excel

        if not reader.fieldnames:
            raise HTTPException(status_code=422,
                                detail="The uploaded CSV file is empty or missing a "
                                       "header row.")

        if missing_headers := set(requiredHeaders.values()) - set(reader.fieldnames):
            raise HTTPException(status_code=422,
                                detail="CSV is missing these required headers: "
                                       f"{', '.join(sorted(missing_headers))}")

        # TODO implement file parsing
        raise HTTPException(status_code=404,
                            detail="Not implemented yet.")
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
                            detail=f"Error during read of the csv file: {e}")
        # note: 500 is not too bad, if the db is not working as is should.
        #       If the contents of the payload are not ok, if should be 422
    finally:
        file.file.close()

    # TODO implement database commit
    # Commit parsed accounts into the database
    # try:
    #     with dbSession() as conn:
    #         with conn.cursor() as cur:
    #             # TODO

    #             return {"status": "ok",
    #                     "detail": (f"Added {len(payloads)} accounts")}
    # except Exception as e:
    #     # TODO specify further (see dbErrors import)
    #     raise HTTPException(status_code=500, detail=str(e))
    #     # note: 500 is not too bad, if the db is not working as is should.
    #     #       If the contents of the payload are not ok, if should be 422
    #     #         -> e.g. incorrect timestamp 2026-04-03 09:75:38+01 should be 422


@router.post("/upload/accounts")
def uploadZip(file: UploadFile) -> dict[str, str]:
    # TODO implement everything
    raise HTTPException(status_code=404,
                        detail="Not implemented yet.")
    # requiredHeaders = {"account": "account", "currency": "currency",
    #                    "initialBalance": "initialBalance", "openingDate":
    #                    "openingDate"}

    # # Check and parse uploaded csv file
    # if file.filename is None or not file.filename.endswith(".csv"):
    #     raise HTTPException(status_code=422, detail="Please upload a CSV file.")

    # # payloads = []
    # try:
    #     reader = DictReader(StringIO(file.file.read().decode("utf-8-sig")))
    #     # "utf-8-sig" due to BOM from e.g. Excel

    #     if not reader.fieldnames:
    #         raise HTTPException(status_code=422,
    #                             detail="The uploaded CSV file is empty or missing a "
    #                                    "header row.")

    #     if missing_headers := set(requiredHeaders.values()) - set(reader.fieldnames):
    #         raise HTTPException(status_code=422,
    #                             detail="CSV is missing these required headers: "
    #                                    f"{', '.join(sorted(missing_headers))}")

    #     raise HTTPException(status_code=404,
    #                         detail="Not implemented yet.")
    # except HTTPException:
    #     # Let through HTTPExceptions
    #     raise
    # except UnicodeDecodeError:
    # # Catches cases where someone uploads a completely incompatible files e.g. .xlsx
    #     raise HTTPException(status_code=422,
    #                         detail="File encoding error. Please ensure the file is a "
    #                                "valid UTF-8 text CSV.")
    # except Exception as e:
    #     # Catch all
    #     raise HTTPException(status_code=500,
    #                         detail=f"Error during read of the csv file: {e}")
    #     # note: 500 is not too bad, if the db is not working as is should.
    #     #       If the contents of the payload are not ok, if should be 422
    # finally:
    #     file.file.close()

    # # Commit parsed accounts into the database
    # # try:
    # #     with dbSession() as conn:
    # #         with conn.cursor() as cur:

    # #             return {"status": "ok",
    # #                     "detail": (f"Added {len(payloads)} accounts")}
    # # except Exception as e:
    # #     raise HTTPException(status_code=500, detail=str(e))
    # #     # note: 500 is not too bad, if the db is not working as is should.
    # #     #       If the contents of the payload are not ok, if should be 422
    # #     #         -> e.g. incorrect timestamp 2026-04-03 09:75:38+01 should be 422


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
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=str(e))
