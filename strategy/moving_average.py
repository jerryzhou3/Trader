# ！/usr/bin/env python
# encoding: utf-8
"""
@Author: Yeju Zhou
@File: ma_strategy.py
@Time: 2022/5/14 14:52
@Describe: 双均线策略
"""

from base import *
from statistical_test import *
import matplotlib.pyplot as plt


def ma_strategy(data: pd.DataFrame, short_window: int = 5, long_window: int = 20) -> pd.DataFrame:
    """
    双均线策略
    :param data: 行情数据，包含 close 列
    :param short_window: 短期移动平均线窗口大小，默认5
    :param long_window: 长期移动平均线窗口大小，默认20
    :return:
    """
    # 计算技术指标：5日20日均线
    data["short_ma"] = data["close"].rolling(window=short_window).mean()
    data["long_ma"] = data["close"].rolling(window=long_window).mean()
    # 生成信号：金叉买入，死叉卖出
    data["buy_signal"] = np.where(data["short_ma"] > data["long_ma"], 1, 0)
    data["sell_signal"] = np.where(data["short_ma"] < data["long_ma"], -1, 0)
    # 整合信号
    data = reduce_signal(data)
    data.drop(columns=["buy_signal", "sell_signal"], inplace=True)
    data = data[data["signal"] != 0]
    return data


if __name__ == "__main__":
    code_list = ["000001.XSHE", "002466.XSHE", "002460.XSHE", "000762.XSHE"]
    for code in code_list:
        data = import_data_wrapper(code, start_date="2020-01-01")
        data = ma_strategy(data)
        data = calculate_profit_pct(data)
        data = calculate_cum_profit(data)
        profit_pct = data["profit_pct"]
        t, p = ttest(profit_pct)
        winning_rate = calculate_winning_rate(data)
        data[["profit_pct", "cum_profit_pct"]].plot()
        plt.plot(data.index, [0] * len(data))
        plt.show()
        plt.clf()
