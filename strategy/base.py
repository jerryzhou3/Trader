import data.stock as st
import numpy as np
import pandas as pd

pd.set_option('display.max_columns', 20)
pd.set_option('display.max_rows', None)


def reduce_signal(data: pd.DataFrame) -> pd.DataFrame:
    """
    整合买入卖出信号
    :param data: 股票数据，包含 buy_signal 和 sell_signal 列
    :return: data
    """
    for col in data.columns:
        if "signal" in col:
            data[col] = np.where((data[col] != 0) & (data[col].shift(1) == data[col]), 0, data[col])
            # 如果全部数据没有任何一次卖出信号，在最后一个交易日卖出
            if len(data[data[col] == -1]) == 0:
                data[col].iloc[-1] = -1
    return data


def calculate_profit_pct(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算单次收益率：开仓，平仓（开仓全部股数）
    :param data: 股票数据，包含 signal 列
    :return: data
    """
    for col in data.columns:
        if isinstance(col, str) and col == "close":
            data["profit_pct"] = data[col].pct_change()
            break
        elif isinstance(col, tuple) and "close" in col:
            code, _ = col
            data[(code, "profit_pct")] = data[col].pct_change()
        elif not isinstance(col, tuple) and not isinstance(col, str):
            raise Exception("Unknown index structure.")
    return data


def calculate_cum_profit(data):
    """
    计算累积收益率
    :param data: 股票数据，包含 profit_pct 列
    :return: data
    """
    multi_index = False
    cum_profit_by_code = {}
    for col in data.columns:
        if isinstance(col, str):
            data = data.drop(data[data["signal"] != -1].index)
            data["cum_profit_pct"] = (data["profit_pct"] + 1).cumprod() - 1
            data.dropna(inplace=True)
            break
        elif isinstance(col, tuple) and "signal" in col:
            multi_index = True
            code, _ = col
            data[code] = data[code].drop(data[data[col] != -1].index)
            data[(code, "cum_profit_pct")] = (data[(code, "profit_pct")] + 1).cumprod() - 1
            cum_profit_by_code[code] = data[(code, "cum_profit_pct")].dropna().iloc[-1]
    if multi_index:
        data = data.sort_index(level=0, axis=1)
        return data, cum_profit_by_code
    else:
        return data


def calculate_max_drawdown(data: pd.DataFrame, window: int = 252) -> pd.DataFrame:
    """
    计算最大回撤比
    :param data: 股票数据
    :param window: 窗口大小
    :return: data
    """
    rolling_max = data["close"].rolling(window, min_periods=1).max()
    data["daily_drawdown"] = data["close"] / rolling_max - 1
    data["max_drawdown"] = data["daily_drawdown"].rolling(window, min_periods=1).min()
    return data


def calculate_sharpe_ratio(data: pd.DataFrame) -> (float, float):
    """
    计算夏普比率
    :param data: 股票数据
    :return: float, float
    """
    daily_return = data["close"].pct_change()
    daily_return_mean = daily_return.mean()
    daily_return_std = daily_return.std()
    sharpe_daily = daily_return_mean / daily_return_std
    sharpe_annual = sharpe_daily * np.sqrt(252)
    return sharpe_daily, sharpe_annual


def import_data_wrapper(code, frequency="daily", start_date=None, end_date=None, use_cols=None):
    data = st.import_data(code, "price", start_date, end_date)
    if frequency != "daily":
        data = st.transfer_price_frequency(data, frequency)
    if use_cols is not None:
        data = data[use_cols]
    # 数据有误
    if data.index.duplicated().any():
        st.update_daily_price(code, "price", fetch=True)
    return data
