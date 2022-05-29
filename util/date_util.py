# ！/usr/bin/env python
# encoding: utf-8
"""
@Author:
@File: date_util.py.py
@Time: 2022/5/22 16:02
@Describe:
"""

import datetime

import pandas as pd

date_format = "%Y-%m-%d"


def get_latest_possible_trading_day(date):
    if not isinstance(date, datetime.datetime):
        date = datetime.datetime.strptime(date, date_format)
    day = date.isoweekday()
    if day > 5:
        date = date - datetime.timedelta(days=day - 5)
    return date.strftime(date_format)


def datetime_to_string(date):
    assert isinstance(date, datetime.datetime), f"datetime.datetime expected, got {type(date)}"
    return date.strftime(date_format)


def timestamp_to_string(timestamp):
    assert isinstance(timestamp, pd.Timestamp), f"pd.Timestamp expected, got {type(timestamp)}"
    return timestamp.to_pydatetime().strftime(date_format)


if __name__ == "__main__":
    print(get_latest_possible_trading_day(datetime.datetime.today()))
