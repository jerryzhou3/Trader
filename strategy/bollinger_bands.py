# ！/usr/bin/env python
# encoding: utf-8
"""
@Author: Yeju Zhou
@File: bollinger_bands.py
@Time: 2022/5/14 16:55
@Describe: 布林道策略
"""

from data.stock import *
from strategy.base import *
from strategy.statistical_test import *
from tqdm import tqdm
from codetiming import Timer
import matplotlib.pyplot as plt


def bollinger_bands(data: pd.DataFrame, window=20, k_std=2):
    """
    布林道策略
    Reference: https://www.investopedia.com/terms/b/bollingerbands.asp
    :param data: 股票行情数据
    :param window: 移动平均线窗口
    :return:
    """
    data["typical_price"] = (data["high"] + data["low"] + data["close"]) / 3
    data["ma"] = data["typical_price"].rolling(window=window).mean()
    data["mstd"] = data["typical_price"].rolling(window=window).std()
    data["upper"] = data["ma"] + k_std * data["mstd"]
    data["lower"] = data["ma"] - k_std * data["mstd"]
    data["buy_signal"] = np.where(data["typical_price"] < data["lower"], 1, 0)
    data["sell_signal"] = np.where(data["typical_price"] > data["upper"], -1, 0)
    data = reduce_signal(data)
    data.drop(columns=["buy_signal", "sell_signal"], inplace=True)
    data = data[data["signal"] != 0]
    return data


if __name__ == "__main__":
    code_list = get_local_stock_list()
    with Timer(text=f"{len(code_list)} stocks " + "running time: {:0.4f} seconds"):
        for code in tqdm(code_list):
            print("-----------------------")
            print(f"{code}")
            data = import_data_wrapper(code, start_date="2020-01-01")
            data = bollinger_bands(data)
            data = calculate_profit_pct(data)
            data = calculate_cum_profit(data)
            valid_trading_count = len(data)
            print(f"有效交易次数：{valid_trading_count}")
            if valid_trading_count > 0:
                print(f"累积收益率：{data['cum_profit_pct'].iloc[-1]}")
                profit_pct = data["profit_pct"]
                t, p = ttest(profit_pct)
                winning_rate = calculate_winning_rate(data)
                data[["profit_pct", "cum_profit_pct"]].plot()
                # plt.plot(data.index, [0] * len(data))
                # plt.show()
                # plt.clf()
            print("-----------------------")
