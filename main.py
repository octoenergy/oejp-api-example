from fastapi import FastAPI

from octopus import get_account_number, get_hh_readings, get_token

app = FastAPI()


@app.get("/")
async def root():
    token = get_token()
    number = get_account_number(token=token)
    readings = get_hh_readings(account_number=number, token=token)
    return {"account_number": number, "readings": readings}
