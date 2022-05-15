# ！/usr/bin/env python
# encoding: utf-8
"""
@Author:
@File: simulator.py
@Time: 2022/5/14 20:53
@Describe:
"""

from strategy.bollinger_bands import bollinger_bands
from strategy.moving_average import ma_strategy
from codetiming import Timer
from strategy.base import *
from strategy.statistical_test import *
from util.string_util import StringBuilder
from celery_interface import app

strategy_dict = {"boll": bollinger_bands, "ma": ma_strategy}


@app.task
def simulate_strategy(strategy: str, code, start_date=None, end_date=None):
    output = StringBuilder()
    output.append("------------------------------")
    output.append(f"股票代码：{code}")
    output.append(f"策略：{strategy}")
    with Timer(text="运行时间: {:0.4f} seconds", logger=output.append):
        data = import_data_wrapper(code, start_date=start_date, end_date=end_date)
        data = strategy_dict[strategy](data)
        data = calculate_profit_pct(data)
        data = calculate_cum_profit(data)
        valid_trading_count = len(data)
        output.append(f"有效交易次数：{valid_trading_count}")
        if valid_trading_count > 0:
            output.append(f"累积收益率：{data['cum_profit_pct'].iloc[-1]}")
            profit_pct = data["profit_pct"]
            t, p = ttest(profit_pct, logger=output.append)
            winning_rate = calculate_winning_rate(data, logger=output.append)
            data[["profit_pct", "cum_profit_pct"]].plot()
    output.append("------------------------------")
    return output.to_string()


if __name__ == "__main__":
    output = simulate_strategy("boll", "000001.XSHE", "2020-01-01")
    print(output)
