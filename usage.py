import argparse
import datetime
import statistics
from collections import defaultdict
from typing import List, Optional

from rich import console as rich_console
from rich import table as rich_table
from rich import text as rich_text

import localtime
import octopus

PURPLE = "#9400FF"
PINK = "#DF00A9"


def print_electricity_usage(
    start_date: datetime.date, end_date: Optional[datetime.date] = None
):
    """
    Print electricity usage statistics.
    """

    readings = _get_readings(start_date, end_date)

    # Prepare usage table.
    usage_table = _build_usage_table(start_date, end_date)
    usage_table.add_row(
        rich_text.Text("Daily Avg", style=PINK, justify="left"),
        rich_text.Text(
            f"{_calculate_daily_average(readings=readings):.2f} kWh",
            justify="right",
        ),
    )
    usage_table.add_row(
        rich_text.Text("Total Usage", style=PURPLE, justify="left"),
        rich_text.Text(
            f"{_calculate_total_usage(readings=readings):.2f} kWh",
            justify="right",
        ),
    )

    console = rich_console.Console(record=True, width=30)
    console.print(usage_table)
    with open("usage.svg", "w") as f:
        f.write(console.export_svg(title="Electricity Usage"))


def _get_readings(
    start_date: datetime.date, end_date: Optional[datetime.date]
) -> List[octopus.HHReading]:
    """
    Return half-hourly readings for the given date range.
    """
    token = octopus.get_token()
    account_number = octopus.get_account_number(token=token)
    return octopus.get_hh_readings(
        account_number=account_number,
        token=token,
        start_at=localtime.midnight(start_date),
        end_at=localtime.midnight(end_date) if end_date else None,
    )


def _build_usage_table(
    start_date: datetime.date, end_date: Optional[datetime.date] = None
) -> rich_table.Table:
    """
    Return a table to hold usage data.
    """
    end_at = end_date.isoformat() if end_date else "now"
    table = rich_table.Table(title=f"{start_date.isoformat()} ~ {end_at}️")
    table.add_column(":octopus:", justify="center")
    table.add_column(":zap:", justify="center")
    return table


def _calculate_total_usage(readings: List[octopus.HHReading]) -> float:
    """
    Return the total electricity usage for all readings.
    """
    return statistics.fsum([reading.value for reading in readings])


def _calculate_daily_average(readings: List[octopus.HHReading]) -> float:
    """
    Return the daily average electricity usage.
    """
    daily_usage = defaultdict(list)
    for reading in readings:
        daily_usage[reading.start_at.date()].append(reading.value)
    return statistics.fmean([sum(reading) for reading in daily_usage.values()])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Electricity Usage")
    parser.add_argument("start_date", metavar="start", type=datetime.date.fromisoformat)
    parser.add_argument(
        "end_date", metavar="end", type=datetime.date.fromisoformat, nargs="?"
    )
    args = parser.parse_args()
    print_electricity_usage(start_date=args.start_date, end_date=args.end_date)
