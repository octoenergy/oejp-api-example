import datetime
from typing import Optional

import fastapi

import localtime
from octopus import get_account_number, get_hh_readings, get_token

app = fastapi.FastAPI()


@app.get("/")
def get_usage(
    start_date: Optional[datetime.date] = None, end_date: Optional[datetime.date] = None
):
    token = get_token()
    number = get_account_number(token=token)

    # Today's date by default.
    if not end_date:
        end_date = localtime.today()
    # Last 3 days of usage by default.
    if not start_date:
        start_date = localtime.days_in_the_past(3, end_date)

    if start_date >= end_date:
        raise fastapi.HTTPException(
            status_code=400,
            detail="The initial date should be prior to the end date.",
        )

    # Get the half-hourly readings using Octopus Energy's API.
    readings = get_hh_readings(
        account_number=number,
        token=token,
        start_at=localtime.midnight(start_date),
        end_at=localtime.midnight(end_date),
    )

    return {"account_number": number, "readings": readings}
