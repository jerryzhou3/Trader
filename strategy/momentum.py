# ！/usr/bin/env python
# encoding: utf-8
"""
@Author: Yeju Zhou
@File: momentum.py
@Time: 2022/5/14 19:35
@Describe: 动量策略（正向）
"""
import sys
import traceback
from strategy.base import *
import matplotlib.pyplot as plt


def get_index_stock_price(start_date=None, end_date=None, index_symbol="000300.XSHG"):
    """
    获取股票收盘价数据，并拼接为一个df
    :param start_date: str
    :param end_date: str
    :param index_symbol: str
    :return data_concat: df，拼接后的数据表
    """
    use_cols = ["close"]
    # 获取股票列表代码：沪深300持有个股、创业板、上证
    stock_list = st.get_index_list(index_symbol)
    # 拼接收盘价数据
    data_concat = pd.DataFrame()
    # 获取股票数据
    for stock in stock_list:
        data = import_data_wrapper(stock, "daily", start_date, end_date, use_cols)
        index_array = [[stock] * len(use_cols), use_cols]
        index_tuple = list(zip(*index_array))
        data.columns = pd.MultiIndex.from_tuples(index_tuple)
        # 拼接多个股票的收盘价：日期 股票A收盘价 股票B收盘价 ...
        data_concat = pd.concat([data_concat, data], axis=1)
    return data_concat


def momentum(data, frequency="W", shift_n=1, top_n=2):
    """
    动量策略，买入📈的股票，卖出📉的股票
    :param data: 股票数据（多列股票）
    :param frequency: 业绩统计周期
    :param shift_n: 业绩评测回退周期
    :param top_n:
    :return:
    """
    # 转换时间频率：日->月
    # 默认使用 close 列
    data = st.transfer_price_frequency(data, frequency)
    # 计算过去N个月的收益率 = 期末值/期初值 - 1 =（期末-期初）/ 期初
    # optional：对数收益率 = log（期末值 / 期初值）
    # 生成交易信号：收益率排前n的>赢家组合>买入1，排最后n个>输家>卖出-1
    data = get_target_stocks(data, shift_n, top_n)
    data = reduce_signal(data)
    return data


def get_target_stocks(data, shift_n=1, top_n=2):
    """
    找到前n位和后n位短期收益率的股票，并产生交易信号
    :param data: df
    :param top_n: int, 表示要产生信号的个数
    :return signals: df, 返回0-1信号数据表
    """
    for multi_index in data.columns:
        code, _ = multi_index
        profit_pct_index = (code, "profit_pct")
        data[profit_pct_index] = data[multi_index] / data[multi_index].shift(shift_n) - 1
    data = data.sort_index(level=0, axis=1)
    # 初始化信号容器
    # 对data的每一行进行遍历，找里面的最大值，并利用bool函数标注0或1信号
    for date, row in data.iterrows():
        nlargest = row[:, "profit_pct"].nlargest(top_n)
        nsmallest = row[:, "profit_pct"].nsmallest(top_n)
        for index in row.index:
            code, _ = index
            signal = 0
            if code in nlargest.index:
                signal = 1
            elif code in nsmallest.index:
                signal = -1
            data.loc[date, (code, "signal")] = signal
    data = data.sort_index(level=0, axis=1)
    return data


if __name__ == '__main__':
    data = get_index_stock_price(start_date="2022-01-01")
    data = momentum(data, top_n=1)
    data = calculate_profit_pct(data)
    print(data)
    data, cum_profit_by_code = calculate_cum_profit(data)
    print(data)
    print(cum_profit_by_code)
    plt.bar(cum_profit_by_code.keys(), cum_profit_by_code.values())
    plt.show()
