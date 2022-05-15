import data.stock as st
import numpy as np
import pandas as pd

# pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)


def reduce_signal(data: pd.DataFrame) -> pd.DataFrame:
    """
    整合买入卖出信号
    :param data: 股票数据，包含 buy_signal 和 sell_signal 列
    :return: data
    """
    data["buy_signal"] = np.where((data["buy_signal"] == 1) & (data["buy_signal"].shift(1) == 1), 0, data["buy_signal"])
    data["sell_signal"] = np.where((data["sell_signal"] == -1) & (data["sell_signal"].shift(1) == -1), 0, data["sell_signal"])
    data["signal"] = data["buy_signal"] + data["sell_signal"]
    return data


def calculate_profit_pct(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算单次收益率：开仓，平仓（开仓全部股数）
    :param data: 股票数据，包含 signal 列
    :return: data
    """
    data.drop(data[data["signal"] == 0].index, inplace=True)
    data["profit_pct"] = data["close"].pct_change()
    data = data[data["signal"] == -1]
    return data


def calculate_cum_profit(data: pd.DataFrame) -> pd.DataFrame:
    """
    计算累积收益率
    :param data: 股票数据，包含 profit_pct 列
    :return: data
    """
    data["cum_profit_pct"] = (data["profit_pct"] + 1).cumprod() - 1
    data.dropna(inplace=True)
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


def import_data_wrapper(code: str, frequency: str = "daily", start_date: str = None, end_date: str = None, local: bool = True) -> pd.DataFrame:
    if local:
        data = st.import_data(code, "price", start_date, end_date)
        if frequency != "daily":
            data = st.transfer_price_frequency(data, frequency)
    else:
        data = st.get_single_price(code, frequency, export=True)
    return data
