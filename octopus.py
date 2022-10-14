import dataclasses
import datetime
import decimal
import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.environ["API_URL"]
OCTOPUS_EMAIL = os.environ["OCTOPUS_EMAIL"]
OCTOPUS_PASSWORD = os.environ["OCTOPUS_PASSWORD"]


@dataclasses.dataclass(frozen=True)
class HHReading:
    start_at: datetime.datetime
    end_at: datetime.datetime
    version: str
    value: decimal.Decimal


AUTH_BODY = """
mutation obtainKrakenToken($input: ObtainJSONWebTokenInput!) {
  obtainKrakenToken(input: $input) {
    refreshToken
    refreshExpiresIn
    payload
    token
  }
}
"""


def get_token() -> str:
    response = requests.post(
        url=API_URL,
        json={
            "query": AUTH_BODY,
            "variables": {
                "input": {
                    "email": OCTOPUS_EMAIL,
                    "password": OCTOPUS_PASSWORD,
                }
            },
        },
    )
    response_dict = response.json()
    _validate_response(response)

    return response_dict["data"]["obtainKrakenToken"]["token"]


GET_ACCOUNT_BODY = """
query accountViewer {
  viewer {
    accounts {
      number
    }
  }
}
"""


def get_account_number(token: str) -> str:
    response = requests.post(
        url=API_URL,
        json={
            "query": GET_ACCOUNT_BODY,
        },
        headers={"authorization": f"JWT {token}"},
    )
    response_dict = response.json()
    _validate_response(response)

    return response_dict["data"]["viewer"]["accounts"][0]["number"]


GET_HH_BODY = """
query halfHourlyReadings($accountNumber: String!, $fromDatetime: DateTime, $toDatetime: DateTime) {
  account(accountNumber: $accountNumber) {
    properties {
      electricitySupplyPoints {
        halfHourlyReadings(fromDatetime: $fromDatetime, toDatetime: $toDatetime) {
          startAt
          endAt
          version
          value
        }
      }
    }
  }
}
"""


def get_hh_readings(
    account_number: str,
    token: str,
    start_at: datetime.datetime,
    end_at: Optional[datetime.datetime] = None,
) -> List[HHReading]:

    variables = {
        "accountNumber": account_number,
        "fromDatetime": start_at.isoformat(),
    }
    if end_at:
        variables["toDatetime"] = end_at.isoformat()
    response = requests.post(
        url=API_URL,
        json={
            "query": GET_HH_BODY,
            "variables": variables,
        },
        headers={"authorization": f"JWT {token}"},
    )
    _validate_response(response)

    response_dict = response.json()
    readings_raw = response_dict["data"]["account"]["properties"][0][
        "electricitySupplyPoints"
    ][0]["halfHourlyReadings"]
    readings: List[HHReading] = []
    for reading_raw in readings_raw:
        readings.append(
            HHReading(
                start_at=datetime.datetime.fromisoformat(reading_raw["startAt"]),
                end_at=datetime.datetime.fromisoformat(reading_raw["endAt"]),
                version=reading_raw["version"],
                value=decimal.Decimal(reading_raw["value"]),
            )
        )

    return readings


def _validate_response(response: requests.Response) -> None:
    if (errors := response.json().get("errors")) and len(errors):
        raise ValueError(errors)
