import dataclasses
import decimal
import os
from datetime import datetime
from typing import List, Optional

import requests
from dotenv import load_dotenv

load_dotenv()


@dataclasses.dataclass(frozen=True)
class HHReading:
    start_at: datetime
    end_at: datetime
    version: str
    value: decimal.Decimal


GRAPHQL_URL = "https://api.oejp-kraken.energy/v1/graphql/"

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
        url=GRAPHQL_URL,
        json={
            "query": AUTH_BODY,
            "variables": {
                "input": {
                    "email": os.environ["OCTOPUS_EMAIL"],
                    "password": os.environ["OCTOPUS_PASSWORD"],
                }
            },
        },
    )
    response_dict = response.json()
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
        url=GRAPHQL_URL,
        json={
            "query": GET_ACCOUNT_BODY,
        },
        headers={"authorization": f"JWT {token}"},
    )
    response_dict = response.json()
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
    start_at: datetime,
    end_at: Optional[datetime] = None,
) -> List[HHReading]:

    variables = {
        "accountNumber": account_number,
        # Add the Z so it's parsed as UTC
        "fromDatetime": start_at.isoformat() + "Z",
    }
    if end_at:
        variables["toDatetime"] = end_at.isoformat() + "Z"
    response = requests.post(
        url=GRAPHQL_URL,
        json={
            "query": GET_HH_BODY,
            "variables": variables,
        },
        headers={"authorization": f"JWT {token}"},
    )
    response_dict = response.json()
    readings_raw = response_dict["data"]["account"]["properties"][0][
        "electricitySupplyPoints"
    ][0]["halfHourlyReadings"]
    readings: List[HHReading] = []
    for reading_raw in readings_raw:
        readings.append(
            HHReading(
                start_at=datetime.fromisoformat(reading_raw["startAt"]),
                end_at=datetime.fromisoformat(reading_raw["endAt"]),
                version=reading_raw["version"],
                value=decimal.Decimal(reading_raw["value"]),
            )
        )

    return readings
